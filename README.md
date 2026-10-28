# KOD3Y Sentinel — Nemotron Security Copilot

A **public, standalone hackathon edition** of a defensive cybersecurity investigation concept. This repository contains independent synthetic-data demo code; it does not publish the original private KOD3Y Sentinel AI project.

## What works

- Browser interface for synthetic JSON event input
- Python standard-library HTTP backend and transparent detection rules
- Repeated login failure detection (3+ attempts within 15 minutes)
- Sensitive security-change flags and event ID references
- Optional **real** Nebius Token Factory chat-completions API adapter
- Honest offline state when no model credentials are configured
- Four unit tests

**Important:** The Nebius integration is implemented but has **not been verified against a live NVIDIA model**. Do not describe the project as fully compliant with hackathon model requirements until a real successful API call is recorded.

## Run locally

Python 3.10+; no packages required.

```bash
python app.py
```

Open http://127.0.0.1:8766 and click **Analyze events**.

Run tests:

```bash
python -m unittest -v test_app.py
```

## Optional Nebius integration

Get access through the official Nebius platform. Check the model catalog for the **exact available NVIDIA Nemotron model ID**. Do not commit credentials.

PowerShell:

```powershell
$env:NEBIUS_API_KEY = "YOUR_KEY_HERE"
$env:NEBIUS_MODEL = "YOUR_AVAILABLE_NVIDIA_MODEL_ID"
python app.py
```

The backend defaults to `https://api.tokenfactory.nebius.com/v1/chat/completions`; override `NEBIUS_BASE_URL` if your Nebius account documents a different endpoint. Select the **Request real Nebius explanation** checkbox to opt in. This may use paid credits. Errors are shown rather than faking a successful AI response.

## Safety and limitations

Only synthetic logs are appropriate for this prototype. There is no authentication, persistence, rate limiting, production hardening or automatic response action. Run on localhost only. Evidence is limited to the synthetic input; AI text is advisory and requires independent verification. Do not deploy this server publicly as-is.

## Hackathon completion checklist

- [x] Independent public repository with Apache-2.0 license
- [x] Python backend, browser UI and offline tests
- [ ] Confirm NVIDIA Nemotron model ID and **successful real Nebius runtime call**
- [ ] Verify actual API responses and security safeguards
- [ ] Host a safe working demo with suitable authentication and controls
- [ ] Record a public YouTube demo under 3 minutes
- [ ] Complete Devpost story, track, feedback and submission before deadline

## Intellectual property

The competition edition is released under the repository's Apache-2.0 license. The separate private flagship repository is not included here.
