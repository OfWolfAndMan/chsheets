# chsheets

A working reference for infrastructure work: operating systems, networking,
automation, delivery tooling, databases, and the security posture around them.
Short, command-first, and — since 2026 — actually checked.

## Status

| Field | Value |
| --- | --- |
| Content last verified | **never** (audit 2026-11-10) |
| Sheets | 21 markdown, 7 notebooks |
| Dormant | 2021-01-21 → 2026-11-10 |
| CI | fence + secret lint on push |
| Licence | MIT (code) / CC BY-SA 4.0 (prose) |

Every sheet below is currently `status: unverified`. They were written between 2018
and 2021 and have not been re-run since. The verification project is in progress;
sheets flip to `verified` only when a command has been executed against a stated
version on a stated date.

## Sheets

The index below is generated from each sheet's front matter by `scripts/index.py`.
Status is `unverified` until someone runs the commands against a stated version.

<!-- BEGIN INDEX -->
| Sheet | Covers | Status |
|---|---|---|
| [ansible-network.md](ansible-network.md) | Ansible for network devices: show commands, config push, output capture | unverified |
| [cumulus-vx.md](cumulus-vx.md) | Cumulus VX / NVIDIA Cumulus Linux lab commands | unverified |
| [docker-basic.md](docker-basic.md) | Docker and Compose basics | unverified |
| [elk-stack.md](elk-stack.md) | OpenSearch install, node configuration, and the Elastic deltas | unverified |
| [f5-bigip-ltm.md](f5-bigip-ltm.md) | F5 BIG-IP LTM — `tmsh` essentials | unverified |
| [git-basic.md](git-basic.md) | git command reference | unverified |
| [java-basic.md](java-basic.md) | Java language basics | unverified |
| [jenkins-basic.md](jenkins-basic.md) | Jenkins install and administration | unverified |
| [jenkins-pipeline-execution.md](jenkins-pipeline-execution.md) | Pipeline execution notes — triggers, stages, post blocks | unverified |
| [jenkinsfile-example.md](jenkinsfile-example.md) | A worked Jenkinsfile | unverified |
| [linux-basic.md](linux-basic.md) | Linux command reference | unverified |
| [pandas-examples.md](pandas-examples.md) | pandas recipes | unverified |
| [postgresql.md](postgresql.md) | PostgreSQL administration and `psql` | unverified |
| [python-basic.md](python-basic.md) | Python basics, environments, tests | unverified |
| [python-regex.md](python-regex.md) | Regex in Python, including network-output parsing | unverified |
| [rabbitmq.md](rabbitmq.md) | RabbitMQ administration | unverified |
| [redteam-shell.md](redteam-shell.md) | Offensive shell one-liners | unverified |
| [sql-basic.md](sql-basic.md) | SQL refresher | unverified |
| [windows-advanced.md](windows-advanced.md) | Windows registry and routing examples | unverified |
| [windows-hardening.md](windows-hardening.md) | Windows client hardening checklist | unverified |
| [yang-models-basic.md](yang-models-basic.md) | YANG data models — Cisco NSO lab | unverified |
| [jupyter_notebooks/](jupyter_notebooks/) | Seven notebooks: pandas, regex, lists, dicts, optimisations | unverified |
<!-- END INDEX -->

## Removed

Removed in the 2026 modernisation pass, with the reason. Git history keeps them.

| File | Reason |
| --- | --- |
| `artifactory` | Empty since 2021-01-19 — a blank page presented as a sheet |
| `gradle.md` | Five lines containing a Java "Hello World"; never contained Gradle content |
| `salt-basic.md` | Salt dropped from the toolkit; Ansible is the automation standard here |
| `vagrant-basic.md` | HashiCorp is retiring the hosted Vagrant service and box hosting; local VMs are covered by `systemd-nspawn` and `libvirt` |

## Roadmap

1. **Hygiene and verification harness** — links, licences, front matter, CI,
   secret scanning. *(in progress)*
2. **Rewrite by wrongness** — the sheets whose content has gone stale: ELK, Docker,
   Linux, Ansible networking, Python, Java.
3. **New sheets for the current stack** — systemd, nftables, Ansible (rewritten),
   Terraform, PostgreSQL administration, CI.
4. **Retire the rest** — anything that cannot be made true again is deleted rather
   than left to mislead.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md). Two rules matter more than the rest: a
sheet is current only if someone ran it, and nothing committed here may expose real
infrastructure, real hostnames, or real people.

Before pushing:

```bash
python3 scripts/shield_lint.py    # credentials, private addresses, personal data
python3 scripts/fence_lint.py     # syntax-checks every fenced code block
```

## Licence

Code under MIT; prose under CC BY-SA 4.0. See [LICENSE](LICENSE).
