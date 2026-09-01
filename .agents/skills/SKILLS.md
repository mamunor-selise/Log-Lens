# SKILLS.md

## Purpose

This document describes the engineering capabilities and reusable implementation patterns expected for this project.

---

# 1. Python Desktop Development

Use modern Python practices:

- Type hints.
- `dataclasses`.
- `pathlib`.
- Context managers.
- Exceptions with clear meaning.
- Small, testable functions.
- Dependency injection where useful.

Prefer composition over inheritance unless inheritance clearly improves the design.

---

# 2. PySide6 / Qt

Use PySide6 for the desktop UI.

Important patterns:

- `QMainWindow` for the main application window.
- `QTableView` + model/view architecture for large datasets.
- `QThread`, `QThreadPool`, or Qt concurrent patterns for background tasks.
- Signals/slots for worker-to-UI communication.
- `QSettings` for user preferences where appropriate.
- Standard Qt dialogs for file selection.
- QAction-based menus and keyboard shortcuts.

Avoid populating huge datasets by creating one QWidget per log row.

For large result sets, prefer Qt's model/view architecture.

---

# 3. Large File Reading

Use streaming/chunked file reading.

A reader should provide an abstraction similar to:

```python
class LogReader(Protocol):
    def iter_entries(self) -> Iterator[LogEntry]:
        ...
```

The reader should avoid coupling itself to the UI.

Consider:

- Chunked byte reading.
- Buffered I/O.
- File offsets.
- Lazy parsing.
- Cancellation support.
- Encoding fallback.
- File rotation detection.

---

# 4. Log Parsing

Create parser components that transform raw text into normalized `LogEntry` objects.

Recommended parser stages:

```text
Raw bytes
  ↓
Decoder
  ↓
Line reader
  ↓
Entry boundary detector
  ↓
Structured field parser
  ↓
Normalized LogEntry
```

A parser should be tolerant.

Unknown fields should not cause the entire entry to fail.

Keep the original raw text.

---

# 5. Multi-Line Detection

Use configurable entry-boundary rules.

Typical patterns:

```text
timestamp line -> starts new entry
indented line  -> continuation
stack trace    -> continuation
JSON payload   -> continuation
```

Do not assume one universal log format.

Parser profiles should be extensible.

---

# 6. Search Engine

Search should support:

- Plain text.
- Case sensitivity.
- Whole words.
- Regex.
- Forward/backward navigation.

For large files, consider scanning in chunks instead of creating a giant string.

When regex is enabled:

- Catch invalid regex syntax.
- Prevent the UI from freezing.
- Consider safeguards against problematic patterns.

---

# 7. Filtering Engine

Filters should be composable.

Example:

```python
filters = [
    LevelFilter({"ERROR", "FATAL"}),
    TextFilter("MongoDB", case_sensitive=False),
    DateRangeFilter(start, end),
]
```

Each filter should have predictable behavior.

Where practical, filters should be pure functions so they can be tested easily.

---

# 8. Parsing Common Diagnostic Fields

Support extraction of useful fields such as:

- Timestamp.
- Level.
- HTTP method.
- HTTP status.
- URL/route.
- Correlation ID.
- Request ID.
- Trace ID.
- User ID.
- Exception type.
- Service name.
- Host name.
- Thread ID.

Field extraction must be parser-profile based where log formats differ.

---

# 9. Background Processing

Any potentially expensive operation should run in a worker:

- Opening large files.
- Parsing.
- Searching.
- Filtering large datasets.
- Building an index.
- Exporting large results.

Workers should support cancellation where practical.

Worker code must not directly mutate widgets.

---

# 10. Model/View Performance

For large data collections:

- Avoid one-widget-per-row designs.
- Use `QAbstractTableModel` or related model classes.
- Fetch only visible/needed data.
- Batch updates to the model.
- Avoid emitting thousands of UI updates individually.
- Keep expensive rendering work out of the paint path.

---

# 11. File Monitoring

For follow/tail mode, monitor:

- File size.
- Modification time.
- File identity where available.

Detect:

- Appended content.
- Truncation.
- Replacement.
- Rotation.

Do not rely solely on the filename.

---

# 12. Configuration

Use configuration objects rather than scattered constants.

Example:

```python
@dataclass
class ParserProfile:
    name: str
    timestamp_patterns: list[str]
    level_patterns: list[str]
    entry_start_patterns: list[str]
```

Profiles should be easy to extend.

---

# 13. Export

Export services should accept filtered entries rather than reaching into UI controls.

Example:

```python
class LogExporter:
    def export_txt(self, entries, destination): ...
    def export_csv(self, entries, destination): ...
```

Export operations should run in the background for large result sets.

---

# 14. Testing Skills

Use pytest.

Recommended test fixtures:

- Small normal log.
- Multi-line stack trace.
- Malformed log.
- UTF-8 file.
- Windows-1252 file.
- Large synthetic log.
- Rotated file set.
- JSON log.
- Mixed log levels.

Property-based testing may be added later for parser robustness.

---

# 15. Profiling

When performance is poor, measure before optimizing.

Useful tools include:

- `cProfile`
- `py-spy`
- `tracemalloc`
- Qt profiling/debugging tools where appropriate

Measure:

- File loading time.
- Parse time.
- Search time.
- Memory usage.
- UI rendering time.

Do not optimize based solely on assumptions.

---

# 16. Packaging

For Windows distribution, consider:

- PyInstaller.
- Versioned releases.
- Application metadata.
- Start menu shortcut.
- Optional installer.

Packaging must be tested on a clean machine or clean environment before release.
