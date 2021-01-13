### Show interfaces
```Shell
net show interface
```

### Enter quagga command line
```Shell
sudo vtysh
```

### Enable OSPF/BGP
```Shell
nano /etc/frr/daemons
#Zebra MUST be set to yes
```

### Enable the service (After options set to yes)
```Shell
sudo systemctl enable frr.service
sudo systemctl start frr.service
```

### Configure OSPF (Must be enabled in FRR)
```Shell
net add ospf router-id <router-id>
net add ospf network <network>/<mask> area <area id>
net add ospf passive-interface <interface>
net add interface <interface> ospf area <area id> (Can only be used if network statement not set)
```