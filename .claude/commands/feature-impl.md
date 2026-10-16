---
description: Implement the next user story from .project/execution with TDD on a feature branch, committing in Conventional Commits.
argument-hint: "[US-NN.MM]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Edit, Write, Bash(git status *), Bash(git diff *), Bash(git log *), Bash(git branch *), Bash(git checkout *), Bash(git switch *), Bash(git add *), Bash(git commit *), Bash(docker compose *)
---

# /feature-impl — implement the next user story

Implement exactly **one** user story, test-first, on its own feature branch.
Requested story (optional): `$ARGUMENTS`

Everything you write — code, comments, docs, commit messages — is in English (AGENTS.md rule zero).

## 1. Preconditions

1. Run `git rev-parse --is-inside-work-tree`. If this is not a git repository, STOP and ask the
   user whether to run `git init` (do not do it on your own).
2. Run `git status --porcelain`. If the working tree is dirty, STOP and report it.
3. Find the default branch (`git symbolic-ref --short refs/remotes/origin/HEAD`, falling back
   to `main`). If you are on a `feat/us-*`, `fix/us-*` or `docs/us-*` branch that is not merged
   into it, STOP: a feature is already in progress — tell the user to run `/feature-review`,
   `/feature-rework` or `/feature-close` first.

## 2. Pick the story

- If `$ARGUMENTS` names a story (e.g. `US-05.03`), use it.
- Otherwise scan `.project/execution/wpNN-*.md` **in WP number order** (ignore `*.review.md`):
  take the first file whose `Status` is not `DONE`, and in it the first story whose line in
  "## 0. Story checklist" is unchecked (`- [ ]`).
- Check the WP's `Depends on` row: if a dependency WP is not `DONE`, STOP and report the
  blocker instead of starting work. Also respect the "## 7. Blockers" section.
- Announce the chosen story (id, title, points) before writing any code.

## 3. Load context

1. Load the `delivering-features` skill (`.agents/skills/delivering-features/SKILL.md`) and
   follow its checklist.
2. Read the whole WP file: objective, scope, the story's acceptance criteria, tasks and tests,
   and the "Constitution", "Guides" and "Skills" rows of the header table.
3. Read the Constitution articles and the guide sections that the WP header cites, plus the
   guides for the area you touch:

   | Area touched | Guide(s) | Topic skill(s) |
   | --- | --- | --- |
   | `services/core`, `services/agents-catalog` (Python) | `.docs/BACKEND.md` | `tracing-events`, `enforcing-kanban-workflow`, `authoring-office-agents` as relevant |
   | `frontend/` (Vue/TS) | `.docs/FRONTEND.md` | `designing-amiga-ui`, `building-office-scene` as relevant |
   | Anything visible (UI, pixel art, copy) | `.docs/DESIGN.md` | `designing-amiga-ui` |
   | Dockerfiles, compose, `.env.example` | `.docs/DOCKER.md` | — |
   | Tables, migrations, event store | `.docs/POSTGRES.md` | `tracing-events` |
   | LLM models, agent runs | `.docs/OLLAMA.md` | `authoring-office-agents` |
   | Any dependency or version | `.docs/STACK.md` | — |

4. Check `.docs/adr/index.md` for ADRs that constrain the story.

## 4. Open the feature branch

- If the WP file `Status` is `READY`, set it to `PROCESSING`.
- Create the branch from the up-to-date default branch, following Constitution §18.5:
  `feat/us-NN-MM-<kebab-slug>` (use `fix/` for a fix story, `docs/` for a docs-only story).
  Example: `feat/us-01-01-uv-workspace-root`.

## 5. Test-first loop

For each acceptance criterion, in order:

1. **Red** — write the test that expresses the criterion (Given/When/Then); run it and see it
   fail for the right reason.
2. **Green** — write the minimum code to pass.
3. **Refactor** — clean up with tests green.
4. Tick the criterion (`- [x] AC…`) and the related tasks in the WP file.
5. Commit: Conventional Commits, English, imperative, subject ≤ 72 chars, body with what/why
   and `Refs: US-NN.MM, Constitution §…, ADR-…`. Prefer small commits: a `test:` + `feat:`
   pair, or a single `feat:` that contains both test and code; `refactor:`, `docs:`,
   `build:`, `chore:` as appropriate. End every commit message with:

   ```
   Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
   ```

Run all tests inside the dockerized toolchain (nothing installed on the host). For scaffolding
stories where a "test" is a tool exit code (e.g. `uv sync --frozen`, `pnpm lint`), run that
command as the check. If a test infrastructure does not exist yet, say so — never pretend a
check ran.

Keep the slice small: if the story needs more than ~400 lines of non-test code, stop and
propose a split to the user.

## 6. Finish

- Update docs touched by the change (glossary, guides, STACK.md, AGENTS.md indexes) and commit
  them.
- Do **not** write the story ADR, check the story line, or open the PR: that is
  `/feature-close`.
- Report: story, branch, commits (`git log --oneline <default>..HEAD`), criteria covered,
  checks actually run with their result, open questions. Suggest `/feature-review` next.
