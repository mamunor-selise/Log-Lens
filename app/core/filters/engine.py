from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Set
from app.core.models.log_entry import LogIndexEntry, LogLevel

class BaseFilter(ABC):
    @abstractmethod
    def matches(self, index_entry: LogIndexEntry) -> bool:
        pass

class LevelFilter(BaseFilter):
    def __init__(self, allowed_levels: Set[LogLevel]):
        self.allowed_levels = allowed_levels

    def matches(self, index_entry: LogIndexEntry) -> bool:
        if not self.allowed_levels:
            return True
        return index_entry.level in self.allowed_levels

class DateRangeFilter(BaseFilter):
    def __init__(self, start_time: Optional[datetime] = None, end_time: Optional[datetime] = None):
        self.start_epoch = start_time.timestamp() if start_time else None
        self.end_epoch = end_time.timestamp() if end_time else None

    def matches(self, index_entry: LogIndexEntry) -> bool:
        if index_entry.timestamp_epoch is None:
            return True
        if self.start_epoch and index_entry.timestamp_epoch < self.start_epoch:
            return False
        if self.end_epoch and index_entry.timestamp_epoch > self.end_epoch:
            return False
        return True

class TextFilter(BaseFilter):
    def __init__(self, text: str, case_sensitive: bool = False):
        self.text = text if case_sensitive else text.lower()
        self.case_sensitive = case_sensitive

    def matches(self, index_entry: LogIndexEntry) -> bool:
        # Note: Text filtering on entry contents is evaluated during search/detail fetch
        return True

class FilterEngine:
    """Composes multiple filters to evaluate LogIndexEntry objects."""

    def __init__(self):
        self.filters: List[BaseFilter] = []

    def add_filter(self, filter_obj: BaseFilter) -> None:
        self.filters.append(filter_obj)

    def clear(self) -> None:
        self.filters.clear()

    def eval(self, index_entry: LogIndexEntry) -> bool:
        for f in self.filters:
            if not f.matches(index_entry):
                return False
        return True
