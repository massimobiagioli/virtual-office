---
name: delivering-features
description: End-to-end workflow for implementing any change in the Virtual Office repository (feature, fix, refactor) - reading the Constitution, slicing work, test-first development, quality gates, docs and ADR updates, Conventional Commits. Use at the start of every coding task in this repository, before editing code.
---

# Delivering features in Virtual Office

## Checklist

Copy this checklist and tick it as you go:

```
- [ ] 1. Read context: AGENTS.md, relevant Constitution articles, STACK.md, PRINCIPLES.md, related ADRs
- [ ] 2. Load the topic skills that apply (see table below)
- [ ] 3. State the slice: one concern, acceptance criteria in Given/When/Then
- [ ] 4. Write failing tests first (domain/application)
- [ ] 5. Implement the minimum to go green, then refactor
- [ ] 6. Update docs, Glossary terms, and ADRs in the same change
- [ ] 7. Run the quality gate
- [ ] 8. Write the story ADR (or reference the WP closing ADR) — skill `writing-adrs`
- [ ] 9. Check the story's checkboxes, update the execution file status (READY/PROCESSING/DONE)
- [ ] 10. Commit with Conventional Commits, in English
```

## 1. Read context

- `.docs/CONSTITUTION.md` is the supreme reference. Find the articles your change touches
  (use the Table of Contents). If your change contradicts a rule, STOP and propose an
  amendment via the `writing-adrs` skill instead of deviating.
- Read `.docs/PRINCIPLES.md` (Agile, XP, TDD, DDD, Twelve-Factor) and `.docs/STACK.md`
  (services, exact versions, version policy).
- Read the tool guide(s) for the area you touch: `.docs/BACKEND.md`, `.docs/FRONTEND.md`,
  `.docs/DESIGN.md`, `.docs/DOCKER.md`, `.docs/OLLAMA.md`, `.docs/POSTGRES.md`.
- Find your work package in `.project/ROADMAP.md` and its file in `.project/execution/`;
  implement one user story at a time and tick its acceptance criteria.
- Read every related ADR (registry: `.docs/adr/index.md`).

## 2. Topic skills

| If the change touches…                                     | Load skill                 |
| ---------------------------------------------------------- | -------------------------- |
| Board columns, transitions, WIP, review gate, assignment   | `enforcing-kanban-workflow` |
| Agent roles, prompts, toolsets, memory, PM chat            | `authoring-office-agents`  |
| Events, projections, work log, audit                       | `tracing-events`           |
| Office canvas, sprites, pathfinding, choreographies        | `building-office-scene`    |
| Any DOM UI, colors, fonts, icons, windows                  | `designing-amiga-ui`       |
| A significant/irreversible decision                        | `writing-adrs`             |

## 3. Slice the work

- One vertical slice per change. If the change needs > ~400 lines of non-test code, split it.
- Write acceptance criteria before code. Map each criterion to at least one test.

## 4–5. Test-first

- Domain (`services/core/src/virtual_office/domain`): pytest, Given events / When command /
  Then events or domain error. No I/O, no clock, no randomness — inject them. Hypothesis for
  invariants.
- Application: Pydantic AI `TestModel`/`FunctionModel` and a fake clock. Never call a real
  LLM in tests. Integration tests use real Postgres via testcontainers.
- Frontend: Vitest + @vue/test-utils; office engine with deterministic seed and fast-check;
  test event → choreography mapping.
- E2E (Playwright): only for the scenarios listed in Constitution Appendix E.

## 6. Docs

- New domain term → add to Constitution Article II (Glossary) — this is a PATCH amendment
  (clarification) and still needs the Amendment Log line.
- New Markdown file in `.docs/` (including every new ADR) → reference it in `AGENTS.md`
  "Documentation index" with a "When to use it" description.
- New skill → reference it in `AGENTS.md` "Skills index".

## 7. Quality gate

Run every gate of Constitution §18.2, inside the dockerized toolchain (nothing installed on
the host):

- Python services: ruff check, ruff format --check, mypy --strict, import-linter, pytest with
  coverage;
- frontend: eslint, prettier --check, vue-tsc, vitest with coverage, OpenAPI type drift check;
- whole system: `docker compose up --build` healthy, Playwright E2E + visual regression;
- repository: `no-latest` check (STACK.md §1).

All must pass. Coverage thresholds: domain ≥ 95 %, application ≥ 90 %, others ≥ 70 %.
If a script does not exist yet, say so explicitly in your report — never claim a gate passed
when it was not run.

## 8. Commit

- Conventional Commits, English, imperative, subject ≤ 72 chars:
  `feat(domain): enforce TODO WIP limit on pulls`
- Body: what and why, plus `Refs: Constitution §8.6, ADR-0004`.

## Code conventions (quick reference)

- Python: mypy strict, ruff, `snake_case` modules, frozen value objects, no `Any`.
- TypeScript: strict, `noUncheckedIndexedAccess`, no `any`; `kebab-case.ts` files,
  `PascalCase.vue` SFCs with `<script setup lang="ts">`.
- UTC ISO 8601 dates, ULID ids. Config only via environment variables (Twelve-Factor).
- Dependency rule in `core`: `domain` ← `application` ← `agents` ← `infrastructure` / `api`;
  frontend `office-engine` imports neither Vue nor PixiJS.
- New dependency: latest stable, exact pin, never `latest`; update STACK.md (ADR if it
  replaces a tool).
- Everything in English (Constitution Article XIX).
