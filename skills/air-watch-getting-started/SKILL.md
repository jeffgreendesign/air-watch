---
name: air-watch-getting-started
description: >-
  Use on Air Watch's first run to connect the owner's Airthings account, set
  country, units, rooms, and quiet hours, install the check script, and create
  the alert routine.
---
Speak to the new owner, one question at a time, in their language. Target: under 5 minutes.

1. "I'm Air Watch. I read your Airthings monitors every 2 hours and message you only when something's out of range. Read-only: I never change settings. I'm not a CO or smoke alarm, and I depend on Airthings' third-party API."
2. "Do you have an Airthings account with at least one monitor online?" If no, explain what's needed and stop.
3. "In dashboard.airthings.com, open Integrations > API and create a client with scope read:device:current_values." Then secure secret request for `AIRTHINGS_CLIENT_ID`, then `AIRTHINGS_CLIENT_SECRET`. Never in chat. Confirm each is set with `[ -n "$AIRTHINGS_CLIENT_ID" ] && echo set` (never print values).
4. "Which country are you in?" Map to a code: US, CA, GB, NO, SE, DE, or EU (other EU member state); anything else is "other". This sets the radon alert level (US 4 pCi/L = 148 Bq/m3; CA, GB, SE 200; NO 100, with 200 as Norway's upper limit; DE and EU 300; other 100 per WHO) and units (US: F and pCi/L; everyone else: C and Bq/m3). Then, as its own question: "I'll show temperature in X and radon in Y. Keep those, or change?" Wait for the answer before step 5.
5. Separate turn: "Quiet hours? During them I hold non-urgent alerts and send them when quiet hours end; radon and offline-device alerts still come through. Default: off." Also ask their time zone if the box clock isn't set to it (IANA name, e.g. Europe/Oslo).
6. If `~/air-watch/config.json` already exists, stop: tell the owner an Air Watch install is already on this computer, show its country and rooms, and ask before replacing it. Other bots on the same box share this folder. Otherwise write the script below to `~/air-watch/airwatch.py` exactly as given (`mkdir -p ~/air-watch`), then write `~/air-watch/config.json`:
   `{"country": "NO", "units": {"temp": "C", "radon": "Bq/m3"}, "rooms": {}, "quiet_hours": null, "timezone": "Europe/Oslo"}`
   (quiet hours as `{"start": "22:00", "end": "07:00"}`, local time). Only add `thresholds` the owner changes, in their display units, as `[low, high]` with `null` for none.
7. Run `python3 ~/air-watch/airwatch.py --diagnose`. Fix the first failed step. Then list each monitor from `diagnose[]` (the script labels unnamed ones by model, e.g. "View Plus 2519") and ask "Which room is each monitor in? Alerts will use these names." If they skip, say once that alerts will show the model label instead, and ask again only if they want. Save names to `rooms` in config.json, keyed by full serial.
8. Run `python3 ~/air-watch/airwatch.py` once and show the readings. If alerts fire now, say: "This is normal on a first check. Many homes run over on CO2 or VOCs, especially bedrooms with doors closed. Try the fix shown, and I'll only message again if it stays out of range after 12 hours or gets worse."
9. Create routine `air-quality-out-of-range-alert`: schedule `0 */2 * * *` in the owner's local time zone, flexible timing; prompt: "Run the airthings-air-check skill. Send the owner only what it says to send; otherwise send nothing." Tell the owner the schedule, their time zone, and the next run time.

Changing country later: never hand-edit units. Run `python3 ~/air-watch/airwatch.py --set-country XX` (codes above, or OTHER). It resets units and the radon level for that country, keeps rooms, quiet hours, and time zone, and drops custom thresholds because they were in the old units; tell the owner which ones were dropped (`dropped_thresholds`) and offer to re-add them.

Script (write verbatim):

```python
#!/usr/bin/env python3
"""Air Watch check: read Airthings monitors, compare to thresholds, print JSON. Stdlib only.
Exit: 0 ok, 2 auth, 3 rate limit, 4 API down. Keys come from env and are never printed."""
import json, os, sys, urllib.request, urllib.parse, urllib.error
from datetime import datetime, timedelta, timezone
try:
    from zoneinfo import ZoneInfo
except ImportError:
    ZoneInfo = None
HOME = os.path.expanduser(os.environ.get("AIRWATCH_HOME", "~/air-watch"))
TOKEN_URL = "https://accounts-api.airthings.com/v1/token"
API = "https://consumer-api.airthings.com/v1"
# Radon alert level in Bq/m3 by country (see README for sources). Anything else: WHO 100.
RADON = {"US": 148, "CA": 200, "GB": 200, "UK": 200, "NO": 100, "SE": 200, "DE": 300, "EU": 300}
URGENT = {"radon", "offline"}  # still sent during quiet hours
FIX = {"radon": "Retest with a long-term radon test; if confirmed, contact a certified mitigation professional.",
       "co2": "Open a window or door, or run ventilation.", "humidity_hi": "Run a dehumidifier or ventilate.",
       "humidity_lo": "Run a humidifier.", "voc": "Ventilate and look for new sources (cleaners, paint, cooking).",
       "pm25": "Ventilate after the source stops, or run an air purifier.", "temp_hi": "Cool the room.",
       "temp_lo": "Warm the room.", "battery": "Replace the batteries.",
       "offline": "Check power, batteries, and hub or phone sync."}
# Serial prefix -> model, used to label monitors the owner hasn't named.
MODELS = {"2900": "Wave", "2920": "Wave Mini", "2930": "Wave Plus", "2950": "Wave Radon", "2960": "View Plus",
          "2980": "View Pollution", "2989": "View Radon", "3210": "Wave Enhance", "3220": "Wave Enhance"}
COUNTRIES = set(RADON) | {"OTHER"}

class ApiError(Exception):
    def __init__(self, code, status):
        super().__init__(status); self.code, self.status = code, status

def http(method, url, data=None, headers=None):
    """Single HTTP point (tests replace this). Returns (status_code, parsed_json)."""
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, {}
    except (urllib.error.URLError, OSError):
        return 0, {}

def call(method, url, data=None, headers=None):
    code, body = http(method, url, data, headers)
    if code in (401, 403): raise ApiError(2, "auth_error")
    if code == 429: raise ApiError(3, "rate_limited")
    if code != 200: raise ApiError(4, "api_down")
    return code, body

def defaults(cfg):
    us = cfg.get("country", "").upper() == "US"
    u = {"temp": "F" if us else "C", "radon": "pCi/L" if us else "Bq/m3", **cfg.get("units", {})}
    rq = RADON.get(cfg.get("country", "").upper(), 100)
    t = {"radon": [None, round(rq / 37, 1) if u["radon"] == "pCi/L" else rq], "co2": [None, 1000],
         "humidity": [30, 60], "voc": [None, 250], "pm25": [None, 10], "battery": [15, None],
         "temp": [64, 78] if u["temp"] == "F" else [18, 25.5]}
    t.update(cfg.get("thresholds", {}))
    return u, t

def convert(metric, v, units):
    if metric == "temp" and units["temp"] == "F": return round(v * 9 / 5 + 32, 1)
    if metric == "radon" and units["radon"] == "pCi/L": return round(v / 37, 1)
    return v

def in_quiet(cfg, now):
    q = cfg.get("quiet_hours")
    if not q: return False
    tz = ZoneInfo(cfg["timezone"]) if cfg.get("timezone") and ZoneInfo else None
    hm = now.astimezone(tz).strftime("%H:%M")
    s, e = q["start"], q["end"]
    return (s <= hm < e) if s < e else (hm >= s or hm < e)

def label(dev, cfg):
    """Owner's room name, else model plus last 4 of serial (e.g. "View Plus 2519"), never a bare serial."""
    sn = str(dev["serialNumber"])
    if cfg.get("rooms", {}).get(sn): return cfg["rooms"][sn]
    model = dev.get("name") or dev.get("productName") or MODELS.get(sn[:4]) or "Monitor"
    return f"{model} {sn[-4:]}"

def set_country(cfg, code):
    """Re-derive units from country; drop unit overrides and thresholds (they were in old units). Keeps rooms, quiet hours, time zone."""
    code = code.upper()
    if code not in COUNTRIES: raise ValueError(f"unknown country {code}; use one of {sorted(COUNTRIES)}")
    new = {k: v for k, v in cfg.items() if k not in ("units", "thresholds")}
    new["country"] = code
    us = code == "US"
    new["units"] = {"temp": "F" if us else "C", "radon": "pCi/L" if us else "Bq/m3"}
    return new

def breaches(dev, cfg, units, thr, now):
    room = label(dev, cfg)
    rec = datetime.fromisoformat(dev["recorded"]).replace(tzinfo=timezone.utc) if dev.get("recorded") else None
    stale = cfg.get("stale_hours", 3)
    if rec is None or now - rec > timedelta(hours=stale):
        return room, [dict(room=room, metric="offline", key="offline", value=dev.get("recorded"), unit="",
                           threshold=f"no reading for {stale}h", side=1, excess=0, scale=1)], {}
    vals = {s["sensorType"].replace("radonShortTermAvg", "radon"): s["value"] for s in dev.get("sensors", [])}
    if dev.get("batteryPercentage") is not None: vals["battery"] = dev["batteryPercentage"]
    out, shown = [], {}
    for m, (lo, hi) in thr.items():
        if m not in vals: continue
        v = convert(m, vals[m], units); shown[m] = v
        unit = {"temp": units["temp"], "radon": units["radon"], "co2": "ppm", "humidity": "%", "voc": "ppb",
                "pm25": "ug/m3", "battery": "%"}[m]
        over = hi is not None and (v >= hi if m == "radon" else v > hi)
        if over or (lo is not None and v < lo):
            side, t = (1, hi) if over else (-1, lo)
            key = m + ("_hi" if over and lo is not None else "_lo" if not over and hi is not None else "")
            out.append(dict(room=room, metric=m, key=key, value=v, unit=unit, threshold=t, side=side,
                            excess=abs(v - t), scale=abs(t) or 1))
    return room, out, shown

def run(cfg, state, now, diagnose=False):
    units, thr = defaults(cfg); diag = []
    res = {"status": "ok", "checked_at": now.isoformat(timespec="seconds"), "alerts": [], "readings": {}}
    try:
        ok = bool(os.environ.get("AIRTHINGS_CLIENT_ID") and os.environ.get("AIRTHINGS_CLIENT_SECRET"))
        diag.append({"step": "keys", "ok": ok, "detail": "set" if ok else "missing"})
        if not ok: raise ApiError(2, "auth_error")
        form = urllib.parse.urlencode({"grant_type": "client_credentials", "scope": "read:device:current_values",
            "client_id": os.environ["AIRTHINGS_CLIENT_ID"], "client_secret": os.environ["AIRTHINGS_CLIENT_SECRET"]}).encode()
        try: _, tok = call("POST", TOKEN_URL, form, {"Content-Type": "application/x-www-form-urlencoded"})
        except ApiError as e: diag.append({"step": "token", "ok": False, "detail": e.status}); raise
        diag.append({"step": "token", "ok": True, "detail": "HTTP 200"})
        h = {"Authorization": "Bearer " + tok["access_token"]}
        accts = call("GET", API + "/accounts", None, h)[1].get("accounts", [])
        diag.append({"step": "account", "ok": bool(accts), "detail": f"{len(accts)} account(s)"})
        if not accts: raise ApiError(4, "no_account")
        devs = call("GET", f"{API}/accounts/{accts[0]['id']}/sensors", None, h)[1].get("results", [])
    except ApiError as e:
        res["status"], code = e.status, e.code
        if code == 2 and not diagnose:
            state["auth_failures"] = state.get("auth_failures", 0) + 1
            if state["auth_failures"] >= 2: res["status"] = "pause_and_ask"
        res["diagnose"] = diag if diagnose else None
        return res, code
    state["auth_failures"], state["last_ok"] = 0, res["checked_at"]
    seen = {d["serialNumber"] for d in devs}
    devs += [{"serialNumber": s} for s in cfg.get("rooms", {}) if s not in seen]  # configured but missing
    found, quiet = [], in_quiet(cfg, now)
    for d in devs:
        room, b, shown = breaches(d, cfg, units, thr, now)
        res["readings"][room] = shown or "offline"; found += b
        diag.append({"step": "device", "ok": not any(x["metric"] == "offline" for x in b), "detail": room,
                     "last_seen": d.get("recorded")})
    res["diagnose"] = diag if diagnose else None
    if diagnose: return res, 0
    last, held, cool = state.setdefault("alerts", {}), state.setdefault("held", {}), cfg.get("cooldown_hours", 12)
    active = {f"{b['room']}|{b['key']}" for b in found}
    for k in [k for k in last if k not in active]: del last[k]
    for b in found:
        k, prev = f"{b['room']}|{b['key']}", last.get(f"{b['room']}|{b['key']}")
        due = (not prev or now - datetime.fromisoformat(prev["t"]) >= timedelta(hours=cool)
               or b["excess"] - prev["excess"] >= 0.1 * b["scale"])
        if not due: continue
        if quiet and b["metric"] not in URGENT:
            held[k] = {**{x: b[x] for x in ("room", "metric", "value", "unit", "threshold")}, "held_at": res["checked_at"]}
            continue
        last[k] = {"t": res["checked_at"], "excess": b["excess"]}
        a = {x: b[x] for x in ("room", "metric", "value", "unit", "threshold")}
        a["fix"] = FIX[b["key"] if b["key"] in FIX else b["metric"]]
        if k in held: a["held_since"] = held.pop(k)["held_at"]
        res["alerts"].append(a)
    if not quiet:  # quiet hours over: deliver held alerts that have since cleared
        for k, h0 in list(held.items()):
            res["alerts"].append({**h0, "fix": "Held during quiet hours; back in range now.", "resolved": True})
            del held[k]
    res["held_count"] = len(held)
    return res, 0

def main(argv):
    diagnose = "--diagnose" in argv
    cp = os.path.join(HOME, "config.json")
    cfg = json.load(open(cp))
    if "--set-country" in argv:
        i = argv.index("--set-country")
        try: new = set_country(cfg, argv[i + 1] if i + 1 < len(argv) else "")
        except ValueError as e: print(json.dumps({"status": "error", "detail": str(e)})); return 1
        json.dump(new, open(cp, "w"), indent=1)
        u, t = defaults(new)
        print(json.dumps({"status": "ok", "country": new["country"], "units": u, "radon_alert": t["radon"][1],
                          "dropped_thresholds": cfg.get("thresholds", {})}, indent=1))
        return 0
    sp = os.path.join(HOME, "state.json")
    state = json.load(open(sp)) if os.path.exists(sp) else {}
    res, code = run(cfg, state, datetime.now(timezone.utc), diagnose)
    if not diagnose:
        json.dump(state, open(sp, "w"), indent=1)
    print(json.dumps(res, indent=1))
    return code

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```
