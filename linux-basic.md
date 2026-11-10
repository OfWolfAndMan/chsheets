---
title: Linux
summary: Linux command reference — services, networking, firewall, storage, logs
tags: [linux, systemd, networking, nftables]
tooling: [coreutils, iproute2, systemd, nftables, util-linux]
verified_on: 2026-11-10
verified_env: CachyOS, kernel 7.3.3-1-cachyos, systemd 262, iproute2 7.3.0, nft 1.1.7, util-linux 2.42.4
status: verified
---

# Linux

Everything below was run on the environment named in the front matter. Three idioms
from the 2018–2021 version of this sheet are gone and should not be reintroduced:

| Retired | Replacement |
|---|---|
| `ifconfig`, `route`, `netstat` | `ip addr`, `ip route`, `ss` |
| `iptables` as the interface | `nft` — modern `iptables` is a translator over `nf_tables`, not the native tool |
| `service foo start` | `systemctl start foo` |

## Orientation

```bash
uname -r                          # kernel release
cat /etc/os-release               # distribution identity
hostnamectl                       # hostname, chassis, kernel, virtualisation
uptime -p                         # human-readable uptime
timedatectl                       # clock, timezone, NTP sync state
```

## Files, disks, and space

```bash
lsblk -f                          # block devices with filesystem, label, UUID, mountpoint
df -h --output=source,size,used,avail,pcent,target
findmnt --real                    # mounted real filesystems, no pseudo-filesystems
du -xh --max-depth=1 /var | sort -h    # where the space went, one level deep
```

`-x` keeps `du` on one filesystem; without it, a stray mount makes the answer wrong.

```bash
find /var/log -type f -name '*.log' -mtime +7 -delete    # by age — dry-run first
find . -type f -newermt '2026-01-01' -not -path './.git/*'
```

## Permissions and identity

```bash
id                                # uid, gid, supplementary groups
getent passwd <user>              # one account, from the same source the system uses
stat -c '%A %U:%G %n' <file>      # symbolic mode, owner, group, name
chmod u=rw,g=r,o= <file>          # symbolic form beats octal for readability
chown -R <user>:<group> <dir>
umask                             # the bits new files will not get
```

ACLs, when ownership alone is not enough:

```bash
setfacl -m u:<user>:rx <dir>
getfacl <dir>
```

## Processes

```bash
ps -eo pid,ppid,user,comm,%cpu,%mem --sort=-%cpu | head
pgrep -af <pattern>               # match and print the full command line
pstree -p <pid>                   # ancestry
kill -TERM <pid>                  # polite; -KILL only if it will not die
kill -l                           # signal names
renice -n 10 -p <pid>             # lower the priority of a running process
```

`kill -9` skips cleanup and leaves locks and sockets behind. Try `-TERM` first.

## systemd services

```bash
systemctl status <unit> --no-pager
systemctl start|stop|restart|reload <unit>
systemctl enable --now <unit>     # enable at boot and start immediately
systemctl list-units --type=service --state=running --no-pager
systemctl list-unit-files --state=enabled
systemctl cat <unit>              # the unit plus any drop-ins, in load order
systemctl show -p ExecStart <unit>
```

Override without editing the vendor unit — drop-ins survive package upgrades:

```bash
systemctl edit <unit>             # writes /etc/systemd/system/<unit>.d/override.conf
systemctl daemon-reload           # required after hand-editing any unit file
systemd-analyze verify <unit>
```

## systemd timers

A timer plus a service replaces most cron jobs and gives you journal integration.

```ini
# /etc/systemd/system/report.timer
[Unit]
Description=Daily report

[Timer]
OnCalendar=*-*-* 09:17:00
Persistent=true

[Install]
WantedBy=timers.target
```

```ini
# /etc/systemd/system/report.service
[Unit]
Description=Daily report writer

[Service]
Type=oneshot
ExecStart=/usr/local/bin/report.sh
```

```bash
systemctl daemon-reload
systemctl enable --now report.timer
systemctl list-timers --all --no-pager
journalctl -u report.service -n 30 --no-pager
```

`Persistent=true` is what makes a laptop timer behave: if the scheduled moment was
missed because the machine was asleep, it fires at the next opportunity instead of
being silently skipped.

## Networking

```bash
ip -brief addr                    # interfaces and addresses, one line each
ip route                          # routing table
ip -s link show <iface>           # counters and errors per interface
ss -tulpn                         # listening sockets with owning processes (root)
ss -tan state established
resolvectl status                 # per-interface DNS configuration
nmcli device status               # NetworkManager's view, when NM is in use
resolvectl query example.com      # name resolution through the system resolver
```

## Firewall — nftables

Rules live in tables, tables hold chains, chains hold rules. The family decides which
address families the table applies to: `inet` covers IPv4 and IPv6 together.

```bash
sudo nft list ruleset             # everything, all families
sudo nft -s list ruleset          # the same, in re-loadable syntax
sudo nft list table inet filter
sudo nft --check -f /etc/nftables.conf   # syntax-check without applying
```

A host firewall:

```nft
table inet example {
  chain input {
    type filter hook input priority filter; policy drop;
    ct state established,related accept
    iif "lo" accept
    tcp dport 22 accept
    icmp type echo-request accept
  }
}
```

Source NAT for a router:

```nft
table ip nat {
  chain postrouting {
    type nat hook postrouting priority srcnat; policy accept;
    oifname "wlan0" masquerade
  }
}
```

Persistence is distribution-specific: on Arch-family systems `nftables.service` loads
`/etc/nftables.conf` at boot. Put the ruleset there, enable the service, and keep the
file in version control.

> If `iptables` is used at all, the kernel table is owned by `iptables-nft`. Hand
> written `nft` rules added to a table that `iptables` manages will be overwritten.
> One tool per table.

## Logs

```bash
journalctl -b                     # this boot
journalctl -b -1                  # previous boot — first stop for "it broke at reboot"
journalctl -u <unit> -f           # follow one unit
journalctl --since '1 hour ago' -p warning
journalctl -k                     # kernel messages only
journalctl --disk-usage && journalctl --vacuum-time=14d
```

## Archives and transfer

```bash
tar --zstd -cvf archive.tar.zst <dir>
tar --zstd -xvf archive.tar.zst
tar -cvf - <dir> | ssh <host> 'tar -xvf - -C /dest'   # copy without an intermediate file
rsync -avh --progress <src>/ <host>:<dest>/
rsync -avhn --delete <src>/ <dest>/    # -n is a dry run; always run it before --delete
```

## Packages (Arch family)

```bash
pacman -Syu <pkg>                 # sync the database, upgrade, install
pacman -Rs <pkg>                  # remove, including orphaned dependencies
pacman -Ql <pkg>                  # files owned by a package
pacman -Qo /usr/bin/<file>        # which package owns this path
pacman -Qdt                       # orphaned dependencies — prune candidates
```

## Text and data

```bash
grep -rn --include='*.conf' '<pattern>' /etc
rg -n '<pattern>' --glob '!*.log'   # ripgrep: respects .gitignore, much faster
sed -i.bak 's/old/new/g' <file>     # -i.bak keeps a copy; bare -i does not
awk -F: '$3 >= 1000 { print $1, $3 }' /etc/passwd
sort | uniq -c | sort -rn           # frequency count
jq -r '.items[] | .name' <file.json>
```

## Troubleshooting order

1. `systemctl --failed` — what actually broke.
2. `journalctl -b -p err --no-pager` — this boot's errors.
3. `systemd-analyze blame` and `critical-chain` — why boot is slow.
4. `systemctl cat <unit>` — which file defined the behaviour you are seeing.
5. `ip -brief addr` and `ss -tulpn` — service problem or network problem.
