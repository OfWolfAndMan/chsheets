### Interface Schema

- Mgmt: 
- 1.1: External
- 1.2: Internal
- 1.3: HA


### Default Login

- CLI: root/default
- GUI: admin/admin

### Terminology

- Self IP: An IP Used by the LTM itself
	* Self IP should be identical in the configuration to the HA device
- Floating IP: Used for HA deployments (Similar to HSRP/VRRP)
	* Floating IP should be the IP specific to the individual box for HA failover
- Node: IP Address
- Pool Member: Node+Service Port
- Pool: Related Pool Members for load balancing

### Default Ports/Protocols Allowed on Self-IP (Port Lockdown)

- OSPF
- TCP 4353 (iQuery)
- UDP 4353 (iQuery)
- TCP 443 (HTTPS)
- TCP 161 (SNMP)
- UDP 161 (SNMP)
- TCP 22 (SSH)
- TCP 53 (DNS)
- UDP 53 (DNS)
- UDP 520 (RIP)
- UDP 1026 (Network Failover)


### Adding Servers

**Nodes**

- Name
- Address (Specific to the server)

**Pools**

**Virtual Servers**

- Name
- Destination Address: Same subnet as external interface
- Service Port
- Default Pool: Pool that was assigned in the pools tab


**Load Balancing Methods**

Static
  - Round Robin
    * Doesn't take into account specific events
  - Ratio
    * Member
    * Node
Dynamic
  -
  -

