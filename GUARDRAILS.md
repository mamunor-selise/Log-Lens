# GUARDRAILS.md

## Purpose

These guardrails define strict safety, quality, and engineering constraints for the Desktop Log Viewer project.

---

# 1. Log Files Are Untrusted Input

Treat every log file as untrusted data.

Never execute, evaluate, deserialize unsafely, or interpret arbitrary log text as executable code.

Examples of prohibited behavior:

```python
eval(log_line)
exec(log_line)
subprocess.run(log_line, shell=True)
```

Do not implement anything equivalent to these patterns.

---

# 2. Read-Only by Default

Opening and analyzing a log must never modify the original source file.

Features such as annotations, bookmarks, or notes must be stored separately.

Never silently:

- Rewrite log files.
- Reformat log files.
- Delete log files.
- Rename log files.
- Compress log files.

Any future file-management feature must require an explicit user action and confirmation where destructive.

---

# 3. No External Data Transmission

The application must not send log contents to:

- Cloud services.
- LLM providers.
- Analytics platforms.
- Remote APIs.

unless the user explicitly invokes a future feature designed for that purpose and the UI clearly explains what is being sent.

The default application must work completely offline.

---

# 4. Sensitive Data Protection

Logs can contain:

- Personal data.
- Authentication information.
- Tokens.
- Internal URLs.
- IDs.
- Customer information.

Therefore:

- Do not log full log contents into the application's own logs.
- Do not display secrets in diagnostics unless they already exist in the selected log.
- Do not include log content in crash reports by default.
- Avoid persisting sensitive search queries unless explicitly configured.

Future export or sharing features must warn users that log entries may contain sensitive information.

---

# 5. UI Responsiveness

Never perform expensive operations on the GUI thread.

Operations that may require workers include:

- Large file opening.
- Full-file scanning.
- Regex search.
- Large exports.
- Index creation.
- Folder scanning.

The UI should provide progress/cancellation for operations that may take noticeable time.

---

# 6. Memory Safety

Do not load unlimited amounts of log content into memory.

Avoid patterns such as:

```python
all_lines = file.readlines()
```

for potentially large files.

Use bounded or incremental processing.

If a feature intentionally requires full-file memory, document:

- Why it is required.
- Expected size limits.
- Failure behavior.

---

# 7. Regex Safety

Regular expressions are user-controlled input.

The application must:

- Handle invalid patterns.
- Avoid freezing the UI.
- Prefer safer regex usage for untrusted input.
- Run expensive matching outside the GUI thread.

Never assume a regex is harmless because it came from a developer.

---

# 8. Encoding Robustness

Never assume every log is UTF-8.

A decoding failure must not crash the application.

Use a controlled fallback strategy and clearly indicate when decoding had to use a fallback.

Do not silently replace large amounts of invalid data without informing the user when data fidelity could be affected.

---

# 9. Parser Isolation

A malformed log entry must not crash the complete parsing process.

Bad input should produce:

- A recoverable parser error.
- An `Unknown`/`None` field where appropriate.
- Preservation of raw text.

The parser should continue where possible.

---

# 10. Exception Handling

Do not use broad exception handling as a substitute for proper design.

Avoid:

```python
try:
    ...
except Exception:
    pass
```

If an exception must be caught broadly at an application boundary:

- Record useful diagnostic information.
- Present a safe user-facing message.
- Continue only when it is safe to do so.

---

# 11. Dependency Control

Do not add a third-party dependency only for convenience.

Before adding one:

1. Check whether the standard library is sufficient.
2. Check current project dependencies.
3. Evaluate maintenance and security risk.
4. Add the dependency with an explicit reason.

Do not introduce libraries that are unnecessary for the MVP.

---

# 12. Secrets and Configuration

Never hard-code:

- API keys.
- Passwords.
- Tokens.
- Credentials.
- Private certificates.

Never commit secrets to the repository.

The application should not require secrets for normal offline log viewing.

---

# 13. Shell and External Process Safety

Do not construct shell commands from:

- Filenames.
- Search terms.
- Regex patterns.
- Log content.

Avoid `shell=True`.

When an external process is genuinely required, pass arguments as a list and validate inputs.

---

# 14. Export Safety

Before writing an export file:

- Validate the destination.
- Avoid accidental overwrite where possible.
- Handle permission errors.
- Keep the original source logs unchanged.

CSV exports must be generated using a proper CSV writer rather than string concatenation.

---

# 15. UI Security

If log data is displayed using HTML/rich text:

- Escape untrusted text.
- Do not allow log data to execute JavaScript.
- Do not load remote content.
- Do not interpret links or HTML from logs unless explicitly designed and sandboxed.

A raw log line must be treated as text.

---

# 16. Performance Guardrail

Do not accept a change that makes large-file behavior significantly worse without a documented reason.

For significant changes to:

- Parsing.
- Search.
- Filtering.
- Rendering.
- Indexing.

consider adding a benchmark or performance regression test.

---

# 17. Backward Compatibility

Changes to parser profiles, saved filters, configuration, or exported formats should consider backward compatibility.

Do not silently break existing user settings.

When a breaking change is unavoidable:

- Detect the old format.
- Migrate it where practical.
- Clearly report migration failures.

---

# 18. Data Integrity

The raw log entry is the source of truth.

Parsed fields are derived data.

Never discard raw content merely because parsing failed.

---

# 19. User Control

The application should make potentially expensive or sensitive operations explicit.

Examples:

- Searching all files.
- Exporting large result sets.
- Opening a large folder.
- Following a live log.
- Applying expensive regex searches.

Avoid surprising automatic behavior.

---

# 20. AI Agent Guardrail

AI agents working on this project must not:

- Invent test results.
- Claim a command was executed when it was not.
- Delete files without explicit authorization.
- Change unrelated project behavior.
- Add hidden telemetry.
- Add cloud integrations without explicit approval.
- Disable security checks to make builds pass.
- Modify production log files.
- Commit secrets.

When uncertain, prefer a safe, reversible implementation.

---

# 21. Final Review Checklist

Before considering a task complete, verify:

- [ ] Source log files remain unchanged.
- [ ] No secrets were introduced.
- [ ] No external transmission was added.
- [ ] Large-file behavior was considered.
- [ ] GUI-thread blocking was avoided.
- [ ] Malformed input is handled.
- [ ] Tests were added or updated.
- [ ] Existing tests pass, where executable.
- [ ] Documentation was updated where necessary.
- [ ] The implementation follows `AGENTS.md` and `PROJECT-REQUIREMENT.md`.
