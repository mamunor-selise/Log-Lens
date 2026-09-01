import unittest
from datetime import datetime
from app.core.models.log_entry import LogEntry, LogIndexEntry, LogLevel

class TestLogEntry(unittest.TestCase):
    def test_log_index_entry_creation(self):
        index_entry = LogIndexEntry(
            entry_id=1,
            file_id="PCXWebHost.log.1659",
            byte_offset=1024,
            length=256,
            timestamp_epoch=1725102600.0,
            level=LogLevel.ERROR,
        )
        self.assertEqual(index_entry.entry_id, 1)
        self.assertEqual(index_entry.file_id, "PCXWebHost.log.1659")
        self.assertEqual(index_entry.byte_offset, 1024)
        self.assertEqual(index_entry.length, 256)
        self.assertEqual(index_entry.level, LogLevel.ERROR)

    def test_log_entry_creation_and_raw_text_preservation(self):
        entry = LogEntry(
            source_file="PCXWebHost.log.1659",
            line_start=10,
            line_end=14,
            timestamp=datetime(2026, 8, 31, 18, 26, 0),
            level="ERROR",
            message="Failed to connect to MongoDB server",
            raw_text="2026-08-31 18:26:00 ERROR Failed to connect to MongoDB server\n   at System.Data.SqlClient...",
            metadata={"correlation_id": "req-123", "service": "PCXWebHost"},
            exception_type="TimeoutException",
            correlation_id="req-123",
        )
        self.assertEqual(entry.source_file, "PCXWebHost.log.1659")
        self.assertEqual(entry.level, "ERROR")
        self.assertIn("MongoDB", entry.message)
        self.assertTrue(entry.raw_text.startswith("2026-08-31"))
        self.assertEqual(entry.metadata["correlation_id"], "req-123")

if __name__ == "__main__":
    unittest.main()
