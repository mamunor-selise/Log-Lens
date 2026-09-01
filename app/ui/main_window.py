from pathlib import Path
from typing import Optional
from app.core.services.log_service import LogService
from app.infrastructure.configuration.remote_ip_config import Environment
from app.ui.models.log_table_model import LogTableModel
from app.core.search.engine import SearchQuery

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
        QLineEdit, QPushButton, QCheckBox, QTableView, QTextEdit,
        QSplitter, QFileDialog, QLabel, QStatusBar, QComboBox, QGroupBox,
        QTreeView, QFileSystemModel, QHeaderView
    )
    from PySide6.QtCore import Qt, QModelIndex, QDir
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
        self.resize(1380, 850)

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

        # 2. Main Horizontal Splitter (Left Sidebar Explorer vs Right Main Content)
        main_h_splitter = QSplitter(Qt.Horizontal)

        # Left Explorer Sidebar
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)

        sidebar_title = QLabel("📁 Directory Explorer")
        sidebar_title.setStyleSheet("font-weight: bold; font-size: 13px;")

        path_bar_layout = QHBoxLayout()
        self.path_bar = QLineEdit()
        self.path_bar.setPlaceholderText("Enter folder or UNC path (e.g. \\\\10.11.64.7\\AKS-Stg-Logs)...")
        self.path_bar.returnPressed.connect(self._on_path_bar_navigate)
        self.go_btn = QPushButton("Go")
        self.go_btn.clicked.connect(self._on_path_bar_navigate)
        path_bar_layout.addWidget(self.path_bar)
        path_bar_layout.addWidget(self.go_btn)

        self.browse_folder_btn = QPushButton("Browse Local/Network Folder...")
        self.browse_folder_btn.clicked.connect(self._on_browse_folder)

        self.scan_folder_btn = QPushButton("🔍 Scan All Folder Logs")
        self.scan_folder_btn.setStyleSheet("background-color: #0066cc; color: white; font-weight: bold;")
        self.scan_folder_btn.clicked.connect(self._scan_active_folder)

        # QFileSystemModel Tree View
        self.fs_model = QFileSystemModel()
        self.fs_model.setFilter(QDir.AllDirs | QDir.Files | QDir.NoDotAndDotDot)
        
        initial_root = str(Path.cwd())
        self.fs_model.setRootPath(initial_root)

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.fs_model)
        self.tree_view.setRootIndex(self.fs_model.index(initial_root))
        self.tree_view.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.tree_view.clicked.connect(self._on_tree_item_clicked)
        self.tree_view.doubleClicked.connect(self._on_tree_item_double_clicked)

        sidebar_layout.addWidget(sidebar_title)
        sidebar_layout.addLayout(path_bar_layout)
        sidebar_layout.addWidget(self.browse_folder_btn)
        sidebar_layout.addWidget(self.scan_folder_btn)
        sidebar_layout.addWidget(self.tree_view)

        # Right Content Area (Search + Log View Table + Detail Panel)
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Search Bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search log messages, keywords, or exceptions (e.g. MongoDB, 500, timeout)...")
        self.search_input.textChanged.connect(self._on_search_text_changed)
        self.case_checkbox = QCheckBox("Case Sensitive")
        self.regex_checkbox = QCheckBox("Regex")
        self.case_checkbox.toggled.connect(self._on_search_text_changed)
        self.regex_checkbox.toggled.connect(self._on_search_text_changed)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.case_checkbox)
        search_layout.addWidget(self.regex_checkbox)

        # Right Vertical Splitter (Table View + Detail Panel)
        right_v_splitter = QSplitter(Qt.Vertical)
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.clicked.connect(self._on_table_row_selected)

        self.detail_panel = QTextEdit()
        self.detail_panel.setReadOnly(True)
        self.detail_panel.setPlaceholderText("Select a log row above to view full raw entry & stack trace...")

        right_v_splitter.addWidget(self.table_view)
        right_v_splitter.addWidget(self.detail_panel)
        right_v_splitter.setSizes([500, 250])

        right_layout.addLayout(search_layout)
        right_layout.addWidget(right_v_splitter)

        # Add left sidebar and right content to main horizontal splitter
        main_h_splitter.addWidget(sidebar_widget)
        main_h_splitter.addWidget(right_widget)
        main_h_splitter.setSizes([350, 950])

        main_layout.addWidget(config_group)
        main_layout.addWidget(main_h_splitter)

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
        self.path_bar.setText(unc)
        self._update_status_message()

    def _update_status_message(self) -> None:
        env = self.env_combo.currentText() if HAS_PYSIDE6 and hasattr(self, 'env_combo') else "Development"
        ip = self.log_service.remote_ip_config.get_remote_ip()
        count = self.log_service.get_total_entry_count()
        self.status_bar.showMessage(f"Environment: {env} | Server IP: {ip} | Loaded Log Entries: {count:,}")

    def _on_path_bar_navigate(self) -> None:
        if not HAS_PYSIDE6:
            return
        target_path = self.path_bar.text().strip()
        if target_path:
            self.fs_model.setRootPath(target_path)
            idx = self.fs_model.index(target_path)
            if idx.isValid():
                self.tree_view.setRootIndex(idx)

    def _on_browse_folder(self) -> None:
        if not HAS_PYSIDE6:
            return
        folder = QFileDialog.getExistingDirectory(self, "Select Directory / UNC Share", self.path_bar.text() or "")
        if folder:
            self.path_bar.setText(folder)
            self._on_path_bar_navigate()
            self._scan_directory(folder)

    def _on_tree_item_clicked(self, index: QModelIndex) -> None:
        file_path = self.fs_model.filePath(index)
        self.path_bar.setText(file_path)

    def _on_tree_item_double_clicked(self, index: QModelIndex) -> None:
        file_path = Path(self.fs_model.filePath(index))
        if file_path.is_dir():
            self._scan_directory(str(file_path))
        elif file_path.is_file():
            count = self.log_service.open_file(file_path)
            filtered = self.log_service.apply_filter()
            self.table_model.set_entries(filtered)
            self._update_status_message()

    def _scan_active_folder(self) -> None:
        active_path = self.path_bar.text().strip()
        if active_path:
            self._scan_directory(active_path)

    def _scan_directory(self, dir_path: str) -> None:
        count = self.log_service.open_directory(dir_path, recursive=True)
        filtered = self.log_service.apply_filter()
        self.table_model.set_entries(filtered)
        self._update_status_message()

    def _on_search_text_changed(self) -> None:
        query_text = self.search_input.text().strip()
        is_case = self.case_checkbox.isChecked()
        is_regex = self.regex_checkbox.isChecked()

        filtered_index = self.log_service.apply_filter()
        if query_text:
            query = SearchQuery(pattern=query_text, case_sensitive=is_case, is_regex=is_regex)
            filtered_index = self.log_service.search_entries(filtered_index, query)

        self.table_model.set_entries(filtered_index)

    def _on_table_row_selected(self, index: QModelIndex) -> None:
        row = index.row()
        if 0 <= row < len(self.table_model._entries):
            index_entry = self.table_model._entries[row]
            try:
                full_entry = self.log_service.get_entry_at(index_entry)
                detail_text = (
                    f"=== LOG ENTRY DETAILS ===\n"
                    f"Source File: {full_entry.source_file}\n"
                    f"Line Range : {full_entry.line_start} - {full_entry.line_end}\n"
                    f"Timestamp  : {full_entry.timestamp or 'Unknown'}\n"
                    f"Level      : {full_entry.level}\n"
                    f"Correlation: {full_entry.correlation_id or 'None'}\n"
                    f"Exception  : {full_entry.exception_type or 'None'}\n"
                    f"==========================\n\n"
                    f"{full_entry.raw_text}"
                )
                self.detail_panel.setPlainText(detail_text)
            except Exception as e:
                self.detail_panel.setPlainText(f"Error reading entry details: {e}")

