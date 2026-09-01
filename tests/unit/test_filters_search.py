import unittest
from app.core.models.log_entry import LogEntry, LogIndexEntry, LogLevel
from app.core.filters.engine import FilterEngine, LevelFilter
from app.core.search.engine import SearchEngine, SearchQuery

class TestFiltersSearch(unittest.TestCase):
    def test_level_filter(self):
        f = LevelFilter(allowed_levels={LogLevel.ERROR, LogLevel.FATAL})
        e1 = LogIndexEntry(entry_id=1, file_id="a.log", byte_offset=0, length=10, level=LogLevel.ERROR)
        e2 = LogIndexEntry(entry_id=2, file_id="a.log", byte_offset=10, length=10, level=LogLevel.INFO)
        
        self.assertTrue(f.matches(e1))
        self.assertFalse(f.matches(e2))

    def test_filter_engine_composition(self):
        engine = FilterEngine()
        engine.add_filter(LevelFilter(allowed_levels={LogLevel.ERROR}))
        
        e1 = LogIndexEntry(entry_id=1, file_id="a.log", byte_offset=0, length=10, level=LogLevel.ERROR)
        e2 = LogIndexEntry(entry_id=2, file_id="a.log", byte_offset=10, length=10, level=LogLevel.WARN)
        
        self.assertTrue(engine.eval(e1))
        self.assertFalse(engine.eval(e2))

    def test_search_engine_plain_and_regex(self):
        engine = SearchEngine()
        entry1 = LogEntry(
            source_file="test.log",
            line_start=1,
            line_end=1,
            message="MongoDB connection timeout error",
            raw_text="2026-08-31 ERROR MongoDB connection timeout error",
        )
        entry2 = LogEntry(
            source_file="test.log",
            line_start=2,
            line_end=2,
            message="User login succeeded",
            raw_text="2026-08-31 INFO User login succeeded",
        )

        query_plain = SearchQuery(pattern="mongodb", case_sensitive=False, is_regex=False)
        self.assertTrue(engine.matches(entry1, query_plain))
        self.assertFalse(engine.matches(entry2, query_plain))

        query_regex = SearchQuery(pattern=r"timeout|failed", case_sensitive=False, is_regex=True)
        self.assertTrue(engine.matches(entry1, query_regex))
        self.assertFalse(engine.matches(entry2, query_regex))

if __name__ == "__main__":
    unittest.main()
