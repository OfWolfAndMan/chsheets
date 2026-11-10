**Remove all docker containers created on your machine**

```bash
for var in $(docker ps -a | awk 'NR!=1{print$1}'); do docker rm $var; done
```

**Snapshot a container**

```bash
docker ps (Show docker containers that have been stopped with -f "status=exited")
docker commit `<container id>` `<snapshot name>`
docker run -t -i `<snapshot name>` `<command in container>` -p `<port number>` -d
```

**Build multi-container applications**

```bash
docker-compose build up
```

**Stop and remove docker compose containers**

```bash
docker-compose down
```

**Verify Docker installed correctly**

```bash
docker run hello-world
```

**Show docker images (Already built)**

```bash
docker images
```

**Build Docker image**

```bash
docker build -t `<image-name>` `<Dockerfile path>`
```

**Rebuild Docker Image (Docker Compose)**

```bash
docker-compose build
```

**Remove snapshot**

```bash
docker rmi `<snapshot name>`
```

**Cleanup dangling docker images**

```bash
docker rmi -f $(docker images -qf dangling=true)
```

**Rename docker container**

```bash
docker rename `<current_name>` `<new_name>`
```

**Start container using imagename**

```bash
docker start $(docker ps -a | grep `<image_name>` | awk '{ print $1 }')
```

**Stopping a docker instance/compose**

```bash
docker stop `<container id>`
docker-compose stop (Same directory as docker compose)
```

**Cleanup dangling containers**

```bash
docker rmi -f $(docker images -qf dangling=true)
```

**Run a command inside of the container**

```bash
docker exec -it $(docker container ls -l --format "{{.Names}}") \
   `<insert shell command here>`
```

**Enter shell**

```bash
docker exec -it `<image id>`
```

**Get Docker container IP**

```bash
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' `<container-name-or-id>`
```

**Get details for a specific container**

```bash
docker inspect `<container id>`
```

**Look at properties of container**

```bash
docker container inspect `<Container name>`
```

**Display current networks**

```bash
docker network ls
```

**Look at network properties for a particular network**

```bash
docker network inspect bridge
```

**Stop all docker containers running**

```bash
docker stop $(docker ps -a -q)
```

**Remove all docker containers**

```bash
docker rm $(docker ps -a -q)
```

### Docker File example

**Base image**

```dockerfile
FROM python:`<Python version>`
MAINTAINER Example Maintainer `<dev@example.com>`

ENV INSTALL_PATH /`<install path name>`
```

**Copies local files into the container**

```dockerfile
COPY requirements.txt requirements.txt
```

**Command ran when the image is started**

```dockerfile
ENTRYPOINT ["ping"]
```

**Command arguments passed to ping**

```dockerfile
CMD ["8.8.8.8", "-c", "3"]
```

**Display logs of container in docker**

```bash
docker logs `<container-id>`
```

**Valid Linux shell command**

```dockerfile
RUN pip install -r requirements.txt
```

**Copies current directory into Docker image**

```text
COPY ..
```

**Listen on a specific network port on docker (Default TCP)**

```dockerfile
EXPOSE `<port>` | `<port>`/`<protocol>`

CMD gunicorn -b 0.0.0.0:`<port number>` --access-logfile
```

**Exporting a container**

```bash
docker export `<container_name>` | gzip `<container_export_name>`.gz
```

**Importing a container**

```bash
scp `<container_export_name>`.gz `<docker_user>`@`<docker_ip>`:/home/`<docker_user>`
zcat `<container_export_name>`.gz | docker import - `<container_name>`
docker run -i -t `<container_name>` /bin/bash
```

**Run image**

```bash
docker run -d -p `<port:port>` `<image name>` `<image id>`
```

### Run specific container instances

**Artifactory**

```bash
docker run --name artifactory -d -p 8081:8081 docker.bintray.io/jfrog/artifactory-cpp-ce:latest
```
