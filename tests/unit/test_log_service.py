import unittest
from pathlib import Path
from app.core.services.log_service import LogService
from app.core.models.log_entry import LogLevel

class TestLogService(unittest.TestCase):
    def test_log_service_open_and_filter_session(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            log_content = (
                "2026-08-31 18:26:00 INFO Service initialized\n"
                "2026-08-31 18:26:01 ERROR Connection to DB timed out\n"
            )
            test_file = tmp_path / "PCXWebHost.log.1659"
            test_file.write_text(log_content, encoding="utf-8")

            service = LogService()
            count = service.open_file(test_file)

            self.assertEqual(count, 2)
            self.assertEqual(service.get_total_entry_count(), 2)

            # Apply filter for ERROR
            filtered_index = service.apply_filter(levels={LogLevel.ERROR})
            self.assertEqual(len(filtered_index), 1)
            self.assertEqual(filtered_index[0].level, LogLevel.ERROR)

            # Lazy fetch full entry
            entry = service.get_entry_at(filtered_index[0])
            self.assertIn("timed out", entry.message)

if __name__ == "__main__":
    unittest.main()
