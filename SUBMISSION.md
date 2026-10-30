# Nebius × NVIDIA — Devpost submission preparation

**Contest:** [Nebius × NVIDIA Global AI Hackathon](https://nebiusglobalaihackathon.devpost.com/)  
**Deadline:** Friday, October 30, 2026, **1:00 PM Toronto (EDT)**  
**Suggested track:** Best Apps and Agents  
**Project:** KOD3Y Sentinel — Nemotron Security Copilot  
**GitHub:** https://github.com/codyhefrey/KOD3Y-Sentinel-Nemotron-hackathon-  
**Working public demo URL:** NOT YET AVAILABLE — must be filled after actual deployment  
**Public YouTube demo URL:** NOT YET AVAILABLE — must be recorded and uploaded

> **Submission gate**: Do not claim the required Nebius+NVIDIA model call until an authenticated live request actually succeeds. Offline rule alerts alone do not qualify. The following text is a draft that must match the final tested version.

## Tagline

Trace security anomalies to evidence — then ask Nemotron for a defensible investigation plan.

## Project description — paste after live integration is verified

KOD3Y Sentinel is a security investigation prototype focused on explainable triage. Analysts explore synthetic event streams and receive deterministic rule-based signals for repeated login failures, a successful sign-in after a login-failure burst, MFA disabling, and audit-logging changes. Each finding references the exact synthetic event IDs, a severity level, and human-reviewed investigation steps.

The optional Nebius Token Factory integration sends a small, structured incident report — not credentials or real customer logs — to an NVIDIA Nemotron model for a separate plain-English explanation. The copilot is instructed to distinguish observed evidence from unverified hypotheses and to cite source event IDs. The UI explicitly distinguishes deterministic analysis from responses obtained through a verified live model call.

The model is advisory only. The prototype uses fictional data, takes no automatic enforcement action, and does not claim that a rule match proves compromise. It demonstrates a path toward evidence-grounded incident response tooling without publishing the separate private KOD3Y Sentinel intellectual property.

### How it works

1. Load one of three built-in synthetic security scenarios.
2. Run deterministic triage; review event IDs and human-reviewed response guidance.
3. If approved credentials, account access and a restricted demo token are configured, request an NVIDIA Nemotron explanation through Nebius Token Factory.
4. Compare the model's explanation with the source-linked rule findings. No remediation is executed.

### Built with

Python standard library, browser JavaScript and CSS, GitHub Actions, Nebius Token Factory, NVIDIA Nemotron (live use **must be verified before naming it as used**).

### Significant changes during hackathon period

Created a public standalone competition edition with a browser investigation workspace, synthetic event triage, evidence citations, optional server-side Nebius adapter, automated tests, demo-safe access guard and deployment configuration. Do not imply the previous private flagship was open-sourced.

### Feedback on Nebius/NVIDIA (edit with actual experience)

Documentation makes the Token Factory chat-completions format approachable. Our principal onboarding obstacle has been an account billing prerequisite while an AI Builder Program application is pending. We recommend faster hackathon credit provisioning or a clearly separated non-billable sandbox for first live tests. Model quality and inference performance **cannot yet be assessed** because a successful live call has not been verified.

## YouTube demo script — target 2 minutes 30 seconds

**0:00–0:20:** Open the public website. Describe the problem: noisy SOC alert queues and the need for evidence, not guesses.

**0:20–0:55:** Click *Account takeover* and *Analyze incident*. Show the numbered event evidence, high-severity/medium-severity findings, and playbook steps.

**0:55–1:15:** Switch to *Quiet baseline*. Explain why no rule match is **not** proof of safety.

**1:15–2:05:** **Only if a successful authorized live Nebius model call is available**, select the live option and demonstrate the actual response labeled NVIDIA Nemotron. Explain the API request path and actual model ID from your account. If it is not available, do **not** fake footage or claim model use.

**2:05–2:30:** Show the public repository, unit tests, license and caveats. Say the flagship private KOD3Y Sentinel platform was not exposed.

Use OBS Studio or Windows Snipping Tool screen recording, record your own narration, upload the video publicly to YouTube and add its actual URL. The competition requires a video **shorter than three minutes**.

## Final submission checklist

- [ ] Live NVIDIA model invocation via Nebius actually tested
- [ ] Verified public demo (judges can use through the judging period)
- [ ] Source and open-source license visible in GitHub
- [ ] YouTube link public, less than 3 minutes
- [ ] Best Apps and Agents track selected
- [ ] Accurate model/service details and feedback entered
- [ ] Project text matches observed behavior
- [ ] Submission accepted by Devpost **before 1:00 PM EDT Oct 30**

**IP warning:** This public Apache-2.0 edition is open source. Do not push proprietary private code or any secrets into it. Read the event rules and grants before submitting.
