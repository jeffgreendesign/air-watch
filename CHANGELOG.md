# Changelog

## v0.2.0 (2026-10-17)

- Moved thresholds, unit conversion, stale data, cooldown, and the auth-failure counter into `script/airwatch.py` (Python 3 stdlib). Setup writes it from the skill; the routine runs it; the model only words alerts.
- Defined "worse": at least 10% of the threshold further past it, same side. Auth failures persist in `state.json`; two in a row return `pause_and_ask`.
- Optional quiet hours (default off): non-urgent alerts are held and delivered when quiet hours end; radon and offline alerts always go out.
- Country-based radon levels and units with cited official sources (US, CA, UK, NO, SE, DE, EU, WHO fallback). Fixed units mismatch: US defaults to F and pCi/L, everyone else C and Bq/m3.
- Added `tests/` with 9 fixture tests (normal, breach, cooldown repeat, worse, offline, auth twice, quiet hours, rate limit/API down, country presets).
- Routine runs in the owner's local time zone and is Test-run at setup.
- Trimmed reference links in the check skill to 4; the README keeps the full list.

## v0.1.0 (2026-10-17)

- First release.
- Skills: `airthings-air-check`, `air-watch-getting-started`.
- Routine: `air-quality-out-of-range-alert`, every 2 hours.
- Added a diagnose mode to `airthings-air-check`: checks keys, token, account, and per-device last-seen in order, reports the first failure, masks secrets.
- Added Airthings resources (README) and Reference links (skill), including status page, privacy, terms, and API rate-limit/authorization docs. Diagnose and error paths now point at the status page on auth or API failure.
