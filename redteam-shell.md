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
