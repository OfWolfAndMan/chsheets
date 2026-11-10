### Copy stdout to a file

```yaml
- tasks:
    - raw: "{{ show arp }}"
      register: show
      #Puts output of the show command into the "show variable"
    - local_action: > #Represents multiline task. Local action denotes it being done on the ansible host
        copy content={{ show.stdout }}
             dest={{ inventory_hostname }}.arp.txt
      run_once: true #Used to prevent multiple runs if running on localhost but the task falls under multiple host
```

### Error handling

```yaml
- hosts: ios
  tasks:
  - ios_command:
      commands: show version
      provider: "{{ cli }}"
    register: result
  - fail: msg="Wrong Cisco IOS version"
    when: "not ('Version {{ version }}' in result.stdout[0])"
```

### Preventing runs when certain variables are not defined

```yaml
- name: Generate device configs
  connection: local
  tasks:
  - assert:
      that:
        - syslog_host is defined
        - snmp_host is defined
      msg: One of the NMS servers is not defined
```

### Rescue block

```yaml
- hosts: ios
  tasks:
  - block:
      - list of actions
    rescue:
      - actions to execute on failure
    always:
      - actions to execute at the end no matter what.
```

### File management (Relevant to ansible host on localhost)

```yaml
- hosts: localhost
  connection: local
  tasks:
  - file: path=version_report.txt state=absent
  - file: path=version_report.txt state=touch
  #Additional file options - (file, directory, link, hardlink)
```

### Adding lines to a text file

```yaml
- lineinfile:
    dest: version_report.txt
    regexp: "{{ inventory_hostname }}"
    line: "{{ inventory_hostname }}" has wrong IOS version"
  when: "not ('Version {{ version }}' in result.stdout[0])"
```

### Adding blocks to text files

```yaml
- blockinfile:
    dest: results.txt
    marker: "### { mark } {{ inventory_hostname }}"
    block: result.stdout[0]

### Marker - Text identifying the begin/end of a block
### Block - Block content
### Backup - Create backup copy before modification
### Create - Create a file if it doesn't exist
```

### Assembling multiple files into an output file

```yaml
- assemble:
    src: directory_path
    regex: file_matching_pattern (Optional)
    dest: file_path
### remote_src: true - Used if source file is on the hose
```

### Summary Report: Configuration changes

```yaml
- name: Document changes
  copy:
    content: |
      **************************************************
      {{ component }} changes on {{ inventory_hostname }}
      **************************************************
      {% for line in changes.commands %}
      {{ line }}
      {% endfor %}
    dest: "{{ configures }}/changes/
           {{ inventory_hostname }}.{{ component }}.changes"
  delegate_to: localhost
```

### Simple loop for a list

```yaml
- hosts: ios
  tasks:
  - name: "Ping targets from IOS devices"
    ios_command: commands="ping {{ item }}"
    register: results
    with_items: "{{ ping_target }}"
```

### Simple loop for a dict

```yaml
- hosts: ios
  tasks:
  - name: "Ping targets from IOS devices"
    ios_command: commands="show standby neigh {{ item.key }}"
    register: results
    with_dict: "{{ interfaces }}"
```

### Loop until a condition is met

```yaml
- hosts: ios
  tasks:
  - name: "Check interface status"
    ios_command: commands="show interface dialer 1"
    register: ifstate
    until: ifstate.stdout[0].find("protocol is up" ) > 0
    retries: 5
    delay: 10
```

### Select subset of elements from a list

```yaml
name: |
  vlans|selectattr('id','equalto',target_vlan)|
  map)attribute='name')|first

vlans:
  - { id: "100", name: "mgmt", subnet: "198.51.100.0/24"}
  - { id: "101", name: "web", subnet: "192.0.2.0/24"}
```

### Extract data from text printout

```yaml
- ios_command:
    commands: "show ip interface brief | exclude Interface"
  register: printout
- set_fact:
    intf: |
      {{ printout.stdout_lines[0] |
         map('regex_findall','^([A-Za-z]+[0-9./]+)') |
         map('join') | list }}
# regex_findall performs regex match and returns a list of matches
# join within a map merges inner lists into strings
# map is a generator
```

### Overwriting the changed flag (In case you don't want) to represent something as "changed" after completion

```yaml
- hosts: all
  tasks:
  - file: path={{ build_dir }} state=directory
    run_once: yes
    changed_when: false
```

### Check mode for a dry run

```yaml
- ios_config:
    src: "config file.config"
  register: changes
- copy:
    content: |
      {% if ansible_check_mode %}
      === Running in check mode ===
      {% endif %}
      {% for line in changes.commands %}
      {{ line }}
      {% endfor %}
    dest: "destination file.config"
  check_mode: yes
```

### Prepopulate SSH known_hosts file

<https://github.com/ipspace/NetOpsWorkshop/tree/master/tools/ssh-keys>

### Authorize connection (Enable mode)

```yaml
- tasks:
  - ios_command:
      commands: show arp
      authorize: yes
```

### Build config snippets

```yaml
- name: BUILD CONFIG SNIPPETS
  template:
    src: "{{ item }}"
    dest: "./outputs/{{ inventory_hostname }}/partials/{{ item | basename | splitext | first }}.cfg"
  with_first_found:
    - files: "{{ file }}"
      paths:
        - "./templates/{{ os }}/{{ platform }}/{{ family }}/"
        - "./templates/{{ os }}/{{ platform }}/main/"
        - "./templates/{{ os }}/main/"
```

### Get Hardware inventory of devices

```yaml
- name: GET FACTS
    hosts: ROUTER
    gather_facts: false
    vars:
        creds:
            username: admin
            password: admin

    tasks:
        - name: create file 
            file:    
              dest: /etc/ansible/backup/inventory.json
              state: touch 
            delegate_to: localhost 
            run_once: true
        - ios_facts:
            gather_subset:
              - hardware
            register: facts
    
        - name: append 
            lineinfile: 
              path: /tmp/foo 
              line: "{{ output }}" 
              insertafter: EOF 
            delegate_to: localhost
```

### Get additional facts from network router

```yaml
- name: GET FACTS
  hosts: R1
  vars:
    creds:
      host: 203.0.113.1
      username: admin
      password: admin
   
  tasks:
    - ios_facts:
        provider: "{{ creds }}"
      tags: facts_only

    - debug:
        var: ansible_net_model
        var: ansible_net_version
        var: ansible_net_hostname
        var: ansible_net_serialnum
        register: config
    - name: save output to /etc/ansible/backups 
        copy: content="{{ config.stdout[0] }}" dest=/etc/ansible/backups/show_run_{{ inventory_hostname }}.txt"
```
