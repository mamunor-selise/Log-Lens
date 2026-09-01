import unittest
import tempfile
from pathlib import Path
from app.core.services.log_service import LogService
from app.ui.models.log_table_model import LogTableModel

class TestLogTableModel(unittest.TestCase):
    def test_log_table_model_basic(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            log_content = (
                "2026-08-31 18:26:00 INFO Initializing service\n"
                "2026-08-31 18:26:01 ERROR Connection failed\n"
            )
            test_file = tmp_path / "PCXWebHost.log.1659"
            test_file.write_text(log_content, encoding="utf-8")

            service = LogService()
            service.open_file(test_file)
            entries = service.apply_filter()

            model = LogTableModel(service)
            model.set_entries(entries)

            self.assertEqual(model.rowCount(), 2)
            self.assertEqual(model.columnCount(), 5)
            self.assertEqual(model.data(model.index(0, 2)), "INFO")
            self.assertEqual(model.data(model.index(1, 2)), "ERROR")

if __name__ == "__main__":
    unittest.main()
