#!/usr/bin/env python3
"""index.py — regenerate the sheet index in README.md from front matter.

The index is derived, never hand-maintained: a table that is written by a script
cannot drift from the files it describes. Markers delimit the region.

Usage: index.py [--check]
"""
import os
import re
import sys

BEGIN = "<!-- BEGIN INDEX -->"
END = "<!-- END INDEX -->"


def parse_frontmatter(path):
    text = open(path, encoding="utf-8").read()
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    block = text[4:end]
    data = {}
    for line in block.split("\n"):
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.strip()
        if v.startswith("[") and v.endswith("]"):
            data[k] = [x.strip() for x in v[1:-1].split(",") if x.strip()]
        else:
            data[k] = None if v in ("null", "") else v.strip('"')
    data["_path"] = path
    return data


def build_table():
    rows = []
    for f in sorted(os.listdir(".")):
        if not f.endswith(".md") or f in ("README.md", "CONTRIBUTING.md"):
            continue
        d = parse_frontmatter(f)
        if not d:
            continue
        status = d.get("status") or "unverified"
        badge = {"verified": "verified", "partial": "partial",
                 "stale": "stale", "retired": "retired"}.get(status, "unverified")
        rows.append(f"| [{f}]({f}) | {d.get('summary') or d.get('title') or f} | {badge} |")
    nb = "| [jupyter_notebooks/](jupyter_notebooks/) | Seven notebooks: pandas, regex, lists, dicts, optimisations | unverified |"
    rows.append(nb)
    head = ["| Sheet | Covers | Status |", "|---|---|---|"]
    return "\n".join(head + rows)


def main():
    check = "--check" in sys.argv
    text = open("README.md", encoding="utf-8").read()
    table = build_table()
    new = re.sub(re.escape(BEGIN) + r".*?" + re.escape(END),
                 BEGIN + "\n" + table + "\n" + END, text, flags=re.S)
    if check:
        if new != text:
            print("README index is stale — run scripts/index.py")
            return 1
        print("README index up to date")
        return 0
    open("README.md", "w", encoding="utf-8").write(new)
    print(f"index regenerated ({table.count(chr(10)) - 1} rows)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
