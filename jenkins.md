---
title: Jenkins
summary: Jenkins — install, agents, declarative pipelines, libraries, credentials
tags: [ci, jenkins, groovy]
tooling: [jenkins, java, docker]
verified_on: null
verified_env: null
status: unverified
---

# Jenkins

Consolidated from the old `jenkins-basic`, `jenkins-pipeline-execution` and
`jenkinsfile-example` sheets, which between them were 740 lines of notes with the code
unfenced. Nothing here has been executed against a Jenkins instance since 2021 —
`status: unverified` says so plainly.

Jenkins LTS at the time of writing is 2.580.x, tested on JDK 21 and 25. The three
changes most likely to break a five-year-old tutorial: pipeline syntax is declarative
by default, plugin installation is scriptable, and `Jenkinsfile` review via
multibranch pipelines is standard practice rather than an advanced topic.

## Install

```bash
# container: the fastest reproducible lab
docker run -d --name jenkins -p 8080:8080 -p 50000:50000 \
  -v jenkins_home:/var/jenkins_home \
  jenkins/jenkins:lts-jdk21

docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword
```

```text
# LTS on Debian/Ubuntu, from the project repository
https://pkg.jenkins.io/debian-stable/
```

Then: install suggested plugins, create the admin user, and *stop using the initial
admin password*.

## Command line

```bash
java -jar jenkins-cli.jar -s http://localhost:8080/ -auth <user>:<api-token> list-jobs
java -jar jenkins-cli.jar -s http://localhost:8080/ build <job> -f
java -jar jenkins-cli.jar -s http://localhost:8080/ console <job> <build> | tail -50
```

```groovy
// script console: http://<host>/script — admin only, arbitrary Groovy
Jenkins.instance.getAllItems(Job).each { println it.fullName }
```

The script console is remote code execution by design. Restrict it, and never leave a
session open to it.

## Declarative pipeline

```groovy
pipeline {
    agent any

    options {
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        buildDiscarder(logRotator(numToKeepStr: '30'))
        disableConcurrentBuilds()
    }

    environment {
        REGISTRY = 'registry.example.com'
    }

    parameters {
        choice(name: 'ENVIRONMENT', choices: ['staging', 'prod'], description: 'target')
        booleanParam(name: 'DRY_RUN', defaultValue: true, description: 'skip the deploy')
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Test') {
            steps {
                sh 'make test'
            }
            post {
                always { junit 'reports/**/*.xml' }
            }
        }

        stage('Build image') {
            when { branch 'main' }
            steps {
                sh 'docker build -t $REGISTRY/app:$BUILD_NUMBER .'
            }
        }

        stage('Deploy') {
            when {
                allOf { branch 'main'; expression { !params.DRY_RUN } }
            }
            steps {
                withCredentials([usernamePassword(
                        credentialsId: 'registry',
                        usernameVariable: 'USER',
                        passwordVariable: 'PASS')]) {
                    sh 'echo "$PASS" | docker login $REGISTRY -u "$USER" --password-stdin'
                    sh 'docker push $REGISTRY/app:$BUILD_NUMBER'
                }
            }
        }
    }

    post {
        success { echo 'build succeeded' }
        failure {
            mail to: 'devops@example.com',
                 subject: "FAILED: ${env.JOB_NAME} #${env.BUILD_NUMBER}",
                 body: "${env.BUILD_URL}"
        }
        always { cleanWs() }
    }
}
```

Points that matter more than they look:

- `when { branch 'main' }` requires a multibranch pipeline. In a plain pipeline job
  it silently evaluates against nothing useful.
- `disableConcurrentBuilds()` prevents two deploys racing over the same environment.
- `timestamps()` is what makes a hung build diagnosable.
- Credentials come from `withCredentials`, never from a plain `environment` block.

## Scripted pipeline

Declarative is a DSL over the scripted model; when declarative cannot express the
logic, drop to scripted inside a `script` block or write the whole pipeline scripted.

```groovy
node('linux') {
    try {
        stage('Checkout') { checkout scm }
        stage('Test')       { sh 'make test' }
        currentBuild.result = 'SUCCESS'
    } catch (err) {
        currentBuild.result = 'FAILURE'
        throw err
    } finally {
        stage('Cleanup') { cleanWs() }
        junit 'reports/**/*.xml'
    }
}
```

```groovy
// loops and parallel branches
def targets = ['api', 'worker', 'web']
def branches = [:]
targets.each { t ->
    branches[t] = { stage("build-${t}") { sh "make ${t}" } }
}
parallel branches
```

## Agents

```groovy
pipeline {
    agent { label 'linux && docker' }
    stages {
        stage('Build') { steps { sh 'make' } }
        stage('Windows') {
            agent { label 'windows' }
            steps { bat 'build.cmd' }
        }
    }
}
```

A node label is a contract: if no agent carries it, the build queues forever rather
than failing. `built-in` — the controller — should not run jobs.

```bash
# add an inbound agent: Manage Jenkins > Nodes > New Node
java -jar agent.jar -jnlpUrl http://<host>:8080/computer/<name>/jenkins-agent.jnlp \
  -secret <secret> -workDir /var/jenkins
```

## Triggers

```groovy
triggers {
    pollSCM('H/5 * * * *')          // only if webhooks are impossible
    cron('H 3 * * *')               // nightly build
}
```

Webhooks from the SCM beat polling: polling burns API quota and delays. GitLab and
GitHub both have a Jenkins integration that triggers on push and on merge request.

## Shared libraries

```text
vars/log.groovy                 # global step, callable as log()
src/org/example/Utils.groovy    # classes, imported in pipelines
resources/                      # non-Groovy files, loaded with libraryResource
```

```groovy
@Library('pipeline-utils@main') _

pipeline {
    agent any
    stages {
        stage('Build') {
            steps { log.info('starting') }
        }
    }
}
```

Pin the ref (`@main`, `@v1.2.0`): an unpinned library means an unrelated commit can
change every pipeline in the organisation.

## Jenkins configuration as code

```yaml
# jenkins.yaml, applied by the configuration-as-code plugin
jenkins:
  systemMessage: "Managed by JCasC"
  numExecutors: 0
  securityRealm:
    local:
      allowsSignup: false
credentials:
  system:
    domainCredentials:
      - credentials:
          - usernamePassword:
              id: registry
              username: deploy
              password: "${REGISTRY_PASSWORD}"
```

Clicking configuration into the UI is configuration nobody can review. JCasC puts it
in git, where a change is a diff.

## Plugins

```bash
# from the CLI jar
java -jar jenkins-cli.jar -s http://localhost:8080/ -auth <user>:<token> \
  install-plugin git workflow-aggregator docker-workflow
java -jar jenkins-cli.jar -s http://localhost:8080/ safe-restart
```

Pin plugin versions and keep a `plugins.txt` in the image or repository. Jenkins
without pinned plugins is a system whose behaviour changes on Tuesday because
somebody clicked update.

## Troubleshooting order

1. `console` output of the failing build — the actual command and its stderr.
2. `http://<host>/systemInfo` — environment, JVM, disk space.
3. `http://<host>/manage` warnings — plugin and configuration problems Jenkins knows about.
4. `java -jar jenkins-cli.jar who-am-i` with the credential the job uses — permission
   problems usually live here.
5. `Jenkins.instance.getAllItems(Job)` in the script console to find the job whose
   definition nobody remembers writing.

## Traps worth remembering

- A pipeline that reports success while the tests did not run: check that `junit`
  found files, and that the step is not inside a `catch`.
- Credentials interpolated into `sh` strings leak into logs; use `withCredentials` and
  single-quoted shell strings so the value is not echoed by the shell.
- `agent any` may land on the controller; set `numExecutors: 0` and label agents.
- Build history grows without `buildDiscarder`; a controller with a full disk stops
  accepting builds.
- Multibranch pipelines create a job per branch per PR — disk and queue grow with
  repository activity, not with merges.
