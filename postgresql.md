# General
### Location of files
/etc/postgresql/<version>/main

## postgresql.conf
```Shell
# Primary location for global instance settings
# - Memory -
shared_buffers = 128MB
# huge_pages = try
# temp_buffers = 8MB
# max_prepared_transactions = 0
```

## pg_hba.conf
Contains client authentication settings


### Add UUID generation function
```SQL
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### SQL Queries (SELECT)
```SQL
SELECT <field(s)> FROM <table>
SELECT * FROM devices;
SELECT hostname,ip_address FROM devices;
```

### Concatenates first and last name into field 'full name'
```SQL
SELECT first_name || ' ' || last_name AS full_name,email FROM customer;
```

### Order results by hostname in a descending order
```SQL
SELECT * FROM devices ORDER BY hostname DESC;
```

### Order results based on length of specific field
```SQL
SELECT * FROM devices ORDER BY LENGTH(hostname);
```

### Get results that contain a hostname that's 3-5 characters
```SQL
SELECT * FROM devices WHERE LENGTH(hostname) BETWEEN 3 AND 5;
```

### Select records that contain a vendor of Cisco
```SQL
SELECT * FROM devices WHERE vendor = 'Cisco';
```

### Select records that don't contain a vendor of Cisco
```SQL
SELECT * FROM devices WHERE vendor != 'Cisco';
```

### select records that are Cisco routers only
```SQL
SELECT * FROM devices WHERE vendor = 'Cisco' AND function = 'router';
```

### Grabs all records that have a hostname starting with r
```SQL
SELECT * FROM devices WHERE hostname LIKE 'R%';
```

### Grabs all records that have a hostname starting with r followed by a single character
```SQL
SELECT * FROM devices WHERE hostname LIKE 'R_';
```

### Grabs all records where vendor of device is Cisco or Juniper
```SQL
SELECT * FROM devices WHERE vendor IN ('Cisco', 'Juniper');
```

### Retrieves devices created between January and May 1, 2020
```SQL
SELECT * FROM devices WHERE created_on BETWEEN '2020-01-01' AND '2020-05-01';
```

### Run an inner join between devices and credentials (Ties in user/password for a device)
```SQL
SELECT hostname, management_ip, vendor, credentials.user, credentials.password FROM devices inner join credentials on devices.credentials = credentials.user;
```

### Update table so 'user' value in credentials table must be unique
```SQL
ALTER TABLE public.credentials ADD CONSTRAINT credentials_un UNIQUE ("user");
```

### Create a field with ENUM values
```SQL
CREATE TYPE net_vendor AS ENUM ('cisco', 'juniper', 'fortinet', 'checkpoint');
CREATE TABLE hardware (
    model text,
    vendor net_vendor,
    dev_type text
);
```

### Create a field where uuid is generated for the field
```SQL
CREATE TABLE public.acls (
    id uuid NOT NULL DEFAULT uuid_generate_v1()
);
```
