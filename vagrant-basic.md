### Install vmware Fusion/Workstation plugins (Requires license)
```Shell
vagrant plugin install vagrant-vmware-fusion
vagrant plugin install vagrant-vmware-workstation
```

### Install plugin for SCP
```Shell
vagrant plugin install vagrant-scp
```

### Copy file to vagrant guest (Loads to home directory)
```Shell
vagrant scp <local_file_or_dir> <vm_name>:<filename>
```

### Startup Vagrant
```Shell
vagrant up
```

### Gracefully shutdown Vagrant
```Shell
vagrant halt
```

### Delete Vagrant VM
```Shell
vagrant destroy
```