**Remove all docker containers created on your machine**

```
for var in $(docker ps -a | awk 'NR!=1{print$1}'); do docker rm $var; done
```

**Snapshot a container**
```
docker ps (Show docker containers that have been stopped with -f "status=exited")
docker commit `<container id>` `<snapshot name>`
docker run -t -i `<snapshot name>` `<command in container>` -p `<port number>` -d
```

**Build multi-container applications**
```
docker-compose build up
```

**Stop and remove docker compose containers**
```
docker-compose down
```


**Verify Docker installed correctly**
```
docker run hello-world
```

**Show docker images (Already built)**
```
docker images
```

**Build Docker image**
```
docker build -t `<image-name>` `<Dockerfile path>`
```

**Rebuild Docker Image (Docker Compose)**
```
docker-compose build
```

**Remove snapshot**
```
docker rmi `<snapshot name>`
```

**Cleanup dangling docker images**

```
docker rmi -f $(docker images -qf dangling=true)
```

**Rename docker container**

```
docker rename `<current_name>` `<new_name>`
```

**Start container using imagename**

```
docker start $(docker ps -a | grep `<image_name>` | awk '{ print $1 }')
```

**Stopping a docker instance/compose**

```
docker stop `<container id>`
docker-compose stop (Same directory as docker compose)
```

**Cleanup dangling containers**

```
docker rmi -f $(docker images -qf dangling=true)
```

**Run a command inside of the container**

```
docker exec -it $(docker container ls -l --format "{{.Names}}") \
   `<insert shell command here>`
```

**Enter shell**

```
docker exec -it `<image id>`
```

**Get Docker container IP**

```
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' `<container-name-or-id>`
```

**Get details for a specific container**

```
docker inspect `<container id>`
```

**Look at properties of container**

```
docker container inspect `<Container name>`
```

**Display current networks**

```
docker network ls
```

**Look at network properties for a particular network**

```
docker network inspect bridge
```

**Stop all docker containers running**

```
docker stop $(docker ps -a -q)
```

**Remove all docker containers**

```
docker rm $(docker ps -a -q)
```

### Docker File example
**Base image**

```
FROM python:`<Python version>`
MAINTAINER John Smith `<john.smith4502@gmail.com>`

ENV INSTALL_PATH /`<install path name>`
```

**Copies local files into the container**

```
COPY requirements.txt requirements.txt
```

**Command ran when the image is started**

```
ENTRYPOINT ["ping"]
```

**Command arguments passed to ping**

```
CMD ["8.8.8.8", "-c", "3"]
```

**Display logs of container in docker**

```
docker logs `<container-id>`
```

**Valid Linux shell command**

```
RUN pip install -r requirements.txt
```

**Copies current directory into Docker image**

```
COPY ..
```

**Listen on a specific network port on docker (Default TCP)**

```
EXPOSE `<port>` | `<port>`/`<protocol>`

CMD gunicorn -b 0.0.0.0:`<port number>` --access-logfile
``` 

**Exporting a container**

```
docker export `<container_name>` | gzip `<container_export_name>`.gz
```

**Importing a container**

```
scp `<container_export_name>`.gz `<docker_user>`@`<docker_ip>`:/home/`<docker_user>`
zcat `<container_export_name>`.gz | docker import - `<container_name>`
docker run -i -t `<container_name>` /bin/bash
```

**Run image**

```
docker run -d -p `<port:port>` `<image name>` `<image id>`
```

### Run specific container instances

**Artifactory**

`docker run --name artifactory -d -p 8081:8081 docker.bintray.io/jfrog/artifactory-cpp-ce:latest`
