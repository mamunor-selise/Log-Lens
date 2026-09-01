import re
from dataclasses import dataclass
from typing import Optional, Pattern
from app.core.models.log_entry import LogEntry

@dataclass(slots=True)
class SearchQuery:
    pattern: str
    case_sensitive: bool = False
    is_regex: bool = False
    whole_word: bool = False

class SearchEngine:
    """Fast search engine supporting plain-text, whole-word, and regex matching."""

    def matches(self, entry: LogEntry, query: SearchQuery) -> bool:
        if not query.pattern:
            return True

        text = entry.raw_text

        if query.is_regex:
            try:
                flags = 0 if query.case_sensitive else re.IGNORECASE
                compiled = re.compile(query.pattern, flags)
                return bool(compiled.search(text))
            except re.error:
                return False

        if query.whole_word:
            flags = 0 if query.case_sensitive else re.IGNORECASE
            escaped = re.escape(query.pattern)
            compiled = re.compile(rf"\b{escaped}\b", flags)
            return bool(compiled.search(text))

        if not query.case_sensitive:
            return query.pattern.lower() in text.lower()
        return query.pattern in text
