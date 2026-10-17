---
name: airthings-air-check
description: >-
  Use when Air Watch's alert routine fires or the owner asks how the air is:
  read Airthings monitors (read-only) and return out-of-range rooms.
---
Needs: env `AIRTHINGS_CLIENT_ID`, `AIRTHINGS_CLIENT_SECRET`; memory rooms + thresholds.

1. Token: POST `https://accounts-api.airthings.com/v1/token` (grant_type client_credentials, scope `read:device:current_values`). Keep it in a shell variable only; `curl -s`, never `-v`, never print it.
2. GET `https://consumer-api.airthings.com/v1/accounts`, then `/v1/accounts/{id}/sensors` (and `/devices` for names). One pass per check; stay under 120 req/hr.
3. Map serial to room from memory (unknown: use the device name). Convert units (API temp is C).
4. Compare to thresholds. Data older than the stale limit is a stale breach; skip its other metrics. Never invent values.
5. Cooldown in `~/air-watch/state.json` (keys `room|metric`: last alert time + value; no secrets). Report a breach if new, worse than last alert, or past 12h. Clear keys back in range.

Output: breaches (room, metric, value+unit, threshold, one next step). Empty in a routine means send nothing; for a manual ask, one-line all-clear with check time.
Errors: 401/403 is an auth failure (twice in a row: pause the routine, ask owner to reissue). 429: back off; mention only if repeated.
Read-only; no approval needed. Not a CO or smoke alarm.

## Diagnose
When the owner says "diagnose": run these checks in order, stop at the first failure, and report it in plain words with a fix. Mask secrets (show only "set" or "missing", never values, tokens, or headers).
1. Keys present: `AIRTHINGS_CLIENT_ID` and `AIRTHINGS_CLIENT_SECRET` are non-empty. Fail: re-enter through the secure secret request.
2. Token: the token request returns HTTP 200 with an access token. Report only the HTTP code. 401/403: reissue the client in dashboard.airthings.com.
3. Account: `/v1/accounts` returns at least one account. Fail: check the client belongs to the account that owns the monitors.
4. Devices: for each device, last-seen time from `/v1/accounts/{id}/sensors`. Flag any older than the stale limit as offline (check power, batteries, hub or phone sync).
All pass: one line per device with last-seen time, then "Diagnose: OK". Output is safe to paste into a public bug report.
