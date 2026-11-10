---
title: Windows
summary: Windows client and server — hardening baseline, registry, networking, updates
tags: [windows, security, network]
tooling: [powershell, reg, netsh, sconfig]
verified_on: null
verified_env: null
status: unverified
---

# Windows

Merged from the old `windows-advanced` and `windows-hardening` sheets, both of which
were Windows 10/Server 2012-era and mostly links. Nothing here has been executed on a
Windows host from this repository's maintainer in the last five years, hence
`status: unverified`. The commands are current PowerShell rather than `cmd` where a
PowerShell equivalent exists — `cmd` still works, but it is the compatibility layer now.

## Hardening baseline — client and server

What actually reduces attack surface, in the order it matters:

| Control | Why it matters | Check |
|---|---|---|
| Full-disk encryption (BitLocker) | the only control that survives a stolen laptop | `Get-BitLockerVolume` |
| Local admin group, minimal | most malware runs as the logged-in user | `Get-LocalGroupMember -Group Administrators` |
| Windows Update, enforced | unpatched SMB/RDP is how ransomware arrives | `Get-WindowsUpdate` (PSWindowsUpdate) |
| SMBv1 disabled | permanent exploit surface, no modern use | `Get-SmbServerConfiguration` |
| RDP not exposed to the internet | brute force and pre-auth bugs | `Get-NetTCPConnection -LocalPort 3389` |
| Defender real-time + cloud | baseline AV, not sufficient alone | `Get-MpComputerStatus` |
| Firewall on all profiles | default-allow is not a firewall | `Get-NetFirewallProfile` |
| Application allow-listing | blocks the unlisted binary | AppLocker or WDAC |
| Script-block logging | visibility into PowerShell abuse | `Get-WinEvent -LogName 'Microsoft-Windows-PowerShell/Operational'` |

```powershell
# audit the current state of the controls above
Get-BitLockerVolume | Select-Object MountPoint, ProtectionStatus
Get-LocalGroupMember -Group Administrators
Get-SmbServerConfiguration | Select-Object EnableSMB1Protocol, RequireSecuritySignature
Get-NetFirewallProfile | Select-Object Name, Enabled, DefaultInboundAction
Get-MpComputerStatus | Select-Object RealTimeProtectionEnabled, AntivirusSignatureLastUpdated
```

```powershell
# disable SMBv1 (requires reboot)
Set-SmbServerConfiguration -EnableSMB1Protocol $false -Force
Disable-WindowsOptionalFeature -Online -FeatureName SMB1Protocol -NoRestart

# require SMB signing
Set-SmbServerConfiguration -RequireSecuritySignature $true -Force
```

## Accounts and privileges

```powershell
Get-LocalUser                                   # local accounts and enabled state
Get-LocalGroupMember -Group Administrators
New-LocalUser -Name appuser -NoPassword -AccountNeverExpires
Add-LocalGroupMember -Group Users -Member appuser

# built-in Administrator: rename and disable where policy allows
Disable-LocalUser -Name Administrator
```

A local account with a weak password and RDP exposed is the single most common
small-network compromise. Either remove RDP from the internet or put it behind a VPN.

## Registry, the supported way

```powershell
# read
Get-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters' `
  -Name IPEnableRouter

# write (requires elevation)
Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters' `
  -Name IPEnableRouter -Value 1 -Type DWord

# enumerate a hive branch
Get-ChildItem 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall' |
  Select-Object PSChildName
```

The old `reg add` form still works and is what most hardening guides quote:

```batch
reg add "HKLM\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" /v IPEnableRouter /t REG_DWORD /d 1 /f
reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v ProductName
```

Prefer the PowerShell provider: it fails loudly, returns objects, and does not depend
on `cmd` quoting rules.

## Networking

```powershell
Get-NetAdapter | Select-Object Name, Status, LinkSpeed
Get-NetIPConfiguration
Get-NetIPAddress -AddressFamily IPv4
Get-NetRoute -DestinationPrefix '0.0.0.0/0'
Get-NetTCPConnection -State Listen | Select-Object LocalAddress, LocalPort, OwningProcess
Resolve-DnsName example.com
Test-NetConnection -ComputerName example.com -Port 443
```

```powershell
# static address, replacing the netsh incantation
New-NetIPAddress -InterfaceAlias 'Ethernet' -IPAddress 192.0.2.10 `
  -PrefixLength 24 -DefaultGateway 192.0.2.1
Set-DnsClientServerAddress -InterfaceAlias 'Ethernet' -ServerAddresses 192.0.2.53
```

```powershell
# port forwarding, equivalent to the netsh interface portproxy form
netsh interface portproxy add v4tov4 listenport=8080 listenaddress=0.0.0.0 `
  connectport=80 connectaddress=192.0.2.20
netsh interface portproxy show v4tov4
```

`New-NetNat`/`Add-NetNatStaticMapping` is the PowerShell route; the `netsh portproxy`
form remains the most reliable across Windows versions.

## Server bring-up (no GUI)

```powershell
sconfig                      # server core: hostname, network, updates, domain join
Get-WindowsFeature           # installed/available roles
Install-WindowsFeature -Name Web-Server -IncludeManagementTools
```

```powershell
# remote management over WinRM
Enable-PSRemoting -Force
Enter-PSSession -ComputerName server1.example.com -Credential (Get-Credential)
Invoke-Command -ComputerName server1.example.com -ScriptBlock { Get-Service }
```

## Event logs worth reading first

```powershell
Get-WinEvent -LogName Security -MaxEvents 50 |
  Where-Object Id -in 4624,4625,4672,4720 |
  Select-Object TimeCreated, Id, Message

Get-WinEvent -FilterHashtable @{LogName='System'; Level=2} -MaxEvents 20
Get-WinEvent -LogName 'Microsoft-Windows-Windows Defender/Operational' -MaxEvents 20
```

4625 is failed logon, 4624 successful, 4672 special privileges assigned, 4720 account
created. A burst of 4625 from one source is the signature of a password spray.

## Tools

Worth installing, all free: Sysinternals Suite (Process Explorer, Autoruns, TCPView),
Wireshark, 7-Zip, KeePassXC for credentials, VeraCrypt for non-system volumes, and
PowerShell 7 as a second shell rather than a replacement.

Download from the vendor's own domain — `learn.microsoft.com/sysinternals`,
`wireshark.org`, `keepassxc.org`, `veracrypt.fr`. A "Windows hardening tool" from a
bundled-downloads site is how hardening becomes infection.

## Traps worth remembering

- `Set-ItemProperty` without `-Type` may create a string where a DWORD was expected; the
  registry accepts both and the service ignores the wrong one.
- `cmd`'s `^` line continuation is not PowerShell's backtick, and mixing them in one
  script produces silent truncation.
- Disabling SMBv1 on a server with a legacy NAS attached breaks the NAS, not Windows.
- BitLocker recovery keys belong in a password manager, not on a sticky note on the
  laptop they protect.
- A hardening baseline that is not re-audited after every feature update is a document
  about 2019.
