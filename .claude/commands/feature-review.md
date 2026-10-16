---
description: Code-review the user story on the current feature branch and write the notes to .project/execution/<wp-file>.review.md.
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(git status *), Bash(git diff *), Bash(git log *), Bash(git branch *), Bash(git show *), Bash(git add *), Bash(git commit *), Bash(docker compose *)
---

# /feature-review — review the current feature

Review the story being worked on the current branch. You review; you do **not** fix code here
(that is `/feature-rework`). Extra focus (optional): `$ARGUMENTS`

## 1. Identify the feature

1. `git branch --show-current` must match `feat|fix|docs/us-NN-MM-*`; otherwise STOP and report.
2. Derive the story id `US-NN.MM` and the WP file `.project/execution/wpNN-*.md`.
3. Find the default branch (`git symbolic-ref --short refs/remotes/origin/HEAD`, fallback
   `main`) and collect the change: `git log --oneline <default>..HEAD` and
   `git diff <default>...HEAD`.

## 2. Load the yardsticks

- The story in the WP file: acceptance criteria, tasks, tests, "Done when".
- `delivering-features` skill, `.docs/PRINCIPLES.md`, the Constitution articles cited by the WP,
  the guides for every area the diff touches (BACKEND, FRONTEND, DESIGN, DOCKER, OLLAMA,
  POSTGRES, STACK) and the matching topic skills.
- Accepted ADRs in `.docs/adr/index.md`.

## 3. Review checklist

Check every item and note concrete evidence (`path:line`):

- **Acceptance** — every AC is implemented and covered by at least one test that would fail
  without the code; nothing out of the story's scope slipped in.
- **TDD & tests** — tests are deterministic (no real clock, randomness, network or LLM), test
  behavior not implementation, coverage thresholds plausible (domain ≥ 95 %, application ≥ 90 %,
  others ≥ 70 %).
- **Architecture** — dependency rule (`domain` ← `application` ← `agents` ← `infrastructure`/`api`;
  `office-engine` imports neither Vue nor PixiJS); workflow rules live in the `core` domain;
  every state change is a domain event; the office scene stays a projection.
- **Standards** — guide conventions, strict typing (no `Any`/`any`), naming, UTC/ULID, config
  via env vars only, comments explain why.
- **Stack** — only STACK.md dependencies, exact pins, never `latest`.
- **Product rules** — English everywhere; no audio; Amiga design tokens for anything visible.
- **Docs & tracking** — docs/indexes updated, WP checkboxes ticked for the work done, commits
  are Conventional Commits ≤ 72 chars.
- **Quality gate** — run the gates of Constitution §18.2 that exist in the dockerized toolchain
  and record the real results; list the gates that do not exist yet as "not available".

## 4. Write the review file

Write (or update) `.project/execution/<wp-file-basename>.review.md`, e.g.
`.project/execution/wp01-repository-and-toolchain.review.md`. One file per WP, one section per
story; if the story already has a section, append a new round (`Round 2`, …) instead of
rewriting history.

```markdown
# Review — WPNN <title>

## US-NN.MM — <story title>

### Round 1 · <YYYY-MM-DD> · branch `<branch>` · head `<short sha>`

**Verdict:** CHANGES REQUESTED | APPROVED

**Quality gate**

| Gate | Result |
| ---- | ------ |
| ruff check | pass / fail / not available |

**Findings**

- [ ] **R1 · Blocker** — `path:line` — what is wrong, why it matters (rule/§ reference), suggested fix.
- [ ] **R2 · Minor** — …

**Notes** — anything positive or for follow-up stories.
```

Severities: **Blocker** (breaks an AC, a Constitution rule or a gate), **Major** (standard or
design violation), **Minor** (should fix), **Nit** (optional). Verdict is `APPROVED` only when
there are no open Blocker or Major findings.

Commit the review file alone:
`docs(review): review US-NN.MM round N` (with the Co-Authored-By trailer
`Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`).

## 5. Report

Summarize the verdict and the count of findings per severity, and suggest `/feature-rework`
(findings open) or `/feature-close` (approved).
