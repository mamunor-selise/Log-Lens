from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

class LogLevel(str, Enum):
    TRACE = "TRACE"
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    WARNING = "WARNING"
    ERROR = "ERROR"
    FATAL = "FATAL"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def normalize(cls, level_str: Optional[str]) -> "LogLevel":
        if not level_str:
            return cls.UNKNOWN
        clean = level_str.strip().upper()
        if clean == "WARN":
            return cls.WARNING
        try:
            return cls(clean)
        except ValueError:
            return cls.UNKNOWN

@dataclass(slots=True)
class LogIndexEntry:
    """Lightweight Tier 1 index descriptor held in memory (<32 bytes footprint per entry)."""
    entry_id: int
    file_id: str
    byte_offset: int
    length: int
    timestamp_epoch: Optional[float] = None
    level: LogLevel = LogLevel.UNKNOWN

@dataclass(slots=True)
class LogEntry:
    """Full Tier 2 Log Entry model populated lazily for visible/selected entries."""
    source_file: str
    line_start: int
    line_end: int
    timestamp: Optional[datetime] = None
    level: Optional[str] = "UNKNOWN"
    message: str = ""
    raw_text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    exception_type: Optional[str] = None
    correlation_id: Optional[str] = None
