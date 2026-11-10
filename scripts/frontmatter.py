#!/usr/bin/env python3
"""frontmatter.py — ensure every sheet carries machine-readable metadata.

Front matter is the difference between a document and a claim: it records what the
sheet covers, which tools it uses, when it was last executed, and against which
versions. The index is generated from it, so metadata cannot drift from the files.

Usage:
  frontmatter.py            # add missing front matter
  frontmatter.py --check    # report sheets without front matter (exit 1)
"""
import os
import re
import sys

SHEETS = {
    "ansible-network.md": dict(
        title="Ansible — network devices",
        tags=["ansible", "network", "automation"],
        tooling=["ansible-core", "ansible.netcommon", "ansible collections"]),
    "cumulus-vx.md": dict(
        title="Cumulus VX / NVIDIA Cumulus Linux",
        tags=["linux", "network", "vendor"],
        tooling=["cumulus vx", "cl-commands"]),
    "docker-basic.md": dict(
        title="Docker",
        tags=["containers", "docker", "compose"],
        tooling=["docker", "docker compose"]),
    "f5-bigip-ltm.md": dict(
        title="F5 BIG-IP LTM",
        tags=["network", "vendor", "load-balancing"],
        tooling=["tmsh"]),
    "git-basic.md": dict(
        title="git",
        tags=["vcs", "git"],
        tooling=["git"]),
    "java-basic.md": dict(
        title="Java",
        tags=["language", "java"],
        tooling=["openjdk", "javac"]),
    "linux-basic.md": dict(
        title="Linux",
        tags=["linux", "systemd", "network"],
        tooling=["coreutils", "iproute2", "systemd", "nftables"]),
    "jenkins.md": dict(
        title="Jenkins",
        tags=["ci", "jenkins", "groovy"],
        tooling=["jenkins", "java", "docker"]),
    "opensearch.md": dict(
        title="OpenSearch",
        tags=["search", "logs", "observability", "opensearch"],
        tooling=["opensearch", "opensearch-dashboards", "logstash", "curl"]),
    "windows.md": dict(
        title="Windows",
        tags=["windows", "security", "network"],
        tooling=["powershell", "reg", "netsh", "sconfig"]),
    "pandas-examples.md": dict(
        title="pandas",
        tags=["python", "data", "pandas"],
        tooling=["python", "pandas"]),
    "postgresql.md": dict(
        title="PostgreSQL",
        tags=["database", "sql", "postgresql"],
        tooling=["postgresql", "psql"]),
    "python-basic.md": dict(
        title="Python",
        tags=["language", "python"],
        tooling=["python", "uv", "pytest"]),
    "python-regex.md": dict(
        title="Python — regular expressions",
        tags=["python", "regex"],
        tooling=["python", "re"]),
    "rabbitmq.md": dict(
        title="RabbitMQ",
        tags=["messaging", "rabbitmq"],
        tooling=["rabbitmq", "rabbitmqctl"]),
    "redteam-shell.md": dict(
        title="Offensive shell",
        tags=["security", "shell"],
        tooling=["curl", "wget", "ettercap"]),
    "yang-models-basic.md": dict(
        title="YANG data models",
        tags=["network", "yang", "nso"],
        tooling=["yang", "pyang", "cisco nso"]),
}

TEMPLATE = """---
title: {title}
tags: [{tags}]
tooling: [{tooling}]
verified_on: null
verified_env: null
status: unverified
---

"""


def has_frontmatter(text):
    return text.startswith("---\n")


def build(fname, meta):
    return TEMPLATE.format(
        title=meta["title"],
        tags=", ".join(meta["tags"]),
        tooling=", ".join(meta["tooling"]),
    )


def main():
    check = "--check" in sys.argv
    missing = []
    for fname, meta in SHEETS.items():
        if not os.path.exists(fname):
            print(f"missing file: {fname}")
            continue
        text = open(fname, encoding="utf-8").read()
        if has_frontmatter(text):
            continue
        missing.append(fname)
        if not check:
            body = text.lstrip("\n")
            # promote a leading H1 if present, otherwise insert a title heading
            if not re.match(r"^# ", body):
                body = f"# {meta['title']}\n\n" + body
            open(fname, "w", encoding="utf-8").write(build(fname, meta) + body)
    if check:
        for m in missing:
            print(f"no front matter: {m}")
        print(f"{len(missing)} sheet(s) missing front matter")
        return 1 if missing else 0
    print(f"{len(missing)} sheet(s) given front matter")
    return 0


if __name__ == "__main__":
    sys.exit(main())
