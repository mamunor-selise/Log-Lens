from pathlib import Path
from typing import Dict, List, Optional, Set, Union
from app.core.filters.engine import FilterEngine, LevelFilter
from app.core.models.log_entry import LogEntry, LogIndexEntry, LogLevel
from app.core.readers.file_reader import LargeFileReader
from app.core.search.engine import SearchEngine, SearchQuery
from app.infrastructure.configuration.remote_ip_config import RemoteIPConfig

class LogService:
    """Application Service coordinating readers, parsers, filters, search engines, and remote configs."""

    def __init__(self, remote_ip_config: Optional[RemoteIPConfig] = None):
        self._readers: Dict[str, LargeFileReader] = {}
        self._index: List[LogIndexEntry] = []
        self._filter_engine = FilterEngine()
        self._search_engine = SearchEngine()
        self.remote_ip_config = remote_ip_config or RemoteIPConfig()

    def get_remote_unc_path(self, share_name: str) -> str:
        return self.remote_ip_config.get_share_unc_path(share_name)

    def clear_session(self) -> None:
        self._readers.clear()
        self._index.clear()

    def open_file(self, filepath: Union[str, Path]) -> int:
        path = Path(filepath)
        reader = LargeFileReader(path)
        self._readers[path.name] = reader

        entries = list(reader.build_index())
        self._index.extend(entries)
        return len(entries)

    def open_directory(self, dirpath: Union[str, Path], recursive: bool = True) -> int:
        path = Path(dirpath)
        if not path.exists() or not path.is_dir():
            return 0

        self.clear_session()
        total_entries = 0

        pattern_iter = path.rglob("*") if recursive else path.glob("*")
        for item in pattern_iter:
            if item.is_file() and self._is_log_file(item):
                try:
                    reader = LargeFileReader(item)
                    self._readers[item.name] = reader
                    entries = list(reader.build_index())
                    self._index.extend(entries)
                    total_entries += len(entries)
                except Exception:
                    continue

        return total_entries

    def _is_log_file(self, path: Path) -> bool:
        name = path.name.lower()
        if name.endswith(".log") or name.endswith(".txt"):
            return True
        # Check rotated pattern .log.1659
        if ".log." in name:
            parts = name.split(".log.")
            if len(parts) > 1 and parts[-1].isdigit():
                return True
        return False

    def get_total_entry_count(self) -> int:
        return len(self._index)

    def apply_filter(self, levels: Optional[Set[LogLevel]] = None) -> List[LogIndexEntry]:
        self._filter_engine.clear()
        if levels:
            self._filter_engine.add_filter(LevelFilter(allowed_levels=levels))

        return [e for e in self._index if self._filter_engine.eval(e)]

    def search_entries(self, entries: List[LogIndexEntry], query: SearchQuery) -> List[LogIndexEntry]:
        results = []
        for index_entry in entries:
            full_entry = self.get_entry_at(index_entry)
            if self._search_engine.matches(full_entry, query):
                results.append(index_entry)
        return results

    def get_entry_at(self, index_entry: LogIndexEntry) -> LogEntry:
        reader = self._readers.get(index_entry.file_id)
        if not reader:
            raise KeyError(f"Reader for file {index_entry.file_id} not registered.")
        return reader.read_entry_at_index(index_entry)
