import sys
from app.core.services.log_service import LogService
from app.ui.main_window import MainWindow

def main():
    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication(sys.argv)
        service = LogService()
        window = MainWindow(log_service=service)
        window.show()
        sys.exit(app.exec())
    except ImportError:
        print("PySide6 is not installed. Running in headless mode.")
        service = LogService()
        print(f"LogService initialized successfully. Total entries: {service.get_total_entry_count()}")

if __name__ == "__main__":
    main()
