# Air Watch

Grok Bot template. Read-only watchdog for Airthings monitors. Checks radon, CO2, humidity, VOCs, PM2.5, temperature, battery, and stale data every 2 hours, and messages you only when a room is out of range.

**Add to Grok Bot:** TBD (install link coming)

Not a CO or smoke alarm. Bring your own Airthings API client.

## What it does

- Reads your Airthings monitors through the Airthings consumer API, scope `read:device:current_values` only.
- A small local Python script (`~/air-watch/airwatch.py`, stdlib only) does all the math: units, thresholds, stale data, cooldown, quiet hours, and the auth-failure counter. The bot only words the alerts.
- Stays quiet when everything is normal.
- When something is out of range, sends you one short alert: room, metric, value, threshold, one next step.
- Repeats a breach after a 12 hour cooldown, or sooner only if it gets worse: at least 10% of the threshold further past it, on the same side (CO2 1000 ppm limit: an alert at 1100 repeats early only at 1200 or more).
- Optional quiet hours (off by default): non-urgent alerts are held and delivered when quiet hours end; radon and offline-device alerts always come through.
- Two auth failures in a row pause the routine and ask you to reissue your Airthings client.

## Setup (about 5 minutes)

1. Install the template. Air Watch starts a guided setup, one question at a time.
2. In dashboard.airthings.com, open Integrations > API and create a client with scope `read:device:current_values`.
3. Enter the client ID and secret through the secure secret fields Air Watch shows you. Never paste them in chat.
4. Tell Air Watch your country. It sets the radon level and units to match (table below).
5. Choose quiet hours, or leave them off.
6. Air Watch writes the check script and config to `~/air-watch/` (templates cannot carry files, so the script lives inside the setup skill).
7. It runs a diagnose, lists your monitors, and asks the room for each.
8. It takes one reading. An alert may fire right away if something is already out of range.
9. It creates the alert routine: every 2 hours in your local time zone.

## Thresholds (defaults, editable)

| Metric | Alert when |
| --- | --- |
| Radon | at or above your country's level (table below) |
| CO2 | above 1000 ppm |
| Humidity | below 30% or above 60% |
| VOC | above 250 ppb |
| PM2.5 | above 10 ug/m3 |
| Temperature | below 18 C / 64 F or above 25.5 C / 78 F |
| Battery | below 15% |
| Stale data | no reading for over 3 hours |

Units follow your country: US gets F and pCi/L; everywhere else gets C and Bq/m3. You can change either during setup.

## Radon levels by country

Air Watch alerts on the short-term reading, while these official levels refer to the long-term (annual) average. Treat an alert as a reason to run a long-term test, not as a diagnosis.

| Country | Air Watch alert level | Official level | Source |
| --- | --- | --- | --- |
| United States | 4 pCi/L (148 Bq/m3) | EPA action level 4 pCi/L | [US EPA](https://www.epa.gov/radon/does-2009-world-health-organizations-recommendation-lower-radon-action-level-affect-epas) |
| Canada | 200 Bq/m3 | Canadian radon guideline 200 Bq/m3 | [Health Canada](https://www.canada.ca/en/health-canada/services/health-risks-safety/radiation/radon/government-canada-radon-guideline.html) |
| United Kingdom | 200 Bq/m3 | Action Level 200, Target Level 100 | [UKHSA](https://www.ukhsa-protectionservices.org.uk/radon/information/level) |
| Norway | 100 Bq/m3 | Action level (tiltaksgrense) 100, upper limit (grenseverdi) 200 | [DSA](https://www.dsa.no/radon/anbefalte-grenser-for-radon) |
| Sweden | 200 Bq/m3 | Reference level 200 (Strålskyddsförordning 2018:506) | [SSM](https://www.stralsakerhetsmyndigheten.se/omraden/radon/referensniva-och-gransvarden-for-radon/) |
| Germany | 300 Bq/m3 | Referenzwert 300 (StrlSchG § 124) | [BfS](https://www.bfs.de/DE/themen/ion/umwelt/radon/regelungen/referenzwert.html) |
| Other EU | 300 Bq/m3 | National reference levels may not exceed 300 (Directive 2013/59/Euratom, Art. 74) | [EUR-Lex](https://eur-lex.europa.eu/eli/dir/2013/59/2014-01-17/eng) |
| Anywhere else | 100 Bq/m3 | WHO reference level 100, max 300 where 100 is not feasible | [WHO](https://www.who.int/news-room/fact-sheets/detail/radon-and-health) |

Many EU countries set lower national levels than 300; set yours during setup if so.

## Safety disclosure

Air Watch is not a carbon monoxide or smoke alarm and must not replace one. It depends on the third-party Airthings API, which can be slow, down, or changed. A missed or late alert is possible. Radon alerts cite your country's official level (or WHO); confirm high readings with a long-term test and a certified mitigation professional. No health advice.

## Privacy

- Read-only. It never changes device settings or your Airthings account.
- Your keys stay in your bot's secret storage. They are never shown, logged, or written to files, and never leave your bot except to call Airthings.
- Alerts go only to you. No email, posts, or messages to anyone else.
- Cooldown and auth-failure state is a small local file (`~/air-watch/state.json`) with no secrets.

## Report an issue

1. Tell Air Watch: "diagnose". It runs `airwatch.py --diagnose`: keys set or missing, token result, account, and each device's last-seen time. The output contains no secrets.
2. Open a [bug report](../../issues/new?template=bug.md) and paste the diagnose output.

Never post your client ID, secret, or tokens.

## Limitations

- Depends on the Airthings consumer API. If Airthings changes it, Air Watch may break until the skills are updated.
- Airthings limits clients to 120 requests per hour.
- Checks every 2 hours, so it is not real time.
- Template copies are independent. The author gets no usage data or error reports unless you file an issue.
- Only tested with a small set of Airthings models so far.

## Airthings resources

Official Airthings links for setup, API docs, status, and support. The bot never emails Airthings support; that address is for you if you need their help.

- **Create API client:** [dashboard.airthings.com](https://dashboard.airthings.com) (Integrations > API; scope `read:device:current_values`)
- **API getting started:** [consumer-api-doc.airthings.com/docs/api/getting-started](https://consumer-api-doc.airthings.com/docs/api/getting-started)
- **API authorization:** [docs/api/authorization](https://consumer-api-doc.airthings.com/docs/api/authorization)
- **API rate limit:** [docs/api/rate-limit](https://consumer-api-doc.airthings.com/docs/api/rate-limit) (120 requests per hour)
- **API reference (OpenAPI):** [api-docs](https://consumer-api-doc.airthings.com/api-docs)
- **Postman setup:** [docs/api/postman-setup](https://consumer-api-doc.airthings.com/docs/api/postman-setup)
- **Code examples:** [github.com/airthings](https://github.com/airthings) ([org repositories](https://github.com/orgs/Airthings/repositories))
- **Status page:** [status.airthings.com/en](https://status.airthings.com/en) (check this when auth or API calls fail)
- **Help center:** [help.airthings.com/en](https://help.airthings.com/en/)
- **Airthings app:** [airthings.com/app](https://www.airthings.com/app)
- **Airthings home:** [airthings.com](https://www.airthings.com/)
- **Privacy notice:** [airthings.com/legal/privacy-notice](https://www.airthings.com/legal/privacy-notice)
- **Terms of use:** [airthings.com/legal/terms-of-use](https://www.airthings.com/legal/terms-of-use)
- **Airthings support (owner only):** support@airthings.com

## Contents

- `script/airwatch.py`: the check script (also embedded verbatim in the setup skill). Exit codes: 0 ok, 2 auth, 3 rate limit, 4 API down.
- `tests/`: fixture tests with a mocked HTTP layer. Run `python3 -m unittest discover -s tests`.
- `skills/airthings-air-check/SKILL.md`: runs the script and words the results, plus diagnose.
- `skills/air-watch-getting-started/SKILL.md`: first-run setup; writes the script and config.
- `routine.md`: the alert routine.
