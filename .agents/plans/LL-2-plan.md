# Implementation Plan - LL-2

**Ticket:** [LL-2](https://mamunorselise.atlassian.net/browse/LL-2) - Configure Log Remote IP Based on Environment  
**Sprint:** sprint-1  
**Status:** verified  
**Branch:** feature/LL-2-configure-remote-ip  
**Counterpart:** N/A (Log-Lens single repo)  

---

## 1. Executive Summary

This ticket requires configuring log server remote IP addresses based on the deployment environment (`development`, `staging`, `production`) so that each environment dynamically loads its corresponding remote IP configuration without hardcoding or requiring source code edits.

We will implement an environment configuration service (`EnvironmentConfig` / `RemoteIPConfig`) under `app/infrastructure/configuration/` supporting environment variable detection (`LOG_LENS_ENV`, `LOG_REMOTE_IP`) and external JSON configuration files (`remote_ips.json`).

---

## 2. Requirements & Traceability

| Requirement ID / AC | Description | Target Component | Test Target | Verified |
| :--- | :--- | :--- | :--- | :--- |
| **AC-1** | Environment-based remote IP resolution (`development`, `staging`, `production`) | `app/infrastructure/configuration/remote_ip_config.py` | `tests/unit/test_remote_ip_config.py` | [x] |
| **AC-2** | Environment variable overrides (`LOG_LENS_ENV`, `LOG_REMOTE_IP`) | `app/infrastructure/configuration/remote_ip_config.py` | `tests/unit/test_remote_ip_config.py` | [x] |
| **AC-3** | External JSON config file loading (`remote_ips.json`) | `app/infrastructure/configuration/remote_ip_config.py` | `tests/unit/test_remote_ip_config.py` | [x] |
| **AC-4** | Zero hardcoded IP addresses; existing logging & file opening functionality preserved | `app/infrastructure/configuration/remote_ip_config.py` | `tests/integration/test_remote_ip_integration.py` | [x] |

---

## 3. Architecture & Layer Mapping

Following `AGENTS.md` dependency direction:
```text
UI (MainWindow / Settings Dialog)
 ↓
Application Services (LogService)
 ↓
Domain/Core (FileReader, LogEntry)
 ↓
Infrastructure (EnvironmentConfig, RemoteIPConfig, Configuration)
```

---

## 4. Work Checklist

- [x] **Item 1:** Implement `RemoteIPConfig` and `EnvironmentConfig` domain/infrastructure service in `app/infrastructure/configuration/remote_ip_config.py`.
- [x] **Item 2:** Support JSON config file parsing (`remote_ips.json`) for custom environment-to-IP mappings.
- [x] **Item 3:** Add environment variable detection (`LOG_LENS_ENV`, `APP_ENV`, `LOG_REMOTE_IP`).
- [x] **Item 4:** Integrate `RemoteIPConfig` into `LogService` to construct remote UNC path helpers (e.g. `\\<remote_ip>\AKS-Stg-Logs`).
- [x] **Item 5:** Add unit tests in `tests/unit/test_remote_ip_config.py`.
- [x] **Item 6:** Add integration tests in `tests/integration/test_remote_ip_integration.py`.

---

## 5. Blocking Questions & Assumptions

### Blocking Questions
- *None*

### Assumptions
- Supported environment identifiers are normalized (`dev`/`development`, `stg`/`stage`/`staging`, `prod`/`production`).
- If no environment or explicit IP is specified, the configuration safely defaults to `development` configuration settings.
