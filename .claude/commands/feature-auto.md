---
description: Run the full story pipeline unattended - feature-impl, feature-review, feature-rework, feature-close - then merge the pull request.
argument-hint: "[US-NN.MM]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(git status *), Bash(git diff *), Bash(git log *), Bash(git branch *), Bash(git show *), Bash(git checkout *), Bash(git switch *), Bash(git add *), Bash(git commit *), Bash(git push *), Bash(git pull *), Bash(git remote *), Bash(docker compose *), Bash(gh pr create *), Bash(gh pr view *), Bash(gh pr checks *), Bash(gh pr merge *)
---

# /feature-auto — implement, review, rework, close and merge one story

Run the four feature commands in sequence for one story, then merge its PR.
Story (optional): `$ARGUMENTS`

The phase commands are not model-invocable, so for each phase **read its file and follow it
completely**, as if the user had typed it, passing `$ARGUMENTS` where the phase accepts it:

1. `.claude/commands/feature-impl.md`
2. `.claude/commands/feature-review.md`
3. `.claude/commands/feature-rework.md` — skip when the review verdict is `APPROVED` with no
   open findings.
4. Re-review: if the rework fixed any Blocker or Major finding, run `feature-review.md` again
   and, if it requests changes, `feature-rework.md` again. At most **2** review rounds in total;
   if Blocker/Major findings are still open after the second round, STOP and report.
5. `.claude/commands/feature-close.md`
6. Merge (below).

## Stop rules

Stop the pipeline at the first phase that STOPs (dirty tree, blocked dependency, failing gate
that is not trivially fixable, disputed Blocker, missing remote or `gh` auth, …). Report which
phase stopped, why, and the command to resume with (e.g. `/feature-rework`). Never skip a phase
silently and never claim a gate passed if it was not run.

## Merge

1. `gh pr view --json url,state,mergeable` — the PR must be open and mergeable.
2. If the repository has CI checks, wait for them: `gh pr checks --watch`. If any check fails,
   STOP and report; do not merge a red PR.
3. Merge keeping the Conventional Commits history:
   `gh pr merge --rebase --delete-branch`.
4. Switch back to the default branch and `git pull --ff-only`.

## Final report

- Story, PR URL, merge commit/head on the default branch.
- Review rounds and finding outcomes.
- Quality gate table (honest).
- ADRs written (they stay `Proposed` until the project owner accepts them).
- WP status (PROCESSING with n stories left, or DONE) and the next story `/feature-auto` would
  pick.
