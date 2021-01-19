## CAVEATS ON CLONING LINUX VMs

- Change IP if static
- Change hostname resolution in /etc/hosts file
- Change services as needed

## General Use

### List all processes
```Shell
ps -aux
```

### Backup things locally
```Shell
rsync {source} {destination}
```

### Create a cronjob
```Shell
crontab -e
```

### Make intermediary directory with multiple
### subdirectories
```Shell
mkdir -p <TopDir>/{<SubDir1>,<SubDir2>}
```

## ZIP FILES

### Create tar.gz file
```Shell
tar -czvf {output.tgz} {folder}
```

### Extract tar.gz file
```Shell
tar -xzvf {input.tgz} {path}
```

### Create zip files
```Shell
zip -r {output.zip} {folder}
```

### Extract zip files
```Shell
unzip {input.zip} -d {folder}
```

### Start a service at startup
```Shell
systemctl enable <service>
```

### Show spaces/tabs in a file
```Shell
cat -e -t -v makefile_name
```



## COMMON FILE LOCATIONS

### Update hostname
```Shell
/etc/hostname
```

### Update IP configuration
```Shell
/etc/network/interfaces
```

### Modify hosts file
```Shell
/etc/hosts
```

## NETWORK

### Get IPs and interfaces
```Shell
ifconfig
```

### Restart daemon after changing IP settings
```Shell
/tc/init.d/networking restart
```

### Display all network devices available
```Shell
lspci
```

### Restart Network Interfaces
- Debian: 
  ip addr flush interface-name
  systemctl restart networking.service

### Display open ports with programs
```Shell
lsof -i -P
```

### Enable routing
```Shell
sysctl net.ipv4.conf.all.forwarding=1
sysctl net.ipv6.conf.all.forwarding=1
```

### Flush NAT rules
```Shell
iptables -t nat -F
```

### Configure SNAT (Static IP)
```Shell
iptables -t nat -A POSTROUTING -o <Interface name> -j SNAT --to <Interface IP>
```

### Configure SNAT (Dynamic IP)
```Shell
iptables -t nat -A POSTROUTING -o <Interface name> -j MASQUERADE
```

### Configure DNAT (IP only)
```Shell
iptables -t nat -A PREROUTING -d <Original IP> -j DNAT --to-destination <New IP>
```

### Configure DNAT (IP/port)
```Shell
iptables -t nat -A PREROUTING -p <TCP/UDP> -d <Original IP> --dport <Original Port> -j DNAT \ --to-destination <New IP>:<New port>
```

## USEFUL PROGRAMS

- Firejail: A useful sandboxing application
  https://github.com/netblue30/firejail

### Check some logs

```
sudo tail -f /var/log/apache2/access.log
sudo less +F  /var/log/apache2/access.log
```

### Checking disk partitions

```Shell
$ sudo fdisk -l
Disk /dev/sda: 500.1 GB, 500107862016 bytes
255 heads, 63 sectors/track, 60801 cylinders, total 976773168 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk identifier: 0x30093008
   Device Boot      Start         End      Blocks   Id  System
/dev/sda1   *          63   146801969    73400953+   7  HPFS/NTFS/exFAT
/dev/sda2       146802031   976771071   414984520+   f  W95 Ext'd (LBA)
/dev/sda5       146802033   351614654   102406311    7  HPFS/NTFS/exFAT
/dev/sda6       351614718   556427339   102406311   83  Linux
/dev/sda7       556429312   560427007     1998848   82  Linux swap / Solaris
/dev/sda8       560429056   976771071   208171008   83  Linux
Disk /dev/sdb: 4048 MB, 4048551936 bytes
54 heads, 9 sectors/track, 16270 cylinders, total 7907328 sectors
Units = sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disk identifier: 0x0001135d
   Device Boot      Start         End      Blocks   Id  System
/dev/sdb1   *        2048     7907327     3952640    b  W95 FAT32
```

```Shell
$ df -h
Filesystem      Size  Used Avail Use% Mounted on
/dev/sda6        97G   43G   49G  48% /
none            4.0K     0  4.0K   0% /sys/fs/cgroup
udev            3.9G  8.0K  3.9G   1% /dev
tmpfs           799M  1.7M  797M   1% /run
none            5.0M     0  5.0M   0% /run/lock
none            3.9G   12M  3.9G   1% /run/shm
none            100M   20K  100M   1% /run/user
/dev/sda8       196G  154G   33G  83% /media/13f35f59-f023-4d98-b06f-9dfaebefd6c1
/dev/sda5        98G   37G   62G  38% /media/4668484A68483B47
```

```Shell
$ lsblk
NAME   MAJ:MIN RM   SIZE RO TYPE MOUNTPOINT
sda      8:0    0 465.8G  0 disk
├─sda1   8:1    0    70G  0 part
├─sda2   8:2    0     1K  0 part
├─sda5   8:5    0  97.7G  0 part /media/4668484A68483B47
├─sda6   8:6    0  97.7G  0 part /
├─sda7   8:7    0   1.9G  0 part [SWAP]
└─sda8   8:8    0 198.5G  0 part /media/13f35f59-f023-4d98-b06f-9dfaebefd6c1
sdb      8:16   1   3.8G  0 disk
└─sdb1   8:17   1   3.8G  0 part
sr0     11:0    1  1024M  0 rom
```

```Shell
$ lsblk -o PATH,SIZE,RO,TYPE,MOUNTPOINT,UUID,MODEL
PATH         SIZE RO TYPE MOUNTPOINT                   UUID                                 MODEL
/dev/loop0  96.5M  1 loop /snap/core/9436
/dev/loop1 229.6M  1 loop /snap/atom/257
/dev/loop2    55M  1 loop /snap/core18/1880
/dev/loop3  54.8M  1 loop /snap/gtk-common-themes/1502
/dev/loop4 156.2M  1 loop /snap/chromium/1213
/dev/loop5    55M  1 loop /snap/core18/1754
/dev/loop6  62.1M  1 loop /snap/gtk-common-themes/1506
/dev/loop7 230.6M  1 loop /snap/atom/258
/dev/loop8 158.4M  1 loop /snap/chromium/1229
/dev/loop9    97M  1 loop /snap/core/9665
/dev/sda   465.8G  0 disk                                                                   Samsung_Portable_SSD_T5
/dev/sda1    420G  0 part                              757dcceb-3e17-4ca8-9ba1-b0cf68fb0134
/dev/sdb   111.8G  0 disk                                                                   Samsung_SSD_840_EVO_120GB
/dev/sdb1   95.4G  0 part /                            19d84ceb-8046-4f8d-a85a-cda49515d92c
/dev/sdc   111.8G  0 disk                                                                   Samsung_SSD_850_EVO_120GB
/dev/sdc1   95.8G  0 part                              f41b21a7-e8be-48ac-b10d-cad641bf709b
$
```

```Shell
$ sudo blkid
/dev/sda1: UUID="5E38BE8B38BE6227" TYPE="ntfs"
/dev/sda5: UUID="4668484A68483B47" TYPE="ntfs"
/dev/sda6: UUID="6fa5a72a-ba26-4588-a103-74bb6b33a763" TYPE="ext4"
/dev/sda7: UUID="94443023-34a1-4428-8f65-2fb02e571dae" TYPE="swap"
/dev/sda8: UUID="13f35f59-f023-4d98-b06f-9dfaebefd6c1" TYPE="ext4"
/dev/sdb1: UUID="08D1-8024" TYPE="vfat"
```

### Ping sweep

```
#!/bin/bash

for ip in $(seq 1 254); do
        ping -c 1 192.168.1.$ip | grep "bytes from" | cut -d " " -f 4 | cut -d ":" -f 1 &
done
```

