---
description: Address the open findings of the latest review of the current feature, test-first, and mark them resolved in the review file.
argument-hint: "[R1 R3 ...]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(git status *), Bash(git diff *), Bash(git log *), Bash(git branch *), Bash(git show *), Bash(git add *), Bash(git commit *), Bash(docker compose *)
---

# /feature-rework — rework after review

Fix the findings recorded by `/feature-review` for the current feature.
Only these findings (optional, default: all open ones): `$ARGUMENTS`

## 1. Load the review

1. `git branch --show-current` must match `feat|fix|docs/us-NN-MM-*`; otherwise STOP.
2. Derive `US-NN.MM` and open `.project/execution/<wp-file-basename>.review.md`. If there is no
   section for this story, STOP and suggest `/feature-review`.
3. Take the **latest round** of the story and list its open findings (`- [ ]`), Blockers first,
   then Major, Minor, Nit.
4. Load the same context as `/feature-impl` (the `delivering-features` skill, the story, the
   guides and topic skills for the touched areas).

## 2. Fix, test-first

For each finding:

1. If it is a behavior defect, write or adjust a test that reproduces it and see it fail.
2. Apply the fix; keep all tests green; refactor if needed.
3. Commit with a Conventional Commit referencing the finding, e.g.
   `fix(domain): reject pull when TODO is full` with body `Refs: US-NN.MM review R1`, ending
   with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
4. In the review file, check the finding and append the resolution:
   `- [x] **R1 · Blocker** — … → Resolved in <short sha>: <one line>`.

If you disagree with a finding, do not silently skip it: leave it unchecked and append
`→ Disputed: <reason>` so the next review round or the user can decide. A Nit may be marked
`→ Won't fix: <reason>`.

Never widen scope: work that belongs to another story is noted as a follow-up, not done here.

## 3. Verify and record

- Rerun the tests and the existing quality gates in the dockerized toolchain; report real
  results only.
- Add under the round a line `**Rework:** <YYYY-MM-DD> · head <short sha> · gates: <summary>`.
- Commit the review file: `docs(review): record rework for US-NN.MM`.

## 4. Report

List each finding with its outcome (resolved / disputed / won't fix) and suggest
`/feature-review` for another round if a Blocker or Major was fixed in a non-trivial way,
otherwise `/feature-close`.
