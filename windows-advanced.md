---
title: Windows — advanced
summary: Windows registry and routing examples
tags: [windows, network]
tooling: [reg, netsh]
verified_on: null
verified_env: null
status: unverified
---

# Windows — advanced

## NETWORKING

## Enable routing

reg add HKLM\System\CurrentControlSet\Services\Tcpip\Parameters ^ /v IPEnableRouter /t REG_DWORD /d 1

## Disable routing

reg add HKLM\System\CurrentControlSet\Services\Tcpip\Parameters ^ /v IPEnableRouter /t REG_DWORD /d 0
