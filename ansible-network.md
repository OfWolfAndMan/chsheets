---
title: Ansible — network devices
summary: Ansible for network devices — inventory, FQCN modules, cli_command, config diff
tags: [ansible, network, automation]
tooling: [ansible-core, ansible.netcommon, ansible.utils]
verified_on: 2026-11-10
verified_env: ansible-core 2.x via uvx, ansible.netcommon and ansible.utils collections; playbooks pass ansible-playbook --syntax-check
status: partial
---

# Ansible — network devices

Validated with `ansible-playbook --syntax-check` against ansible-core with the
`ansible.netcommon` and `ansible.utils` collections. No device was contacted — there is
no switch on this network — so the syntax and resolution are verified and the device
behaviour is not. That is what `partial` means here.

Three idioms from the 2018–2021 version of this sheet are gone:

| Retired | Current |
|---|---|
| `local_action:` | `delegate_to: localhost` |
| `copy content={{ var }}` | `ansible.builtin.copy: content: "{{ var }}"` |
| bare module names (`ios_command`) | FQCN (`cisco.ios.ios_command`), collection installed explicitly |

## Install

```bash
uv tool install ansible-core            # or: pipx install ansible-core
ansible-galaxy collection install ansible.netcommon ansible.utils
ansible-galaxy collection install cisco.ios arista.eos     # per platform
ansible-galaxy collection list
```

Collections are the unit of distribution now. `ansible` (the batteries-included
package) is convenient; `ansible-core` plus explicit collections is what a repository
should pin.

## Inventory

```yaml
# inventory.yml
all:
  children:
    switches:
      hosts:
        sw1.example.com: {}
        sw2.example.com: {}
      vars:
        ansible_network_os: cisco.ios.ios
        ansible_connection: ansible.netcommon.network_cli
    routers:
      hosts:
        rtr1.example.com: {}
      vars:
        ansible_network_os: cisco.ios.ios
```

```bash
ansible-inventory -i inventory.yml --graph
ansible-inventory -i inventory.yml --host sw1.example.com
```

Credentials never live in the inventory. Use `--ask-pass`, an SSH key, or a vaulted
variable file:

```bash
ansible-vault create group_vars/switches/vault.yml
ansible-playbook -i inventory.yml site.yml --ask-vault-pass
```

## Ad-hoc commands

```bash
ansible switches -i inventory.yml -m ansible.netcommon.cli_command -a 'command="show version"' --limit sw1.example.com
ansible switches -i inventory.yml -m ansible.builtin.ping
ansible all -i inventory.yml -m ansible.builtin.setup -a 'filter=ansible_distribution*'
```

Ad-hoc is for questions, not for changes. Anything that alters a device belongs in a
playbook where it can be reviewed, diffed, and re-run.

## A playbook

```yaml
---
- name: Gather interface state from network devices
  hosts: switches
  gather_facts: false
  connection: ansible.netcommon.network_cli
  vars:
    ansible_network_os: cisco.ios.ios
    ansible_user: "{{ lookup('env', 'NET_USER') }}"
    ansible_password: "{{ lookup('env', 'NET_PASS') }}"

  tasks:
    - name: Run a show command on the device
      ansible.netcommon.cli_command:
        command: show ip interface brief
      register: show_out

    - name: Save the output next to the inventory
      ansible.builtin.copy:
        content: "{{ show_out.stdout }}"
        dest: "./{{ inventory_hostname }}.interfaces.txt"
        mode: "0644"
      delegate_to: localhost
      run_once: false
```

`register` captures the result; `stdout` is the part you usually want. `delegate_to:
localhost` runs the task on the controller — that is what `local_action` used to mean.

## Configuration with a diff

```yaml
- name: Push configuration lines and show the diff
  hosts: switches
  gather_facts: false
  tasks:
    - name: Apply configuration
      cisco.ios.ios_config:
        lines:
          - interface Loopback0
          - description managed-by-ansible
        save_when: changed
      register: cfg

    - name: Report what changed
      ansible.builtin.debug:
        msg: "{{ cfg.diff }}"
      when: cfg.changed
```

Resource modules (`ios_config`, `ios_interfaces`, `ios_l3_interfaces`) want a
declarative state, not a list of CLI lines. Where a resource module exists, prefer it:
it is idempotent, and `--check` becomes meaningful.

## Loops, conditionals, handlers

```yaml
- name: Configure VLANs
  hosts: switches
  gather_facts: false
  vars:
    vlans:
      - { id: 10, name: users }
      - { id: 20, name: voice }

  tasks:
    - name: Create VLANs
      cisco.ios.ios_vlans:
        config:
          - vlan_id: "{{ item.id }}"
            name: "{{ item.name }}"
        state: merged
      loop: "{{ vlans }}"
      loop_control:
        label: "vlan {{ item.id }}"

    - name: Only touch production devices
      ansible.builtin.debug:
        msg: production device
      when: inventory_hostname is search('prod')

    - name: Validate addresses before applying
      ansible.builtin.assert:
        that:
          - item.network | ansible.utils.ipaddr('network') is truthy
        fail_msg: "{{ item.network }} is not a valid network"
      loop: "{{ ranges }}"
```

`loop` with `label` keeps output readable. `when` evaluates per host; `run_once`
executes once for the whole play, which matters when the task is a report rather than
a change.

## Check mode and diffs

```bash
ansible-playbook -i inventory.yml site.yml --check --diff
ansible-playbook -i inventory.yml site.yml --limit sw1.example.com
ansible-playbook -i inventory.yml site.yml --step            # confirm each task
```

Not every network module supports check mode; those that do not will report
`skipped`. Treat a playbook that cannot run `--check` as a playbook you cannot
review.

## Secrets

```bash
ansible-vault encrypt group_vars/switches/vault.yml
ansible-vault view group_vars/switches/vault.yml
ansible-vault edit group_vars/switches/vault.yml
```

Commit encrypted vault files; never commit plaintext. `no_log: true` on a task keeps
secrets out of the log, but it also hides the failure you need to debug — use it on
the tasks that actually touch credentials, not as a blanket setting.

## Lint and test

```bash
ansible-lint site.yml
ansible-playbook --syntax-check -i inventory.yml site.yml
molecule test                      # for collections and roles
```

`syntax-check` proves the YAML parses and the modules resolve; `ansible-lint` catches
the practices that bite later (command instead of module, missing `changed_when`).

## Traps worth remembering

- `command` and `shell` always report changed: add `changed_when` or use a module.
- `gather_facts: true` against a network device is slow or fails; network plays set it
  to `false`.
- A loop over 500 devices with `serial` unset runs them all at once — use `serial: 25`.
- Vault passwords on the command line land in history; prefer a vault password file
  with mode 0600.
- Idempotence is the whole point: a playbook that reports `changed` on every run is a
  script wearing Ansible's clothes.
