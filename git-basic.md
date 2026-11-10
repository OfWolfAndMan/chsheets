## Trust SSH key from Github

```bash
ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts
```

## Clone an existing repository

```bash
git clone [ssh/http/https]://`<user>`@`<domain>`.com/`<repo.git>`
```

## Branch Management

### Display all branches in a repo

```bash
git branch -a
```

### Switching to a new branch

```bash
git checkout -b `<branch_name>`
```

### Delete/Force Delete a local branch

```bash
git branch -d `<branch_name>`
git branch -D `<branch_name>`
```

### Delete a remote branch

```bash
git push `<remote_name>` --delete `<branch_name>`
```

### Push to a specific branch

```bash
git push origin development
```

## Create a new local repository

```bash
git init
```

## Show the changes between current code and your last commit

```bash
git diff
```

## File Management

## Display changed files in working directory

```bash
git status
```

### Snapshots the file in preparation for versioning (Staged)

```bash
git add `<file/folder/wildcard>`
```

### Deletes file from working directory and staged for deletion

```bash
git rm `<file>`
```

### Removes file from version control but locally preserved

```bash
git rm --cached `<file>`
```

### Unstages the file, but preserves content

```bash
git reset `<file>`
```

## Commit Management

### Add a message for the updates and commit

```bash
git commit -m `<Message>`
```

### Change the commit message after already committing

```bash
git commit --amend
```

### Show commit details

```bash
git show `<commit-id>`
```

### Get all available commits from remote repo

```bash
git fetch
```

### Show previous commits (Time/author/commit message)

```bash
git log
```

### Show previous commits with changes

```bash
git log -p
```

### Show previous commits with changes to last x entries

```bash
git log -p -`<number of previous commits>`
```

## Push to the master branch

```bash
git push
```

## Show changes over time to a specified file

```bash
git log -p `<file>`
```

## Download changes and directly merge/integrate into the HEAD

```bash
git pull `<remote>` `<branch>`
```

## Create a new branch and switch to it

```bash
git checkout -b `<new_branch_name>`
```

## Create new branch on git server after creating it

```bash
git push origin `<new_branch_name>`
```

## Mark the current commit with a tag

```bash
git tag `<tag name>`
```

## Show local repo git config

```bash
git config --list
```

## Set git global variables (Username/email)

```bash
git config --global user.name "Username"
git config --global user.email "user@example.com"
git remote set-url origin git@github.com:`<username>`/`<repo>`
```

## Fork Management

### Retrieve updates from branch that you forked from

```bash
git fetch upstream
```

## Move a commit or set of commits from one branch to another

```bash
git checkout `<branch to add commit changes to>`
git cherry-pick `<commit id 1 from other branch>`
```

## Discard changes in working directory

```bash
git checkout -- `<file>`
```

## SSH Key Management

### Add SSH key to Github

```bash
ssh-keygen
cat /home/`<user>`/.ssh/id_rsa.pub
```

### Copy the SSH key

### Add new SSH key into Github site (Under SSH and GPG keys)

## Fix permissions in a certain git repo (Used if accidentally pushing with sudo)

```bash
sudo chown -R $(id -u):$(id -g) "$(git rev-parse --show-toplevel)/.git"
```

## Promoting a secondary branch to master

```bash
git stash
git checkout development
git checkout master
git merge development
git push origin master
```

## Tag the release

```bash
git tag `<tag_name>`
```
