---
name: airthings-air-check
description: >-
  Use when Air Watch's alert routine fires, the owner asks how the air is, or
  the owner says "diagnose": run the local Airthings check script (read-only)
  and word its results.
---
Needs: env `AIRTHINGS_CLIENT_ID`, `AIRTHINGS_CLIENT_SECRET`; `~/air-watch/airwatch.py` and `~/air-watch/config.json` (written by air-watch-getting-started). If either file is missing, rerun setup steps 6-7; never improvise the math.

Readings come only from the Airthings consumer API, scope `read:device:current_values`, by running the check script in this skill. Do not change devices, accounts, or settings, and do not send the keys any other way. Credentials are collected only through the secure secret request. Never ask for them in chat, and never print, echo, log, or write them. If the owner pastes a client ID or secret in chat, do not repeat it; tell them to revoke that client and re-enter it through the secret request.

Run: `python3 ~/air-watch/airwatch.py` (add `--diagnose` for diagnose). The script does all fetching, unit conversion, thresholds, staleness, cooldown, "worse", quiet hours, and the auth-fail counter, and prints JSON. Do not recompute or second-guess it. Never invent or estimate a reading. Room names and thresholds are the ones saved at setup; if a sensor has no room name, the script labels it with its Airthings device name when the API sends one, and never with a guessed room.

Exit codes and `status`:
- 0 `ok`: one short message for the whole check, then stop. Per item in `alerts[]`, one line: room, metric, value + unit, threshold, and the `fix` as the one next step. Word `metric` `offline` as stale data and include its last-seen time (`value`). For radon, cite EPA guidance and send the script's `fix` (confirm with a long-term test and a certified mitigation pro). No health diagnoses. The threshold in the message is the one saved for the owner. Note `held_since` (held during quiet hours) or `resolved: true` (held, now back in range). Empty `alerts[]` in a routine: send nothing. Manual ask: one-line summary of `readings` with `checked_at` in the owner's local time. No messages to anyone but the owner, and no product links.
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
