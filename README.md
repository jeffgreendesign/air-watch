# Air Watch

Grok Bot template. Read-only watchdog for Airthings monitors. Checks radon, CO2, humidity, VOCs, PM2.5, temperature, battery, and stale data every 2 hours, and messages you only when a room is out of range.

**Add to Grok Bot:** TBD (install link coming)

Not a CO or smoke alarm. Bring your own Airthings API client.

## What it does

- Reads your Airthings monitors through the Airthings consumer API, scope `read:device:current_values` only.
- Stays quiet when everything is normal.
- When something is out of range, sends you one short alert: room, metric, value, threshold, one next step.
- Repeats a breach only if it gets worse or after a 12 hour cooldown.

## Setup (about 5 minutes)

1. Install the template. Air Watch starts a guided setup, one question at a time.
2. In dashboard.airthings.com, open Integrations > API and create a client with scope `read:device:current_values`.
3. Enter the client ID and secret through the secure secret fields Air Watch shows you. Never paste them in chat.
4. Air Watch takes one reading and lists your devices.
5. Name the room for each monitor.
6. Keep or change the default thresholds and units.
7. Air Watch creates its alert routine (every 2 hours). An alert may fire on the first check if something is already out of range.

## Thresholds (defaults, editable)

| Metric | Alert when |
| --- | --- |
| Radon | 148 Bq/m3 (4 pCi/L) or higher (EPA action level) |
| CO2 | above 1000 ppm |
| Humidity | below 30% or above 60% |
| VOC | above 250 ppb |
| PM2.5 | above 10 ug/m3 |
| Temperature | below 64F or above 78F |
| Battery | below 15% |
| Stale data | no reading for over 3 hours |

## Safety disclosure

Air Watch is not a carbon monoxide or smoke alarm and must not replace one. It depends on the third-party Airthings API, which can be slow, down, or changed. A missed or late alert is possible. Radon alerts cite EPA guidance only; confirm high readings with a long-term test and a certified mitigation professional. No health advice.

## Privacy

- Read-only. It never changes device settings or your Airthings account.
- Your keys stay in your bot's secret storage. They are never shown, logged, or written to files, and never leave your bot except to call Airthings.
- Alerts go only to you. No email, posts, or messages to anyone else.
- Cooldown state is a small local file (`~/air-watch/state.json`) with no secrets.

## Report an issue

1. Tell Air Watch: "diagnose". It checks keys, token, account, and each device's last-seen time, and reports the first failure with secrets masked.
2. Open a [bug report](../../issues/new?template=bug.md) and paste the diagnose output.

Never post your client ID, secret, or tokens.

## Limitations

- Depends on the Airthings consumer API. If Airthings changes it, Air Watch may break until the skills are updated.
- Airthings limits clients to 120 requests per hour.
- Checks every 2 hours, so it is not real time.
- Template copies are independent. The author gets no usage data or error reports unless you file an issue.
- Only tested with a small set of Airthings models so far.

## Contents

- `skills/airthings-air-check/SKILL.md`: reading, thresholds, cooldown, diagnose.
- `skills/air-watch-getting-started/SKILL.md`: first-run setup.
- `routine.md`: the alert routine.
