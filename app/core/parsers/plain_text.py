import re
from datetime import datetime
from typing import Optional, Tuple
from app.core.models.log_entry import LogEntry, LogLevel
from app.core.parsers.base import BaseParser

class PlainTextParser(BaseParser):
    """Parser for standard plain-text and multi-line log entries."""

    TIMESTAMP_PATTERNS = [
        ("%Y-%m-%d %H:%M:%S.%f", r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{1,6}"),
        ("%Y-%m-%d %H:%M:%S", r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"),
        ("%Y-%m-%dT%H:%M:%S.%f", r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{1,6}"),
        ("%Y-%m-%dT%H:%M:%S", r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"),
    ]

    LEVEL_REGEX = re.compile(
        r"\b(TRACE|DEBUG|INFO|WARN|WARNING|ERROR|FATAL)\b", re.IGNORECASE
    )

    CORRELATION_REGEX = re.compile(
        r"\b(?:correlationId|requestId|traceId|OrderId|id)[:=]\s*([a-zA-Z0-9_\-]+)", re.IGNORECASE
    )

    def parse_entry(
        self,
        raw_text: str,
        source_file: str,
        line_start: int,
        line_end: int,
    ) -> LogEntry:
        first_line = raw_text.splitlines()[0] if raw_text else ""
        
        # 1. Parse timestamp
        timestamp = self._parse_timestamp(first_line)
        
        # 2. Parse log level
        level = self._parse_level(first_line)
        
        # 3. Extract correlation ID / metadata
        correlation_id = self._parse_correlation_id(raw_text)
        metadata = {}
        if correlation_id:
            metadata["correlation_id"] = correlation_id

        # 4. Extract exception type if stack trace exists
        exception_type = self._parse_exception_type(raw_text)
        
        # 5. Extract main message
        message = first_line

        return LogEntry(
            source_file=source_file,
            line_start=line_start,
            line_end=line_end,
            timestamp=timestamp,
            level=level,
            message=message,
            raw_text=raw_text,
            metadata=metadata,
            exception_type=exception_type,
            correlation_id=correlation_id,
        )

    def _parse_timestamp(self, line: str) -> Optional[datetime]:
        for fmt, regex in self.TIMESTAMP_PATTERNS:
            match = re.search(regex, line)
            if match:
                dt_str = match.group(0)
                try:
                    # Truncate microseconds if more than 6 digits
                    if "." in dt_str:
                        base, ms = dt_str.split(".")
                        ms = ms[:6]
                        dt_str = f"{base}.{ms}"
                    return datetime.strptime(dt_str, fmt)
                except ValueError:
                    continue
        return None

    def _parse_level(self, line: str) -> str:
        match = self.LEVEL_REGEX.search(line)
        if match:
            return LogLevel.normalize(match.group(1)).value
        return LogLevel.UNKNOWN.value

    def _parse_correlation_id(self, text: str) -> Optional[str]:
        match = self.CORRELATION_REGEX.search(text)
        return match.group(1) if match else None

    def _parse_exception_type(self, text: str) -> Optional[str]:
        match = re.search(r"([a-zA-Z0-9_\.]+(?:Exception|Error)):", text)
        return match.group(1) if match else None
