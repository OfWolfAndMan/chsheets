# Elasticsearch
## Getting Started

All nodes:

```Shell
sudo rpm --import https://artifacts.elastic.co/GPG-KEY-elasticsearch
sudo curl -O https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-7.6.0-x86_64.rpm
sudo rpm --install elasticsearch-7.6.0-x86_64.rpm

sudo systemctl daemon-reload
sudo systemctl enable elasticsearch
```


## Configuring the cluster

Master node -

*/etc/elasticsearch/elasticsearch.yml*

```Shell
cluster.name: playground
node.name: master-1
network.host: [_local_, _site_]
discovery.seed_hosts: ["{master_private ip}"]
cluster.initial_master_nodes: ["master-1"]
node.master: true
node.data: false
node.ingest: true
node.ml: false
```

*/etc/elasticsearch/jvm.options*

```Shell
-Xms768m
-Xmx768m
```

Data node 1 -

*/etc/elasticsearch/elasticsearch.yml*

```Shell
cluster.name: playground
node.name: data-1
network.host: [_local_, _site_]
discovery.seed_hosts: ["172.31.116.224"]
cluster.initial_master_nodes: ["master-1"]
node.master: false
node.data: true
node.ingest: false
node.ml: false
```

Data node 2 -

*/etc/elasticsearch/elasticsearch.yml*

```Shell
cluster.name: playground
node.name: data-2
network.host: [_local_, _site_]
discovery.seed_hosts: ["172.31.116.224"]
cluster.initial_master_nodes: ["master-1"]
node.master: false
node.data: true
node.ingest: false
node.ml: false
```

## Starting things up

```Shell
systemctl start elasticsearch
systemctl status elasticsearch
less /var/log/elasticsearch/playground.log
curl localhost:9200
curl localhost:9200/_cat/{endpoint}
```


## Encryption

*mkdir /etc/elasticsearch/certs*

Master node -

```Shell
/usr/share/elasticsearch/bin/elasticsearch-certutil cert --name playground --out /etc/elasticsearch/certs/playground
cp /etc/elasticsearch/certs/playground /tmp/
cd /tmp/
chown cloud_user:cloud_user playground
exit
```

Move to other nodes:

```Shell
scp playground {data-1 private ip}/tmp
scp playground {data-2 private ip}/tmp
```

Data nodes -
```Shell
cp /tmp/playground /etc/elasticsearch/certs/
```

All nodes -
```Shell
cd /etc/elasticsearch/certs
chmod 640 playground
```

*/etc/elasticsearch/elasticsearch.yml*

```Shell
#
## ---------------------------------- Security -----------------------------------
#
xpack.security.enabled: true
xpack.security.transport.ssl.enabled: true
xpack.security.transport.ssl.verification_mode: certificate
xpack.security.transport.ssl.keystore.path: certs/playground
xpack.security.transport.ssl.truststore.path: certs/playground
```

```Shell
systemctl restart elasticsearch

/usr/share/elasticsearch/bin/elasticsearch-setup-passwords interactive
```