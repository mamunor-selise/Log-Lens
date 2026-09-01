from abc import ABC, abstractmethod
from typing import Optional
from app.core.models.log_entry import LogEntry

class BaseParser(ABC):
    """Abstract base class for log entry parsers."""

    @abstractmethod
    def parse_entry(
        self,
        raw_text: str,
        source_file: str,
        line_start: int,
        line_end: int,
    ) -> LogEntry:
        """Parse raw log text into a normalized LogEntry object."""
        pass
