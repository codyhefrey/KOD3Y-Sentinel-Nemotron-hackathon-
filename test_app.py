import unittest
from app import analyze

class DetectorTests(unittest.TestCase):
    def test_login_burst(self):
        events=[{"timestamp":f"2026-10-28T09:0{i}:00Z","action":"login","result":"failure","user":"demo"} for i in range(3)]
        self.assertEqual(analyze(events)["findings"][0]["title"],"Repeated failed logins")
    def test_no_alert_on_success(self):
        events=[{"timestamp":"2026-10-28T09:00:00Z","action":"login","result":"success"}]
        self.assertEqual(analyze(events)["findings"],[])
    def test_invalid_timestamp(self):
        with self.assertRaises(ValueError):analyze([{"timestamp":"invalid"}])
    def test_sensitive_change(self):
        events=[{"timestamp":"2026-10-28T09:00:00Z","action":"mfa_disabled","result":"success"}]
        self.assertEqual(analyze(events)["findings"][0]["evidence"],["EVT-001"])

if __name__=="__main__":unittest.main()
