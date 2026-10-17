# Changelog

## v0.2.4
- Check skill: key-reissue directions now point to the Airthings help article instead of the old dashboard path.

## v0.2.3 (2026-10-17)

- Setup step 3 expanded into five numbered steps for getting API keys, matching Airthings' current help article (My Applications > Create New Application), replacing the old dashboard Integrations > API path.
- README setup and links updated to match.

## v0.2.2 (2026-10-17)

Fixes from the second review round.
- The script enforces the overwrite guard: `--init '<json>'` creates config.json and refuses to replace an existing one unless `--force` is passed. Setup now writes the config only through `--init`. `--set-country` still edits in place.
- A missing or invalid config.json prints a one-line message and exits 1 instead of a traceback.
- Removed the stale "run once with Test" line from routine.md.
- 3 new tests (14 total).

## v0.2.1 (2026-10-17)

Fixes from a fresh-install test run.
- `--set-country XX` re-derives units and the radon level from the country, keeps rooms, quiet hours, and time zone, and drops custom thresholds (reported back). The skills say to use it instead of hand-editing.
- Unnamed monitors are labeled by model plus last 4 of the serial (e.g. "View Plus 2519"), never a bare serial. Setup pushes harder to name rooms.
- Setup asks units and quiet hours as separate turns, explains alerts on the first check, and dropped the "Test" step bots can't run.
- Setup won't replace an existing `~/air-watch/config.json` without asking (bots on one box share the folder).
- 2 new tests (11 total).

## v0.2.0 (2026-10-17)

- Moved thresholds, unit conversion, stale data, cooldown, and the auth-failure counter into `script/airwatch.py` (Python 3 stdlib). Setup writes it from the skill; the routine runs it; the model only words alerts.
- Defined "worse": at least 10% of the threshold further past it, same side. Auth failures persist in `state.json`; two in a row return `pause_and_ask`.
- Optional quiet hours (default off): non-urgent alerts are held and delivered when quiet hours end; radon and offline alerts always go out.
- Country-based radon levels and units with cited official sources (US, CA, UK, NO, SE, DE, EU, WHO fallback). Fixed units mismatch: US defaults to F and pCi/L, everyone else C and Bq/m3.
- Added `tests/` with 9 fixture tests (normal, breach, cooldown repeat, worse, offline, auth twice, quiet hours, rate limit/API down, country presets).
- Routine runs in the owner's local time zone.
- Trimmed reference links in the check skill to 4; the README keeps the full list.

## v0.1.0 (2026-10-17)

- First release.
- Skills: `airthings-air-check`, `air-watch-getting-started`.
- Routine: `air-quality-out-of-range-alert`, every 2 hours.
- Added a diagnose mode to `airthings-air-check`: checks keys, token, account, and per-device last-seen in order, reports the first failure, masks secrets.
- Added Airthings resources (README) and Reference links (skill), including status page, privacy, terms, and API rate-limit/authorization docs. Diagnose and error paths now point at the status page on auth or API failure.
