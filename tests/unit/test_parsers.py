import unittest
from datetime import datetime
from app.core.parsers.plain_text import PlainTextParser
from app.core.parsers.multiline import MultiLineBoundaryDetector

class TestParsers(unittest.TestCase):
    def test_multiline_boundary_detector_header_and_continuation(self):
        detector = MultiLineBoundaryDetector()
        header1 = "2026-08-31 18:26:00 ERROR [PCXWebHost] Request failed with exception"
        continuation1 = "   System.NullReferenceException: Object reference not set to an instance"
        continuation2 = "      at PCX.Service.ProcessRequest() in Service.cs:line 42"
        header2 = "2026-08-31 18:26:05 INFO [PCXWebHost] Request completed successfully"

        self.assertTrue(detector.is_entry_header(header1))
        self.assertFalse(detector.is_entry_header(continuation1))
        self.assertFalse(detector.is_entry_header(continuation2))
        self.assertTrue(detector.is_entry_header(header2))

    def test_plain_text_parser_level_and_timestamp_extraction(self):
        parser = PlainTextParser()
        raw_lines = [
            "2026-08-31 18:26:00 ERROR Failed to process request",
            "System.NullReferenceException: Object reference not set...",
            "   at SomeNamespace.Service.Process()",
        ]
        raw_text = "\n".join(raw_lines)
        entry = parser.parse_entry(raw_text=raw_text, source_file="test.log", line_start=1, line_end=3)

        self.assertEqual(entry.level, "ERROR")
        self.assertEqual(entry.timestamp, datetime(2026, 8, 31, 18, 26, 0))
        self.assertIn("Failed to process request", entry.message)
        self.assertIn("NullReferenceException", entry.raw_text)

if __name__ == "__main__":
    unittest.main()
