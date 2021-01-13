```Groovy
pipeline {
    agent any
    options {
        //Limits the number of builds to keep to 3
        buildDiscarder(logRotator(numToKeepStr: '3'))
        //If build takes more than 30 minutes, stop and
        //reported as timed out
        timeout(time: 30, unit: 'MINUTES')
    }
    //Need to look into this more
    tools {
        jdk "java8"
    }
    environment {
        MAJOR_VERSION = 1
    }
    stages {
        stage('Build') {
            steps {
                echo 'Build phase commencing!'
                sh './myshellscript.sh'
            }
        stage('Validate YAML syntax') {
            steps {
                sh 'bash ./yaml-verify.sh'
            }
        }
        stage('Approve Deployment') {
            steps {
                //Requires selection of 'Proceed' and 'Abort' options
                input 'Deploy this config to production?'
            }
        }
        }
    }
//Runs after stages above completed
  post {
        //Always run the following, regardless of what occurs
        always { 
            // Archive Unit and integration test results (Artifact), if any
          archiveArtifacts artifacts: 'dist/*.jar', fingerprint: true
        }
        //Run the following if something changed
        changed {
            mail to: "${env.EMAIL_RECIPIENTS}",
                 subject: "${JOB_NAME} - Version ${MAJOR_VERSION} - Build #${BUILD_NUMBER} - ${currentBuild.currentResult}!",
                 body: "Check console output at ${BUILD_URL} to view the results."
        }
        success {
            //Send a Slack notification
            slackSend (color: '#00FF00', message: "SUCCESSFUL: Job '${env.JOB_NAME} [${env.BUILD_NUMBER}]' (${env.BUILD_URL})")

        }
    }
    //Starts a separate pipeline
    //Use only if specifying an agent each stage
    agent none
    stages {
        stage('Unit Tests') {
            agent {
                label 'Centos'
            }
            //Import some libraries
            libraries {
                lib("mylib@master")
                lib("alib")
            }
            steps {
                sh 'cp <mydir>/<myfile>_${BUILD_NUMBER} <mydir2>/'
            }
        }
        stage('Apache testing') {
            //May run from a docker container
            agent {
                docker '<container_name>'
            }
            //Only run this stage when the Github branch is development
            //Multibranch pipeline is a project option in Jenkins
            when {
                branch 'development'
            }
            //Creates directory if doesn't exist
            steps {
                sh "if ![ -d '/var/www/html/my_main/all/${env.BRANCH_NAME}' ]; then mkdir /var/www/html/my_main/all/$BRANCH_NAME" 
            }
        }
    }

}
```