---
title: Tailscale
summary: Tailscale — status, file transfer, serve, ssh, ACLs, exit nodes
tags: [network, vpn, tailscale, wireguard]
tooling: [tailscale, tailscaled]
verified_on: 2026-11-10
verified_env: tailscale 1.104.5 on Linux; read-only subcommands executed, writes not applied
status: verified
---

# Tailscale

Tailscale is a WireGuard mesh with a coordination server: every node gets a stable
100.x address, NAT traversal is automatic, and access is governed by an ACL policy
rather than by firewall rules you hand-maintain. Everything below was run against
tailscale 1.104.5; the read-only commands were executed, the state-changing ones are
documented but were not applied to a live tailnet.

Node names, addresses and the tailnet name in any example here are placeholders. Never
paste real ones into a public repository or a screenshot.

## Enrol a node

```bash
sudo tailscale up                                  # interactive login via browser
sudo tailscale up --authkey "$TS_AUTHKEY"          # unattended, key from a secret store
sudo tailscale up --ssh --accept-routes            # enable Tailscale SSH, accept subnet routes
sudo tailscale up --advertise-routes=192.0.2.0/24  # offer a subnet route to the tailnet
sudo tailscale up --advertise-exit-node            # offer this node as an exit node
```

`--authkey` on a command line lands in shell history and in `ps`. The client accepts
`--authkey=file:/run/secrets/ts-authkey`, which reads the key from a file — the option
to use with systemd credentials or a container secret. Make the key ephemeral and
pre-authorised where the tailnet policy allows.

## State and reachability

```bash
tailscale status                    # peers, addresses, connection type
tailscale status --json | jq '.Peer | to_entries[] | {name: .value.HostName, online: .value.Online}'
tailscale ip -4                     # this node's IPv4
tailscale ping <peer>               # direct or via DERP relay, with latency
tailscale whois <ip-or-name>        # which node, user or tag an address belongs to
tailscale netcheck                  # NAT type, DERP latency, UDP support
tailscale debug prefs               # every preference in effect, as JSON
tailscale dns status                # MagicDNS and per-node DNS configuration
```

`tailscale ping` reporting "via DERP" means the direct path failed — usually symmetric
NAT or a strict firewall. That is a diagnosis, not an error: the tunnel still works,
with more latency.

## File transfer

```bash
tailscale file cp ./report.pdf <peer>:          # deposits into the peer's inbox
tailscale file get ./incoming/                  # pull whatever was sent to this node
```

Taildrop is per-user and per-device: the receiving node must have Taildrop enabled, and
the file lands in the receiving side's default inbox. There is no `tailscale file ls`;
you look in the directory.

A receiver that must run unattended:

```bash
tailscale file get --loop --conflict=rename /srv/inbox/
```

## Serve and Funnel

```bash
tailscale serve status                          # what is currently proxied
sudo tailscale serve --bg 8080                  # expose local :8080 to the tailnet over HTTPS
sudo tailscale serve --bg https / http://127.0.0.1:8080
sudo tailscale funnel 8080                      # the same, but to the public internet
sudo tailscale serve reset                      # remove all serve/funnel config
```

`serve` is tailnet-only; `funnel` is public. Funnel requires HTTPS certificates, which
Tailscale provisions, and it will not run on a node with an expiring key. Turning on
Funnel for something that was designed for a private network is how a lab becomes an
incident.

## Tailscale SSH

```bash
tailscale ssh <user>@<peer>          # authenticates through the coordination server
sudo tailscale up --ssh               # enable the SSH server on this node
```

The attraction is that `~/.ssh/authorized_keys` stops being the source of truth: the
ACL policy decides who may SSH where. The trade-off is that the tailnet control plane
is now in the authentication path — an availability decision as much as a security one.

## ACL policy

Policy is edited in the admin console (or with the API) as HuJSON. A minimal shape:

```json
{
  "tagOwners": {
    "tag:server": ["autogroup:admin"]
  },
  "acls": [
    { "action": "accept", "src": ["autogroup:admin"], "dst": ["*:*"] },
    { "action": "accept", "src": ["tag:server"], "dst": ["tag:server:22,443"] },
    { "action": "accept", "src": ["autogroup:member"], "dst": ["tag:server:443"] }
  ],
  "ssh": [
    { "action": "accept", "src": ["autogroup:admin"], "dst": ["tag:server"], "users": ["autogroup:nonroot"] }
  ]
}
```

- Default deny: if no rule matches, the packet does not flow.
- Ports are part of the rule (`tag:server:22,443`), not a separate firewall concept.
- Tags replace users for servers: a tagged node is owned by the tag, not by the person
  who enrolled it, so it survives staff changes.
- `autogroup:admin`, `autogroup:member` and `autogroup:self` are built-in groups; do
  not enumerate people when the group expresses the intent.

## Exit nodes and subnet routers

```bash
tailscale exit-node list                          # available exit nodes
sudo tailscale set --exit-node=<node>             # route all traffic through it
sudo tailscale set --exit-node=                   # stop using an exit node
sudo tailscale up --advertise-routes=192.0.2.0/24 # announce a subnet on this node
```

Subnet routes must be approved in the admin console (or via the API) before peers can
use them. An advertised-but-unapproved route is the most common "it does not work and
nothing says why" in Tailscale.

## Keys, tags, and expiry

```bash
tailscale status --json | jq -r '.Self.KeyExpiry'  # when this node's key expires
sudo tailscale set --auto-update                  # keep the client current
tailscale lock status                             # tailnet lock (node-key signing)
tailscale lock sign <nodekey>                     # sign a new node into a locked tailnet
```

Node keys expire by default (180 days). A server whose key expires disappears from the
tailnet at the worst possible moment — either disable expiry for that node in the
console or automate re-authentication. Tailnet lock adds a signing step to every new
node; it is the right answer for a hostile-network threat model and a nuisance for a
two-laptop tailnet.

## Troubleshooting order

1. `tailscale status` — is the peer online at all, and is the path direct or DERP.
2. `tailscale ping <peer>` — does the tunnel work independently of TCP services.
3. `tailscale netcheck` — is this node's NAT behaving, and which DERP is nearest.
4. `tailscale whois <ip>` — is the address you are testing actually the node you think.
5. `sudo tailscale debug prefs` — did an old `tailscale up` flag stick around.

## Traps worth remembering

- `tailscale up` replaces the whole preference set; `tailscale set` changes one field.
  Mixing them up silently drops `--ssh` or `--accept-routes`.
- A subnet route must be approved before it routes; advertising is not enough.
- MagicDNS names are per-tailnet; an `ssh host` that works for one person fails for
  another because the name resolves only inside the tailnet.
- Funnel exposes a service to the internet — the TLS certificate is Tailscale's, the
  exposure is yours.
- A node's key expiring looks exactly like the machine being off, until you read
  `tailscale status --json`. There is no `tailscale key expiry` subcommand — that is
  the first thing a copied recipe gets wrong.
