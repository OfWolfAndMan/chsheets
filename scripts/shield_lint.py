#!/usr/bin/env python3
"""shield_lint.py — pre-publication scrub for a public cheatsheet repository.

Directive SHIELD applies: nothing in a public repo may expose credentials, private
infrastructure, or identifying data. This scans working-tree files for the classes of
leak that a human proofread misses, and prints a location for each hit.

Usage:  shield_lint.py [--staged] [path ...]
Exit:   1 if any finding, 0 if clean.

Severity:
  CRITICAL  secrets and key material — must never be committed
  HIGH      private addressing, real hostnames, personal identifiers
  MEDIUM    user paths, emails, MAC addresses
  INFO      documentation-range addresses that are fine but worth seeing
"""
import argparse
import ipaddress
import os
import re
import subprocess
import sys

# --- patterns -----------------------------------------------------------------

SECRET_PATTERNS = [
    ("aws-access-key",     r"\b(AKIA|ASIA)[0-9A-Z]{16}\b"),
    ("github-token",       r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"),
    ("gitlab-token",       r"\bglpat-[A-Za-z0-9_-]{20,}\b"),
    ("slack-token",        r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"),
    ("openai-style-key",   r"\bsk-[A-Za-z0-9]{32,}\b"),
    ("private-key-block",  r"-----BEGIN (RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----"),
    ("vault-token",        r"\b(hvs\.[A-Za-z0-9_-]{20,}|s\.[A-Za-z0-9]{24})\b"),
    ("assigned-secret",    r"(?i)\b(password|passwd|secret|api[_-]?key|token)\s*[:=]\s*"
                           r"(?!['\"]?(x{3,}|\*{3,}|<[^>]+>|\.\.\.|changeme|example|redacted|REPLACE)[\"']?)"
                           r"[\"']?[A-Za-z0-9!@#$%^&*_+=-]{8,}"),
]

IDENTITY_PATTERNS = [
    ("home-path",   r"/(?:home|Users)/([a-z][a-z0-9_-]{2,})/"),
    ("email",       r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    ("mac-address", r"\b(?:[0-9A-Fa-f]{2}:){5}[0-9A-Fa-f]{2}\b"),
    ("phone-us",    r"\b(?:\+1[-. ]?)?\(?\d{3}\)?[-. ]\d{3}[-. ]\d{4}\b"),
]

DOC_NETS = [
    ipaddress.ip_network("192.0.2.0/24"),     # TEST-NET-1
    ipaddress.ip_network("198.51.100.0/24"),  # TEST-NET-2
    ipaddress.ip_network("203.0.113.0/24"),   # TEST-NET-3
    ipaddress.ip_network("2001:db8::/32"),    # documentation v6
]
IP_RE = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")

TEXT_EXT = {".md", ".org", ".txt", ".sh", ".py", ".yml", ".yaml", ".conf", ".cfg", ".json"}


def classify_ip(text):
    try:
        ip = ipaddress.ip_address(text)
    except ValueError:
        return None
    for n in DOC_NETS:
        if ip in n:
            return "INFO", "documentation range (fine)"
    if ip.is_unspecified or str(ip) in ("8.8.8.8", "1.1.1.1", "9.9.9.9"):
        return "INFO", "well-known/any-address (fine in examples)"
    if ip.is_loopback:                                   # 127.0.0.0/8 is fine in examples
        return "INFO", "loopback (fine)"
    if ip in ipaddress.ip_network("100.64.0.0/10"):   # noqa: shield  (pattern definition)
        return "HIGH", "CGNAT / tailnet address"
    if ip.is_private:
        return "HIGH", "RFC1918 private address"
    if ip.is_loopback or ip.is_link_local or ip.is_unspecified:
        return "INFO", "loopback/link-local (usually fine)"
    if ip.is_multicast or ip.is_reserved:
        return "INFO", "reserved"
    return "MEDIUM", "public address (verify it is not yours)"


def scan_file(path):
    findings = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for n, line in enumerate(f, 1):
                if len(line) > 4000:
                    line = line[:4000]
                if "noqa: shield" in line:
                    continue
                for name, pat in SECRET_PATTERNS:
                    for m in re.finditer(pat, line):
                        findings.append(("CRITICAL", name, path, n, m.group(0)[:60]))
                for name, pat in IDENTITY_PATTERNS:
                    for m in re.finditer(pat, line):
                        tok = m.group(0)
                        if name == "email" and (tok.endswith(("example.com", "example.org", "example.net"))
                                                or tok in ("git@github.com", "user@example.com")):
                            continue
                        sev = "HIGH" if name == "home-path" and m.group(1) not in ("user", "username") else "MEDIUM"
                        findings.append((sev, name, path, n, m.group(0)[:60]))
                for m in IP_RE.finditer(line):
                    c = classify_ip(m.group(0))
                    if c and c[0] in ("HIGH", "MEDIUM"):
                        findings.append((c[0], "ip-address", path, n, f"{m.group(0)} — {c[1]}"))
    except Exception as e:  # unreadable/binary
        findings.append(("INFO", "unreadable", path, 0, str(e)[:60]))
    return findings


def tracked_files(staged=False):
    if staged:
        out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                             capture_output=True, text=True).stdout
    else:
        out = subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout
    return [p for p in out.split() if os.path.splitext(p)[1].lower() in TEXT_EXT or "." not in os.path.basename(p)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--staged", action="store_true", help="scan only staged files")
    ap.add_argument("paths", nargs="*")
    a = ap.parse_args()

    files = a.paths or tracked_files(a.staged)
    all_findings = []
    for p in files:
        if os.path.isfile(p):
            all_findings.extend(scan_file(p))

    order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "INFO": 3}
    all_findings.sort(key=lambda f: (order[f[0]], f[2], f[3]))
    counts = {}
    for sev, kind, path, ln, sample in all_findings:
        counts[sev] = counts.get(sev, 0) + 1
        if sev != "INFO":
            print(f"{sev:8} {kind:16} {path}:{ln}: {sample}")

    print("\n" + "  ".join(f"{k}={v}" for k, v in sorted(counts.items(), key=lambda kv: order[kv[0]]))
          or "clean")
    blocking = counts.get("CRITICAL", 0) + counts.get("HIGH", 0)
    if blocking:
        print(f"BLOCKED: {blocking} finding(s) at CRITICAL/HIGH — do not publish.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
