---
title: OpenSearch
summary: OpenSearch — install, cluster health, indices, ingest, security
tags: [search, logs, observability, opensearch]
tooling: [opensearch, opensearch-dashboards, logstash, curl]
verified_on: null
verified_env: null
status: partial
---

# OpenSearch

> *Why OpenSearch and not Elasticsearch.* In 2021 Elastic moved Elasticsearch and
> Kibana from Apache 2.0 to the SSPL and the Elastic License. AWS forked the last
> Apache release (7.10.2), and that fork became OpenSearch — Apache 2.0, under the
> Linux Foundation. Elastic later added AGPLv3 as a third option. This sheet targets
> OpenSearch 3.x because it carries no licence arithmetic and ships security in the
> box. An appendix lists what differs if you are handed an Elastic cluster instead.

Commands below are drawn from the OpenSearch 3.x documentation. They have **not** been
executed against a live cluster from this workstation — there is no OpenSearch
installation here — which is why the status of this sheet is `partial` and not
`verified`.

## Install (single node, lab)

```bash
# Debian/Ubuntu
sudo apt install -y opensearch opensearch-dashboards

# RHEL family
sudo dnf install -y opensearch opensearch-dashboards

# The service does not start until the initial admin password is set
sudo /usr/share/opensearch/plugins/opensearch-security/tools/install_demo_configuration.sh
sudo systemctl enable --now opensearch opensearch-dashboards
```

Container form, which is how most labs should run it:

```bash
docker run -d --name opensearch -p 9200:9200 -p 9600:9600 \
  -e discovery.type=single-node \
  -e OPENSEARCH_INITIAL_ADMIN_PASSWORD='<Strong-Password-Here>' \
  opensearchproject/opensearch:3
```

The demo security script generates self-signed certificates and enables TLS. In a lab
that is fine; in anything else, use certificates from your own CA.

## Cluster and node health

```bash
curl -k -u admin:'<password>' https://localhost:9200
curl -k -u admin:'<password>' https://localhost:9200/_cluster/health?pretty
curl -k -u admin:'<password>' https://localhost:9200/_cat/nodes?v
curl -k -u admin:'<password>' https://localhost:9200/_cat/indices?v&s=store.size:desc
curl -k -u admin:'<password>' https://localhost:9200/_cluster/allocation/explain?pretty
```

`_cluster/health` returns `status` of `green`, `yellow`, or `red`. Yellow on a
single-node cluster is normal: replicas cannot be allocated when there is only one
node. Red means at least one primary shard is unassigned — start with
`_cluster/allocation/explain`.

`-k` disables certificate verification. It belongs in a lab command line, never in a
script that runs against production.

## Indices and documents

```bash
# create an index with explicit settings and mapping
curl -k -u admin:'<password>' -X PUT 'https://localhost:9200/logs-2026.11.10' \
  -H 'Content-Type: application/json' -d '
{
  "settings": { "number_of_shards": 1, "number_of_replicas": 0 },
  "mappings": {
    "properties": {
      "@timestamp": { "type": "date" },
      "host":       { "type": "keyword" },
      "message":    { "type": "text" },
      "status":     { "type": "integer" }
    }
  }
}'

# index one document
curl -k -u admin:'<password>' -X POST 'https://localhost:9200/logs-2026.11.10/_doc?refresh=true' \
  -H 'Content-Type: application/json' -d '{"@timestamp":"2026-11-10T12:00:00Z","host":"web1","message":"ok","status":200}'

# search
curl -k -u admin:'<password>' 'https://localhost:9200/logs-*/_search?pretty' \
  -H 'Content-Type: application/json' -d '{"query":{"match":{"message":"ok"}},"size":5}'

# delete by query (irreversible — test with a small time range first)
curl -k -u admin:'<password>' -X POST 'https://localhost:9200/logs-2026.11.10/_delete_by_query' \
  -H 'Content-Type: application/json' -d '{"query":{"range":{"@timestamp":{"lt":"2026-01-01"}}}}'
```

`text` is analyzed for full-text search; `keyword` is stored verbatim for filtering
and aggregation. Choosing the wrong one is the most common mapping mistake, and it is
expensive to fix later because the mapping cannot be changed in place.

## Index lifecycle

```bash
curl -k -u admin:'<password>' 'https://localhost:9200/_cat/aliases?v'
curl -k -u admin:'<password>' -X POST 'https://localhost:9200/logs-2026.11.10/_rollover?dry_run=true'
```

Use time-stamped indices (`logs-YYYY.MM.DD`) behind an alias and a rollover policy;
deleting whole indices by age is cheap, deleting documents from a giant index is not.

## Snapshots

```bash
# register a filesystem repository first (path must be in path.repo in opensearch.yml)
curl -k -u admin:'<password>' -X PUT 'https://localhost:9200/_snapshot/backups' \
  -H 'Content-Type: application/json' -d '{"type":"fs","settings":{"location":"/mnt/backups/os"}}'

curl -k -u admin:'<password>' -X PUT 'https://localhost:9200/_snapshot/backups/snap-2026-11-10?wait_for_completion=true'
curl -k -u admin:'<password>' 'https://localhost:9200/_snapshot/backups/_all?pretty'
```

A snapshot is only a backup if you have restored one. Restore into a differently named
index at least once.

## Security plugin

OpenSearch ships authentication, TLS, and role-based access control without a paid
tier. Configuration lives in `/etc/opensearch/opensearch-security/`:

```bash
# internal users, roles, role mappings, action groups
sudo cat /etc/opensearch/opensearch-security/internal_users.yml
sudo cat /etc/opensearch/opensearch-security/roles_mapping.yml

# apply configuration changes to a running cluster
sudo /usr/share/opensearch/plugins/opensearch-security/tools/securityadmin.sh \
  -cd /etc/opensearch/opensearch-security/ -icl -nhnv \
  -cacert /etc/opensearch/certs/root-ca.pem \
  -cert  /etc/opensearch/certs/admin.pem \
  -key   /etc/opensearch/certs/admin-key.pem
```

The default demo users (`admin`, `kibanaserver`, `logstash`) exist to get you started
and are the first thing an auditor will ask about. Replace them, and do not leave
`admin` with the demo password.

## Ingest

Logstash is the traditional shipper; OpenSearch also has Data Prepper and Beats can
target OpenSearch via their OSS builds.

```ruby
# logstash pipeline: /etc/logstash/conf.d/nginx.conf
input {
  file { path => "/var/log/nginx/access.log" start_position => "beginning" }
}
filter {
  grok { match => { "message" => "%{COMBINEDAPACHELOG}" } }
  date { match => ["timestamp", "dd/MMM/yyyy:HH:mm:ss Z"] }
}
output {
  opensearch {
    hosts => ["https://localhost:9200"]
    index => "nginx-%{+YYYY.MM.dd}"
    user => "logstash"
    password => "<password>"
    ssl => true
    cacert => "/etc/opensearch/certs/root-ca.pem"
  }
}
```

## Dashboards

```bash
sudo systemctl status opensearch-dashboards
# https://<host>:5601 — the admin credentials from the install are used here too
```

Dashboards is the UI; the API is where automation belongs. Save saved-objects (index
patterns, dashboards) as JSON in version control rather than clicking them into
existence.

## If you are handed Elasticsearch instead

| Concern | OpenSearch 3.x | Elasticsearch 9.x |
|---|---|---|
| Licence | Apache 2.0 | Elastic 2.0 / SSPL / AGPLv3 (triple) |
| Security | plugin included, free | free tier limited; SSO and advanced roles are paid |
| UI | OpenSearch Dashboards | Kibana |
| Shippers | Logstash, Data Prepper, Beats OSS | Beats, Elastic Agent |
| Query language | Query DSL | Query DSL plus ES\|QL |
| Repository names | `opensearch` packages/repos | `elastic` packages/repos |

Endpoints and query DSL are close enough that most examples transfer. What does not
transfer is the security configuration, the package and repository names, and the
shipper ecosystem — the three places a copy-paste from an Elastic tutorial fails.

## Traps worth remembering

- Yellow cluster health on one node is expected; red is not.
- `text` versus `keyword` in mappings cannot be changed in place — reindex instead.
- `-k` and plaintext `admin` passwords belong in a lab, nowhere else.
- Snapshot repositories require `path.repo` in the node configuration before they work.
- Deleting by query on a large index is expensive; design for whole-index retention.
