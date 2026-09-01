import unittest
import tempfile
from pathlib import Path
from app.core.services.log_service import LogService
from app.core.models.log_entry import LogLevel
from app.core.search.engine import SearchQuery

class TestIntegration(unittest.TestCase):
    def test_full_log_investigation_workflow(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            log_file_1 = tmp_path / "PCXWebHost.log.1659"
            log_file_1.write_text(
                "2026-08-31 18:26:00 INFO [PCXWebHost] Service starting\n"
                "2026-08-31 18:26:05 ERROR [PCXWebHost] NullReferenceException at Service.Process()\n"
                "   at System.NullReferenceException: Object reference not set\n"
                "   at PCX.Controller.Execute()\n",
                encoding="utf-8"
            )

            log_file_2 = tmp_path / "PCXWebHost.log.1658"
            log_file_2.write_text(
                "2026-08-30 15:10:00 WARN [PCXWebHost] High memory usage detected\n"
                "2026-08-30 15:10:30 ERROR [PCXWebHost] TimeoutException connecting to MongoDB\n",
                encoding="utf-8"
            )

            service = LogService()
            count1 = service.open_file(log_file_1)
            count2 = service.open_file(log_file_2)

            self.assertEqual(count1, 2)
            self.assertEqual(count2, 2)
            self.assertEqual(service.get_total_entry_count(), 4)

            # Filter to ERROR level entries
            error_entries = service.apply_filter(levels={LogLevel.ERROR})
            self.assertEqual(len(error_entries), 2)

            # Search for MongoDB
            query = SearchQuery(pattern="MongoDB", case_sensitive=False, is_regex=False)
            search_results = service.search_entries(error_entries, query)
            self.assertEqual(len(search_results), 1)

            # Fetch full log entry detail
            detail = service.get_entry_at(search_results[0])
            self.assertEqual(detail.source_file, "PCXWebHost.log.1658")
            self.assertIn("MongoDB", detail.raw_text)
            self.assertEqual(detail.level, "ERROR")

if __name__ == "__main__":
    unittest.main()
