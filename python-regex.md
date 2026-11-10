---
title: Python — regular expressions
summary: Regex in Python, including network-output parsing
tags: [python, regex]
tooling: [python, re]
verified_on: null
verified_env: null
status: unverified
---

# Python — regular expressions

## Separate a line in an ARP table based on regex

```python
import re
from netmiko import ConnectHandler
import getpass

net_connect = ConnectHandler(
    device_type=device, ip=ip_address, username=username, password=getpass.getpass()
)
output = net_connect.send_command(commands)

try:
    match = re.search(r"(.+?) +(.+?) +(\d+) +(.+ \d+?) +(.+) +(\d+?) +(.)", variable)
    x, y = match.group(1), match.group(2)
    print(f"The MAC address of IP {x} is {y}.")
except AttributeError:
    # Some lines will not match this expression and return NoneType; skip those.
    pass
```
