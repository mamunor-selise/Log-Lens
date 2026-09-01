import re
from typing import List, Pattern

class MultiLineBoundaryDetector:
    """Detects multi-line entry boundaries and continuation lines."""

    def __init__(self, custom_timestamp_patterns: Optional[List[str]] = None):
        patterns = [
            r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?",  # ISO / YYYY-MM-DD HH:MM:SS
            r"^\[?\d{4}/\d{2}/\d{2}[ T]\d{2}:\d{2}:\d{2}",
            r"^(?:TRACE|DEBUG|INFO|WARN|WARNING|ERROR|FATAL)\b",
        ]
        if custom_timestamp_patterns:
            patterns = custom_timestamp_patterns + patterns

        self._header_res: List[Pattern[str]] = [re.compile(p, re.IGNORECASE) for p in patterns]
        self._continuation_res: List[Pattern[str]] = [
            re.compile(r"^\s+"),                     # Indented line (whitespace or tab)
            re.compile(r"^\s*at\s+"),                 # Stack trace 'at ...'
            re.compile(r"^\s*Caused by:"),            # Stack trace 'Caused by:'
            re.compile(r"^\s*\.\.\.\s+\d+\s+more"),   # Java stack trace remainder
            re.compile(r"^\s*[\{\[\}\]]"),            # JSON continuation bracket
        ]

    def is_entry_header(self, line: str) -> bool:
        """Return True if line matches a new log entry header."""
        stripped = line.strip()
        if not stripped:
            return False
        # Check continuation patterns first
        for cre in self._continuation_res:
            if cre.search(line):
                return False
        # Check header patterns
        for hre in self._header_res:
            if hre.search(line):
                return True
        return True  # Fallback default: non-indented line is treated as header
