### Install Salt

```Shell
sudo systemctl start salt-master
```

### Without systemd

```Shell
sudo salt-master -d
sudo systemctl start salt-proxy@device1
```

### Without systemd

```Shell
sudo salt-proxy -d --proxyid device1
```

### Accept for Salt-key initially

Proxy minion for network devices

### CLI syntax

```Shell
sudo salt <target> <function> [<arguments>]
```

### Examples

```Shell
sudo salt <hostname> net.load.config <path>
sudo salt <hostname> net.load_template [<https:// | salt:// | s3:// | ftp://>]<path>
```

## Common Arguments

### Dry run mode (Argument)

```Shell
test=True
```

### Format into JSON

```Shell
pretty=True
```

## Recommendations

Separate data (Pillar) from automation logic (SLS)

## File Locations

### Salt proxy minion

/var/log/salt/proxy