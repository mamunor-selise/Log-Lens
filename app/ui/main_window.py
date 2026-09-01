from typing import Optional
from app.core.services.log_service import LogService
from app.infrastructure.configuration.remote_ip_config import Environment
from app.ui.models.log_table_model import LogTableModel

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLineEdit, QPushButton, QCheckBox, QTableView, QTextEdit,
        QSplitter, QFileDialog, QLabel, QStatusBar, QComboBox, QGroupBox
    )
    from PySide6.QtCore import Qt
    HAS_PYSIDE6 = True
except ImportError:
    HAS_PYSIDE6 = False

class MainWindow(QMainWindow if HAS_PYSIDE6 else object):  # type: ignore
    """Main Application Window for Log-Lens."""

    def __init__(self, log_service: Optional[LogService] = None):
        self.log_service = log_service or LogService()
        if not HAS_PYSIDE6:
            return

        if QApplication.instance() is None:
            self._qapp = QApplication([])

        super().__init__()
        self.setWindowTitle("Log-Lens — Desktop Log Viewer & Analyzer")
        self.resize(1280, 850)

        self.table_model = LogTableModel(self.log_service)
        self._setup_ui()

    def _setup_ui(self) -> None:
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # 1. Environment & Remote IP Configuration Bar
        config_group = QGroupBox("Environment & Remote Log Server Configuration")
        config_layout = QHBoxLayout(config_group)

        env_label = QLabel("Environment:")
        self.env_combo = QComboBox()
        self.env_combo.addItems(["Development", "Staging", "Production"])
        
        # Set initial index based on config
        current_env = self.log_service.remote_ip_config.get_environment()
        if current_env == Environment.STAGING:
            self.env_combo.setCurrentIndex(1)
        elif current_env == Environment.PRODUCTION:
            self.env_combo.setCurrentIndex(2)
        else:
            self.env_combo.setCurrentIndex(0)

        ip_label = QLabel("Remote IP:")
        self.ip_input = QLineEdit()
        self.ip_input.setText(self.log_service.remote_ip_config.get_remote_ip())

        self.unc_preview_label = QLabel(f"UNC Root: {self.log_service.get_remote_unc_path('AKS-Stg-Logs')}")
        self.unc_preview_label.setStyleSheet("color: #0066cc; font-weight: bold;")

        self.env_combo.currentIndexChanged.connect(self._on_env_changed)
        self.ip_input.textChanged.connect(self._on_ip_changed)

        config_layout.addWidget(env_label)
        config_layout.addWidget(self.env_combo)
        config_layout.addWidget(ip_label)
        config_layout.addWidget(self.ip_input)
        config_layout.addWidget(self.unc_preview_label)

        # 2. Search Toolbar
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

        # 3. Main Content Splitter
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

        main_layout.addWidget(config_group)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(splitter)

        self.setCentralWidget(central_widget)
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status_message()

    def _on_env_changed(self, index: int) -> None:
        env_map = [Environment.DEVELOPMENT, Environment.STAGING, Environment.PRODUCTION]
        selected_env = env_map[index]
        self.log_service.remote_ip_config._environment = selected_env
        new_ip = self.log_service.remote_ip_config.get_remote_ip()
        self.ip_input.setText(new_ip)
        self._update_unc_preview()

    def _on_ip_changed(self, text: str) -> None:
        if text.strip():
            import os
            os.environ["LOG_REMOTE_IP"] = text.strip()
        self._update_unc_preview()

    def _update_unc_preview(self) -> None:
        env_name = self.env_combo.currentText()
        share = "AKS-Stg-Logs" if env_name == "Staging" else ("AKS-Dev-Logs" if env_name == "Development" else "AKS-Prod-Logs")
        unc = self.log_service.get_remote_unc_path(share)
        self.unc_preview_label.setText(f"UNC Root: {unc}")
        self._update_status_message()

    def _update_status_message(self) -> None:
        env = self.env_combo.currentText() if HAS_PYSIDE6 and hasattr(self, 'env_combo') else "Development"
        ip = self.log_service.remote_ip_config.get_remote_ip()
        self.status_bar.showMessage(f"Active Environment: {env} | Remote Server IP: {ip}")

    def _open_file_dialog(self) -> None:
        if not HAS_PYSIDE6:
            return
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Log File", "", "Log Files (*.log *.txt *.log.*);;All Files (*)")
        if filepath:
            count = self.log_service.open_file(filepath)
            filtered = self.log_service.apply_filter()
            self.table_model.set_entries(filtered)
            self.status_bar.showMessage(f"Opened {filepath} ({count} entries indexed)")
