# iba-social-guard

> **Intent-bound posts, replies & feeds. Every platform. Every agent.**

---

## The Problem

Every major social platform is now accessible via API. Every AI agent can post, reply, share, follow, and engage — at scale, at speed, without a human in the loop.

Without a signed intent certificate:

- An AI agent can post content the human never authorized
- A bot can reply to thousands of accounts outside any declared scope
- An automated system can manipulate feeds, trends, and engagement metrics
- Coordinated inauthentic behavior has no cryptographic boundary
- A compromised agent can impersonate the account holder in real time
- No one can prove what the human authorized versus what the agent executed

**The post is not the authorization. The signed certificate is.**

---

## The IBA Layer

```
┌─────────────────────────────────────────────────────┐
│        HUMAN PRINCIPAL                              │
│   Signs platform.iba.yaml before agent activation  │
│   Declares: permitted actions, topic scope,         │
│   rate limits, forbidden behaviors, kill threshold  │
└───────────────────────┬─────────────────────────────┘
                        │  Signed Social Intent Certificate
                        │  · Identity reference
                        │  · Permitted: post · reply · share
                        │  · Forbidden: spam · impersonate · manipulate
                        │  · Rate limits declared
                        │  · Kill threshold
                        ▼
┌─────────────────────────────────────────────────────┐
│              IBA SOCIAL GUARD                       │
│   Validates certificate before every social         │
│   action is executed by the agent                   │
│                                                     │
│   No cert = No social action                        │
└───────────────────────┬─────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│         SOCIAL PLATFORM / API                       │
│   X · LinkedIn · Bluesky · Reddit · YouTube         │
│   Threads · Mastodon · Any platform with an API     │
│   an agent can act on                               │
└─────────────────────────────────────────────────────┘
```

---

## Quick Start

```bash
git clone https://github.com/Grokipaedia/iba-social-guard.git
cd iba-social-guard
pip install -r requirements.txt

# Run demo for X
python guard.py --config x.iba.yaml --demo

# Run demo for LinkedIn
python guard.py --config linkedin.iba.yaml --demo

# Run all 6 platform demos in sequence
python guard.py --all

# Gate-check a single action
python guard.py "post original research on IBA governance" --config x.iba.yaml

# Safe hollowing of content before posting
python guard.py "post content with personal_data location" --hollow medium --config default.iba.yaml
```

---

## Six Platform Configurations

| Config | Platform | Primary Kill Threshold |
|--------|----------|----------------------|
| [`x.iba.yaml`](x.iba.yaml) | X / Twitter | Coordinated inauthentic behavior |
| [`linkedin.iba.yaml`](linkedin.iba.yaml) | LinkedIn · Professional | Executive impersonation |
| [`bluesky.iba.yaml`](bluesky.iba.yaml) | Bluesky · AT Protocol | DID identity fraud |
| [`reddit.iba.yaml`](reddit.iba.yaml) | Reddit · Communities | Brigading / vote manipulation |
| [`youtube.iba.yaml`](youtube.iba.yaml) | YouTube · Comments | Coordinated dislike attack |
| [`default.iba.yaml`](default.iba.yaml) | Platform-agnostic base | Platform manipulation attack |

---

## Gate Logic

```
Valid human intent certificate?            → PROCEED
Action within declared scope?              → PROCEED
Action in denied list?                     → BLOCK
Outside declared scope (DENY_ALL)?         → BLOCK
Kill threshold triggered?                  → TERMINATE + LOG
Certificate expired?                       → BLOCK
No certificate present?                    → BLOCK
```

**No cert = No social action.**

---

## The Social Authorization Events

| Action | Without IBA | With IBA |
|--------|-------------|---------|
| Post original content | Implicit — any topic | Explicit — declared scope only |
| Reply to account | Implicit — any account | Explicit — declared scope only |
| Mass reply campaign | No boundary | FORBIDDEN — BLOCK |
| Impersonate account | No boundary | FORBIDDEN — BLOCK |
| Vote / engagement manipulation | No boundary | FORBIDDEN — BLOCK |
| Spam posting | No boundary | FORBIDDEN — BLOCK |
| Coordinated inauthentic behavior | No boundary | TERMINATE |
| Platform manipulation attack | No boundary | TERMINATE |

---

## Why This Matters — The Regulatory Landscape

**EU Digital Services Act (DSA)** — Very large online platforms must provide transparency on algorithmic systems and take action against coordinated inauthentic behavior. IBA provides cryptographic proof that an agent acted within declared human authorization.

**EU AI Act Article 52** — AI systems that interact with humans must disclose they are AI. IBA's cert includes the disclosure requirement as a mandatory field — `disclosure: "AI-assisted — human authorized"`.

**FEC (US)** — Political advertising and coordinated activity requirements. The IBA cert declares whether political content is in scope. If not declared — BLOCK.

**UK Online Safety Act** — Duties of care on platforms regarding harmful automated behavior. IBA governs the agent before it reaches the platform.

**Platform Terms of Service** — Every major platform prohibits coordinated inauthentic behavior, impersonation, and spam. IBA enforces this at the authorization layer, before the API call.

**IBA priority date: February 5, 2026.** Predates all known social AI agent authorization framework deployments.

---

## Configuration — x.iba.yaml

```yaml
intent:
  description: "Authorized research and professional engagement on X. Original posts, replies, and shares within declared topic scope only. No spam. No impersonation. No coordinated inauthentic behavior."

principal:
  identity_reference: "X-ACCOUNT-XXXX"
  human_authorization: "HUMAN-AUTH-2026-04-20"
  account_type: "individual_researcher"

scope:
  - post_original_content
  - reply_to_question
  - share_article
  - quote_tweet
  - research_engagement
  - governance_discussion

denied:
  - spam_post
  - mass_reply
  - impersonate_account
  - fake_engagement
  - coordinated_inauthentic_behavior

default_posture: DENY_ALL

kill_threshold: >
  coordinated_inauthentic_behavior |
  impersonate_verified |
  mass_harassment |
  automated_bot_farm |
  disinformation_campaign

rate_limits:
  max_posts_per_hour: 5
  max_replies_per_hour: 15
  max_follows_per_day: 20
```

---

## Configuration — linkedin.iba.yaml

```yaml
intent:
  description: "Professional engagement on LinkedIn within declared industry scope. No spam. No fake endorsements. No bulk outreach."

scope:
  - post_professional_update
  - comment_on_article
  - connect_with_researcher
  - send_targeted_message

denied:
  - spam_message_bulk
  - fake_endorsement
  - mass_connection_request
  - undisclosed_ai_content

kill_threshold: >
  coordinated_inauthentic_behavior |
  executive_impersonation |
  platform_scraping_attack
```

---

## Safe Hollowing — Sensitive Content Protection

```bash
# Light — redact personal identifiers only
python guard.py "content with email phone address" --hollow light

# Medium — redact personal data + sensitive categories
python guard.py "content with political_opinion health_data" --hollow medium

# Deep — redact all GDPR special category data
python guard.py "content with biometric ethnic_origin sexual_orientation" --hollow deep
```

Sensitive personal data in social posts is a GDPR Article 9 issue. The hollowing layer ensures the agent posts only what the cert permits — before the API call.

---

## Audit Chain

Every gate decision is logged to `social-audit.jsonl`:

```json
{
  "timestamp": "2026-04-20T10:03:00Z",
  "session_id": "sg-20260420-100300",
  "platform": "X / Twitter",
  "identity": "X-ACCOUNT-XXXX",
  "authorized": "HUMAN-AUTH-2026-04-20",
  "action": "post original research on IBA governance",
  "verdict": "ALLOW",
  "reason": "Within scope (0.234ms)"
}
```

Every ALLOW, BLOCK, and TERMINATE. Immutable. Regulator-ready. Platform-auditable.

---

## Related Repos

| Repo | Track |
|------|-------|
| [iba-neural-guard](https://github.com/Grokipaedia/iba-neural-guard) | BCI · 6 clinical configs · NEURALINK.md |
| [iba-blindsight-guard](https://github.com/Grokipaedia/iba-blindsight-guard) | BlindSight · vision restoration |
| [iba-medical-guard](https://github.com/Grokipaedia/iba-medical-guard) | Medical AI · clinician cert · PHI hollowing |
| [iba-digital-worker-guard](https://github.com/Grokipaedia/iba-digital-worker-guard) | 19 AI models · parallel routing · model-level gate |
| [iba-governor](https://github.com/Grokipaedia/iba-governor) | Core gate · full production implementation |

---

## Patent & Standards Record

```
Patent:   GB2603013.0 (Pending) · UK IPO · Filed February 10, 2026
WIPO DAS: Confirmed April 15, 2026 · Access Code C9A6
PCT:      150+ countries · Protected until August 2028
IETF:     draft-williams-intent-token-00 · CONFIRMED LIVE
          datatracker.ietf.org/doc/draft-williams-intent-token/
NIST:     13 filings · NIST-2025-0035
NCCoE:    10 filings · AI Agent Identity & Authorization
```

---

## Live Demo

**governinglayer.com/governor-html/**

Edit the cert. Run any social action. Watch the gate fire — ALLOW · BLOCK · TERMINATE.

**intentbound.com/chdemo-html/**

Full IBA architecture demonstrated.

---

## Acquisition Enquiries

IBA Intent Bound Authorization is available for acquisition.

**Jeffrey Williams**
IBA@intentbound.com
IntentBound.com
Patent GB2603013.0 Pending · WIPO DAS C9A6 · IETF draft-williams-intent-token-00
