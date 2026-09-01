# AGENTS.md

## Purpose

This file defines the working rules for AI coding agents contributing to the Python Desktop Log Viewer project.

The agent must prioritize correctness, maintainability, testability, performance, and user experience.
## Application name : Log-Lens
---

## 1. Before Making Changes

Before implementing a feature or fixing a bug:

1. Inspect the repository structure.
2. Read `requirement/PROJECT-REQUIREMENT.md`.
3. Read `skills/SKILLS.md`.
4. Read `GUARDRAILS.md`.
5. Identify the affected architecture layer.
6. Inspect existing implementations before creating new abstractions.
7. Determine the smallest safe change that satisfies the requirement.

Do not assume a framework, parser, or library is already installed. Inspect `pyproject.toml`, `requirements.txt`, and existing imports.

---

## 2. Technology Guidelines

Preferred stack:

- Python 3.12+
- PySide6 for desktop UI
- pytest for testing
- Type hints throughout the application
- `pathlib` for filesystem paths
- `dataclasses` or strongly typed models for domain objects

Avoid adding dependencies unless there is a clear benefit.

When a dependency is added:

- Explain why it is needed.
- Check whether an existing dependency already solves the problem.
- Add tests covering important integration points.

---

## 3. Architecture

Follow this dependency direction:

```text
UI
 ↓
Application Services
 ↓
Domain/Core
 ↓
Infrastructure
```

The domain/core layer must not depend on Qt widgets.

File reading, parsing, filtering, and searching should be independently testable.

Do not place business logic directly inside button-click handlers or Qt widgets.

---

## 4. Performance Rules

Log files can be very large.

Agents must assume that:

- A file may be hundreds of MB.
- A file may contain millions of lines.
- A single entry may be unusually large.
- Multiple rotated files may be opened simultaneously.

Never introduce code that blindly reads an entire large file into memory without a documented reason.

Expensive work must run outside the UI thread.

Prefer streaming, chunked reading, lazy loading, and indexes where appropriate.

---

## 5. UI Rules

The UI should be:

- Simple.
- Fast.
- Keyboard-friendly.
- Suitable for long debugging sessions.
- Clear at high information density.

Do not introduce decorative UI that interferes with log investigation.

Important actions such as search, filters, next/previous match, and opening files must be easy to find.

---

## 6. Search and Filter Rules

Search and filtering must produce deterministic results.

Do not silently change the user's query.

Regex errors must be handled gracefully.

Filtering should preserve the original raw log entry.

When a parser cannot determine a field, use `None` or `Unknown` rather than inventing a value.

---

## 7. File Safety

Log files are input data, not executable content.

Never:

- Execute commands from log contents.
- Evaluate log contents as Python.
- Interpret arbitrary text as code.
- Automatically upload logs.
- Modify source logs unless the feature explicitly requires it.

Opening a log must be read-only by default.

---

## 8. Testing

Every non-trivial change should include tests.

Prioritize tests for:

- Parsers.
- Filters.
- Search.
- File reading.
- Encoding handling.
- Multi-line logs.
- Large-file behavior.
- Failure scenarios.

Do not weaken tests merely to make a build pass.

Tests should verify behavior rather than implementation details whenever possible.

---

## 9. Error Handling

Errors should be handled at the correct architectural boundary.

Library/domain code should provide meaningful exceptions or result objects.

UI code should translate failures into useful user-facing messages.

Never swallow an exception silently.

Avoid exposing internal stack traces to normal users.

---

## 10. Code Quality

Use:

- Clear names.
- Small focused functions.
- Explicit types.
- Useful docstrings for public APIs.
- Early validation.
- Constants/enums instead of repeated magic strings.

Avoid:

- Giant classes.
- Giant functions.
- Duplicated parsing logic.
- Global mutable state.
- Hidden side effects.
- Unnecessary metaprogramming.

---

## 11. Change Discipline

When fixing an issue:

1. Reproduce or model the problem.
2. Identify the root cause.
3. Implement the smallest appropriate fix.
4. Add regression tests.
5. Run relevant tests.
6. Review for performance impact.
7. Review for UI responsiveness.
8. Update documentation if behavior changed.

Do not refactor unrelated code during a focused bug fix.

---

## 12. Agent Output

For each completed task, provide:

- What changed.
- Why it changed.
- Files changed.
- Tests added/updated.
- Tests executed and results.
- Any known limitations.

Do not claim that tests were executed if they were not.

---

## 13. Definition of Success

An implementation is successful when it is:

- Correct.
- Tested.
- Understandable.
- Maintainable.
- Responsive for large logs.
- Safe for untrusted log input.
- Consistent with the project requirements and guardrails.
