## Clone an existing repository

```
git clone [ssh/http/https]://`<user>`@`<domain>`.com/`<repo.git>`
```

## Branch Management
### Display all branches in a repo

```
git branch -a
```

### Switching to a new branch

```
git checkout -b `<branch_name>`
```

### Delete/Force Delete a local branch

```
git branch -d `<branch_name>`
git branch -D `<branch_name>`
```

### Delete a remote branch

```
git push `<remote_name>` --delete `<branch_name>`
```

### Push to a specific branch

```
git push origin development
```

## Create a new local repository

```
git init
```

## Show the changes between current code and your last commit

```
git diff
```


## File Management
## Display changed files in working directory

```
git status
```

### Snapshots the file in preparation for versioning (Staged)

```
git add `<file/folder/wildcard>`
```

### Deletes file from working directory and staged for deletion

```
git rm `<file>`
```

### Removes file from version control but locally preserved

```
git rm --cached `<file>`
```

### Unstages the file, but preserves content

```
git reset `<file>`
```

## Commit Management
### Add a message for the updates and commit

```
git commit -m `<Message>`
```

### Change the commit message after already committing

```
git commit --amend
```

### Show commit details

```
git show `<commit-id>`
```

### Get all available commits from remote repo

```
git fetch
```

### Show previous commits (Time/author/commit message)

```
git log
```

### Show previous commits with changes

```
git log -p
```

### Show previous commits with changes to last x entries

```
git log -p -`<number of previous commits>`
```

## Push to the master branch

```
git push
```

## Show changes over time to a specified file

```
git log -p `<file>`
```

## Download changes and directly merge/integrate into the HEAD

```
git pull `<remote>` `<branch>`
```

## Create a new branch and switch to it

```
git checkout -b `<new_branch_name>`
```

## Create new branch on git server after creating it

```
git push origin `<new_branch_name>`
```

## Mark the current commit with a tag

```
git tag `<tag name>`
```

## Show local repo git config

```
git config --list
```

## Set git global variables (Username/email)

```
git config --global user.name "Username"
git config --global user.email "email@email.com"
git remote set-url origin git@github.com:`<username>`/`<repo>`
```

## Fork Management
### Retrieve updates from branch that you forked from

```
git fetch upstream
```

## Move a commit or set of commits from one branch to another

```
git checkout `<branch to add commit changes to>`
git cherry-pick `<commit id 1 from other branch>`
```

## Discard changes in working directory

```
git checkout -- `<file>`
```

## SSH Key Management
### Add SSH key to Github

```
ssh-keygen
cat /home/`<user>`/.ssh/id_rsa.pub
```

### Copy the SSH key
### Add new SSH key into Github site (Under SSH and GPG keys)

## Fix permissions in a certain git repo (Used if accidentally pushing with sudo)

```
sudo chown -R $(id -u):$(id -g) "$(git rev-parse --show-toplevel)/.git"
```

## Promoting a secondary branch to master

```
git stash
git checkout development
git checkout master
git merge development
git push origin master
```

## Tag the release

```
git tag `<tag_name>`
```