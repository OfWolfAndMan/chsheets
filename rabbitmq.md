---
title: RabbitMQ
summary: RabbitMQ — vhosts, users, queues, exchanges, bindings, management API
tags: [messaging, rabbitmq]
tooling: [rabbitmq, rabbitmqctl, rabbitmqadmin]
verified_on: 2026-11-10
verified_env: RabbitMQ 4.4.0 (rabbitmq:4-management container)
status: verified
---

# RabbitMQ

Verified against RabbitMQ 4.4.0 in the official `rabbitmq:4-management` image. The
2021 sheet targeted 3.x; 4.x removed a number of legacy features (classic mirrored
queues, some deprecated policies), so a 3.x tutorial copied wholesale will produce
warnings and, in places, errors.

## The model

A producer publishes to an **exchange**; the exchange routes to **queues** by
**bindings**; consumers read queues. A **vhost** is a namespace containing its own
exchanges, queues and permissions. Every operation happens inside a vhost.

| Exchange type | Routing rule |
|---|---|
| `direct` | routing key must match exactly |
| `topic` | routing key matched by pattern (`*` one word, `#` zero or more) |
| `fanout` | every bound queue gets a copy |
| `headers` | matched on message headers instead of routing key |

## Users and permissions

```bash
rabbitmqctl add_user <user> '<password>'
rabbitmqctl set_user_tags <user> administrator
rabbitmqctl list_users

rabbitmqctl add_vhost <vhost>
rabbitmqctl set_permissions -p <vhost> <user> '.*' '.*' '.*'
rabbitmqctl list_permissions -p <vhost>
```

The three permission patterns are configure / write / read, as regular expressions
matched against queue and exchange names. `.*` `.*` `.*` is the lab shortcut and a
production liability; scope by prefix (`^app\.`, `^app\..*`, `^app\..*`).

## Declaring topology

`rabbitmqadmin` in RabbitMQ 4.x is a rewritten Go binary (2.x) with clap-style
arguments. The old `name=value` positional syntax — `declare exchange name=events
type=topic` — is gone; every value is a named flag now.

```bash
admin="rabbitmqadmin -H localhost -u <user> -p '<password>' -V <vhost>"

$admin declare exchange --name events --type topic --durable true
$admin declare queue --name events.audit --durable true
$admin declare binding --source events --destination-type queue \
  --destination events.audit --routing-key 'event.#'

$admin list exchanges
$admin list queues
```

Topology declared by hand is topology that exists on one node. Export it instead:

```bash
$admin definitions export_from_vhost --file /tmp/vhost-defs.json
$admin definitions import_into_vhost --file /tmp/vhost-defs.json
rabbitmqctl export_definitions /tmp/defs-cli.json
```

## Publish and consume

```bash
$admin publish message -e events -k event.created -m '{"id":1}'
$admin get messages -q events.audit -c 1
```

`get messages` acknowledges by default (`ack_requeue_false`), so the message is gone
after it is printed. Use `-a ack_requeue_true` to peek without consuming.

From code, the connection is to the vhost, and the exchange must exist (or be
declared) before publishing. Declaring topology from application code is convenient
and dangerous: every service then owns the schema, and they disagree eventually.
Declare in one place — a deployment step or a definitions file — and publish from
everywhere.

## Inspecting a running node

```bash
rabbitmqctl status
rabbitmqctl list_queues name messages messages_ready messages_unacknowledged consumers
rabbitmqctl list_connections user peer_host state
rabbitmqctl list_channels connection number consumer_count
rabbitmqctl list_bindings
rabbitmq-diagnostics -q alarms
rabbitmq-diagnostics -q memory_breakdown
```

A queue with a growing `messages_ready` and no consumers is the standard symptom:
either the consumer died or it is consuming from a different vhost or routing key.
`list_bindings` answers the second case in one command.

## Management API

The `-management` image serves the HTTP API on 15672 and the UI at the same port.

```bash
curl -s -u <user>:'<password>' http://localhost:15672/api/overview | jq '.queue_totals'
curl -s -u <user>:'<password>' http://localhost:15672/api/queues/%2F | jq '.[].name'
curl -s -u <user>:'<password>' http://localhost:15672/api/health/checks/alarms
```

`%2F` is the default vhost `/`, URL-encoded. Anything you can click in the UI is a
REST call, which is what belongs in monitoring.

## Operations that fix things

```bash
rabbitmqctl purge_queue <queue>             # discard all messages — irreversible
rabbitmqctl delete_queue <queue>
rabbitmqctl close_connection '<conn>' '<reason>'
rabbitmqctl forget_cluster_node <node>      # after a node is gone for good
rabbitmqctl stop_app && rabbitmqctl reset   # last resort, wipes node state
```

`purge_queue` deletes messages with no confirmation and no undo. It is the correct
tool when a poison message is blocking a queue, and the wrong tool when the queue is
the only copy of anything.

## Clustering and quorum queues

In 4.x, durability across nodes means **quorum queues** — the classic mirrored queue
was removed. A quorum queue keeps its data on a majority of nodes and survives the
loss of a minority.

```bash
rabbitmqctl join_cluster rabbit@<other-node>
rabbitmqctl cluster_status
rabbitmqadmin declare queue name=events.audit durable=true arguments='{"x-queue-type":"quorum"}'
```

Quorum queues are heavier per message than classic queues. For transient, high-rate
workloads a classic queue without mirroring is still correct — it just is not
replicated.

## Traps worth remembering

- Publishing to a non-existent exchange fails silently if you do not enable publisher
  confirms; the message simply disappears.
- `messages_ready` growing with `consumers: 0` is a consumer problem, not a broker one.
- The default vhost `/` in a URL must be `%2F`.
- `durable=true` on the queue plus a non-persistent message still loses the message on
  restart; both halves are required.
- A single node with `disk_free_limit` breached blocks publishers by design — check
  `rabbitmq-diagnostics alarms` before blaming the application.
