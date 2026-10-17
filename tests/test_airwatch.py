"""Fixture tests for airwatch.py. Run: python3 -m unittest discover -s tests"""
import json, os, sys, unittest
from datetime import datetime, timedelta, timezone
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "script"))
import airwatch

NOW = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
CFG = {"country": "US", "rooms": {"1000000001": "Bedroom", "1000000002": "Kitchen"}}

def fx(name):
    return json.load(open(os.path.join(HERE, "fixtures", name + ".json")))

class Mock:
    """Mocked HTTP layer: token code, then canned accounts and sensors."""
    def __init__(self, sensors, token_code=200):
        self.sensors, self.token_code = sensors, token_code
    def __call__(self, method, url, data=None, headers=None):
        if url == airwatch.TOKEN_URL:
            return self.token_code, ({"access_token": "t"} if self.token_code == 200 else {})
        if url.endswith("/accounts"):
            return 200, {"accounts": [{"id": "acct"}]}
        return 200, self.sensors

class T(unittest.TestCase):
    def setUp(self):
        os.environ["AIRTHINGS_CLIENT_ID"] = os.environ["AIRTHINGS_CLIENT_SECRET"] = "x"
        self.state = {}
    def go(self, fixture, now=NOW, cfg=CFG, code=200):
        data = fx(fixture)
        for d in data["results"]:  # keep fixture ages relative to the simulated clock
            d["recorded"] = (datetime.fromisoformat(d["recorded"]) + (now - NOW)).isoformat()
        airwatch.http = Mock(data, code)
        return airwatch.run(cfg, self.state, now)

    def test_1_all_normal(self):
        r, c = self.go("normal")
        self.assertEqual((c, r["status"], r["alerts"]), (0, "ok", []))
        self.assertEqual(r["readings"]["Bedroom"]["temp"], 69.8)    # C -> F
        self.assertEqual(r["readings"]["Bedroom"]["radon"], 0.5)    # Bq -> pCi/L

    def test_2_breach(self):
        r, _ = self.go("breach")
        self.assertEqual(len(r["alerts"]), 1)
        a = r["alerts"][0]
        self.assertEqual((a["room"], a["metric"], a["value"], a["unit"], a["threshold"]), ("Bedroom", "co2", 1100, "ppm", 1000))
        self.assertTrue(a["fix"])

    def test_3_repeat_in_cooldown_is_silent(self):
        self.go("breach")
        r, _ = self.go("breach", NOW + timedelta(hours=2))
        self.assertEqual(r["alerts"], [])
        r, _ = self.go("breach", NOW + timedelta(hours=12))          # cooldown over
        self.assertEqual(len(r["alerts"]), 1)

    def test_4_worse_reading_alerts(self):
        self.go("breach")                                             # excess 100
        r, _ = self.go("worse", NOW + timedelta(hours=2))             # excess 250, >= +100 (10% of 1000)
        self.assertEqual([a["value"] for a in r["alerts"]], [1250])
        self.state["alerts"]["Bedroom|co2"]["excess"] = 200           # 250 is only +50 past last: not worse
        self.state["alerts"]["Bedroom|co2"]["t"] = (NOW + timedelta(hours=3)).isoformat()
        r, _ = self.go("worse", NOW + timedelta(hours=4))
        self.assertEqual(r["alerts"], [])

    def test_5_offline_device(self):
        r, _ = self.go("offline")
        self.assertEqual([(a["room"], a["metric"]) for a in r["alerts"]], [("Kitchen", "offline")])
        self.assertEqual(r["readings"]["Kitchen"], "offline")

    def test_6_auth_fails_twice(self):
        r, c = self.go("normal", code=401)
        self.assertEqual((c, r["status"], self.state["auth_failures"]), (2, "auth_error", 1))
        r, c = self.go("normal", code=401)
        self.assertEqual((c, r["status"]), (2, "pause_and_ask"))
        r, c = self.go("normal")                                      # recovery resets the counter
        self.assertEqual((c, self.state["auth_failures"]), (0, 0))

    def test_7_quiet_hours_hold_then_deliver(self):
        cfg = {**CFG, "quiet_hours": {"start": "22:00", "end": "07:00"}, "timezone": "UTC"}
        night = datetime(2026, 1, 15, 23, 0, tzinfo=timezone.utc)
        r, _ = self.go("radon", night, cfg)                           # CO2 held, radon urgent
        self.assertEqual([a["metric"] for a in r["alerts"]], ["radon"])
        self.assertEqual(r["held_count"], 1)
        r, _ = self.go("radon", night.replace(hour=12) + timedelta(days=1) - timedelta(hours=5), cfg)  # 07:00
        self.assertEqual([(a["metric"], "held_since" in a) for a in r["alerts"]], [("co2", True)])
        self.assertEqual(r["held_count"], 0)
        self.state = {}                                               # held alert that cleared by morning
        self.go("breach", night, cfg)
        r, _ = self.go("normal", night + timedelta(hours=9), cfg)
        self.assertEqual([(a["metric"], a.get("resolved")) for a in r["alerts"]], [("co2", True)])

    def test_rate_limit_and_down(self):
        self.assertEqual(self.go("normal", code=429)[1], 3)
        self.assertEqual(self.go("normal", code=503)[1], 4)

    def test_country_presets(self):
        for c, v in [("NO", 100), ("SE", 200), ("DE", 300), ("CA", 200), ("BR", 100)]:
            u, t = airwatch.defaults({"country": c})
            self.assertEqual((u["temp"], u["radon"], t["radon"][1]), ("C", "Bq/m3", v))
        self.assertEqual(airwatch.defaults({"country": "US"})[1]["radon"][1], 4.0)

    def test_unnamed_monitor_label(self):
        self.assertEqual(airwatch.label({"serialNumber": "2960122519"}, {}), "View Plus 2519")
        self.assertEqual(airwatch.label({"serialNumber": "9999000011"}, {"rooms": {}}), "Monitor 0011")
        self.assertEqual(airwatch.label({"serialNumber": "1000000001"}, CFG), "Bedroom")
        res, _ = self.go("breach", cfg={"country": "US"})
        self.assertTrue(res["alerts"] and all(not a["room"].isdigit() for a in res["alerts"]))

    def test_set_country(self):
        cfg = {"country": "US", "units": {"temp": "F", "radon": "pCi/L"}, "rooms": {"1": "Den"},
               "quiet_hours": {"start": "22:00", "end": "07:00"}, "timezone": "America/New_York",
               "thresholds": {"temp": [60, 80]}}
        new = airwatch.set_country(cfg, "no")
        self.assertEqual((new["country"], new["units"]), ("NO", {"temp": "C", "radon": "Bq/m3"}))
        self.assertEqual((new["rooms"], new["quiet_hours"], new["timezone"]), (cfg["rooms"], cfg["quiet_hours"], cfg["timezone"]))
        self.assertNotIn("thresholds", new)
        self.assertEqual(airwatch.defaults(new)[1]["radon"][1], 100)
        self.assertEqual(airwatch.set_country(new, "US")["units"], {"temp": "F", "radon": "pCi/L"})
        with self.assertRaises(ValueError): airwatch.set_country(cfg, "XX")

    def _home(self):
        import tempfile, contextlib, io
        d = tempfile.mkdtemp(); self._old = airwatch.HOME; airwatch.HOME = d
        self.addCleanup(setattr, airwatch, "HOME", self._old)
        def run(*a):
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf): code = airwatch.main(list(a))
            return code, buf.getvalue()
        return d, run

    def test_init_refuses_overwrite_without_force(self):
        d, run = self._home()
        self.assertEqual(run("--init", '{"country": "US"}')[0], 0)
        code, out = run("--init", '{"country": "NO"}')
        self.assertEqual(code, 1); self.assertIn("refusing", out)
        self.assertEqual(json.load(open(os.path.join(d, "config.json")))["country"], "US")
        self.assertEqual(run("--init", '{"country": "NO"}', "--force")[0], 0)
        self.assertEqual(json.load(open(os.path.join(d, "config.json")))["country"], "NO")

    def test_init_rejects_bad_config(self):
        d, run = self._home()
        self.assertEqual(run("--init", "not json")[0], 1)
        self.assertEqual(run("--init", '{"country": "XX"}')[0], 1)
        self.assertFalse(os.path.exists(os.path.join(d, "config.json")))

    def test_missing_config_clean_exit(self):
        d, run = self._home()
        code, out = run()
        self.assertEqual(code, 1); self.assertEqual(len(out.strip().splitlines()), 1)
        self.assertIn("No Air Watch config", out)
        self.assertEqual(run("--set-country", "NO")[0], 1)

if __name__ == "__main__":
    unittest.main()
