"""KOD3Y Sentinel — Nemotron Security Copilot (synthetic-data demo).

Public deterministic triage works without credentials. Optional Nebius inference
is disabled by default and requires a separately configured access token.
"""
import hmac
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
BASE_URL = "https://api.tokenfactory.nebius.com/v1"
MAX_BODY = 32000
PLAYBOOKS = {
    "login_burst": ["Confirm affected account and source in identity-provider logs.",
                    "Check recent successful sign-ins, MFA challenges, and unusual devices.",
                    "Apply account controls only after human review."],
    "mfa_disabled": ["Confirm who approved the MFA change and why.",
                     "Review related login activity and restore MFA if unauthorized."],
    "audit_logging_disabled": ["Confirm whether the logging change was approved.",
                               "Restore logging and preserve available audit evidence."],
    "possible_takeover": ["Escalate to the incident owner for urgent verification.",
                          "Review session history and revoke unauthorized sessions if confirmed."],
}


def _stamp(value):
    if not isinstance(value, str):
        raise ValueError("Every event needs an ISO timestamp with timezone.")
    try:
        instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if instant.utcoffset() is None:
            raise ValueError("Timezone required")
        return instant.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        raise ValueError("Every event needs an ISO timestamp with timezone.") from None


def analyze(events):
    """Deterministic rules; no inference, external calls, or claims of compromise."""
    if not isinstance(events, list) or not 1 <= len(events) <= 100:
        raise ValueError("Provide 1–100 synthetic security events.")
    clean = []
    for i, item in enumerate(events):
        if not isinstance(item, dict):
            raise ValueError("Each event must be a JSON object.")
        instant = _stamp(item.get("timestamp"))
        action = str(item.get("action", "")).strip().lower()[:64]
        result = str(item.get("result", "")).strip().lower()[:32]
        user = str(item.get("user", "demo")).strip()[:64]
        if not action or not result or not user:
            raise ValueError("Each event needs action, result, and user.")
        clean.append({"id": f"EVT-{i+1:03}", "time": instant,
                      "action": action, "result": result, "user": user})
    clean.sort(key=lambda x: (x["time"], x["id"]))
    findings = []

    def flag(code, title, severity, user, evidence):
        evidence_ids = list(dict.fromkeys(evidence))
        findings.append({"id": f"F-{len(findings)+1:03}", "code": code,
                         "title": title, "severity": severity, "user": user,
                         "evidence": evidence_ids, "confidence": "deterministic-rule-match",
                         "next_steps": PLAYBOOKS[code]})

    for row in clean:
        if row["result"] == "success" and row["action"] in ("mfa_disabled", "audit_logging_disabled"):
            code = row["action"]
            flag(code, code.replace("_", " ").title(), "high", row["user"], [row["id"]])

    by_user = defaultdict(list)
    for row in clean:
        by_user[row["user"]].append(row)
    for user, rows in sorted(by_user.items()):
        failures = [row for row in rows if row["action"] == "login" and row["result"] == "failure"]
        burst = []
        for row in failures:
            window = [r for r in failures if timedelta(0) <= row["time"]-r["time"] <= timedelta(minutes=15)]
            if len(window) >= 3:
                burst = window
                break
        if burst:
            flag("login_burst", "Repeated failed logins", "medium", user, [r["id"] for r in burst])
            after = [r for r in rows if r["action"] == "login" and r["result"] == "success"
                     and timedelta(0) <= r["time"]-burst[-1]["time"] <= timedelta(minutes=15)]
            if after:
                flag("possible_takeover", "Login after repeated failures (review needed)",
                     "high", user, [r["id"] for r in burst] + [after[0]["id"]])

    severity_counts = dict(Counter(f["severity"] for f in findings))
    return {"event_count": len(clean), "finding_count": len(findings),
            "severity_counts": {"high": severity_counts.get("high", 0),
                                "medium": severity_counts.get("medium", 0)},
            "findings": findings,
            "timeline": [{"id": e["id"], "timestamp": e["time"].isoformat(),
                          "action": e["action"], "result": e["result"], "user": e["user"]}
                         for e in clean[:20]],
            "notice": "Synthetic educational data. Rule matches are not proof of compromise."}


def nebius(report):
    """Protected and explicitly enabled NVIDIA Nemotron inference."""
    key = os.environ.get("NEBIUS_API_KEY", "").strip()
    model = os.environ.get("NEBIUS_MODEL", "").strip()
    if not key or not model:
        return {"status": "not_configured", "message": "Nebius credentials/model not configured."}
    if not model.lower().startswith("nvidia/") or "nemotron" not in model.lower():
        raise ValueError("NEBIUS_MODEL must be an NVIDIA Nemotron model ID.")
    base = os.environ.get("NEBIUS_BASE_URL", BASE_URL).rstrip("/")
    if not base.startswith("https://"):
        raise ValueError("HTTPS Nebius endpoint required.")
    payload = {"model": model, "max_tokens": 450, "temperature": 0.2, "messages": [
        {"role": "system", "content": (
            "You are a defensive security analysis assistant reviewing ONLY synthetic "
            "event evidence. Present: (1) observed facts with EVT IDs, "
            "(2) hypotheses explicitly marked unconfirmed, and "
            "(3) recommended human-reviewed verification steps. "
            "Never invent events, claim compromise, or initiate response actions.")},
        {"role": "user", "content": json.dumps({
            "event_count": report["event_count"], "findings": report["findings"],
            "timeline": report["timeline"],
        }, separators=(",", ":"))}
    ]}
    req = Request(base + "/chat/completions", json.dumps(payload).encode("utf-8"),
                  {"Authorization": "Bearer " + key, "Content-Type": "application/json"},
                  method="POST")
    try:
        with urlopen(req, timeout=18) as response:
            answer = json.load(response)
        content = answer["choices"][0]["message"]["content"]
        if not isinstance(content, str) or not content.strip():
            raise ValueError("Empty model response")
        return {"status": "live", "model": model, "text": content[:5000],
                "notice": "Model-generated analysis must be independently verified."}
    except HTTPError as exc:
        status = "authentication_required" if exc.code in (401, 403) else (
            "rate_limited" if exc.code == 429 else "upstream_error")
    except (URLError, TimeoutError, ValueError, KeyError, IndexError, TypeError, OSError):
        status = "upstream_error"
    return {"status": status, "message": "No verified model response. Check Nebius access and credits."}


class Handler(BaseHTTPRequestHandler):
    def reply(self, status, obj):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        for name, value in [("Content-Type", "application/json; charset=utf-8"),
                            ("Cache-Control", "no-store"),
                            ("X-Content-Type-Options", "nosniff"),
                            ("Content-Length", str(len(body)))]:
            self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def do_HEAD(self):
        # Hosting providers and link-preview clients commonly probe with HEAD.
        path = urlsplit(self.path).path
        if path in ("/", "/index.html", "/api/health"):
            self.send_response(200)
            self.send_header("Content-Length", "0")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
        else:
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()

    def do_GET(self):
        path = urlsplit(self.path).path
        if path == "/api/health":
            return self.reply(200, {"status": "ok", "demo": "synthetic",
                                    "ai_enabled": os.getenv("NEBIUS_AI_ENABLED") == "1"
                                                  and bool(os.getenv("DEMO_ACCESS_TOKEN"))})
        if path not in ("/", "/index.html"):
            return self.reply(404, {"error": "Not found"})
        page = (ROOT / "index.html").read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(page)

    def do_POST(self):
        if urlsplit(self.path).path != "/api/analyze":
            return self.reply(404, {"error": "Not found"})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= MAX_BODY:
                return self.reply(413, {"error": "Invalid request size."})
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict):
                raise ValueError("Expected a JSON object.")
            report = analyze(payload.get("events"))
            ai = {"status": "not_requested"}
            if payload.get("use_ai") is True:
                access = os.getenv("DEMO_ACCESS_TOKEN", "")
                if os.getenv("NEBIUS_AI_ENABLED") != "1" or not access:
                    ai = {"status": "disabled", "message": "AI calls are disabled for this public demo."}
                elif not hmac.compare_digest(self.headers.get("X-Demo-Token", ""), access):
                    return self.reply(403, {"error": "Demo authorization required for live AI."})
                else:
                    ai = nebius(report)
            return self.reply(200, {"report": report, "ai": ai})
        except (ValueError, TypeError, json.JSONDecodeError) as exc:
            return self.reply(400, {"error": str(exc)})


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8766"))
    host = os.getenv("HOST", "127.0.0.1")
    print(f"Visit http://{host}:{port}", flush=True)
    ThreadingHTTPServer((host, port), Handler).serve_forever()
