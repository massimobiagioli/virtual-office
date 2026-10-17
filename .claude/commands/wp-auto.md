---
description: Run /feature-auto for every open user story of a work package, one story at a time, starting from the first unchecked one; fans read-only work out to at most 3 subagents.
argument-hint: "[WPNN]"
disable-model-invocation: true
allowed-tools: Agent, Read, Grep, Glob, Edit, Write, Bash(git rev-parse *), Bash(git symbolic-ref *), Bash(git status *), Bash(git diff *), Bash(git log *), Bash(git branch *), Bash(git show *), Bash(git checkout *), Bash(git switch *), Bash(git add *), Bash(git commit *), Bash(git push *), Bash(git pull *), Bash(git remote *), Bash(docker compose *), Bash(docker build *), Bash(docker run *), Bash(gh pr create *), Bash(gh pr view *), Bash(gh pr checks *), Bash(gh pr merge *)
---

# /wp-auto — deliver a whole work package, story by story

Repeat the `/feature-auto` pipeline (impl → review → rework → close → merge) for every unchecked
story of one work package, in checklist order, until the WP is `DONE` or a phase STOPs.
Work package (optional): `$ARGUMENTS`

Everything you write — code, comments, docs, commit messages, PRs — is in English (AGENTS.md rule
zero).

## Concurrency model

- **One feature at a time.** Exactly one story is in flight: it is merged into the default
  branch before the next one starts. Stories of a WP build on each other, share the WP file and
  take consecutive ADR numbers, so they are never implemented in parallel.
- **One writer at a time.** At any moment at most one subagent (or you) edits files, commits,
  pushes or merges.
- **At most 3 subagents running at once**, the writer included. The extra slots are only for
  **read-only** work (they read files, run `git diff`/`git log` and the dockerized gates, and
  return text; they never edit, commit or switch branches).
- You are the **orchestrator**: you pick the stories, launch the subagents, verify the git
  state between phases, write the merged review round and keep the run log. Keep your own
  context lean — rely on the subagents' reports, not on re-reading their work.
- If the `Agent` tool is not available, run `.claude/commands/feature-auto.md` inline for each
  story instead; everything else in this file still applies.

## 1. Preconditions

1. `git rev-parse --is-inside-work-tree`; if this is not a git repository, STOP.
2. Find the default branch (`git symbolic-ref --short refs/remotes/origin/HEAD`, fallback
   `main`).
3. `git status --porcelain` must be empty; otherwise STOP and report.
4. If you are on a `feat/us-*`, `fix/us-*` or `docs/us-*` branch that is not merged into the
   default branch, STOP: a story is in progress — finish it with `/feature-auto` (or the single
   phase commands) first. Otherwise switch to the default branch and `git pull --ff-only`.
5. There must be an `origin` remote and `gh auth status` must succeed, because every story ends
   with a merge; otherwise STOP and suggest `! gh auth login`.

## 2. Pick the work package and plan

1. If `$ARGUMENTS` names a WP (`WP05`, `wp05`, `5`), use `.project/execution/wp05-*.md`.
   Otherwise scan `.project/execution/wpNN-*.md` in WP number order (ignore `*.review.md`) and
   take the first file whose `Status` is not `DONE`.
2. If the WP is `DONE`, report it and stop.
3. Check its `Depends on` row (every dependency WP must be `DONE`) and its "## 7. Blockers"
   section; if anything blocks it, STOP and report the blocker.
4. Read "## 0. Story checklist" and list the unchecked stories (`- [ ]`) in order. The run
   starts from the **first unchecked** story and never skips one.
5. Announce the plan: WP id and title, stories to deliver (id, title, points), total points.

## 3. Story loop

For each unchecked story `US-NN.MM`, in order, run phases A–E. Every subagent prompt must be
self-contained (subagents do not see this conversation) and must say:

- the story id, the WP file path and the default branch;
- "the phase command is not model-invocable: read `<command file>` and follow it completely, as
  if the user had typed it";
- everything is written in English; every commit ends with
  `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`, every PR body with
  `🤖 Generated with [Claude Code](https://claude.com/claude-code)`;
- do not spawn subagents; if the phase STOPs, stop and say why;
- what to return (listed per phase below), and nothing longer than needed.

### A. Implement (1 writer + optional 1 read-only)

1. **Writer** — one `general-purpose` subagent follows `.claude/commands/feature-impl.md` with
   argument `US-NN.MM`. Return: branch, `git log --oneline <default>..HEAD`, criteria covered,
   checks actually run with results, open questions, or the STOP reason.
2. **Look-ahead (optional, read-only)** — while the writer runs, and only if there is a next
   unchecked story, one `Explore` subagent prepares a context brief for it: its acceptance
   criteria, the Constitution articles, guides, topic skills and ADRs that constrain it, the
   files it will probably touch, and dependencies on the story in flight. The brief is advice
   for the next writer, never a substitute for `feature-impl.md` §3; drop it if the story in
   flight changed the picture.
3. Verify: the current branch is `feat|fix|docs/us-NN-MM-*`, the tree is clean and there are
   commits ahead of the default branch. If not, STOP.

### B. Review (up to 3 read-only reviewers in parallel)

1. Size the diff (`git diff --stat <default>...HEAD`). For a small diff (≲ 150 changed lines),
   launch **one** reviewer with the whole checklist of `.claude/commands/feature-review.md` §3.
   Otherwise launch **three** reviewers in parallel, each owning a slice of that checklist:
   - **R-accept** — Acceptance, TDD & tests, and the Quality gate (the only reviewer that runs
     the dockerized gates, so they never run concurrently);
   - **R-arch** — Architecture, Standards, Stack;
   - **R-product** — Product rules, Docs & tracking (indexes, WP checkboxes, commit format).
   Each reviewer loads the yardsticks of `feature-review.md` §2 for its slice, reads only, and
   returns findings as `severity — path:line — what is wrong, rule/§ reference, suggested fix`
   (severities as in `feature-review.md` §4), plus the gate table for R-accept.
2. Merge the results yourself: drop duplicates, keep the higher severity on overlaps, number the
   findings `R1…`, set the verdict (`APPROVED` only with no open Blocker/Major), write the
   round into `.project/execution/<wp-file-basename>.review.md` exactly in the
   `feature-review.md` §4 format, and commit it alone:
   `docs(review): review US-NN.MM round N`.

### C. Rework (1 writer)

Skip when the verdict is `APPROVED` with no open findings. Otherwise one `general-purpose`
subagent follows `.claude/commands/feature-rework.md`. Return: each finding with its outcome,
commits, checks run.

Re-review as `.claude/commands/feature-auto.md` step 4: if the rework fixed any Blocker or Major
finding, repeat phase B (round 2) and, if it requests changes, phase C again. At most **2**
review rounds per story; if Blocker/Major findings are still open after round 2, STOP.

### D. Close and merge (1 writer)

One `general-purpose` subagent follows `.claude/commands/feature-close.md` and then the "Merge"
section of `.claude/commands/feature-auto.md` (never merge a red PR). Return: PR URL, quality
gate table, ADRs written, WP status after the close, head of the default branch.

### E. Verify and record

1. You are on the default branch, up to date, with a clean tree.
2. The story line in "## 0. Story checklist" is checked and carries its ADR id; the PR is
   merged (`gh pr view <url> --json state`).
3. Append a row to the run log (story, PR, review rounds, gates, ADR).
4. If any check fails, STOP. Otherwise continue with the next unchecked story.

## 4. When the run ends

- **WP complete** — the last story's `/feature-close` writes the WP closing ADR and sets the WP
  `Status` to `DONE`; confirm both. Do **not** start the next WP: report it as the next
  `/wp-auto` target.
- **Stopped** — stop the loop at the first phase that STOPs (dirty tree, blocked dependency,
  failing gate that is not trivially fixable, disputed Blocker, review rounds exhausted, red CI,
  missing remote or `gh` auth, a split proposed by `feature-impl`, …). Never start the next
  story on top of an unfinished one. Report which story and phase stopped, why, and how to
  resume (e.g. `/feature-rework`, then `/feature-close`, then `/wp-auto` again).

Never skip a story or a phase silently and never claim a gate passed if it was not run.

## Final report

- WP id, title and final status.
- Run log table: story · PR URL · review rounds (findings by severity and outcome) · quality
  gate summary · ADR.
- ADRs written (they stay `Proposed` until the project owner accepts them).
- Stories left, the STOP reason if any, and the next command to run.
