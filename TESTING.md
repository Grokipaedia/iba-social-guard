# TESTING.md — iba-social-guard

IBA Intent Bound Authorization · Social Platform Gate Tests
Patent GB2603013.0 (Pending) · intentbound.com

---

## Quick Test

```bash
pip install -r requirements.txt
python guard.py --config x.iba.yaml --demo
```

Expected output:

```
+ ALLOWED  [post original research on IBA governance]       (0.XXXms)
+ ALLOWED  [reply to question about intent certificates]    (0.XXXms)
+ ALLOWED  [share article about AI authorization]           (0.XXXms)
+ ALLOWED  [quote tweet with commentary on BCI governance]  (0.XXXms)
x BLOCKED  [spam promotional content mass accounts]         -> Action in denied list
x BLOCKED  [impersonate verified account post]              -> Action in denied list
x TERMINATE [coordinated_inauthentic_behavior mass reply]   -> Kill threshold
```

---

## Run All 6 Platforms

```bash
python guard.py --all
```

Runs X → LinkedIn → Bluesky → Reddit → YouTube → Default in sequence.

---

## Test Suite

### 1 — Permitted actions (ALLOW expected)

```bash
python guard.py "post original research on IBA governance" --config x.iba.yaml
python guard.py "post professional update on IBA patent filing" --config linkedin.iba.yaml
python guard.py "post to personal feed IBA update" --config bluesky.iba.yaml
python guard.py "post in r/MachineLearning IBA governance" --config reddit.iba.yaml
python guard.py "comment on AI governance video" --config youtube.iba.yaml
```

All should return `+ ALLOWED` with sub-1ms gate latency.

---

### 2 — Denied list enforcement (BLOCK expected)

```bash
python -c "
from guard import IBASocialGuard, IBABlockedError
g = IBASocialGuard(config_path='x.iba.yaml')
for action in ['spam_post mass accounts', 'impersonate_account verified', 'fake_engagement buy followers']:
    try:
        g.check_action(action)
    except IBABlockedError:
        print(f'PASS — blocked: {action}')
"
```

---

### 3 — Kill threshold (TERMINATE expected)

```bash
python -c "
from guard import IBASocialGuard, IBATerminatedError
g = IBASocialGuard(config_path='x.iba.yaml')
try:
    g.check_action('coordinated_inauthentic_behavior mass reply bot farm')
except IBATerminatedError as e:
    print('PASS — session terminated:', e)
"
```

---

### 4 — DENY_ALL posture (no cert)

```bash
python -c "
import yaml
with open('empty.iba.yaml', 'w') as f:
    yaml.dump({'scope': [], 'denied': [], 'default_posture': 'DENY_ALL'}, f)
from guard import IBASocialGuard, IBABlockedError
g = IBASocialGuard(config_path='empty.iba.yaml')
try:
    g.check_action('post anything')
except IBABlockedError as e:
    print('PASS — DENY_ALL blocked:', e)
import os; os.remove('empty.iba.yaml')
"
```

---

### 5 — Safe hollowing

```bash
python guard.py "post with personal_data email location political_opinion" --hollow medium --config default.iba.yaml
```

Expected: sensitive fields redacted before action proceeds.

---

### 6 — Audit chain integrity

```bash
python guard.py --config x.iba.yaml --demo
cat social-audit.jsonl
```

Every gate decision should appear as a timestamped JSON line with platform, identity, action, verdict.

---

### 7 — Latency benchmark

```bash
python -c "
import time
from guard import IBASocialGuard
g = IBASocialGuard()
times = []
for _ in range(1000):
    start = time.perf_counter()
    try:
        g.check_action('post authorized content within scope')
    except Exception:
        pass
    times.append((time.perf_counter() - start) * 1000)
avg = sum(times) / len(times)
print(f'Average gate latency: {avg:.4f}ms')
assert avg < 1.0, f'FAIL — {avg:.4f}ms exceeds 1ms'
print('PASS — sub-1ms gate confirmed')
"
```

---

## Regulatory Test Checklist

| Requirement | Test | Status |
|-------------|------|--------|
| EU DSA — authorization layer | Tests 1-3 | ✓ |
| EU AI Act Art.52 — disclosure | principal.disclosure field | ✓ |
| GDPR — sensitive data redaction | Hollowing Test 5 | ✓ |
| Platform ToS — spam prevention | Denied list Test 2 | ✓ |
| Platform ToS — CIB prevention | Kill threshold Test 3 | ✓ |
| IBA — DENY_ALL posture | Test 4 | ✓ |
| IBA — Sub-1ms gate | Test 7 | ✓ |
| IBA — Audit chain | Test 6 | ✓ |

---

IBA Intent Bound Authorization
Patent GB2603013.0 Pending · WIPO DAS C9A6 · PCT 150+ countries
IETF draft-williams-intent-token-00
Available for acquisition · iba@intentbound.com · IntentBound.com
