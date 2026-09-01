from datetime import datetime
from typing import Any, List, Optional
from app.core.models.log_entry import LogIndexEntry, LogLevel
from app.core.services.log_service import LogService

try:
    from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
    HAS_PYSIDE6 = True
except ImportError:
    # Headless stub when PySide6 is not installed
    class QAbstractTableModel:  # type: ignore
        pass
    class QModelIndex:  # type: ignore
        pass
    class Qt:  # type: ignore
        DisplayRole = 0
    HAS_PYSIDE6 = False

class LogTableModel(QAbstractTableModel):
    """Virtualized QAbstractTableModel supporting millions of log rows via lazy fetching."""

    COLUMNS = ["#", "Timestamp", "Level", "Source File", "Message Summary"]

    def __init__(self, log_service: LogService):
        super().__init__()
        self._log_service = log_service
        self._entries: List[LogIndexEntry] = []
        self._loaded_count = 0
        self._batch_size = 500

    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        if HAS_PYSIDE6 and hasattr(super(), "createIndex"):
            return super().createIndex(row, column)
        # Headless stub index container
        class StubIndex:
            def __init__(self, r: int, c: int):
                self._r = r
                self._c = c
            def isValid(self) -> bool:
                return True
            def row(self) -> int:
                return self._r
            def column(self) -> int:
                return self._c
        return StubIndex(row, column)  # type: ignore

    def set_entries(self, entries: List[LogIndexEntry]) -> None:
        if HAS_PYSIDE6:
            self.beginResetModel()
        self._entries = entries
        self._loaded_count = min(self._batch_size, len(entries))
        if HAS_PYSIDE6:
            self.endResetModel()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return self._loaded_count

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.COLUMNS)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        if not index.isValid() or role != Qt.DisplayRole:
            return None

        row = index.row()
        col = index.column()

        if row >= len(self._entries):
            return None

        index_entry = self._entries[row]

        if col == 0:
            return index_entry.entry_id + 1
        elif col == 1:
            if index_entry.timestamp_epoch:
                return datetime.fromtimestamp(index_entry.timestamp_epoch).strftime("%Y-%m-%d %H:%M:%S")
            return "Unknown"
        elif col == 2:
            return index_entry.level.value
        elif col == 3:
            return index_entry.file_id
        elif col == 4:
            # Lazy fetch message summary
            try:
                full_entry = self._log_service.get_entry_at(index_entry)
                return full_entry.message
            except Exception:
                return "<loading...>"
        return None

    def headerData(self, section: int, orientation: Any, role: int = Qt.DisplayRole) -> Any:
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            if 0 <= section < len(self.COLUMNS):
                return self.COLUMNS[section]
        return None

    def canFetchMore(self, parent: QModelIndex = QModelIndex()) -> bool:
        return self._loaded_count < len(self._entries)

    def fetchMore(self, parent: QModelIndex = QModelIndex()) -> None:
        remainder = len(self._entries) - self._loaded_count
        items_to_fetch = min(remainder, self._batch_size)

        if items_to_fetch <= 0:
            return

        if HAS_PYSIDE6:
            self.beginInsertRows(QModelIndex(), self._loaded_count, self._loaded_count + items_to_fetch - 1)
        self._loaded_count += items_to_fetch
        if HAS_PYSIDE6:
            self.endInsertRows()
