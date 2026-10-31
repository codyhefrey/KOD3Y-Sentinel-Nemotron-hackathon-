# KOD3Y Sentinel — Nemotron Security Copilot

**Public demonstration:** https://kod3y-sentinel-nemotron-demo.onrender.com

The hosted synthetic-event investigation engine is live on Render. **NVIDIA Nemotron model inference through Nebius is not yet verified and remains disabled** in the public service. The public service's rule-based demonstration is not a substitute for the contest's required live model use.

**Evidence-first security investigation** for the 2026 Nebius x NVIDIA Global AI Hackathon. This is a **public, standalone, synthetic-only competition edition** under KOD3Y T3CH. The private flagship Sentinel repository is **not** included.

## What runs today

- Browser investigation studio with three preloaded synthetic scenarios
- Deterministic analyst rules: login failure bursts, successful login after failures, MFA and audit-logging changes
- Findings traceable to immutable demo event IDs, severity and human-review playbooks
- Server-side optional NVIDIA Nemotron explanation via Nebius Token Factory's OpenAI-compatible endpoint
- Live AI is **disabled by default**, requires an issued key, NVIDIA Nemotron model, feature flag and separate demo authorization token
- Automated GitHub Actions unit and local HTTP smoke tests; no dependencies beyond Python 3.10+

**Live Nebius inference has NOT been verified with an authorized account or credits.** Without a successful real Token Factory call, this repository does **not** meet the hackathon's qualifying model/runtime requirement.

## Prerequisites

- **Python 3.10+**: Uses standard library modules only (`http.server`, `urllib`, `json`, `datetime`, `unittest`). No external packages or `pip install` required.
- **Web Browser**: Any modern browser (Chrome, Edge, Firefox, Safari) to interact with the local investigation studio UI.
- **Git**: For version control and cloning the repository.
- *(Optional)* **Node.js 18+ / 22+**: Only needed if verifying the inline JavaScript syntax check locally prior to CI (`node --check`).

## Run locally

Clone the repository and start the server:

**Windows (PowerShell):**
```powershell
git clone https://github.com/codyhefrey/KOD3Y-Sentinel-Nemotron-hackathon-.git
cd KOD3Y-Sentinel-Nemotron-hackathon-
py app.py
```

**macOS / Linux:**
```bash
git clone https://github.com/codyhefrey/KOD3Y-Sentinel-Nemotron-hackathon-.git
cd KOD3Y-Sentinel-Nemotron-hackathon-
python3 app.py
```

Open <http://127.0.0.1:8766> in your browser. Choose a scenario, then click **Analyze incident**. The synthetic rule engine runs entirely offline **without payment or an API key**. Press `Ctrl+C` in your terminal to stop the local server.

> **Tip:** You can customize the server host or port with environment variables, e.g. `$env:PORT="9000"` (Windows PowerShell) or `PORT=9000 python3 app.py` (macOS/Linux).

## Running tests

Run the reproducible test suite locally matching the GitHub Actions CI workflow:

**Windows (PowerShell):**
```powershell
py -m unittest discover -s . -p 'test_*.py' -v
```

**macOS / Linux:**
```bash
python3 -m unittest discover -s . -p 'test_*.py' -v
```

To quickly verify Python syntax across all modules:
```bash
python -m compileall -q .
```

The automated test suite runs completely offline with no network or API key required:
- `test_app.py`: 12 detector unit tests verifying deterministic rules (bursts, account takeover, MFA/audit log changes) and offline safety guards.
- `test_http.py`: 5 local loopback HTTP smoke tests verifying `/`, `/api/health`, `/api/analyze`, and error handling.

## Configure optional live Nebius/NVIDIA Nemotron

The official Nebius Token Factory API is OpenAI-compatible at `https://api.tokenfactory.nebius.com/v1/chat/completions`. The verified model ID must come from the model catalog available to **your account**. An example documented by Nebius is `nvidia/Nemotron-3_5-Lightning`.

First obtain the issued credentials and explicitly authorize any billing required in your own Nebius account. **Do not bypass billing requirements, enable charges unintentionally, or share access keys.**

```powershell
$env:NEBIUS_API_KEY = Read-Host "Paste the issued Nebius API key"
$env:NEBIUS_MODEL = "nvidia/Nemotron-3_5-Lightning"
$env:NEBIUS_AI_ENABLED = "1"
$env:DEMO_ACCESS_TOKEN = Read-Host "Create a separate, random demo access token"
py app.py
```

Only after choosing the **Request live NVIDIA Nemotron explanation** checkbox and supplying the separate demo access token will the server try a live request. The browser must **never** receive the Nebius API key. The access token protects the billable route; **do not post it publicly**. A passing offline test is not a verified live AI demonstration.

For public hosting, enable only the offline path by default; to provide judges an authenticated live AI demonstration, review provider allowances, grant restricted judge access and assess credit/cost exposure. Public unauthenticated requests will not trigger paid inference.

## Deployment preparation

A `render.yaml` free-tier blueprint is included. The service reads its port from `PORT`, uses `HOST=0.0.0.0` for hosting, and responds at `/api/health`. The service has been deployed at https://kod3y-sentinel-nemotron-demo.onrender.com on Render's free plan. The live host returns its UI, but **no Nebius model inference has been verified**. Public hosting alone does not meet the hackathon's qualifying runtime requirement.

## Safety

This is not a production SOC tool. Use **fictional/synthetic events only**. No log ingestion, persistence, identity verification, case management, rate limiting, production-grade authentication, enforcement, or automated remediation. Human verification is required for any finding or AI suggestion. Do not expose an unrestricted billable AI endpoint to the internet.

## Submission checklist

- [x] Public Apache-2.0 repository separate from the private flagship
- [x] Rules, source-linked evidence and synthetic scenario UI
- [x] CI test workflow
- [x] Render configuration ready and deployed (offline demo)
- [ ] **Actual successful NVIDIA Nemotron runtime request on Nebius**
- [ ] Hosted working demo and verified judge access
- [ ] Public YouTube demo under 3 minutes showing the required Nebius/NVIDIA inference
- [ ] Devpost fields, feedback and submission completed by **Oct 30, 2026, 1:00 PM EDT**

See [SUBMISSION.md](SUBMISSION.md) for the Devpost draft and video plan.

## Licensing

Apache License 2.0 applies only to files in **this** public repository. No private flagship source, credentials or trade secrets are included. Rights to external models, APIs and service output remain governed by their own terms.
