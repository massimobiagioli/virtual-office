---
description: Fix a bug unattended - branch, reproduce test-first, fix, review, rework, run the quality gate, open the pull request and merge it.
argument-hint: "<bug description>"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(git status *), Bash(git diff *), Bash(git log *), Bash(git branch *), Bash(git show *), Bash(git checkout *), Bash(git switch *), Bash(git stash *), Bash(git add *), Bash(git commit *), Bash(git push *), Bash(git pull *), Bash(git remote *), Bash(docker compose *), Bash(docker build *), Bash(docker run *), Bash(gh pr create *), Bash(gh pr view *), Bash(gh pr checks *), Bash(gh pr merge *)
---

# /bugfix — fix, review and merge one bug

Run the same pipeline as `/feature-auto` for a bug that is not a roadmap story: fix → review →
rework → close → merge. Bug: `$ARGUMENTS`

Everything you write — code, comments, docs, commit messages, PR — is in English (AGENTS.md rule
zero), even when the bug description is not.

## 1. Preconditions

1. If `$ARGUMENTS` is empty, STOP and ask for a bug description.
2. Run `git rev-parse --is-inside-work-tree`; if this is not a git repository, STOP.
3. Find the default branch (`git symbolic-ref --short refs/remotes/origin/HEAD`, fallback
   `main`). If you are on a `feat/*`, `fix/*` or `docs/*` branch that is not merged into it,
   STOP: other work is in progress.
4. Run `git status --porcelain`. If the tree is dirty, STOP and report it — unless the user
   said in this conversation that the uncommitted changes are the fix for this bug: then carry
   them onto the fix branch (`git stash` → switch → `git stash pop`) and treat them as the
   Green step of §3.

## 2. Understand and branch

1. Restate the bug in English: observed behavior, expected behavior, where it happens. Locate
   the code (`path:line`). If you cannot reproduce or locate it, STOP and report what you
   tried.
2. Load the `delivering-features` skill and the guides and topic skills for the area touched
   (same table as `.claude/commands/feature-impl.md` §3). Check `.docs/adr/index.md` for ADRs
   that constrain the fix.
3. If the fix needs a decision the roadmap has not taken, or more than ~150 lines of non-test
   code, STOP and propose turning it into a story instead.
4. Branch from the up-to-date default branch, following Constitution §18.5:
   `fix/<kebab-slug>` (never `fix/us-*`, which is reserved for stories). Example:
   `fix/lifespan-async-generator-annotation`.

## 3. Fix, test-first

1. **Red** — write a test that reproduces the bug and see it fail for the right reason. When
   the bug is a tool diagnostic (lint, type checker, deprecation warning), the failing tool
   run is the reproduction: record its output.
2. **Green** — apply the minimum fix; apply it everywhere the same defect occurs.
3. **Refactor** — keep everything green.
4. Commit: `fix(<scope>): <imperative subject ≤ 72 chars>`, body with what/why and
   `Refs: Constitution §…, ADR-…` where relevant, ending with
   `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

Run every check inside the dockerized toolchain (see `.docs/DOCKER.md`; nothing on the host).
If the documented compose command is not available yet, build the service `dev` stage
(`docker build --target dev -t vo-<service>-dev services/<service>`) and run the tools with
`docker run --rm --entrypoint sh vo-<service>-dev -c "…"`.

## 4. Review and rework

Review the diff (`git diff <default>...HEAD`) with the checklist of
`.claude/commands/feature-review.md` §3, leaving out the story-only items (acceptance criteria,
WP checkboxes); instead check that the bug is reproduced by a test or tool run, that the fix
covers every occurrence, and that nothing out of scope slipped in.

- Classify findings as in `/feature-review` (Blocker, Major, Minor, Nit).
- Fix open findings as in `.claude/commands/feature-rework.md` §2, one commit each.
- At most **2** review rounds; if Blocker/Major findings are still open after the second
  round, STOP and report.
- Bugs have no WP file, so do not write a `.review.md`: the review rounds go in the PR body.

## 5. Close

1. Run every quality gate of Constitution §18.2 that exists for the touched services (as in
   `.claude/commands/feature-close.md` §2). Record each as pass / fail / not available. Never
   claim a gate passed if it was not run.
2. ADR: only if the fix took a real decision (library, pattern, trade-off), write one with the
   `writing-adrs` skill (`.docs/adr/NNNN-fix-<kebab-title>.md`, status `Proposed`), register it
   in `.docs/adr/index.md` and the AGENTS.md Documentation index, and commit
   `docs(adr): record ADR-NNNN for <bug slug>`. Do not invent a decision for a trivial fix.
3. If there is no `origin` remote or `gh` is not authenticated, STOP after the commits and tell
   the user what is missing (suggest `! gh auth login`).
4. `git push -u origin <branch>`, then `gh pr create --base <default branch>` with the fix
   commit subject as title and a body (via heredoc) containing:
   - `## Bug` — observed vs expected, in English;
   - `## Cause` — the verified root cause;
   - `## Fix` — bullet summary with `path:line`;
   - `## Reproduction` — the test (or tool run) that failed before and passes now;
   - `## Quality gate` — the honest table;
   - `## Review` — rounds and findings with outcomes, open Minor/Nit;
   - `## References` — Constitution articles and ADRs touched;
   - last line: `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.

## 6. Merge

Exactly as `.claude/commands/feature-auto.md` "Merge": PR open and mergeable, wait for CI checks
if any (do not merge a red PR), `gh pr merge --rebase --delete-branch`, switch back to the
default branch and `git pull --ff-only`.

## Stop rules

Stop at the first step that STOPs. Report which step stopped, why, and how to resume. Never skip
a step silently and never claim a gate passed if it was not run.

## Final report

- Bug, cause, PR URL, head of the default branch after the merge.
- Review rounds and finding outcomes.
- Quality gate table (honest).
- ADR written, if any (it stays `Proposed` until the project owner accepts it).
