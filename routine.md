# Routine: air-quality-out-of-range-alert

Schedule: `0 */2 * * *` (every 2 hours, flexible timing), in the owner's local time zone. Created at the end of setup only with the owner's OK. Ask first. Do not create it otherwise, and do not create any other routine.

Prompt:

> Run the airthings-air-check skill. Send the owner only what it says to send; otherwise send nothing.

All decisions (thresholds, units, 12h cooldown, "worse" = at least 10% of the threshold further past it on the same side, quiet hours, stale data, auth-fail counter) are made by `~/air-watch/airwatch.py`. The model only words the alerts. Two auth failures in a row return `pause_and_ask`: pause this routine and ask the owner to reissue the Airthings client. Results go only to the owner in this chat.
