# Log-Lens — Desktop Log Viewer & Analyzer

A high-performance, Windows-first desktop log viewer and analyzer built in Python 3.12+ and PySide6. Designed specifically for analyzing large application logs and rotated log file sequences across local drives and network UNC shares (such as `\\10.11.64.7\AKS-Stg-Logs`).

---

## 🚀 How to Run

### 1. Prerequisites & Dependencies

Ensure Python 3.12+ is installed, then install required packages:

```bash
pip install PySide6 pytest
```

---

### 2. Launching the GUI Application

From the project root directory, run:

```bash
python -m app.main
```

This opens the PySide6 Desktop User Interface featuring:
- **Search Bar:** Fast plain-text, whole-word, and regex searching.
- **Virtualized Log Table:** High-performance `QAbstractTableModel` supporting millions of entries.
- **Detail Panel:** Raw log text, parsed timestamps, log levels, and stack trace viewer.
- **UNC Path & Rotated Log Support:** Direct loading for network shares (`\\10.11.64.7\AKS-Stg-Logs`) and rotated files (`PCXWebHost.log.1659`).

---

### 3. Running Automated Tests

To execute the automated unit and integration test suite:

```bash
python -m pytest
```

---

## 🏗️ Architecture

Following the layered architecture in `AGENTS.md`:

```text
UI (PySide6 / QAbstractTableModel / Main UI Window)
 ↓
Application Services (LogService)
 ↓
Domain/Core (LogEntry, BaseParser, FilterEngine, SearchEngine, LargeFileReader)
 ↓
Infrastructure (Configuration & Filesystem)
```
