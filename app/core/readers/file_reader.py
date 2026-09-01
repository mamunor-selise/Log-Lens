import io
from pathlib import Path
from typing import Iterator, Optional, Union
from app.core.models.log_entry import LogEntry, LogIndexEntry, LogLevel
from app.core.parsers.multiline import MultiLineBoundaryDetector
from app.core.parsers.plain_text import PlainTextParser
from app.core.readers.base import BaseLogReader

class LargeFileReader(BaseLogReader):
    """Large file reader implementing Tier 1 Indexing & Tier 2 Lazy Loading."""

    def __init__(self, filepath: Union[str, Path], encoding_fallback: str = "latin-1"):
        self.filepath = Path(filepath)
        self.encoding_fallback = encoding_fallback
        self._boundary_detector = MultiLineBoundaryDetector()
        self._parser = PlainTextParser()

    def build_index(self) -> Iterator[LogIndexEntry]:
        """Read file line-by-line using byte offsets to build lightweight Tier 1 Index."""
        if not self.filepath.exists():
            raise FileNotFoundError(f"Log file not found: {self.filepath}")

        entry_id = 0
        file_id = self.filepath.name

        with open(self.filepath, "rb") as f:
            current_entry_offset = 0
            current_entry_bytes = bytearray()
            first_line_of_entry = ""
            line_offset = 0

            for line_bytes in f:
                line_str = self._decode_bytes(line_bytes)
                is_header = self._boundary_detector.is_entry_header(line_str)

                if is_header and current_entry_bytes:
                    # Flush previous entry
                    level = LogLevel.normalize(self._parser._parse_level(first_line_of_entry))
                    dt = self._parser._parse_timestamp(first_line_of_entry)
                    ts_epoch = dt.timestamp() if dt else None

                    yield LogIndexEntry(
                        entry_id=entry_id,
                        file_id=file_id,
                        byte_offset=current_entry_offset,
                        length=len(current_entry_bytes),
                        timestamp_epoch=ts_epoch,
                        level=level,
                    )
                    entry_id += 1
                    current_entry_offset = line_offset
                    current_entry_bytes = bytearray()
                    first_line_of_entry = line_str
                elif not current_entry_bytes:
                    current_entry_offset = line_offset
                    first_line_of_entry = line_str

                current_entry_bytes.extend(line_bytes)
                line_offset += len(line_bytes)

            # Flush final entry
            if current_entry_bytes:
                level = LogLevel.normalize(self._parser._parse_level(first_line_of_entry))
                dt = self._parser._parse_timestamp(first_line_of_entry)
                ts_epoch = dt.timestamp() if dt else None

                yield LogIndexEntry(
                    entry_id=entry_id,
                    file_id=file_id,
                    byte_offset=current_entry_offset,
                    length=len(current_entry_bytes),
                    timestamp_epoch=ts_epoch,
                    level=level,
                )

    def read_entry_at_index(self, index_entry: LogIndexEntry) -> LogEntry:
        """Lazy load full Tier 2 LogEntry from disk using byte offset."""
        with open(self.filepath, "rb") as f:
            f.seek(index_entry.byte_offset)
            raw_bytes = f.read(index_entry.length)

        raw_text = self._decode_bytes(raw_bytes)
        line_count = raw_text.count("\n") + 1

        return self._parser.parse_entry(
            raw_text=raw_text,
            source_file=index_entry.file_id,
            line_start=index_entry.entry_id,
            line_end=index_entry.entry_id + line_count - 1,
        )

    def _decode_bytes(self, raw_bytes: bytes) -> str:
        try:
            return raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return raw_bytes.decode(self.encoding_fallback, errors="replace")
