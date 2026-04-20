# guard.py - IBA governance for X posts, replies & feeds
import json
from datetime import datetime
import sys
import argparse

def create_iba_x_guard(action: str, hollow_level: str = None):
    cert = {
        "iba_version": "2.0",
        "certificate_id": f"x-guard-{datetime.now().strftime('%Y%m%d-%H%M')}",
        "issued_at": datetime.now().isoformat(),
        "principal": "human-user",
        "declared_intent": f"X platform action: {action}. Posts, replies, and feeds must stay within approved scope and consent.",
        "scope_envelope": {
            "resources": ["post", "reply", "quote", "feed-interaction"],
            "denied": ["spam", "impersonation", "algo-tweak", "mass-reply", "sensitive-disclosure"],
            "default_posture": "DENY_ALL"
        },
        "temporal_scope": {
            "hard_expiry": (datetime.now().replace(year=datetime.now().year + 1)).isoformat()
        },
        "entropy_threshold": {
            "max_kl_divergence": 0.12,
            "flag_at": 0.08,
            "kill_at": 0.12
        },
        "iba_signature": "demo-signature"
    }

    protected_file = f"x-action-{action.replace(' ', '-').lower()[:30]}.iba-protected.md"

    content = f"# X Action Request: {action}\n\n[Post / reply / feed interaction would execute here under IBA governance]\n\n<!-- IBA PROTECTED X ACTION -->\n"

    if hollow_level:
        content += f"\n<!-- Hollowed ({hollow_level}): Sensitive content protected by IBA certificate -->\n"

    with open(protected_file, "w", encoding="utf-8") as f:
        f.write("<!-- IBA PROTECTED X PLATFORM ACTION -->\n")
        f.write(f"<!-- Intent Certificate: {json.dumps(cert, indent=2)} -->\n\n")
        f.write(content)

    print(f"✅ IBA-protected X action file created: {protected_file}")
    if hollow_level:
        print(f"   Hollowing level applied: {hollow_level}")
    else:
        print("   Full X action protected by IBA certificate")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Governed X posts, replies & feeds with IBA")
    parser.add_argument("action", help="Description of the X action (post/reply/feed)")
    parser.add_argument("--hollow", choices=["light", "medium", "heavy"], help="Apply safe hollowing")
    args = parser.parse_args()

    create_iba_x_guard(args.action, args.hollow)
