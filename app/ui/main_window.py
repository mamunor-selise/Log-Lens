from typing import Optional
from app.core.services.log_service import LogService
from app.ui.models.log_table_model import LogTableModel

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLineEdit, QPushButton, QCheckBox, QTableView, QTextEdit,
        QSplitter, QFileDialog, QLabel, QStatusBar
    )
    from PySide6.QtCore import Qt
    HAS_PYSIDE6 = True
except ImportError:
    HAS_PYSIDE6 = False

class MainWindow(QMainWindow if HAS_PYSIDE6 else object):  # type: ignore
    """Main Application Window for Log-Lens."""

    def __init__(self, log_service: Optional[LogService] = None):
        if not HAS_PYSIDE6:
            self.log_service = log_service or LogService()
            return

        super().__init__()
        self.setWindowTitle("Log-Lens — Desktop Log Viewer & Analyzer")
        self.resize(1280, 800)

        self.log_service = log_service or LogService()
        self.table_model = LogTableModel(self.log_service)

        self._setup_ui()

    def _setup_ui(self) -> None:
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # 1. Search Toolbar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search log messages or raw text...")
        self.case_checkbox = QCheckBox("Case Sensitive")
        self.regex_checkbox = QCheckBox("Regex")
        self.open_btn = QPushButton("Open File/Folder")
        self.open_btn.clicked.connect(self._open_file_dialog)

        search_layout.addWidget(self.open_btn)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.case_checkbox)
        search_layout.addWidget(self.regex_checkbox)

        # 2. Main Content Splitter
        splitter = QSplitter(Qt.Vertical)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)

        self.detail_panel = QTextEdit()
        self.detail_panel.setReadOnly(True)
        self.detail_panel.setPlaceholderText("Select a log row above to view raw log entry & stack trace...")

        splitter.addWidget(self.table_view)
        splitter.addWidget(self.detail_panel)
        splitter.setSizes([500, 250])

        main_layout.addLayout(search_layout)
        main_layout.addWidget(splitter)

        self.setCentralWidget(central_widget)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def _open_file_dialog(self) -> None:
        if not HAS_PYSIDE6:
            return
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Log File", "", "Log Files (*.log *.txt *.log.*);;All Files (*)")
        if filepath:
            count = self.log_service.open_file(filepath)
            filtered = self.log_service.apply_filter()
            self.table_model.set_entries(filtered)
            self.status_bar.showMessage(f"Opened {filepath} ({count} entries indexed)")
