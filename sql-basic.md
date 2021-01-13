```SQL
create table devices (
    hostname VARCHAR(30) NOT NULL PRIMARY KEY,
    management_ip inet NOT NULL,
    model VARCHAR(30) NOT NULL,
    vendor VARCHAR(20) NOT NULL CHECK (vendor in ('Cisco',
    'Juniper', 'Arista', 'Fortinet', 'Checkpoint', 'HP', 'Brocade')),
    credential_id VARCHAR(20) REFERENCES credentials (name)
);
```

```SQL
create table credentials (
    name VARCHAR(20) NOT NULL PRIMARY KEY,
    username VARCHAR(20) NOT NULL,
    password VARCHAR(25) NOT NULL
);
```