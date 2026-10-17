# Changelog

## v0.1.0 (2026-10-17)

- First release.
- Skills: `airthings-air-check`, `air-watch-getting-started`.
- Routine: `air-quality-out-of-range-alert`, every 2 hours.
- Added a diagnose mode to `airthings-air-check`: checks keys, token, account, and per-device last-seen in order, reports the first failure, masks secrets.
- Added Airthings resources (README) and Reference links (skill), including status page, privacy, terms, and API rate-limit/authorization docs. Diagnose and error paths now point at the status page on auth or API failure.
