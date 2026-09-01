# Project Requirements — Desktop Log Viewer & Analyzer

## 1. Project Overview

Build a Windows-first desktop application in Python that allows developers, QA engineers, support engineers, and operations teams to open, inspect, search, filter, and analyze application log files efficiently.

The application is intended for log files similar to the example shown in the provided screenshot, where many rotated files exist with names such as:

- `PCXWebHost.log.1659`
- `PCXWebHost.log.1658`
- `PCXWebHost.log.1657`
- `PCXWebHost.log.1656`

The primary goal is to make troubleshooting faster by providing a user-friendly interface for finding relevant log entries without manually opening large files or using text editors.

### Recommended UI Technology

- Python 3.12+
- PySide6 / Qt for the desktop UI
- Standard Python libraries for file handling and text processing
- `pytest` for automated tests
- Optional: `pydantic` for strongly typed configuration/models
- Optional: `rapidfuzz` for fuzzy search
- Optional: `orjson` for high-performance JSON parsing when required

The application should be designed so that the core log-processing engine is independent from the UI layer.

---

## 2. Goals

### Primary Goals

1. Open one or more log files quickly.
2. Handle large log files without freezing the UI.
3. Search for keywords and phrases.
4. Filter log entries using multiple criteria.
5. Highlight matching text.
6. Display log entries in a structured and readable format.
7. Quickly identify errors, warnings, exceptions, and related requests.
8. Navigate between matches.
9. Support rotated log files and groups of related files.
10. Provide useful diagnostic context around a selected log line.
11. Remember commonly used filters and application preferences.
12. Provide a clean, professional developer-tool experience.

### Non-Goals for the Initial Version

- Editing or modifying source log files.
- Deleting log files.
- Sending logs to external services.
- Automatic production-system access.
- Automatic uploading of logs to the cloud.
- Running arbitrary code contained in log files.

---

# 3. Core Functional Requirements

## 3.1 File and Folder Opening

The application must allow users to:

- Open a single log file.
- Open multiple log files at once.
- Open an entire folder.
- Drag and drop log files into the application.
- Add files to an existing session.
- Remove files from the current session.
- Refresh a file when its content changes.
- Reopen recently used files.
- Remember the last opened location.

### Supported File Types

Initially support:

- `.log`
- `.txt`
- Rotated files such as `.log.1659`
- Files with unknown extensions when explicitly selected by the user

The file type handling should be configuration-driven rather than hard-coded.

---

## 3.2 Large File Handling

Large logs are a primary requirement.

The application must:

- Avoid loading an entire large file into memory unnecessarily.
- Read files incrementally.
- Use lazy loading where practical.
- Keep the UI responsive during file loading.
- Support cancellation of long-running load/search operations.
- Show progress for expensive operations.
- Prevent accidental memory exhaustion.
- Handle files that are several hundred MB or larger when the machine has sufficient resources.

### Recommended Architecture

Use a background worker architecture:

`UI Thread -> Worker -> Log Reader/Parser -> Filter/Search Engine`

The UI thread must never perform expensive file scanning synchronously.

---

## 3.3 Log Display

Provide a main log viewer with:

- Line number.
- Source file name.
- Timestamp when detected.
- Log level when detected.
- Message/body.
- Search highlighting.
- Optional metadata columns.

Example logical columns:

| Column | Description |
|---|---|
| # | Display line/entry number |
| Timestamp | Parsed timestamp if available |
| Level | TRACE / DEBUG / INFO / WARN / ERROR / FATAL |
| Source | Log file name |
| Message | Main log content |
| Exception | Detected exception information |

The exact columns should be configurable.

---

## 3.4 Search

Provide a fast search bar with:

- Plain-text search.
- Case-sensitive option.
- Case-insensitive option.
- Whole-word option.
- Regular-expression mode.
- Search current file.
- Search all opened files.
- Search filtered results only.
- Next match.
- Previous match.
- Match count.

The application should clearly show:

`245 matches found`

and allow navigation through matches.

### Search Examples

Search terms may include:

- `NullReferenceException`
- `403`
- `500`
- `timeout`
- `MongoDB`
- `requestId=abc123`
- `OrderId:12345`

---

# 3.5 Filters

Filtering is one of the most important features.

The UI should provide a dedicated filter panel.

### Recommended Filters

- Log level
  - Trace
  - Debug
  - Info
  - Warning
  - Error
  - Fatal
- Date/time range
- File name
- Keyword
- Exception type
- HTTP status code
- Request ID / Correlation ID
- User ID, when present
- Endpoint/API path
- Thread ID
- Service/application name
- Include/exclude text
- Regular expression

### Filter Combination

Filters must support logical combinations such as:

`Level = Error AND Date >= 2026-08-31 AND Message contains "MongoDB"`

Future versions may support advanced expressions such as:

`level:error AND ("timeout" OR "connection refused")`

---

# 3.6 Quick Filters

Provide one-click filter buttons for common troubleshooting scenarios.

Examples:

- Errors only
- Warnings + Errors
- HTTP 4xx
- HTTP 5xx
- Exceptions
- MongoDB errors
- Timeout errors
- Authentication/authorization failures
- Recent entries
- Entries containing the current search term

Quick filters should be visually prominent but should not replace the advanced filter panel.

---

# 3.7 Log Level Detection

The application should automatically detect common log-level formats, including examples such as:

```text
INFO
WARN
WARNING
ERROR
DEBUG
TRACE
FATAL
```

The parser must also support common structured formats where the level is stored in JSON or a named field.

If a level cannot be detected, the entry should remain `Unknown`.

The parser must never corrupt or discard an entry simply because a field could not be detected.

---

# 3.8 Timestamp Detection

The application should detect common timestamp patterns, including:

- ISO-8601
- `yyyy-MM-dd HH:mm:ss`
- `yyyy-MM-dd HH:mm:ss.fff`
- UTC timestamps
- Timestamps containing timezone offsets

Timestamp parsing must be configurable.

If parsing fails, preserve the original text.

---

# 3.9 Multi-Line Log Entries

The application must support multi-line log entries.

This is especially important for:

- Exceptions
- Stack traces
- JSON payloads
- Request/response details

Example:

```text
ERROR 2026-08-31 12:10:10 Failed to process request
System.NullReferenceException: Object reference not set...
   at SomeNamespace.Service.Process()
   at SomeNamespace.Controller.Execute()
```

The complete stack trace should be treated as one logical log entry when the configured parser can determine the entry boundary.

---

# 3.10 Detail Panel

When a user selects an entry, display a detailed view.

The detail panel should show:

- Full raw log entry.
- Parsed timestamp.
- Log level.
- Source file.
- Line number.
- Correlation/request ID.
- Extracted exception.
- Parsed metadata.
- Related lines where available.

The raw text must remain available because parsing may not capture every field.

---

# 3.11 Context Viewer

Allow users to inspect surrounding entries.

Example:

`Show 50 lines before and 50 lines after`

The context viewer should:

- Keep the selected entry centered where possible.
- Clearly mark the original matching entry.
- Support jumping to the previous/next matching event.
- Preserve the source file position.

---

# 3.12 Follow / Tail Mode

Provide an optional **Follow Log** mode.

When enabled:

- Detect appended content.
- Display new entries automatically.
- Scroll to the newest entry.
- Allow the user to pause auto-scrolling.
- Clearly indicate when new content is available.

The application must handle files being rotated.

---

# 3.13 Multiple Files and Sessions

A user should be able to work with several related log files simultaneously.

Example:

```text
PCXWebHost.log.1659
PCXWebHost.log.1658
PCXWebHost.log.1657
PCXWebHost.log.1656
```

Features:

- Open multiple files.
- Show files in a tab or source selector.
- Search across all files.
- Filter across all files.
- Display the originating source file for each entry.
- Sort files by filename or modification time.

---

# 3.14 Log File Grouping

The application should optionally identify rotated logs belonging to the same base file.

For example:

```text
PCXWebHost.log
PCXWebHost.log.1656
PCXWebHost.log.1657
PCXWebHost.log.1658
PCXWebHost.log.1659
```

Group them under:

`PCXWebHost`

The user should be able to select the entire group and search across it.

---

# 3.15 Encoding Support

The application must support common encodings:

- UTF-8
- UTF-8 with BOM
- Windows-1252
- Configurable fallback encoding

Encoding detection should be handled safely.

If decoding fails, the application should provide a useful error message rather than crashing.

---

# 3.16 Results and Navigation

Provide:

- Total entries.
- Visible entries.
- Match count.
- Current match position.
- Filter state.
- Source file information.

Navigation must include:

- First result.
- Previous result.
- Next result.
- Last result.
- Jump to line.
- Jump to timestamp when possible.

---

# 3.17 Copy and Export

Users must be able to:

- Copy selected entries.
- Copy raw log text.
- Copy parsed fields.
- Export filtered results.

Initial export formats:

- `.txt`
- `.csv`

Future extension:

- `.json`

Export should respect the active filters.

---

# 3.18 Bookmarks

Allow users to bookmark important log entries.

Bookmarks should support:

- Add/remove bookmark.
- Bookmark description.
- Navigate between bookmarks.
- Optional persistence during the current session.

Future versions may persist bookmarks across sessions.

---

# 3.19 Recent Files

Provide a Recent Files menu containing recently opened files and folders.

Requirements:

- Configurable number of recent items.
- Remove individual recent items.
- Clear all recent items.
- Gracefully handle moved/deleted files.

---

# 3.20 Application Preferences

Settings should include:

- Theme.
- Font family.
- Font size.
- Tab size.
- Line wrapping.
- Timestamp display.
- Visible columns.
- Search behavior.
- Default encoding.
- Maximum recent files.
- Follow/tail behavior.
- Parser configuration.

---

# 4. Recommended User Interface

## Main Window Layout

Recommended structure:

```text
+---------------------------------------------------------------+
| File  View  Search  Filters  Tools  Help                      |
+---------------------------------------------------------------+
| [Open] [Folder] [Refresh] [Follow] [Errors] [Warnings]        |
+---------------------------------------------------------------+
| Search: [____________________________] [Aa] [Regex] [Find]    |
+---------------------------------------------------------------+
| Filters                                                       |
| Level [All]  Date [----]  File [All]  Exception [All]        |
+--------------------------+------------------------------------+
| Source / Files            | Log Viewer                         |
|                          |                                    |
| PCXWebHost.log.1659      | # | Time | Level | Message        |
| PCXWebHost.log.1658      |------------------------------------|
| PCXWebHost.log.1657      | 1 | ...  | INFO  | ...            |
| PCXWebHost.log.1656      | 2 | ...  | ERROR | ...            |
|                          | 3 | ...  | WARN  | ...             |
+--------------------------+------------------------------------+
| Detail / Stack Trace / Raw Entry                             |
+---------------------------------------------------------------+
| 245 matches | 12,430 visible | File: PCXWebHost.log.1659     |
+---------------------------------------------------------------+
```

The design should prioritize readability and speed over decoration.

---

# 5. Architecture Requirements

Use a layered architecture.

Recommended structure:

```text
log-viewer/
├── app/
│   ├── main.py
│   ├── ui/
│   ├── core/
│   │   ├── models/
│   │   ├── parsers/
│   │   ├── filters/
│   │   ├── search/
│   │   ├── readers/
│   │   └── services/
│   ├── infrastructure/
│   │   ├── filesystem/
│   │   └── configuration/
│   └── resources/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── docs/
├── scripts/
├── requirements.txt
├── pyproject.toml
├── README.md
├── AGENTS.md
├── SKILLS.md
└── GUARDRAILS.md
```

### Architectural Rules

- UI must depend on application services, not directly on file parsing.
- File readers must not depend on Qt widgets.
- Parsers must be independently testable.
- Filters must be pure/testable where possible.
- Search logic should be reusable without the GUI.
- Configuration must not be hard-coded into UI components.
- Long-running operations must run outside the UI thread.

---

# 6. Data Model

Define a normalized internal model such as:

```python
class LogEntry:
    source_file: str
    line_start: int
    line_end: int
    timestamp: datetime | None
    level: str | None
    message: str
    raw_text: str
    metadata: dict[str, str]
    exception_type: str | None
    correlation_id: str | None
```

The exact implementation can evolve, but the model must preserve the raw source text.

---

# 7. Performance Requirements

The application should be optimized for real-world log investigation.

Target behavior:

- UI remains responsive while opening/searching large files.
- Search operations run in background workers.
- Filtering should avoid unnecessary reparsing.
- Repeated searches should reuse parsed/indexed information where practical.
- Memory usage should be bounded for very large files.
- Large files should support incremental rendering.

### Suggested Future Optimization

For very large logs, introduce an index:

```text
File
 └── Offset Index
      ├── Entry 1 -> byte offset
      ├── Entry 2 -> byte offset
      └── ...
```

This enables fast jumping and partial loading without storing every full log entry in memory.

---

# 8. Error Handling Requirements

The application must gracefully handle:

- Missing files.
- Permission denied.
- File locked by another process.
- File deleted while open.
- File being rotated.
- Invalid encoding.
- Malformed lines.
- Unsupported log format.
- Very large single log entries.
- Regex syntax errors.
- Search cancellation.
- Unexpected parser failures.

User-facing errors must be actionable and understandable.

Example:

> Unable to read `PCXWebHost.log.1659` because the file is currently inaccessible. Check permissions or whether another process has locked the file.

Do not show raw stack traces to normal users unless debugging mode is enabled.

---

# 9. Security and Privacy

The application may be used with production logs. Therefore:

- Never upload logs automatically.
- Never send log contents to external APIs by default.
- Do not include log contents in telemetry.
- Do not execute text extracted from logs.
- Treat log files as untrusted input.
- Sanitize data before displaying it in rich text/HTML views.
- Regex processing must be protected against catastrophic backtracking where feasible.
- Export destinations should be explicitly chosen by the user.

---

# 10. Testing Requirements

Minimum test areas:

### Unit Tests

- Timestamp parsing.
- Log-level parsing.
- Multi-line entry detection.
- File rotation detection.
- Keyword filtering.
- Regex filtering.
- Date filtering.
- Combined filters.
- Encoding fallback.
- Malformed input handling.

### Integration Tests

- Open large log.
- Search across multiple files.
- Apply and clear filters.
- Follow/tail mode.
- Export filtered results.
- File rotation behavior.

### UI Tests

Test important user journeys:

1. Open a log file.
2. Search for an error.
3. Filter to ERROR.
4. Select an entry.
5. Inspect the stack trace.
6. Navigate to the next match.
7. Export results.

---

# 11. Logging for the Application

The application itself should have structured internal logging.

Recommended levels:

- DEBUG
- INFO
- WARNING
- ERROR
- CRITICAL

Internal application logs must never include full user log contents by default.

---

# 12. MVP Scope

The first production-capable version should include:

1. Open one/multiple log files.
2. Folder scanning.
3. File list.
4. Large-file-safe reading.
5. Search.
6. Case-sensitive/case-insensitive search.
7. Regex search.
8. Log-level detection.
9. Timestamp detection.
10. Level/date/text filters.
11. Multi-line entry handling.
12. Log detail panel.
13. Context viewer.
14. Copy results.
15. Export to TXT/CSV.
16. Recent files.
17. Dark/light theme.
18. Background processing.
19. Clear error handling.
20. Automated unit tests.

---

# 13. Phase 2 Features

After the MVP:

- Advanced query syntax.
- Persistent bookmarks.
- File group detection.
- Tail/follow mode.
- Saved filters.
- Search history.
- Persistent parsing profiles.
- JSON log support.
- Custom parser configuration.
- Indexed search.
- Highlight rules.
- Compare two log files.
- Timeline visualization.
- Error frequency summary.
- HTTP/API diagnostics dashboard.

---

# 14. Definition of Done

A feature is considered complete when:

- The implementation is reviewed.
- Automated tests are included.
- Error handling is implemented.
- UI remains responsive for expected workloads.
- The feature works with malformed input.
- Documentation is updated.
- No unrelated behavior is broken.
- The code follows the project guardrails.
- Performance-sensitive code has an appropriate benchmark or test where needed.

---

# 15. Suggested Development Order

1. Project setup and architecture.
2. Domain models.
3. File reader abstraction.
4. Plain-text parser.
5. Multi-line parser.
6. Search engine.
7. Filter engine.
8. Basic Qt UI.
9. Large-file incremental viewer.
10. Detail/context panels.
11. Multi-file support.
12. Export.
13. Preferences.
14. Testing and performance hardening.
15. Packaging for Windows.

---

# 16. Success Criteria

The product should allow a developer to take a folder containing hundreds of rotated application logs and answer questions such as:

- What errors happened?
- When did they happen?
- Which file contains the error?
- What happened immediately before the error?
- What request/correlation ID is associated with it?
- How many times did the error occur?
- Did the same issue occur in older rotated logs?
- Can I export only the relevant entries?

The application succeeds when common log-investigation tasks that previously required manually opening many files can be completed quickly through search, filtering, and context navigation.
