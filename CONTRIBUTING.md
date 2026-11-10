# Contributing

Two rules govern this repository. Everything else here is style.

## 1. A command is current only if someone ran it

Documentation rots silently. A command that worked in 2021 is not a fact; it is a
rumour with a timestamp. So every sheet carries front matter declaring when its
content was last verified and against which version:

```yaml
---
title: Linux — core commands
tags: [linux, systemd, networking]
tooling: [coreutils, iproute2, nftables, systemd]
verified_on: 2026-11-15
verified_env: CachyOS 7.3.3, nft 1.1.7, systemd 256
status: verified        # verified | partial | stale | retired
---
```

- `status: verified` requires an actual run on the stated environment. If you have
  not executed it, write `partial` and say which parts you did run.
- Anything older than twelve months is downgraded to `stale` on sight. That is not
  a comment on its accuracy; it is a statement that nobody has checked lately.
- When a sheet is wrong, the fix is the correction **and** the run that proved it.

## 2. This repository is public, so SHIELD applies

Nothing committed here may expose real infrastructure or real people. That means:

| Do not commit                        | Write instead                                    |
|--------------------------------------|--------------------------------------------------|
| Real private IPs (`10.`, `172.16-31.`, `192.168.`) | `192.0.2.10`, `198.51.100.20`, `203.0.113.5` (RFC 5737 documentation ranges) |
| Real public IPs you own or administer | the documentation ranges above                  |
| Real hostnames, tailnet names, domain names | `host1.example.com`, `example.com`       |
| Personal or colleague email addresses | `devops@example.com`, `user@example.com`        |
| Local paths containing your username | `/var/lib/service/`, `/opt/app/`, `~/`           |
| Any credential of any kind           | `<token>`, `<password>`, or Vault path reference |

Credentials belong in a secret manager, never in a file that git remembers — and
redacting them later does not work, because the history keeps them forever.

A deny list of personal identifiers lives on the workstation, not in the repository —
`~/.config/cicero/shield-deny.txt`, one term per line, or the path in `$SHIELD_DENY_FILE`.
It is deliberately outside the tree: a list inside the repo would itself contain the
strings it exists to keep out. `shield_lint.py` loads it when present and treats any
match as CRITICAL.

Run the scrub before you push:

```bash
python3 scripts/shield_lint.py      # exit 1 blocks the commit
python3 scripts/fence_lint.py       # syntax-checks fenced blocks
```

## 3. Formatting

- One sheet per file, lowercase-hyphenated name, `.md`.
- Every fenced block gets a language tag (`bash`, `python`, `yaml`, `sql`,
  `groovy`, `text`). An untagged block cannot be linted and cannot be copied
  without guessing.
- Headings carry meaning; a 200-line paste with two headings is not a sheet.
- Prefer a runnable example to a prose description of one.

## 4. Scope

In scope: operating systems, networking, automation, build and delivery tooling,
databases, and the security posture around them — the things an infrastructure
engineer types at a terminal.

Out of scope: application-framework tutorials, cloud-provider marketing, and any
tool nobody here runs. A sheet for a tool you do not use is clutter that ages
into misinformation.
