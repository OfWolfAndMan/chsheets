#!/usr/bin/env python3
"""link_lint.py — verify that relative links in Markdown resolve to real files.

External URLs are not fetched: a network check in CI is slow and flaky, and a dead
external link is a footnote while a dead internal link makes the index lie.

Usage: link_lint.py [paths...]
Exit 1 if any relative link does not resolve.
"""
import os
import re
import sys

LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
SKIP_PREFIX = ("http://", "https://", "mailto:", "tel:", "#")


def check(path):
    bad = []
    base = os.path.dirname(path)
    text = open(path, encoding="utf-8", errors="replace").read()
    # ignore fenced code blocks
    lines, in_f = text.split("\n"), False
    for n, line in enumerate(lines, 1):
        if re.match(r"^\s*```", line):
            in_f = not in_f
            continue
        if in_f:
            continue
        for m in LINK.finditer(line):
            target = m.group(1)
            if target.startswith(SKIP_PREFIX):
                continue
            target = target.split("#", 1)[0]
            if not target:
                continue
            resolved = os.path.normpath(os.path.join(base, target))
            if not os.path.exists(resolved):
                bad.append((n, target))
    return bad


def main():
    paths = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not paths:
        paths = []
        for root, _, files in os.walk("."):
            if "/.git" in root:
                continue
            paths += [os.path.join(root, f) for f in files if f.endswith(".md")]
    total = 0
    for p in sorted(paths):
        for line, target in check(p):
            print(f"{p}:{line}: broken relative link -> {target}")
            total += 1
    print(f"{total} broken relative link(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
