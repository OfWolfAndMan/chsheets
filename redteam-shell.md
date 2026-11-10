---
title: Offensive shell
summary: Offensive shell one-liners
tags: [security, shell]
tooling: [curl, wget, ettercap]
verified_on: null
verified_env: null
status: unverified
---

# Offensive shell

## Get public ip address

### Less Detail

```shell
curl -4 icanhazip.com
```

### More Detail

```shell
curl ipinfo.io
```

### Clone a website

```shell
wget -r -nH $MY_URL
```

### Start Ettercap GUI

```shell
ettercap -G
```

## Status

Unverified, and deliberately small. Two of the tools named here (`ettercap`, `wget -r`)
are for networks you own or have written permission to test. Nothing in this sheet
belongs on a network you do not control, and an offensive command without a scope
statement is evidence of nothing except carelessness.
