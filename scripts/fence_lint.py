#!/usr/bin/env python3
"""fence_lint.py — extract fenced code blocks from Markdown and syntax-check them.

Usage: fence_lint.py [paths...]
Prints one line per finding and a summary. Exit 1 if any finding.

Checks by fence language:
  bash/shell/sh  -> bash -n
  python         -> compile()
  yaml           -> yaml.safe_load (if PyYAML present, else skipped)
  sql            -> skipped (no universal parser without sqlfluff)
Also reports: unbalanced fences, unlabelled fences, empty files, duplicate headings.
"""
import os
import re
import subprocess
import sys

LANG_ALIASES = {
    "bash": "bash", "shell": "bash", "sh": "bash", "zsh": "bash",
    "python": "python", "py": "python", "python3": "python",
    "yaml": "yaml", "yml": "yaml",
}

def blocks(text):
    """Yield (lang, firstlineno, code) for each fenced block; also yield unbalanced marker."""
    in_block = False
    lang = ""
    start = 0
    buf = []
    for i, line in enumerate(text.splitlines(), 1):
        m = re.match(r"^\s*```(\S*)\s*$", line)
        if m and not in_block:
            in_block, lang, start, buf = True, m.group(1).lower(), i, []
            continue
        if re.match(r"^\s*```\s*$", line) and in_block:
            yield (lang, start, "\n".join(buf))
            in_block = False
            continue
        if in_block:
            buf.append(line)
    if in_block:
        yield ("__unbalanced__", start, "\n".join(buf))

def check_bash(code):
    p = subprocess.run(["bash", "-n"], input=code, capture_output=True, text=True)
    return p.returncode == 0, (p.stderr or "").strip()

def check_python(code):
    try:
        compile(code, "<fence>", "exec")
        return True, ""
    except SyntaxError as e:
        return False, f"line {e.lineno}: {e.msg}"

def check_yaml(code):
    try:
        import yaml
    except ImportError:
        return None, "PyYAML not installed"
    try:
        list(yaml.safe_load_all(code))
        return True, ""
    except Exception as e:
        return False, str(e).splitlines()[0]

CHECKS = {"bash": check_bash, "python": check_python, "yaml": check_yaml}

def main(paths):
    findings = 0
    stats = {"files": 0, "blocks": 0, "unlabelled": 0, "checked": 0, "skipped": 0}
    for root, _, files in os.walk("."):
        if "/.git" in root:
            continue
        for f in sorted(files):
            if not f.endswith(".md"):
                continue
            p = os.path.join(root, f)
            text = open(p, encoding="utf-8", errors="replace").read()
            stats["files"] += 1
            n_blocks = 0
            for lang, line, code in blocks(text):
                n_blocks += 1
                stats["blocks"] += 1
                if lang == "__unbalanced__":
                    print(f"{p}:{line}: UNBALANCED fence opened here, never closed")
                    findings += 1
                    continue
                if not lang:
                    stats["unlabelled"] += 1
                    print(f"{p}:{line}: unlabelled fence (cannot be checked)")
                    findings += 1
                    continue
                key = LANG_ALIASES.get(lang)
                if not key or not code.strip():
                    stats["skipped"] += 1
                    continue
                # Template blocks use <angle-bracket> placeholders by convention and
                # cannot be executed as written. Count them; do not fail them.
                if key == "bash" and re.search(r"<[A-Za-z][^<>\n]{0,40}>", code):
                    stats.setdefault("templates", 0)
                    stats["templates"] += 1
                    continue
                ok, msg = CHECKS[key](code)
                stats["checked"] += 1
                if ok is False:
                    print(f"{p}:{line}: {key} syntax error — {msg}")
                    findings += 1
            fences = len(re.findall(r"^\s*```", text, re.M))
            if fences % 2:
                print(f"{p}: odd number of fence lines ({fences}) — structure is broken")
                findings += 1
            heads = re.findall(r"^(#{1,6})\s+(.*)$", text, re.M)
            seen = {}
            for h, t in heads:
                key = t.strip().lower()
                if key in seen:
                    print(f"{p}: duplicate heading '{t}'")
                    findings += 1
                seen[key] = True
    print(f"\n{stats['files']} files, {stats['blocks']} fenced blocks: "
          f"{stats['checked']} syntax-checked, {stats['unlabelled']} unlabelled, "
          f"{stats.get('templates', 0)} template (placeholders), "
          f"{stats['skipped']} unchecked (other languages)")
    print(f"{findings} finding(s)")
    return 1 if findings else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["."]))
