---
description: Close the current feature - run tests and lint, write the story ADR, check the story, update the WP status and open the pull request.
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(git status *), Bash(git diff *), Bash(git log *), Bash(git branch *), Bash(git show *), Bash(git add *), Bash(git commit *), Bash(git push *), Bash(git remote *), Bash(docker compose *), Bash(gh pr create *), Bash(gh pr view *)
---

# /feature-close — close the current feature

Bring the current story to a reviewable, mergeable PR. Extra notes for the PR (optional):
`$ARGUMENTS`

## 1. Preconditions

1. `git branch --show-current` must match `feat|fix|docs/us-NN-MM-*`; otherwise STOP.
2. Derive `US-NN.MM` and the WP file `.project/execution/wpNN-*.md`.
3. Open `.project/execution/<wp-file-basename>.review.md`. If the story has no review, or its
   latest round still has open **Blocker** or **Major** findings, STOP and suggest
   `/feature-review` or `/feature-rework`. Open Minor/Nit findings are listed in the PR body.
4. The working tree must be clean.

## 2. Quality gate

Run every gate of Constitution §18.2 that exists, inside the dockerized toolchain (see
`.docs/DOCKER.md`): Python `ruff check`, `ruff format --check`, `mypy --strict`,
`lint-imports`, `pytest` with coverage; frontend `eslint`, `prettier --check`, `vue-tsc`,
`vitest` with coverage, OpenAPI drift check; `no-latest` check; compose health and Playwright
when the story touches them.

- If a gate fails, fix it (Conventional Commit) and rerun. If the fix is non-trivial, STOP and
  report instead of piling changes into the close.
- Record each gate as pass / fail / not available. Never claim a gate passed if it was not run.

## 3. Story ADR

Follow the `writing-adrs` skill (`.agents/skills/writing-adrs/SKILL.md`):

- If the story took decisions (libraries, patterns, schemas, trade-offs): take the next number
  from `.docs/adr/index.md`, copy `.docs/adr/0000-adr-template.md` to
  `.docs/adr/NNNN-us-NN-MM-<kebab-title>.md`, title `US-NN.MM: <decision>`, status `Proposed`,
  fill every section (≥ 2 real alternatives, a verifiable Compliance check). Register it in
  `.docs/adr/index.md` **and** in the AGENTS.md "Documentation index".
- If the story took no decision of its own, do not invent one: the story line will reference
  the WP closing ADR (fill it when that ADR exists).

## 4. Tracking

In the WP file:

- Story section: tick `- [x] **US-NN.MM completed**`, set `**ADR:** ADR-NNNN`, and make sure all
  its AC and task checkboxes are ticked.
- "## 0. Story checklist": tick the story line and append `· ADR: ADR-NNNN`.
- **WP status check:** if every story of the WP is now checked, also:
  - write the WP closing ADR (`WPNN closing: <work package name>`) summarizing the WP's
    decisions, deviations from the roadmap, consequences and follow-ups; register it in the ADR
    registry and AGENTS.md; fill story lines that reference it;
  - tick the "## 5. WP Definition of Done" items that are now true (report any that are not);
  - set the file `Status` to `DONE`.
  Otherwise the status stays `PROCESSING`. Report how many stories of the WP remain.

Commit: `docs(adr): record ADR-NNNN for US-NN.MM` and/or
`docs(execution): close US-NN.MM`, with `Refs:` and the trailer
`Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.

## 5. Pull request

1. If there is no `origin` remote or `gh` is not authenticated, STOP after the commits and
   tell the user what is missing (suggest `! gh auth login`).
2. `git push -u origin <branch>`.
3. `gh pr create --base <default branch> --title "<conventional subject for the story>"` with a
   body (via heredoc) containing:
   - `## Story` — `US-NN.MM — <title>` and a link to the WP file;
   - `## Changes` — bullet summary;
   - `## Acceptance criteria` — each AC with the test that covers it;
   - `## Quality gate` — the table from step 2, honest;
   - `## Review` — link to the review file, rounds, open Minor/Nit findings;
   - `## References` — Constitution articles, ADRs (new and touched);
   - `## WP status` — PROCESSING (n stories left) or DONE;
   - user notes from `$ARGUMENTS`, if any;
   - last line: `🤖 Generated with [Claude Code](https://claude.com/claude-code)`.
4. Report the PR URL. Do not merge (that is `/feature-auto`, or the user).
