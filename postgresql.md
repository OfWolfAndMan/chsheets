---
title: PostgreSQL
summary: PostgreSQL 18 — roles, psql, schema, indexes, backup, plus a SQL refresher
tags: [database, sql, postgresql]
tooling: [postgresql, psql, pg_dump]
verified_on: 2026-11-10
verified_env: PostgreSQL 18.6 (container), psql 18.6 client
status: verified
---

# PostgreSQL

Executed against PostgreSQL 18.6. The SQL refresher at the end replaces the separate
`sql-basic` sheet — that file was eighteen lines and belonged here.

## Connect

```bash
psql "postgresql://<user>@<host>:5432/<db>"        # password via ~/.pgpass, never the URI
psql -h <host> -U <user> -d <db> -c 'select now();'
psql -h <host> -U <user> -d <db> -f script.sql
```

Never put a password on the command line: it lands in shell history and in `ps`. Use
`~/.pgpass` with mode 0600, or a service file.

## psql meta-commands

```text
\l                 list databases
\c <db>            connect to another database
\dt                tables
\dt+ <pattern>     tables with size
\d <table>         describe a table, its indexes and constraints
\di                indexes
\dn                schemas
\du                roles
\df                functions
\e                 edit the current query in $EDITOR
\timing on         time each statement
\x auto            expanded output when it helps
\copy (select 1) to '/tmp/out.csv' csv header
```

## Databases and roles

```sql
CREATE ROLE app_user LOGIN PASSWORD '<password>';
CREATE DATABASE app_db OWNER app_user;

GRANT CONNECT ON DATABASE app_db TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT ON TABLES TO app_user;
```

Application users should not be superusers, and should not own the schema they write
to. Keep the migration role separate from the runtime role.

## Schema

```sql
CREATE TABLE hosts (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name        text NOT NULL UNIQUE,
    address     inet,
    environment text NOT NULL DEFAULT 'prod'
                CHECK (environment IN ('prod','staging','dev')),
    owner       text NOT NULL DEFAULT current_user,
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE settings (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    environment text NOT NULL,
    is_default  boolean NOT NULL DEFAULT false,
    payload     jsonb NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE events (
    id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    host_id    bigint NOT NULL REFERENCES hosts(id) ON DELETE CASCADE,
    kind       text NOT NULL,
    occurred   timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE hosts ADD COLUMN notes text;
```

`timestamptz` over `timestamp`: it stores UTC and renders in the session timezone.
`text` over `varchar(n)` unless the limit is a real business rule.

## Indexes

```sql
CREATE INDEX events_host_time_idx ON events (host_id, occurred DESC);
CREATE INDEX hosts_name_lower_idx ON hosts (lower(name));
CREATE UNIQUE INDEX one_default_per_env ON settings (environment) WHERE is_default;
```

- Composite index order matters: the leading column must match the query predicate.
- An index on `lower(name)` is what makes `WHERE lower(name) = ...` fast.
- Partial indexes are cheap and precise when the query always filters on the predicate.

## Reading a plan

```sql
EXPLAIN ANALYZE
SELECT h.name, count(*) AS events
FROM hosts h
JOIN events e ON e.host_id = h.id
WHERE e.occurred > now() - interval '7 days'
GROUP BY h.name
ORDER BY events DESC
LIMIT 10;
```

`EXPLAIN` shows the plan; `EXPLAIN ANALYZE` runs it and shows actual rows and timings.
Look for a `Seq Scan` on a large table with a selective predicate, and for row
estimates that are orders of magnitude away from actual — that means stale statistics,
which `ANALYZE` fixes. The scan itself needs an index or a rewritten predicate.

## Transactions

```sql
BEGIN;
UPDATE hosts SET environment = 'staging' WHERE name = 'web1';
SAVEPOINT before_events;
DELETE FROM events WHERE occurred < now() - interval '1 year';
ROLLBACK TO SAVEPOINT before_events;
COMMIT;
```

PostgreSQL is MVCC: readers do not block writers and writers do not block readers.
Long transactions hold back vacuum and inflate tables — keep them short.

## Maintenance and statistics

```sql
VACUUM (ANALYZE) hosts;
ANALYZE hosts;

SELECT relname, n_live_tup, n_dead_tup, last_autovacuum
FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 10;

SELECT pid, state, wait_event_type, now() - query_start AS duration, left(query, 60)
FROM pg_stat_activity
WHERE state <> 'idle' ORDER BY duration DESC;

SELECT pg_size_pretty(pg_total_relation_size('events'));
```

## Backup and restore

```bash
pg_dump -U <user> -Fc -d <db> -f backup.dump            # custom format: compressed, selective restore
pg_dump -U <user> -Fc -t '<table>' -d <db> -f table.dump
pg_restore -l backup.dump | head              # what is inside
pg_restore -U <user> -C -d postgres backup.dump         # create the database and restore into it
pg_dump -U <user> -Fc -d <db> | ssh <host> 'cat > /backups/db.dump'
```

A dump is not a backup until a restore has been rehearsed. `pg_upgrade` handles major
version moves; logical replication is the lower-downtime alternative for large
databases.

## Row-level security

```sql
ALTER TABLE events ENABLE ROW LEVEL SECURITY;

CREATE POLICY events_own_rows ON events
  FOR SELECT TO app_user
  USING (host_id IN (SELECT id FROM hosts WHERE owner = current_user));
```

RLS is enforced by the database, which is a stronger guarantee than a filter in the
application.

## Partitioning

```sql
CREATE TABLE events_p (LIKE events INCLUDING DEFAULTS) PARTITION BY RANGE (occurred);
CREATE TABLE events_2026_11 PARTITION OF events_p
  FOR VALUES FROM ('2026-11-01') TO ('2026-12-01');
```

Partition when retention is by time and the table is large enough that deleting rows
is painful. Dropping a partition is instant; `DELETE` is not.

## SQL refresher

```sql
SELECT id, name FROM hosts WHERE environment = 'prod' ORDER BY name LIMIT 5;

SELECT environment, count(*) AS n FROM hosts GROUP BY environment HAVING count(*) > 1;

SELECT h.name, e.kind FROM hosts h
JOIN events e ON e.host_id = h.id
WHERE e.occurred > now() - interval '1 day';

SELECT h.name, e.kind FROM hosts h
LEFT JOIN events e ON e.host_id = h.id;      -- keeps hosts with no events

INSERT INTO hosts (name, address) VALUES ('web2', '192.0.2.20')
ON CONFLICT (name) DO UPDATE SET address = EXCLUDED.address;

UPDATE events SET kind = 'error' WHERE kind = 'err';
DELETE FROM events WHERE occurred < now() - interval '90 days';

SELECT name,
       row_number() OVER (PARTITION BY environment ORDER BY id) AS seq
FROM hosts;

WITH recent AS (
  SELECT * FROM events WHERE occurred > now() - interval '1 hour'
)
SELECT kind, count(*) FROM recent GROUP BY kind;
```

`ON CONFLICT ... DO UPDATE` is the upsert; `EXCLUDED` is the row that was proposed.

## Traps worth remembering

- `NULL` is not equal to anything, including itself; use `IS NULL` / `IS DISTINCT FROM`.
- `count(*)` counts rows; `count(col)` skips nulls.
- `OFFSET` pagination degrades; keyset pagination (`WHERE id > $last ORDER BY id`) does not.
- Unindexed foreign keys make cascading deletes slow in a way that only shows at scale.
- A `DELETE` without a `WHERE` is a `TRUNCATE` with extra logging and reconciliation.
