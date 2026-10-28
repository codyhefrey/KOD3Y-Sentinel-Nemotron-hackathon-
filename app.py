"""Synthetic-only KOD3Y Sentinel hackathon prototype. Python 3.10+."""
import json
import os
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import Request, urlopen

def analyze(events):
    if not isinstance(events,list) or not 1 <= len(events) <= 200:
        raise ValueError("Supply 1–200 synthetic events")
    clean=[]
    for i,e in enumerate(events):
        if not isinstance(e,dict): raise ValueError("Event must be an object")
        try:
            t=datetime.fromisoformat(e["timestamp"].replace("Z","+00:00"))
            if t.tzinfo is None: raise ValueError("Timezone required")
        except (KeyError,ValueError,TypeError) as exc:
            raise ValueError("Event needs ISO timestamp with timezone") from exc
        clean.append({"id":f"EVT-{i+1:03}","time":t,"action":str(e.get("action",""))[:64].lower(),
                      "result":str(e.get("result",""))[:32].lower(),"user":str(e.get("user","demo"))[:64]})
    clean.sort(key=lambda e:e["time"])
    findings=[]
    for e in clean:
        if e["action"] in ("mfa_disabled","audit_logging_disabled") and e["result"]=="success":
            findings.append({"title":e["action"].replace("_"," ").title(),"severity":"high","evidence":[e["id"]]})
    users={e["user"] for e in clean}
    for user in users:
        failures=[e for e in clean if e["user"]==user and e["action"]=="login" and e["result"]=="failure"]
        for end,row in enumerate(failures):
            window=[e for e in failures[:end+1] if timedelta(0)<=row["time"]-e["time"]<=timedelta(minutes=15)]
            if len(window)>=3:
                findings.append({"title":"Repeated failed logins","severity":"high","evidence":[e["id"] for e in window]})
                break
    return {"event_count":len(clean),"findings":findings,"notice":"Synthetic demo; findings are not proof of compromise."}

def nebius(report):
    key=os.getenv("NEBIUS_API_KEY"); model=os.getenv("NEBIUS_MODEL")
    if not key or not model: return {"status":"not_configured","message":"No live AI request made"}
    base=os.getenv("NEBIUS_BASE_URL","https://api.tokenfactory.nebius.com/v1").rstrip("/")
    if not base.startswith("https://"): raise ValueError("HTTPS endpoint required")
    data=json.dumps({"model":model,"messages":[
        {"role":"system","content":"Defensive security assistant. Use only provided synthetic evidence. Cite EVT identifiers; separate facts from hypotheses; suggest human-reviewed next steps. Never invent evidence."},
        {"role":"user","content":json.dumps(report)}]}).encode()
    req=Request(base+"/chat/completions",data=data,headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},method="POST")
    with urlopen(req,timeout=20) as res: answer=json.load(res)
    return {"status":"live","model":model,"text":answer["choices"][0]["message"]["content"]}

class Handler(BaseHTTPRequestHandler):
    def reply(self,status,obj):
        data=json.dumps(obj).encode();self.send_response(status)
        self.send_header("Content-Type","application/json")
        self.send_header("Cache-Control","no-store")
        self.send_header("Content-Length",str(len(data)));self.end_headers();self.wfile.write(data)
    def do_GET(self):
        if self.path=="/api/health":return self.reply(200,{"status":"ok","nebius_configured":bool(os.getenv("NEBIUS_API_KEY") and os.getenv("NEBIUS_MODEL"))})
        if self.path not in ("/","/index.html"):return self.reply(404,{"error":"Not found"})
        data=Path(__file__).with_name("index.html").read_bytes();self.send_response(200)
        self.send_header("Content-Type","text/html; charset=utf-8")
        self.send_header("Content-Security-Policy","default-src 'none'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; connect-src 'self'")
        self.send_header("Content-Length",str(len(data)));self.end_headers();self.wfile.write(data)
    def do_POST(self):
        if self.path!="/api/analyze":return self.reply(404,{"error":"Not found"})
        try:
            size=int(self.headers.get("Content-Length","0"))
            if not 0<size<=128000:return self.reply(413,{"error":"Invalid request size"})
            payload=json.loads(self.rfile.read(size)); report=analyze(payload["events"])
            ai=nebius(report) if payload.get("use_ai") is True else {"status":"not_requested"}
            return self.reply(200,{"report":report,"ai":ai})
        except (ValueError,KeyError,TypeError) as exc:return self.reply(400,{"error":str(exc)})
        except Exception:return self.reply(502,{"error":"Nebius request failed; verify access, model and credits"})

if __name__=="__main__":
    port=int(os.getenv("PORT","8766"))
    print(f"Open http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1",port),Handler).serve_forever()
