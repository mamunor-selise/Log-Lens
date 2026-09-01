from abc import ABC, abstractmethod
from typing import Iterator
from app.core.models.log_entry import LogEntry, LogIndexEntry

class BaseLogReader(ABC):
    """Abstract base class for streaming log readers."""

    @abstractmethod
    def build_index(self) -> Iterator[LogIndexEntry]:
        """Streamingly build Tier 1 index descriptors."""
        pass

    @abstractmethod
    def read_entry_at_index(self, index_entry: LogIndexEntry) -> LogEntry:
        """Lazy load Tier 2 full LogEntry from disk using byte offset."""
        pass
