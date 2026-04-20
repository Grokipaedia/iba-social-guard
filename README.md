# iba-x-guard

**Intent-bound posts, replies & feeds. No more chaos on X.**

Haha cousin — IBA governance on X? Wild pivot indeed.

This tool adds real cryptographic intent binding to every post, reply, quote, and feed interaction.

Wrap any X action with a signed **IBA Intent Certificate** so your content stays within your exact approved scope and consent rules.

## Features
- Requires IBA-signed intent before posting, replying, or engaging
- Enforces scope (research-only, no spam, no sensitive topics, no impersonation)
- Hard-denies unauthorized algo tweaks, mass-replies, or feed manipulation
- Optional safe hollowing of sensitive content
- Works with any X client, bot, or API integration

## Patent & Filings
- **Patent Pending**: GB2603013.0 (filed 5 Feb 2026, PCT route open — 150+ countries)
- **NIST Docket**: NIST-2025-0035 (13 IBA filings)
- **NCCoE Filings**: 10 submissions on AI agent authorization

## Quick Start
```bash
git clone https://github.com/Grokipaedia/iba-x-guard.git
cd iba-x-guard
pip install -r requirements.txt
python guard.py "post about IBA governance on X" --hollow medium
