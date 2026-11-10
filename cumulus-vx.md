---
title: Cumulus VX / NVIDIA Cumulus Linux
summary: Cumulus VX / NVIDIA Cumulus Linux lab commands
tags: [linux, network, vendor]
tooling: [cumulus vx, cl-commands]
verified_on: null
verified_env: null
status: unverified
---

# Cumulus VX / NVIDIA Cumulus Linux

## Show interfaces

```shell
net show interface
```

### Enter quagga command line

```shell
sudo vtysh
```

### Enable OSPF/BGP

```shell
nano /etc/frr/daemons
#Zebra MUST be set to yes
```

### Enable the service (After options set to yes)

```shell
sudo systemctl enable frr.service
sudo systemctl start frr.service
```

### Configure OSPF (Must be enabled in FRR)

```shell
net add ospf router-id <router-id>
net add ospf network <network>/<mask> area <area id>
net add ospf passive-interface <interface>
net add interface <interface> ospf area <area id> (Can only be used if network statement not set)
```

## Status

Unverified. Cumulus Linux is now NVIDIA Cumulus Linux, and the command surface changed
with the release train: `net show ...` was replaced by `nv show ...` in current
versions, and the `apt` repositories moved under NVIDIA's hosting. Read the commands
below as the shape of the workflow, not as strings to paste, until this sheet is
re-verified against a current VX image.
