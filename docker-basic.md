---
title: Docker
summary: Docker and Compose — images, containers, multi-stage builds, healthchecks
tags: [containers, docker, compose]
tooling: [docker, docker compose, buildx]
verified_on: 2026-11-10
verified_env: Docker 29.9.3, Compose 5.7.0 — CLI and compose config executed; the Dockerfile was reviewed but not built
status: partial
---

# Docker

Verified against Docker 29.9.3 and Compose 5.7.0. The interface in older material —
`docker-compose` as a separate binary — is now a subcommand: `docker compose`. The
hyphenated binary still exists as a compatibility shim, but every command below uses
the plugin form.

## Images

```bash
docker pull alpine:3.21              # always pin a tag that is not :latest in production
docker images                        # local images
docker image inspect alpine:3.21 --format '{{.Id}} {{.Config.Cmd}}'
docker history --no-trunc <image>
docker rmi <image>
docker image prune                   # dangling images only
```

## Containers

```bash
docker run --rm -it alpine:3.21 sh                 # throwaway, interactive
docker run -d --name web -p 8080:80 nginx:1.27     # detached, port published
docker run --rm -v "$PWD":/work -w /work alpine:3.21 ls -la
docker ps                                          # running
docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Image}}'
docker logs -f --tail 50 <container>
docker exec -it <container> sh
docker inspect <container> --format '{{.State.Health.Status}}'
docker stop <container> && docker rm <container>
docker stats --no-stream
```

`--rm` on one-shot containers is not optional housekeeping; it is the difference
between a clean machine and a graveyard of exited containers.

## Ports and networking

```bash
docker run -d --name web -p 127.0.0.1:8080:80 nginx:1.27   # loopback only
docker network ls
docker network create appnet
docker run -d --name api --network appnet alpine:3.21 sleep 3600
docker network inspect appnet --format '{{range .Containers}}{{.Name}} {{end}}'
```

Name resolution works by container name inside a user-defined network; the default
bridge network does not provide it. Publishing to `127.0.0.1` instead of `0.0.0.0`
is the difference between a dev service and an exposed one.

## Volumes

```bash
docker volume create appdata
docker run --rm -v appdata:/data alpine:3.21 sh -c 'echo hi > /data/x && cat /data/x'
docker volume ls
docker volume inspect appdata
docker volume rm appdata
```

Bind mounts (`-v /host/path:/container/path`) share the host filesystem; named volumes
are managed by Docker and survive `docker rm`. Data written into a container's own
filesystem dies with the container.

## Images from a Dockerfile

```dockerfile
FROM python:3.13-slim AS build
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.13-slim
WORKDIR /app
COPY --from=build /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY . .
RUN useradd --create-home appuser
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/health')"
CMD ["python", "-m", "http.server", "8000"]
```

```bash
docker build -t demo:0.1 .
docker build --build-arg VERSION=0.1 -t demo:0.1 .
docker run --rm demo:0.1
```

Multi-stage builds keep compilers and build caches out of the shipped image. `USER`
before `CMD` means the process does not run as root; `HEALTHCHECK` is what lets an
orchestrator tell "running" from "working".

`.dockerignore` decides what the build context is — the file that most often makes a
build slow and an image fat:

```text
.git
.venv
__pycache__
*.log
node_modules
```

## Compose

```yaml
# compose.yaml
services:
  web:
    image: nginx:1.27
    ports:
      - "127.0.0.1:8080:80"
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./site:/usr/share/nginx/html:ro

  db:
    image: postgres:17
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/db_password
    secrets:
      - db_password
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  pgdata:

secrets:
  db_password:
    file: ./db_password.txt
```

```bash
docker compose up -d
docker compose ps
docker compose logs -f web
docker compose exec web sh
docker compose config          # validate and see the resolved file
docker compose down            # keeps volumes
docker compose down -v         # deletes volumes too
```

`depends_on` with `condition: service_healthy` waits for the healthcheck rather than
merely for the container to start — the difference between a service that works and
one that races its database on every restart.

Secrets belong in `secrets:` or the environment of the process, never baked into the
image or committed to `compose.yaml`.

## Cleanup

```bash
docker system df                     # what is actually taking space
docker container prune
docker image prune -a                # every image no container uses
docker builder prune
docker system prune -a --volumes     # nuclear: removes unused volumes too
```

`--volumes` on `system prune` deletes data you may not have backed up. Read the
prompt before typing `y`.

## Traps worth remembering

- `latest` is a tag, not a version: a rebuild can change behaviour with no diff in
  your Dockerfile.
- A container that exits immediately is usually a foreground process problem — check
  `docker logs`, not the exit code.
- Ports published to `0.0.0.0` are reachable from the network; use `127.0.0.1:` for
  anything local-only.
- Image size is a security property as well as a speed one: fewer packages, fewer CVEs.
- `docker exec` into a container to fix something is a diagnostic, not a deployment.
