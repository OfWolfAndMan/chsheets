---
title: git
summary: git — everyday commands, the undo ladder, rebase, worktrees
tags: [vcs, git]
tooling: [git]
verified_on: 2026-11-10
verified_env: git 2.56.0, Linux
status: verified
---

# git

Verified against git 2.56.0. The one idiom worth unlearning from older material:
`git checkout <file>` is now `git restore <file>`, and `git checkout <branch>` is
`git switch <branch>`. The old form still works; the new pair says which one you meant.

## Identity and configuration

```bash
git config --global user.name "<Your Name>"
git config --global user.email "<you@example.com>"
git config --global init.defaultBranch main
git config --global pull.rebase true        # rebase on pull, no merge bubbles
git config --global push.default simple
git config --list --show-origin             # where each setting comes from
```

SSH access to a forge, and the test that proves it:

```bash
ssh-keygen -t ed25519 -C "<you@example.com>"
ssh -T git@github.com          # "successfully authenticated" or it is not enrolled
```

## Starting work

```bash
git init
git clone git@github.com:<owner>/<repo>.git
git clone --depth 1 <url>      # shallow: history only to the tip — CI and quick looks
git remote -v
git remote add upstream git@github.com:<upstream>/<repo>.git
```

## The daily loop

```bash
git status -sb                 # short form, with branch and ahead/behind
git add -p                     # stage hunk by hunk — the habit that produces good commits
git diff                       # unstaged
git diff --staged              # staged
git commit -m "<message>"      # message states why, not what
git commit --amend --no-edit   # fold into the last commit, before it is pushed
git push -u origin <branch>
```

## Reading history

```bash
git log --oneline --graph --decorate -20
git log -p -- <path>                     # history of one file, with diffs
git log -S '<string>' --oneline          # commits that added or removed a string
git log --since '2 weeks ago' --author '<name>'
git show <sha>:<path>                    # a file as it was at that commit
git blame -L 10,20 <file>
git shortlog -sn --all                   # commits per author
```

## Branches

```bash
git switch -c <branch>         # create and move
git switch <branch>
git branch -vv                 # local branches with upstream and divergence
git branch -d <branch>         # refuses if unmerged; -D forces
git branch -m <new-name>
git push origin --delete <branch>
```

## The undo ladder

The right command depends on one question: has anyone else seen it?

| Situation | Command | Effect |
|---|---|---|
| Discard unstaged changes in a file | `git restore <file>` | throws the working copy away |
| Unstage, keep the changes | `git restore --staged <file>` | back to modified-but-not-staged |
| Fix the last commit, not yet pushed | `git commit --amend` | rewrites that commit |
| Undo a pushed commit | `git revert <sha>` | new commit that reverses it — safe on shared history |
| Move the branch back, keep changes staged | `git reset --soft HEAD~1` | rewrites local history |
| Move back, keep changes in the working tree | `git reset --mixed HEAD~1` | the default |
| Move back, discard changes | `git reset --hard HEAD~1` | destructive; the reflog is your only net |
| Recover after a bad reset | `git reflog` then `git reset --hard <sha>` | reflog keeps ~90 days |

`git revert` is the only one of these that is safe on a branch other people have.

## Stash

```bash
git stash push -m "<why>"      # include -u to take untracked files too
git stash list
git stash show -p stash@{0}
git stash pop                  # apply and drop
git stash apply stash@{0}      # apply and keep
git stash drop stash@{0}
```

## Rebase and conflicts

```bash
git rebase main                # replay this branch on top of main
git rebase -i HEAD~3           # squash, reword, reorder local commits
git rebase --continue          # after resolving a conflict
git rebase --abort             # give up cleanly
git merge --no-ff <branch>     # when a merge commit is the honest representation
```

During a conflict: `git status` lists the paths; `git diff` shows the markers; fix the
file, `git add` it, then continue. `git checkout --ours <file>` and
`git checkout --theirs <file>` take one side wholesale.

## Branches that move under you

```bash
git fetch --prune              # update refs, drop deleted remote branches
git pull --rebase              # replay local work on top of upstream
git push --force-with-lease    # force, but refuse if someone else pushed
```

`--force-with-lease` is the only acceptable force. `--force` overwrites other people's
commits silently.

## Worktrees

Two branches checked out at once, without stashing:

```bash
git worktree add ../repo-hotfix hotfix/branch
git worktree list
git worktree remove ../repo-hotfix
```

Useful for reviewing a PR while keeping your working tree untouched.

## Finding the commit that broke it

```bash
git bisect start
git bisect bad                 # current state is broken
git bisect good <known-good-sha>
# git tests a commit; mark each with `git bisect good` or `git bisect bad`
git bisect reset
```

`git bisect run ./test.sh` automates the loop entirely — the script's exit status is
the verdict.

## Tags and releases

```bash
git tag -a v1.2.0 -m "release 1.2.0"
git push origin v1.2.0
git tag -l 'v1.*'
git describe --tags --always   # nearest tag, or a short sha
```

## Ignoring and untracking

```bash
git status --ignored           # what is being ignored, and by which rule
git rm --cached <file>         # stop tracking, keep on disk
git check-ignore -v <file>     # which .gitignore line matched
```

A file added to `.gitignore` after it was committed stays tracked; `git rm --cached`
is the missing step. History keeps the old content — rotate any secret that was ever
committed rather than assuming removal was enough.

## Hooks

```bash
ls .git/hooks                  # samples end in .sample; drop the suffix to enable
git config core.hooksPath .githooks    # version-controlled hooks directory
```

Keep hooks in the repository under `.githooks/` and set `core.hooksPath`, so the team
gets the same checks instead of each person's local copies.

## Traps worth remembering

- `git commit -a` skips untracked files; it is not "commit everything".
- `git pull` without a strategy merges; on a busy branch, `--rebase` keeps history
  readable.
- Editing a commit that has been pushed requires a force push and rewrites everyone
  else's base. Prefer `revert`.
- `git clean -fdx` deletes ignored and untracked files. Run `git clean -ndx` first.
