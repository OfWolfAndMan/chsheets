### Install Jenkins in a Docker container
```Shell
docker run \
  -u root \
  --rm \
  -d \
  -p 8080:8080 \
  -p 50000:50000 \
  -v jenkins-data:/var/jenkins_home \
  -v /var/run/docker.sock:/var/run/docker.sock \
  jenkinsci/blueocean
```

### Access command line to get initial password
```Shell
docker ps
docker exec -it <container id> bash
cat /var/jenkins_home/secrets/initialAdminPassword
```

***
# TERMINOLOGY

Master:
- Primary, controlling system for a Jenkins instance
- Has complete access to all Jenkins configurations and options
- Not intended for running heavyweight tasks
- Not recommended to run jobs in the master node

Node:
- Any system that can run Jenkins jobs
- Covers both masters and agents

Agent:
- AKA a slave (Any non-master system)
- Managed by the master system
- Agents run on nodes

Executor:
- A slot to run a job in a node/agent

Node Labels:
- Identifies a specific node
- Groups classes of nodes together
- Identifies some characteristic of a node that is useful to know for processing

***

# SIMPLE PIPELINE EXAMPLE
### Jenkins DSL modeled after the Groovy framework

```Groovy
node ('worker1') {
  // The stage allows to group individual settings,
  // DSL commands, and logic together.
  // Stage names arbitrary
	 stage('Source') { // for display purposes
	  // Get some code from our Git repository
	  git 'https://github.com/brentlaster/gradle-greetings.git'
	  }

    stage('Build') {
      //Run a shell script
      sh myshellscript.sh
    }
}
```

- 'worker1': Name of the node
- stage: Groups together individual settings, DSL commands, and logic
- steps: NOT Groovy commands. 

### Example of a parallel structure to designate mappings

```Groovy
parallel (
            win: { node ('win64'){
             ...
             }},
            linux: { node ('ubuntu') {
             ...
             }},
          )
```
      
***

# DECLARATIVE PIPELINE STRUCTURE

```
+*****************************************************+
** pipeline                                          **
**                                                   **
**  +___________+                                    **
**  |  agent    |                                    **
**  +___________+                                    **                                               
**  +***********+                                    **
**  |environment|                                    **
**  +***********+                                    **                                               
**  +***********+                                    **
**  |  tools    |                                    **
**  +***********+                                    **
**  +***********+                                    **
**  | options   |                                    **
**  +***********+                                    **
**  +***********+                                    **
**  | triggers  |                                    **
**  +***********+                                    **
**  +***********+                                    **
**  |parameters |                                    **
**  +***********+                                    **
**  +***********+                                    **
**  |libraries  |                                    **
**  +***********+                                    **
**  +*******************************************+    **
**  |  stages                                   |    **
**  |    +***********************************+  |    **
**  |    | stage                             |  |    **
**  |    |      +***********+                |  |    **
**  |    |      |  agent    |                |  |    **
**  |    |      +***********+                |  |    **
**  |    |      +***********+                |  |    **
**  |    |      |environment|                |  |    **
**  |    |      +***********+                |  |    **
**  |    |      +***********+                |  |    **
**  |    |      |  tools    |                |  |    **
**  |    |      +***********+                |  |    **
**  |    |      +_______________________+    |  |    **
**  |    |      |  steps                |    |  |    **
**  |    |      |       +______________+|    |  |    **                   
**  |    |      |       |DSL statements||    |  |    **
**  |    |      |       +______________+|    |  |    **  
**  |    |      +_______________________+    |  |    **
**  |    |      +***********+                |  |    **
**  |    |      |   post    |                |  |    **
**  |    |      +***********+                |  |    **
**  |    +***********************************+  |    **
**  |    +***********************************+  |    **
**  |    | stage                             |  |    **
**  |    |      ...                          |  |    **
**  |    +***********************************+  |    **
**  +*******************************************+    **
**  +***********+                                    **
**  |   post    |                                    **
**  +***********+                                    ** 
+******************************************************

***
```

# ENVIRONMENT VARIABLES 

- $BUILD_NUMBER
- $NODE_NAME
- $JOB_NAME
- $EXECUTOR_NUMBER
- $WORKSPACE
- $GIT_COMMIT (SHA of commit being accessed)
- $GIT_BRANCH (Branch name of git repo)
- For additional environment vars, visit http://<ip>:<port>/env-vars.html/

 SHARED LIB SCOPE

```
+**********************************************************************************+
**                              Jenkins Environment                               **
**  +****************************************************************+            **
**  |     Workflow Libs (internal - trusted)                         |            **
**  +****************************************************************+            **
**                                                                                **
**  +****************************************************************+            **
**  |     Workflow Libs (internal - trusted)                         |            **
**  +****************************************************************+            **
**                                                                                **
**  +**********************+   +**********************+ +**********************+  **                           
**  |    +**************+  |   |    +**************+  | |    +**************+  |  **      
**  |    | Local Shared |  |   |    | Local Shared |  | |    | Local Shared |  |  **
**  |    |Library (ext- |  |   |    |Library (ext- |  | |    |Library (ext- |  |  **
**  |    |ernal untrust)|  |   |    |ernal untrust)|  | |    |ernal untrust)|  |  **
**  |    +**************+  |   |    +**************+  | |    +**************+  |  **
**  | Multibranch Pipeline |   | Github Organization  | |         Folder       |  **                               
**  +**********************+   +**********************+ +**********************+  **
+**********************************************************************************+
```

# PLUGINS

## Build Pipeline

### Used to visualize pipeline in Jenkins
    - Blue: Job hasn't run yet
    - Yellow: Job in progress
    - Green: Job completed successfully
    - Red: Job failed

### Setting up the Slack API
    - In Slack, 