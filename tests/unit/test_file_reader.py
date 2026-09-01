import unittest
import tempfile
from pathlib import Path
from app.core.readers.file_reader import LargeFileReader

class TestFileReader(unittest.TestCase):
    def test_large_file_reader_indexing_and_lazy_load(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            log_content = (
                "2026-08-31 18:26:00 INFO Initializing service\n"
                "2026-08-31 18:26:01 ERROR Connection failed\n"
                "   at Database.Connect()\n"
                "2026-08-31 18:26:02 WARN Retrying connection...\n"
            )
            test_file = tmp_path / "PCXWebHost.log.1659"
            test_file.write_text(log_content, encoding="utf-8")

            reader = LargeFileReader(filepath=test_file)
            index_entries = list(reader.build_index())

            self.assertEqual(len(index_entries), 3)
            self.assertEqual(index_entries[0].level.value, "INFO")
            self.assertEqual(index_entries[1].level.value, "ERROR")
            self.assertEqual(index_entries[2].level.value, "WARNING")

            # Test Tier 2 lazy load of entry 1 (ERROR + stacktrace)
            full_entry = reader.read_entry_at_index(index_entries[1])
            self.assertEqual(full_entry.level, "ERROR")
            self.assertIn("Connection failed", full_entry.message)
            self.assertIn("Database.Connect()", full_entry.raw_text)

if __name__ == "__main__":
    unittest.main()
