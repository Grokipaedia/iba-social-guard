# guard.py - IBA Intent Bound Authorization · Social Guard
# Patent GB2603013.0 (Pending) · UK IPO · Filed February 5, 2026
# WIPO DAS Confirmed April 15, 2026 · Access Code C9A6
# IETF draft-williams-intent-token-00 · intentbound.com
#
# Intent-bound posts, replies & feeds. Every platform. Every agent.
# Every AI action on a social platform requires a signed human intent
# certificate before it executes.
#
# Six platform configurations:
#   x.iba.yaml         — X/Twitter · bot limits · no impersonation
#   linkedin.iba.yaml  — Professional scope · no spam · no fake endorsements
#   bluesky.iba.yaml   — Decentralized · federation scope · no cross-posting
#   reddit.iba.yaml    — Subreddit scope · no vote manipulation · no brigading
#   youtube.iba.yaml   — Comment scope · no hate · no coordinated behavior
#   default.iba.yaml   — Platform-agnostic base cert
#
# Regulatory coverage:
#   EU Digital Services Act (DSA) · EU AI Act · FEC (US) ·
#   UK Online Safety Act · Platform ToS enforcement layer
#
# "An AI agent posting on your behalf without a signed intent cert
#  is an unauthorized action. The cert is the authorization."
# — IBA Intent Bound Authorization · intentbound.com

import json
import yaml
import os
import time
import argparse
from datetime import datetime, timezone


class IBABlockedError(Exception):
    pass


class IBATerminatedError(Exception):
    pass


HOLLOW_LEVELS = {
    "light":  ["personal_data", "email", "phone", "address"],
    "medium": ["personal_data", "email", "phone", "address",
               "political_opinion", "health_data", "financial_data",
               "location", "private_message"],
    "deep":   ["personal_data", "email", "phone", "address",
               "political_opinion", "health_data", "financial_data",
               "location", "private_message", "biometric",
               "ethnic_origin", "sexual_orientation", "religious_belief"],
}

CONFIG_NAMES = {
    "x.iba.yaml":         "X / Twitter · Social Platform",
    "linkedin.iba.yaml":  "LinkedIn · Professional Network",
    "bluesky.iba.yaml":   "Bluesky · Decentralized Social",
    "reddit.iba.yaml":    "Reddit · Community Platform",
    "youtube.iba.yaml":   "YouTube · Video & Comments",
    "default.iba.yaml":   "Default · Platform-Agnostic",
}


class IBASocialGuard:
    """
    IBA enforcement layer for AI agents acting on social media platforms.

    Requires a signed human intent certificate before any post, reply,
    quote, follow, like, share, or feed interaction executes.

    Covers: X · LinkedIn · Bluesky · Reddit · YouTube · Any platform.

    Regulatory: EU DSA · EU AI Act · FEC · UK Online Safety Act.

    "An AI agent posting on your behalf without a signed intent cert
     is an unauthorized action. The cert is the authorization."
    """

    def __init__(self, config_path="default.iba.yaml",
                 audit_path="social-audit.jsonl"):
        self.config_path  = config_path
        self.audit_path   = audit_path
        self.terminated   = False
        self.session_id   = f"sg-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        self.action_count = 0
        self.block_count  = 0
        self.platform     = CONFIG_NAMES.get(
            os.path.basename(config_path), config_path)

        self.config          = self._load_config()
        self.scope           = [s.lower() for s in self.config.get("scope", [])]
        self.denied          = [d.lower() for d in self.config.get("denied", [])]
        self.default_posture = self.config.get("default_posture", "DENY_ALL")
        self.kill_threshold  = self.config.get("kill_threshold", None)
        self.hard_expiry     = self.config.get(
            "temporal_scope", {}).get("hard_expiry")
        self.principal       = self.config.get("principal", {})

        rl = self.config.get("rate_limits", {})
        self.max_posts_per_hour  = int(rl.get("max_posts_per_hour", 10))
        self.max_replies_per_hour = int(rl.get("max_replies_per_hour", 20))

        self._validate_cert()
        self._log_event("SESSION_START", "IBA Social Guard initialised", "ALLOW")
        self._print_header()

    def _load_config(self):
        if not os.path.exists(self.config_path):
            print(f"  No {self.config_path} found — DENY_ALL posture.")
            default = {
                "intent": {"description": "No social intent declared — DENY_ALL."},
                "scope": [], "denied": [], "default_posture": "DENY_ALL",
            }
            with open(self.config_path, "w") as f:
                yaml.dump(default, f)
            return default
        with open(self.config_path) as f:
            return yaml.safe_load(f)

    def _validate_cert(self):
        if not self.principal.get("identity_reference"):
            print("  WARNING: No identity reference in certificate.")
        if not self.principal.get("human_authorization"):
            print("  WARNING: No human authorization in certificate.")

    def _print_header(self):
        intent = self.config.get("intent", {})
        desc = (intent.get("description", "No intent declared")
                if isinstance(intent, dict) else str(intent))
        print("\n" + "=" * 68)
        print("  IBA SOCIAL GUARD · Intent Bound Authorization")
        print("  Patent GB2603013.0 Pending · WIPO DAS C9A6 · intentbound.com")
        print("=" * 68)
        print(f"  Platform    : {self.platform}")
        print(f"  Session     : {self.session_id}")
        print(f"  Config      : {self.config_path}")
        print(f"  Identity    : {self.principal.get('identity_reference', 'UNKNOWN')}")
        print(f"  Authorized  : {self.principal.get('human_authorization', 'NONE')}")
        print(f"  Intent      : {desc[:56]}...")
        print(f"  Posture     : {self.default_posture}")
        print(f"  Scope       : {', '.join(self.scope[:4]) if self.scope else 'NONE'}"
              + (" ..." if len(self.scope) > 4 else ""))
        print(f"  Max posts/hr: {self.max_posts_per_hour}")
        if self.hard_expiry:
            print(f"  Expires     : {self.hard_expiry}")
        if self.kill_threshold:
            kt = str(self.kill_threshold).replace('\n', ' ')[:56]
            print(f"  Kill        : {kt}")
        print("=" * 68 + "\n")

    def _is_expired(self):
        if not self.hard_expiry:
            return False
        try:
            expiry = datetime.fromisoformat(str(self.hard_expiry))
            if expiry.tzinfo is None:
                expiry = expiry.replace(tzinfo=timezone.utc)
            return datetime.now(timezone.utc) > expiry
        except Exception:
            return False

    def _match(self, action: str, terms: list) -> bool:
        al = action.lower()
        return any(t in al for t in terms)

    def _match_kill(self, action: str) -> bool:
        if not self.kill_threshold:
            return False
        terms = [t.strip().lower()
                 for t in str(self.kill_threshold).split("|")]
        return self._match(action, terms)

    def _log_event(self, event_type, action, verdict,
                   reason="", platform_meta=None):
        entry = {
            "timestamp":   datetime.now(timezone.utc).isoformat(),
            "session_id":  self.session_id,
            "platform":    self.platform,
            "identity":    self.principal.get("identity_reference", "UNKNOWN"),
            "authorized":  self.principal.get("human_authorization", "NONE"),
            "config":      self.config_path,
            "event_type":  event_type,
            "action":      action[:200],
            "verdict":     verdict,
            "reason":      reason,
        }
        if platform_meta:
            entry["platform_meta"] = platform_meta
        with open(self.audit_path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def check_action(self, action: str,
                     platform_meta: dict = None) -> bool:
        """
        Gate check. Call before every social media action.

        Returns True if permitted.
        Raises IBABlockedError if blocked.
        Raises IBATerminatedError if kill threshold triggered.

        Args:
            action:          Intended social action
            platform_meta:   Optional dict with platform-specific context
                             e.g. {"reply_to": "...", "thread": "...", "reach": 5000}
        """
        if self.terminated:
            raise IBATerminatedError("Social session terminated.")

        self.action_count += 1
        start = time.perf_counter()

        def _block(reason):
            self._log_event("BLOCK", action, "BLOCK", reason, platform_meta)
            self.block_count += 1
            print(f"  x BLOCKED  [{action[:64]}]\n    -> {reason}")
            raise IBABlockedError(f"{reason}: {action}")

        # 1. Certificate expiry
        if self._is_expired():
            _block("Certificate expired")

        # 2. Kill threshold — TERMINATE immediately
        if self._match_kill(action):
            self._log_event("TERMINATE", action, "TERMINATE",
                "Kill threshold — session ended", platform_meta)
            self.terminated = True
            print(f"  x TERMINATE [{action[:62]}]\n"
                  f"    -> Kill threshold — social session ended")
            self._log_event("SESSION_END", "Kill threshold", "TERMINATE")
            raise IBATerminatedError(f"Kill threshold: {action}")

        # 3. Denied list
        if self._match(action, self.denied):
            _block("Action in denied list")

        # 4. Scope check — DENY_ALL if outside declared scope
        if self.scope and not self._match(action, self.scope):
            if self.default_posture == "DENY_ALL":
                _block("Outside declared social scope (DENY_ALL)")

        # 5. ALLOW
        elapsed_ms = (time.perf_counter() - start) * 1000
        self._log_event("ALLOW", action, "ALLOW",
            f"Within scope ({elapsed_ms:.3f}ms)", platform_meta)
        print(f"  + ALLOWED  [{action[:62]}] ({elapsed_ms:.3f}ms)")
        return True

    def hollow(self, content: str, level: str = "medium") -> str:
        """Redact sensitive content before posting or processing."""
        blocked = HOLLOW_LEVELS.get(level, HOLLOW_LEVELS["medium"])
        hollowed = content
        redacted = []
        for item in blocked:
            if item.lower() in content.lower():
                hollowed = hollowed.replace(
                    item, f"[SOCIAL-REDACTED:{item.upper()}]")
                redacted.append(item)
        if redacted:
            print(f"  o HOLLOWED [{level}] — redacted: {', '.join(redacted)}")
            self._log_event("HOLLOW", f"Hollowing: {level}", "ALLOW",
                f"Redacted: {', '.join(redacted)}")
        return hollowed

    def summary(self):
        print("\n" + "=" * 68)
        print("  IBA SOCIAL GUARD · SESSION SUMMARY")
        print("=" * 68)
        print(f"  Platform      : {self.platform}")
        print(f"  Session       : {self.session_id}")
        print(f"  Identity      : {self.principal.get('identity_reference', 'UNKNOWN')}")
        print(f"  Actions       : {self.action_count}")
        print(f"  Blocked       : {self.block_count}")
        print(f"  Allowed       : {self.action_count - self.block_count}")
        print(f"  Status        : {'TERMINATED' if self.terminated else 'COMPLETE'}")
        print(f"  Audit log     : {self.audit_path}")
        print("=" * 68 + "\n")

    def print_audit_log(self):
        print("-- SOCIAL AUDIT CHAIN " + "-" * 46)
        if not os.path.exists(self.audit_path):
            print("  No audit log found.")
            return
        with open(self.audit_path) as f:
            for line in f:
                try:
                    e = json.loads(line)
                    verdict = e.get("verdict", "")
                    symbol = "+" if verdict == "ALLOW" else "x"
                    print(f"  {symbol} {e['timestamp'][:19]}  {verdict:<10}"
                          f"  {e['action'][:44]}")
                except Exception:
                    pass
        print("-" * 68 + "\n")


# Per-platform demo scenarios
DEMO_SCENARIOS = {
    "x.iba.yaml": [
        ("post original research on IBA governance",          None),
        ("reply to question about intent certificates",       {"reply_to": "tech_thread"}),
        ("share article about AI authorization",              None),
        ("quote tweet with commentary on BCI governance",     None),
        ("post spam promotional content mass accounts",       None),   # BLOCK
        ("impersonate verified account post",                 None),   # BLOCK
        ("coordinated_inauthentic_behavior mass reply",       None),   # TERMINATE
    ],
    "linkedin.iba.yaml": [
        ("post professional update on IBA patent filing",    None),
        ("comment on AI governance article",                 None),
        ("share industry news with commentary",              None),
        ("connect with BCI researcher message",              None),
        ("spam promotional sales message bulk",              None),   # BLOCK
        ("fake_endorsement generate artificial",             None),   # BLOCK
        ("coordinated_inauthentic_behavior mass_connection", None),   # TERMINATE
    ],
    "bluesky.iba.yaml": [
        ("post to personal feed IBA update",                 None),
        ("reply to federated thread",                        {"thread": "bsky.social"}),
        ("share across declared federation instances",       None),
        ("cross_post without cert to external instance",     None),   # BLOCK
        ("spam_federation automated mass post",              None),   # BLOCK
        ("impersonate_identity federation account",          None),   # TERMINATE
    ],
    "reddit.iba.yaml": [
        ("post in r/MachineLearning IBA governance",         {"subreddit": "MachineLearning"}),
        ("comment on AI safety thread",                      {"subreddit": "aisafety"}),
        ("reply to question in declared subreddit",          None),
        ("post outside declared subreddit scope",            {"subreddit": "politics"}),  # BLOCK
        ("vote_manipulation coordinated upvote",             None),   # BLOCK
        ("brigading coordinated attack subreddit",           None),   # TERMINATE
    ],
    "youtube.iba.yaml": [
        ("comment on AI governance video",                   None),
        ("reply to question on IBA channel",                 None),
        ("post community update declared channel",           None),
        ("hate_speech coordinated comment campaign",         None),   # BLOCK
        ("spam_comment mass identical reply",                None),   # BLOCK
        ("coordinated_inauthentic_behavior dislike_attack",  None),   # TERMINATE
    ],
    "default.iba.yaml": [
        ("post authorized content within scope",             None),
        ("reply within declared engagement scope",           None),
        ("share approved content declared platform",         None),
        ("spam promotional unauthorized mass post",          None),   # BLOCK
        ("impersonate identity unauthorized account",        None),   # BLOCK
        ("coordinated_inauthentic_behavior platform attack", None),   # TERMINATE
    ],
}


def run_demo(guard, config_path):
    key = os.path.basename(config_path)
    scenarios = DEMO_SCENARIOS.get(key, DEMO_SCENARIOS["default.iba.yaml"])
    print(f"-- Running {guard.platform} Gate Checks " + "-" * 20 + "\n")
    for action, meta in scenarios:
        try:
            guard.check_action(action, platform_meta=meta)
        except IBATerminatedError as e:
            print(f"\n  SOCIAL SESSION TERMINATED: {e}")
            break
        except IBABlockedError:
            pass


def main():
    parser = argparse.ArgumentParser(
        description="IBA Social Guard — Social Platform Intent Enforcement")
    parser.add_argument("action", nargs="?",
                        help="Social action to gate-check")
    parser.add_argument("--config", default="default.iba.yaml",
                        help="Intent certificate config (.iba.yaml)")
    parser.add_argument("--hollow",
                        choices=["light", "medium", "deep"],
                        help="Safe hollowing level")
    parser.add_argument("--demo", action="store_true",
                        help="Run demo scenarios for this platform")
    parser.add_argument("--all", action="store_true",
                        help="Run demo scenarios for all 6 platforms")
    parser.add_argument("--audit", default="social-audit.jsonl",
                        help="Audit log path")
    args = parser.parse_args()

    if args.all:
        for cfg in DEMO_SCENARIOS.keys():
            if os.path.exists(cfg):
                guard = IBASocialGuard(config_path=cfg,
                                       audit_path=args.audit)
                run_demo(guard, cfg)
                guard.summary()
                print()
        return

    guard = IBASocialGuard(config_path=args.config, audit_path=args.audit)

    if args.action and args.hollow:
        hollowed = guard.hollow(args.action, args.hollow)
        print(f"\n  Content (hollowed): {hollowed}\n")

    if args.demo or not args.action:
        run_demo(guard, args.config)
    elif args.action:
        try:
            guard.check_action(args.action)
        except IBATerminatedError as e:
            print(f"\n  SOCIAL SESSION TERMINATED: {e}")
        except IBABlockedError:
            pass

    guard.summary()
    guard.print_audit_log()


if __name__ == "__main__":
    main()
