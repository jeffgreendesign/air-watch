# Routine: air-quality-out-of-range-alert

Schedule: `0 */2 * * *` (every 2 hours, flexible timing). Created during setup step 7.

Prompt:

> Run the airthings-air-check skill. If it returns breaches, send the owner one short alert with room, metric, value, threshold, and one next step. If nothing is new or worse, or still in its 12h cooldown, send nothing. If auth fails twice in a row, pause this routine and ask the owner to reissue the Airthings client. Result goes only to the owner in this chat.
