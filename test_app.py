import unittest
from unittest.mock import patch
from datetime import datetime
from app import analyze, nebius


def evt(minute, action, result, user="demo"):
    return {"timestamp": f"2026-10-28T09:{minute:02d}:00Z", "action": action,
            "result": result, "user": user}


class DetectorTests(unittest.TestCase):
    def test_login_burst(self):
        events = [evt(i, "login", "failure") for i in (0, 2, 4)]
        result = analyze(events)
        self.assertEqual(result["finding_count"], 1)
        self.assertEqual(result["findings"][0]["code"], "login_burst")
        self.assertEqual(result["findings"][0]["evidence"], ["EVT-001", "EVT-002", "EVT-003"])

    def test_success_after_burst(self):
        result = analyze([evt(i, "login", "failure") for i in (0, 2, 4)] +
                         [evt(5, "login", "success")])
        self.assertIn("possible_takeover", [x["code"] for x in result["findings"]])

    def test_no_burst_across_users(self):
        result = analyze([evt(0, "login", "failure", "a"),
                          evt(2, "login", "failure", "b"),
                          evt(4, "login", "failure", "a")])
        self.assertEqual(result["finding_count"], 0)

    def test_no_burst_outside_window(self):
        events = [evt(0, "login", "failure"), evt(16, "login", "failure"),
                  evt(35, "login", "failure")]
        self.assertEqual(analyze(events)["finding_count"], 0)

    def test_no_alert_on_success(self):
        self.assertEqual(analyze([evt(0, "login", "success")])["findings"], [])

    def test_invalid_timestamp(self):
        with self.assertRaises(ValueError):
            analyze([{"timestamp": "invalid", "action": "login", "result": "failure"}])

    def test_naive_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            analyze([{"timestamp": "2026-10-28T09:00:00", "action": "login",
                      "result": "failure"}])

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            analyze([])

    def test_sensitive_change(self):
        result = analyze([evt(0, "mfa_disabled", "success")])
        self.assertEqual(result["findings"][0]["evidence"], ["EVT-001"])
        self.assertEqual(result["severity_counts"]["high"], 1)

    def test_unsorted_events_preserve_evidence(self):
        result = analyze([evt(4, "login", "failure"), evt(0, "login", "failure"),
                          evt(2, "login", "failure")])
        self.assertEqual(result["findings"][0]["code"], "login_burst")
        self.assertEqual(set(result["findings"][0]["evidence"]),
                         {"EVT-001", "EVT-002", "EVT-003"})

    def test_nebius_without_credentials_does_not_call_network(self):
        with patch.dict("os.environ", {"NEBIUS_API_KEY": "", "NEBIUS_MODEL": ""}):
            with patch("app.urlopen") as mocked:
                self.assertEqual(nebius({"findings": []})["status"], "not_configured")
                mocked.assert_not_called()

    def test_model_must_be_nvidia_nemotron(self):
        with patch.dict("os.environ", {"NEBIUS_API_KEY": "dummy", "NEBIUS_MODEL": "openai/gpt-4"}):
            with self.assertRaises(ValueError):
                nebius({"findings": [], "timeline": [], "event_count": 0})


if __name__ == "__main__":
    unittest.main()
