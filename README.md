# chsheets

A working reference for infrastructure work: operating systems, networking,
automation, delivery tooling, databases, and the security posture around them.
Short, command-first, and — since 2026 — actually checked.

## Status

| Field | Value |
| --- | --- |
| Content last verified | 2026-11-10 — 11 verified by execution, 3 partial, 6 unverified |
| Sheets | 20 markdown, 7 notebooks |
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
| [ansible-network.md](ansible-network.md) | Ansible for network devices — inventory, FQCN modules, cli_command, config diff | partial |
| [cumulus-vx.md](cumulus-vx.md) | Cumulus VX / NVIDIA Cumulus Linux lab commands | unverified |
| [docker-basic.md](docker-basic.md) | Docker and Compose — images, containers, multi-stage builds, healthchecks | partial |
| [f5-bigip-ltm.md](f5-bigip-ltm.md) | F5 BIG-IP LTM — `tmsh` essentials | unverified |
| [git-basic.md](git-basic.md) | git — everyday commands, the undo ladder, rebase, worktrees | verified |
| [github-actions.md](github-actions.md) | GitHub Actions — workflows, matrix builds, caching, secrets, permissions | verified |
| [java-basic.md](java-basic.md) | Java — language core, records, streams, modern switch, virtual threads | verified |
| [jenkins.md](jenkins.md) | Jenkins — install, agents, declarative pipelines, libraries, credentials | unverified |
| [linux-basic.md](linux-basic.md) | Linux command reference — services, networking, firewall, storage, logs | verified |
| [opensearch.md](opensearch.md) | OpenSearch — install, cluster health, indices, ingest, security | partial |
| [pandas-examples.md](pandas-examples.md) | pandas 2.x — loading, selecting, grouping, joining, time series | verified |
| [postgresql.md](postgresql.md) | PostgreSQL 18 — roles, psql, schema, indexes, backup, plus a SQL refresher | verified |
| [python-basic.md](python-basic.md) | Python — environments, language core, typing, pathlib, async, testing | verified |
| [python-regex.md](python-regex.md) | Regex in Python, including network-output parsing | unverified |
| [rabbitmq.md](rabbitmq.md) | RabbitMQ — vhosts, users, queues, exchanges, bindings, management API | verified |
| [redteam-shell.md](redteam-shell.md) | Offensive shell one-liners | unverified |
| [tailscale.md](tailscale.md) | Tailscale — status, file transfer, serve, ssh, ACLs, exit nodes | verified |
| [terraform.md](terraform.md) | Terraform — init/plan/apply, state, modules, variables, and the OpenTofu fork | verified |
| [windows.md](windows.md) | Windows client and server — hardening baseline, registry, networking, updates | unverified |
| [yang-models-basic.md](yang-models-basic.md) | YANG — module structure, pyang validation, and the two lab modules from the NSO course | verified |
| [jupyter_notebooks/](jupyter_notebooks/) | Seven notebooks: pandas, regex, lists, dicts, optimisations | unverified |
<!-- END INDEX -->

## Removed

Removed in the 2026 modernisation pass, with the reason. Git history keeps them.

| File | Reason |
|---|---|
| `artifactory` | Empty since 2021-01-19 — a blank page presented as a sheet |
| `gradle.md` | Five lines containing a Java "Hello World"; never contained Gradle content |
| `salt-basic.md` | Salt dropped from the toolkit; Ansible is the automation standard here |
| `vagrant-basic.md` | HashiCorp is retiring the hosted Vagrant service; local VMs are covered by `systemd-nspawn` and `libvirt` |
| `elk-stack.md` | Replaced by `opensearch.md` — it installed Elasticsearch 7.6.0 from 2020 |
| `sql-basic.md` | Merged into `postgresql.md` as a refresher section; eighteen lines was not a sheet |
| `windows-advanced.md`, `windows-hardening.md` | Merged into `windows.md` |
| `jenkins-basic.md`, `jenkins-pipeline-execution.md`, `jenkinsfile-example.md` | Consolidated into `jenkins.md`; 740 lines of overlapping notes with the code unfenced |

## Roadmap

1. **Hygiene and verification harness** — links, licences, front matter, CI,
   secret scanning. *(done 2026-11-10)*
2. **Rewrite by wrongness** — ELK, Docker, Linux, Ansible networking, Python, Java.
   *(done 2026-11-10; ELK became OpenSearch)*
3. **New sheets for the current stack** — systemd and nftables (inside `linux-basic`),
   Tailscale, Terraform, GitHub Actions. *(done 2026-11-10)*
4. **Retire the rest** — four sheets were removed rather than left to mislead;
   five carry `unverified` status with the reason stated. *(ongoing)*

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
