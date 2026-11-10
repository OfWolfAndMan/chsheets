---
title: YANG data models
summary: YANG — module structure, pyang validation, and the two lab modules from the NSO course
tags: [network, yang, nso, netconf]
tooling: [yang, pyang]
verified_on: 2026-11-10
verified_env: pyang (uvx), ietf-yang-types module; both modules below validate cleanly
status: verified
---

# YANG data models

YANG is the schema language behind NETCONF and RESTCONF: it describes what a device can
be configured with, and what it can report. A **module** is the unit — a namespace, a
prefix, imports, a revision, and a tree of `container`, `leaf`, `list` and `grouping`
statements.

Both modules below were pulled from a 2018 Cisco NSO training lab and were, as written,
not valid YANG. During this pass they were repaired and then validated:

| Defect in the original | Repair |
|---|---|
| The second module was a bare `grouping` outside any module | wrapped in `module switchport` with its own namespace and revision |
| `import ietf-inet-type` was never used and never resolvable | removed |
| `yang:` types used with no import | `import ietf-yang-types { prefix yang; }` added |

Validation:

```bash
uvx pyang module.yang                      # parses and checks semantics
uvx pyang -f tree module.yang              # the schema as a tree — the useful view
uvx pyang -f yang module.yang              # canonical reformatting
```

`pyang` is also what a CI job should run: a YANG module that does not parse is a
configuration model that will fail on the device, at the worst moment.

## The two lab modules

### switches.yang — hardware inventory model

```yang
module switches {
  namespace "http://example.com/switches";
  prefix "switches";

  // Example usage of ietf-inet-type
  // leaf interface_ip {
  //   type inet:ipv4-address;
  // }
  organization "Cisco Systems";
  contact "noc@example.com";
  description "Module to Model switches. Lab for Cisco System IT NSO Training.";
  //Defines the revision
  revision 2018-09-19 {
    description
      "Initial revision.";
    reference
      "RFC 7317: A YANG Data Model for System Management";
  }

    list Switches {
      key Model_Number;
      description "Model that repersents generic switches across manufacturers";

      leaf Manufacturer {
        type enumeration {
          enum 'Cisco' {
              description "Cisco Systems, cisco.com";
              reference "Ref goes here";
          }
          enum 'Juniper' {
              description "Juniper Networks, juniper.com";
          }
          enum 'Arista' {
              description "Arista Networks, arista.com";
          }
          enum 'HP' {
              description "Hewlett Packard, hp.com";
          }
        }
        description "Manufacturer of the switch";
      }
      leaf host-name {
        type string;
        description "Hostname for this system";
      }

      leaf Model_Number {
        type string;
        description "The PID or unique product identifier for the model";
      }

      leaf Platform_Series {
        type string;
        description "The model series that the PID belongs to. For example a 3850 would belong to the 3800 series switches";
      }

      list Interfaces {
        key Interface_Type;
        description "List of Interface Type adn number of interfaces available of that type";

        leaf Interface_Type {
          type enumeration {
            enum 'FastEthernet' {
              description "For FastEthernet interfaces";
            }
            enum 'GigabitEthernet'{
              description "For GigabitEthernet interfaces";
            }
            enum 'TenGigabitEthernet' {
              description "For TenGigEthernet interfaces";
            }
            enum 'FortyGigabitEthernet' {
              description "For FortyGigEthernet interfaces";
            }
            enum 'Tunnel' {
              description "For tunnel interfaces";
            }
          }
          description "The physical type of interface. ie Fe, Ge, TeG, etc..";
        }

        leaf Number_of_Interfaces {
          type int64 {
          range "0 .. 48";
          }
          description "The number of interfaces of the provided type that the switch has.";
        }
      }

      leaf MSRP {
        type int64;
        description "The Manufacturer Specified Retail Price of the switch in (currency of choice)";
      }

    }
}
```

### switchport.yang — interface configuration model

```yang
module switchport {
  namespace "http://example.com/switchport";
  prefix sp;

  import ietf-yang-types {
    prefix yang;
  }

  revision 2018-09-19 { description "Initial revision."; }

  grouping config-interface-switchport-grouping {
        container access {
          description
            "Set access mode characteristics of the interface";
          container vlan {
            description
              "Set VLAN when interface is in access mode";
            leaf vlan {
              type union {
                type uint16 {
                  range "1..4094";
                }
                type enumeration {
                  enum "dynamic";
                }
              }
            }
            leaf name {
              description
                "Vlan name";
              type string;
            }
          }
        }
        //  backup         Set backup for the interface
        // interface * / switchport block
        container block {
          description
            "Disable forwarding of unknown uni/multi cast addresses";
          leaf multicast {
            description
              "Block unknown multicast addresses";
            type empty;
          }
          leaf unicast {
            description
              "Block unknown unicast addresses";
            type empty;
          }
        }
        //  dot1q          Set interface dot1q properties

        // interface * / switchport mode
        container mode {
          description
            "Set trunking mode of the interface";
          choice mode-choice {
            container access {
              presence "true";
              description
                "Set trunking mode to ACCESS unconditionally";
            }
            container dot1q-tunnel {
              presence "true";
              description
                "set trunking mode to TUNNEL unconditionally";
            }
            leaf dynamic {
              description
                "Set trunking mode to dynamically negotiate access or trunk mode";
              type enumeration {
                enum "auto";
                enum "desirable";
              }
            }
            container private-vlan {
              description
                "Set private-vlan mode";
              leaf host {
                description
                  "Set the mode to private-vlan host";
                type empty;
              }
              leaf promiscuous {
                description
                  "Set the mode to private-vlan promiscuous";
                type empty;
              }
            }
            container trunk {
              presence "true";
              description
                "Set trunking mode to TRUNK unconditionally";
            }
          }
        }
        // interface * / switchport nonegotiate
        leaf nonegotiate {
          description
            "Device will not engage in negotiation protocol on this interface";
          type empty;
        }
        // interface * / switchport port-security
        container port-security {
          description
            "Security related command";
          presence "true";
          container aging {
            description
              "Port-security aging commands";
            leaf static {
              description
                "Enable aging for configured secure addresses";
              type empty;
            }
            leaf time {
              description
                "Port-security aging time";
              type uint16 {
                range "1..1440";
              }
            }
            leaf type {
              description
                "Port-security aging type";
              type enumeration {
                enum "absolute";
                enum "inactivity";
              }
            }
          }
          container mac-address {
            description
              "Secure mac address";
            leaf sticky {
              description
                "Configure dynamic secure addresses as sticky";
              type empty;
            }
            leaf hw-address {
              type yang:mac-address;
            }
            leaf vlan {
              description
                "set VLAN ID of the VLAN on which this address can be learned";
              type uint16 {
                range "1..4094";
              }
            }
          }
          container maximum {
            description
              "Max secure addresses";
            leaf max-addresses {
              type uint16 {
                range "1..4097";
              }
            }
            leaf vlan {
              description
                "Max secure addresses per vlan";
              type string;
            }
          }
          leaf violation {
            description
              "Security violation mode";
            type enumeration {
              enum "protect";
              enum "restrict";
              enum "shutdown";
            }
          }
        }
        // interface * / switchport trunk
        container trunk {
          description
            "Set trunking characteristics of the interface";
            // interface * / switchport trunk allowed
          container allowed {
            description
              "Set allowed VLAN characteristics when interface is in trunking mode";
              // interface * / switchport trunk allowed vlan
            container vlan {
              description
                "Set allowed VLANs when interface is in trunking mode";
              choice vlan-choice {
                leaf vlans {
                  type string;
                }
                leaf add {
                  description
                    "VLAN IDs of the allowed VLANs when this port is in trunking mode";
                  type union {
                    type uint16;
                    type string;
                  }
                }
                leaf all {
                  description
                    "all VLANs";
                  type empty;
                }
                leaf-list except {
                  description
                    "all VLANs except the following";
                  type union {
                    type uint16;
                    type string;
                  }
                }
                leaf none {
                  description
                    "no VLANs";
                  type empty;
                }
                leaf remove {
                  description
                    "VLAN IDs of disallowed VLANS when this port is in trunking mode";
                  type union {
                    type uint16;
                    type string;
                  }
                }
              }
            }
          }
          // interface * / switchport trunk encapsulation
          leaf encapsulation {
            description
              "Set encapsulation format on trunk port";
            type enumeration {
              enum "dot1q";
              enum "isl";
              enum "negotiate";
            }
          }
          // interface * / switchport trunk native
          container native {
            description
              "Set trunking native characteristics when interface is in trunking mode";
            leaf vlan {
              description
                "Set native VLAN when interface is in trunking mode";
              type union {
                type enumeration {
                  enum "tag";
                }
                type uint16 {
                  range "1..4094";
                }
              }
            }
          }
          // interface * / switchport trunk pruning
          container pruning {
            description
              "Set pruning VLAN characteristics when interface is in trunking mode";
            container vlan {
              description
                "Set VLANs enabled for pruning when interface is in trunking mode";
              choice vlan-choice {
                leaf-list vlans {
                  type union {
                    type uint16;
                    type string;
                  }
                }
                leaf add {
                  description
                    "VLAN IDs of the allowed VLANs when this port is in trunking mode";
                  type union {
                    type uint16;
                    type string;
                  }
                }
                leaf-list except {
                  description
                    "all VLANs except the following";
                  type union {
                    type uint16;
                    type string;
                  }
                }
                leaf none {
                  description
                    "no VLANs";
                  type empty;
                }
                leaf remove {
                  description
                    "VLAN IDs of disallowed VLANS when this port is in trunking mode";
                  type union {
                    type uint16;
                    type string;
                  }
                }
              }
            }
          }
        }
        // interface * / switchport voice
        container voice {
          description
            "Voice appliance attributes";
          container vlan {
            description
              "Vlan for voice traffic";
            leaf vlan {
              type union {
                type enumeration {
                  enum "dot1p";
                  enum "none";
                  enum "untagged";
                }
                type uint16 {
                  range "1..4094";
                }
                type string;
              }
            }
            leaf name {
              description
                "Vlan name";
              type string;
            }
          }
          container detect {
            description
              "detection enhancement keyword";
            container cisco-phone {
              description
                "Cisco IP phone";
              presence "true";
              leaf full-duplex {
                description
                  "full duplex keyword";
                type empty;
              }
            }
          }
        }
        // interface * / switchport priority
        container priority {
          description
            "Set appliance 802.1p priority";
          container extend {
            description
              "Set appliance 802.1p priority";
            choice trust-choice {
              leaf trust {
                description
                  "Trust 802.1p priorities of devices on appliance";
                type empty;
              }
              leaf cos {
                description
                  "Override 802.1p priority of devices on appliance";
                type uint8 {
                  range "0..7";
                }
              }
            }
          }
        }
        // interface * / switchport autostate
        container autostate {
          description
            "Include or exclude this port from vlan link up calculation";
          leaf exclude {
            description
              "Exclude this port from vlan link up calculation";
            type empty;
          }
        }
        // interface * / switchport protected
        leaf protected {
          description
            "Configure an interface to be a protected port";
          type empty;
        }
        // interface * / switchport host
        leaf host {
          description
            "Set port host";
          type empty;
        }
        //interface * /switchport private-vlan
        container private-vlan {
          description
            "Set the private VLAN configuration";
          container association {
            description
              "Set the private VLAN association";
            container host {
              description
                "Set the private VLAN host association";
              leaf primary-range {
                description
                  "Primary normal range VLAN ID of the private VLAN port association";
                type uint16 {
                  range "2..1001 | 1006..4094";
                }
              }
              leaf secondary-range {
                description
                  "Secondary normal range VLAN ID of the private VLAN host port association";
                type uint16 {
                  range "2..1001 | 1006..4094";
                }
              }
            }
            container mapping {
              description
                "Set the private VLAN promiscuous mapping";
              leaf primary-range {
                description
                  "Primary normal range VLAN ID of the private VLAN promiscuous port mapping";
                type uint16 {
                  range "2..1001 | 1006..4094";
                }
              }
              leaf secondary-range {
                description
                  "Secondary VLAN IDs of the private VLAN promiscuous port mapping";
                type string;
              }
              leaf add {
                description
                  "Secondary VLAN IDs of the private VLAN promiscuous port mapping";
                type string;
              }
              leaf remove {
                description
                  "Secondary VLAN IDs of the private VLAN promiscuous port mapping";
                type string;
              }
            }
          }
          container host-association {
            description
              "Set the private VLAN host association";
            leaf primary-range {
              description
                "Primary normal range VLAN ID of the private VLAN port association";
              type uint16 {
                range "2..1001 | 1006..4094";
              }
            }
            leaf secondary-range {
              description
                "Secondary normal range VLAN ID of the private VLAN host port association";
              type uint16 {
                range "2..1001 | 1006..4094";
              }
            }
          }
          container mapping {
            description
              "Set the private VLAN promiscuous mapping";
            leaf primary-range {
              description
                "Primary normal range VLAN ID of the private VLAN promiscuous port mapping";
              type uint16 {
                range "2..1001 | 1006..4094";
              }
            }
            leaf secondary-range {
              description
                "Secondary VLAN IDs of the private VLAN promiscuous port mapping";
              type string;
            }
            leaf add {
              description
                "Secondary VLAN IDs of the private VLAN promiscuous port mapping";
              type string;
            }
            leaf remove {
              description
                "Secondary VLAN IDs of the private VLAN promiscuous port mapping";
              type string;
            }
          }
        }
        // interface * / switchport vepa enabled
        container vepa {
          description
            "Reflective relay configuration";
          leaf enabled {
            description
              "Enable reflective relay";
              type empty;
          }
        }
    }
}
```

## What the structure is telling you

- `container` groups related nodes; it holds no value itself.
- `leaf` is a single value with a type; `leaf-list` is a list of values.
- `list` is a table of entries, keyed by one or more `leaf`s — a `key` statement.
- `grouping`/`uses` is the reuse mechanism; the definition is inlined at each use.
- `type union` allows several types, as `vlan` does above: a number, or the string
  `dynamic`.
- `type empty` is a flag: present means true, absent means false.

## Where these fit

- **NETCONF/RESTCONF**: the device exposes a data tree that conforms to its modules;
  `get-config`, `edit-config` and `get` operate on that tree.
- **NSO**: loads device YANG modules to build the device model, then applies service
  models on top of them.
- **Vendor deviations**: the same feature is rarely modelled identically across
  vendors. Reading the vendor's YANG is more reliable than reading its CLI guide.

## Traps worth remembering

- A YANG module that parses is not necessarily a module a device will accept; vendor
  devices carry platform-specific constraints and deviations.
- `pyang` validates structure, not intent: `range "1..4094"` for a VLAN is your claim,
  and the device may disagree.
- A `grouping` outside a module is not legal YANG, however sensible it looks — that was
  the defect in the second half of this lab.
- Imports must resolve at build time. An unused import that cannot be found is still a
  validation failure.
