#!/usr/bin/env python3
"""tag_fences.py — infer a language for unlabelled fenced blocks and tag them.

Untagged blocks cannot be linted, highlighted, or copied without guessing. This
classifies each one by content and rewrites the opening fence. The body of a
block is never modified.

Usage: tag_fences.py [--dry-run] [paths...]
"""
import os
import re
import sys

# Order matters: the first rule that matches wins, so narrow dialects come before
# the broad languages that would also match them (Java before Python, for instance,
# because `class Foo {` and `import java.util.*` both look like Python at a glance).
RULES = [
    ("dockerfile", [r"(?m)^\s*FROM\s+\S+", r"(?m)^\s*RUN\s+\S+", r"(?m)^\s*CMD\s+"]),
    ("groovy",     [r"(?m)^\s*pipeline\s*\{", r"(?m)^\s*stage\s*\(", r"(?m)^\s*agent\s+any"]),
    ("java",       [r"(?m)^\s*(public|private|protected)\s+(static\s+)?(class|void|int|String)",
                    r"(?m)^\s*import\s+java\.", r"(?m)System\.out\.print"]),
    ("sql",        [r"(?mi)^\s*(select|insert\s+into|create\s+(table|database|user)|alter\s+table|"
                    r"update\s+\w+\s+set|grant\s+|\\d)\b"]),
    ("ini",        [r"(?m)^\[(tox|testenv|testenv:\w+|pytest|tool:pytest|pytest-runner)[^\]]*\]"]),
    ("yang",       [r"(?m)^\s*(module|namespace|container|leaf|leaf-list|list|revision)\s+\w*\s*[\{;]"]),
    ("powershell", [r"(?im)^\s*(Get-\w+|Set-\w+|New-\w+|Invoke-\w+|Import-Module|Where-Object)\b"]),
    ("batch",      [r"(?im)^\s*(reg\s+(add|delete|query)|net\s+(user|localgroup|start)|sc\s+config)\b"]),
    ("python",     [r"(?m)^\s*(import\s+\w+|from\s+[\w.]+\s+import|def\s+\w+\s*\(|class\s+\w+\s*[\(:])",
                    r"(?m)^\s*(print\(|@\w+\s*$)"]),
    ("yaml",       [r"(?m)^\s*-\s+[\w\"']+\s*:\s*\S", r"(?m)^\s*- name:\s", r"(?m)^\s*tasks:\s*$"]),
    ("bash",       [r"(?m)^\s*\$\s+\S",
                    r"(?m)^\s*(sudo|apt|apt-get|yum|dnf|pacman|systemctl|service|ip|ifconfig|iptables|nft|"
                    r"docker|docker-compose|kubectl|git|ssh|scp|tar|zip|unzip|curl|wget|chmod|chown|grep|"
                    r"sed|awk|find|mount|useradd|usermod|crontab|virsh|vagrant|ansible|ansible-playbook|"
                    r"psql|rabbitmqctl|tmsh|echo|export|mkdir|rm|cp|mv|cat|less|tail|head|uniq|sort|"
                    r"netstat|ss|tee|xargs|dd|ls)\b"]),
]


def infer(body):
    for lang, pats in RULES:
        for p in pats:
            if re.search(p, body):
                return lang
    return "text"


def process(path, dry):
    """Walk fences with a proper state machine; return list of (line, lang)."""
    lines = open(path, encoding="utf-8").read().split("\n")
    out, changed = [], []
    i = 0
    while i < len(lines):
        m = re.match(r"^(\s*)```(.*)$", lines[i])
        if m:
            indent, info = m.group(1), m.group(2).strip()
            # find closing fence
            j = i + 1
            while j < len(lines) and not re.match(r"^\s*```\s*$", lines[j]):
                j += 1
            body = "\n".join(lines[i + 1:j])
            if info:
                out.append(lines[i])           # already tagged: leave alone
            else:
                lang = infer(body)
                out.append(f"{indent}```{lang}")
                changed.append((i + 1, lang))
            out.extend(lines[i + 1:j])
            if j < len(lines):
                out.append(lines[j])
            i = j + 1
            continue
        out.append(lines[i])
        i += 1
    if changed and not dry:
        open(path, "w", encoding="utf-8").write("\n".join(out))
    return changed


def main():
    dry = "--dry-run" in sys.argv
    paths = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not paths:
        paths = []
        for root, _, files in os.walk("."):
            if "/.git" in root:
                continue
            paths += [os.path.join(root, f) for f in files if f.endswith(".md")]
    total = 0
    for p in sorted(paths):
        ch = process(p, dry)
        if ch:
            total += len(ch)
            kinds = {}
            for _, l in ch:
                kinds[l] = kinds.get(l, 0) + 1
            print(f"{p}: {len(ch)} tagged  " + " ".join(f"{k}={v}" for k, v in sorted(kinds.items())))
    print(f"\n{total} fence(s) {'would be ' if dry else ''}tagged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
