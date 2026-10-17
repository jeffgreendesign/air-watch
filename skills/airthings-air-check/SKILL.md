---
name: airthings-air-check
description: >-
  Use when Air Watch's alert routine fires, the owner asks how the air is, or
  the owner says "diagnose": run the local Airthings check script (read-only)
  and word its results.
---
Needs: env `AIRTHINGS_CLIENT_ID`, `AIRTHINGS_CLIENT_SECRET`; `~/air-watch/airwatch.py` and `~/air-watch/config.json` (written by air-watch-getting-started). If either file is missing, rerun setup steps 6-7; never improvise the math.

Run: `python3 ~/air-watch/airwatch.py` (add `--diagnose` for diagnose). The script does all fetching, unit conversion, thresholds, staleness, cooldown, "worse", quiet hours, and the auth-fail counter, and prints JSON. Do not recompute or second-guess it; never print or echo the keys.

Exit codes and `status`:
- 0 `ok`: for each item in `alerts[]`, send one short line: room, metric, value + unit, threshold, `fix`. Note `held_since` (held during quiet hours) or `resolved: true` (held, now back in range). Empty `alerts[]` in a routine: send nothing. Manual ask: one-line summary of `readings` with `checked_at` in the owner's local time.
- 2 `auth_error`: say nothing on the first one. `pause_and_ask`: pause the alert routine and ask the owner to create a new API client (sign in at https://consumer-api-doc.airthings.com/dashboard, then Edit or create an application) and re-enter both keys through secure secret requests.
- 3 `rate_limited`: send nothing; mention only if it repeats on 3 runs.
- 4 `api_down`: check the status page below; mention only if it repeats on 3 runs.

Diagnose: run with `--diagnose` and report `diagnose[]` in order (keys set/missing, token HTTP result, account count, each device's last-seen); stop at the first `ok: false` with one fix. No secrets appear in the output, so it is safe to paste into a public bug report. Diagnose does not change state.

Config edits (rooms, thresholds, units, quiet hours) go in `~/air-watch/config.json`; thresholds are in the owner's display units. To change country, run `python3 ~/air-watch/airwatch.py --set-country XX`; never hand-edit units.
Read-only; no approval needed. Not a CO or smoke alarm.

Reference:
- API docs: https://consumer-api-doc.airthings.com/docs/api/getting-started
- Create or reissue client: https://consumer-api-doc.airthings.com/dashboard (sign in, then Edit or create an application)
- Status page: https://status.airthings.com/en
- Support (owner-facing only; never email it yourself): support@airthings.com
