# AGENTS.md — Virtual Office

Entry point for every contributor, human or AI coding agent. Read this file first, then the
documents it references.

## What this project is

**Virtual Office** is a virtual office of AI agents working on per-project Kanban boards,
presented as a dashboard called **My Workbench** with Amiga 500 Workbench graphics. The user
writes notes; the Project Manager agent turns them into Backlog cards, pulls them into TODO
(max 3), and assigns them to Developers, the Architect or the Designer; QA reviews and moves
cards to DONE or back to TODO. Support triages bug reports. Agents walk around a top-down
pixel-art office as work changes hands. Everything is event-sourced and traceable, decisions
are recorded as ADRs, and the user can chat with the PM about any work.

## Rule zero — always English

**Everything in this repository MUST be written in English**: code, identifiers, comments,
documentation, ADRs, commit messages, PR descriptions, UI copy, log messages, prompts and agent
outputs. This applies even when the instructions you receive are written in another language.
(Constitution Article XIX.)

## Rules for contributors

1. **The Constitution is supreme.** Precedence: Constitution > accepted ADRs > STACK.md and
   PRINCIPLES.md > tool guides (BACKEND, FRONTEND, DESIGN, DOCKER, OLLAMA, POSTGRES) >
   AGENTS.md > skills > other docs > code comments.
2. **Never silently deviate.** If a rule blocks necessary work, stop and propose an amendment
   through an ADR (skill `writing-adrs`).
3. **Start every coding task with the `delivering-features` skill**, then load the topic
   skills and the tool guides it points to.
4. **Work from the roadmap:** pick a user story from the current work package in
   `.project/execution/`, one story at a time.
5. **Work the way PRINCIPLES.md says:** Agile, XP, TDD, DDD, Twelve-Factor, technical
   excellence.
6. **Use only what STACK.md allows:** everything dockerized, latest stable versions, exact
   pins, never obsolete libraries, never `latest`.
7. **No audio, ever.** Virtual Office never produces sound (Constitution §14.10).
8. **Workflow rules live in the domain** of the `core` service, never only in prompts or UI.
9. **Every state change is a domain event**; never mutate state directly; never rewrite events.
10. **The office scene is a projection**: it never produces domain state and never delays it.
11. **Significant decisions need an ADR**, registered in the ADR registry.
12. **Every file in `.docs/` MUST be listed in the Documentation index below**, with a "When to
    use" description. Adding, renaming or removing a file in `.docs/` without updating this
    index is a broken change. The same applies to skills (Skills index) and to roadmap files
    (Project plan).
13. **Track progress in the execution files.** Every file in `.project/execution/` has a status
    `READY`, `PROCESSING` or `DONE`; every user story is a checklist that starts unchecked
    (`- [ ]`) and is checked (`- [x]`) as it is worked. Update status and checkboxes in the same
    PR as the work.
14. **Write an ADR after every user story and every work package.** A completed story records
    its decisions in a repository ADR (`.docs/adr/`, registered in `.docs/adr/index.md`) and
    writes the ADR id on its story line; a story without decisions of its own references the
    WP closing ADR. Every completed WP gets a WP closing ADR. Each new ADR is also added to the
    Documentation index below (rule 12).
15. **Report honestly**: never claim a quality gate passed if it was not run.
16. **Conventional Commits**, English, imperative, subject ≤ 72 chars.

## Documentation index (`.docs/`)

### Foundations

| Document | What it is | When to use it |
| -------- | ---------- | -------------- |
| [`.docs/CONSTITUTION.md`](.docs/CONSTITUTION.md) | Supreme reference: vision, roles, Kanban rules, agents, traceability, office view, design principles, architecture, quality, governance, acceptance scenarios | Before any change, to find the rules that apply; whenever two documents disagree; to look up domain terms (Glossary), events (Appendix B), choreographies (Appendix C), scenarios (Appendix E) |
| [`.docs/PRINCIPLES.md`](.docs/PRINCIPLES.md) | How we work: Agile, XP, TDD, DDD, Twelve-Factor, technical excellence | When planning or slicing work, writing tests, modeling the domain, deciding where code belongs, reviewing a PR |
| [`.docs/STACK.md`](.docs/STACK.md) | Services, frameworks, libraries and exact versions; version policy; graphics library decision | Before adding or updating any dependency, image or tool; when you need a version number; when choosing how to implement something technical |

### Tool guides

| Document | What it is | When to use it |
| -------- | ---------- | -------------- |
| [`.docs/BACKEND.md`](.docs/BACKEND.md) | Standards for Python services: layout, layering, Pydantic, FastAPI, async, Pydantic AI agents, logging, tests | Whenever you write or review code in `services/core` or `services/catalog` (domain, application, API, agents, infrastructure) |
| [`.docs/FRONTEND.md`](.docs/FRONTEND.md) | Standards for the Vue/TypeScript SPA: layout, boundaries, SFC shape, Pinia, API/WebSocket clients, styling, office engine/renderer code rules, tests | Whenever you write or review code in `frontend/` |
| [`.docs/DESIGN.md`](.docs/DESIGN.md) | Amiga 500 design specification: tokens, measures, typography, components, icons, sprites, tiles, animation timing, asset pipeline, copy, no audio | Whenever you create or change anything visible: UI components, layouts, colors, icons, pixel art, animations, UI text |
| [`.docs/DOCKER.md`](.docs/DOCKER.md) | Dockerfile and Compose standards, image tags, security defaults, everyday commands, CI usage | When touching any Dockerfile, compose file, `.env.example`, container configuration, or when you need to run, test or debug the stack |
| [`.docs/OLLAMA.md`](.docs/OLLAMA.md) | Ollama service, model pinning and lock, role → model assignment, how `core` calls models, fake mode, evals, platforms | When adding/changing an LLM model or role assignment, tuning inference, debugging agent runs, or running evaluations |
| [`.docs/POSTGRES.md`](.docs/POSTGRES.md) | Databases, roles, schemas, naming, event store DDL, SQLAlchemy usage, Alembic migrations, indexing, backups | When creating tables or migrations, writing queries, touching the event store or projections, or managing backups |

### Architecture Decision Records

| Document | What it is | When to use it |
| -------- | ---------- | -------------- |
| [`.docs/adr/index.md`](.docs/adr/index.md) | **ADR registry** with the status of every repository ADR | To check which decisions are in force before designing anything; to take the next ADR number |
| [`.docs/adr/0000-adr-template.md`](.docs/adr/0000-adr-template.md) | Template for new repository ADRs | When writing a new ADR (copy it) |
| [`.docs/adr/0001-record-architecture-decisions.md`](.docs/adr/0001-record-architecture-decisions.md) | ADR-0001: use ADRs and ratify the Constitution | When unsure whether a decision needs an ADR or how amendments work |
| [`.docs/adr/0002-technology-stack.md`](.docs/adr/0002-technology-stack.md) | ADR-0002: technology stack and its rationale | When questioning or proposing to replace a framework, service or library |
| [`.docs/adr/0003-amend-constitution-no-audio-and-delivery-tracking.md`](.docs/adr/0003-amend-constitution-no-audio-and-delivery-tracking.md) | ADR-0003: no audio, roadmap/execution tracking, ADR after every story and WP | When wondering why sound is forbidden, how progress is tracked, or when an ADR is required |
| [`.docs/adr/0004-per-service-python-projects.md`](.docs/adr/0004-per-service-python-projects.md) | ADR-0004: self-contained subprojects (own manifest, lock, Dockerfile, build context); only `docker-compose.yml` and `Makefile` at the root | Before adding any file at the repository root, a Python/Node manifest, a Dockerfile or a compose build context; when wondering why there is no root uv workspace |
| [`.docs/adr/0005-us-01-01-root-compose-and-makefile-first.md`](.docs/adr/0005-us-01-01-root-compose-and-makefile-first.md) | ADR-0005: root `docker-compose.yml` and `Makefile` exist from US-01.01; each scaffold story adds its Dockerfile and compose service; WP02 hardens | When adding a subproject or a service to compose, or changing the `Makefile` |
| [`.docs/adr/0006-us-01-02-core-settings-and-app-factory.md`](.docs/adr/0006-us-01-02-core-settings-and-app-factory.md) | ADR-0006: `VO_*` names in settings errors, `create_app` factory started with `uvicorn --factory`, `uv_build` backend, temporary compose defaults | When touching `Settings`, the app factory or uvicorn entrypoint, a service build backend, or the core compose entry |
| [`.docs/adr/0007-amend-constitution-rename-agents-catalog-to-catalog.md`](.docs/adr/0007-amend-constitution-rename-agents-catalog-to-catalog.md) | ADR-0007: the `agents-catalog` service is named `catalog` everywhere (folder, package, image, compose); Constitution v3.1.2 | When wondering why accepted ADR-0004 still says `agents-catalog`, or when configuring coverage for the `catalog` package |
| [`.docs/adr/0008-us-01-03-catalog-mirrors-core-with-minimal-settings.md`](.docs/adr/0008-us-01-03-catalog-mirrors-core-with-minimal-settings.md) | ADR-0008: `catalog` mirrors `core` file by file, settings only `VO_DATABASE_URL`/`VO_LOG_LEVEL`, `UV_CACHE_DIR` in dev images | When touching the catalog `Settings`, Dockerfile or compose entry, or when `uv` fails in a dev image |

## Project plan (`.project/`)

| Document | What it is | When to use it |
| -------- | ---------- | -------------- |
| [`.project/ROADMAP.md`](.project/ROADMAP.md) | Milestones M0–M6, work packages WP01–WP24, detailed deliverables and objectives | To know what to build next, why, and how a WP fits the whole; before starting or re-scoping any work |
| [`.project/execution/`](.project/execution/) | One file per work package (`wpNN-<slug>.md`) with user stories, acceptance criteria, tasks and tests | When implementing: pick the next Ready story of the current WP and follow it |
| `.project/execution/wpNN-<slug>.review.md` | Code review notes of a WP, one section per story, one round per review (written by `/feature-review`) | When reworking a story after review, or checking whether a story can be closed |

Work package files:
[WP01](.project/execution/wp01-repository-and-toolchain.md) ·
[WP02](.project/execution/wp02-containerized-platform.md) ·
[WP03](.project/execution/wp03-continuous-integration.md) ·
[WP04](.project/execution/wp04-event-store-and-persistence.md) ·
[WP05](.project/execution/wp05-kanban-domain.md) ·
[WP06](.project/execution/wp06-board-api-and-realtime.md) ·
[WP07](.project/execution/wp07-amiga-ui-kit.md) ·
[WP08](.project/execution/wp08-workbench-shell-and-board-ui.md) ·
[WP09](.project/execution/wp09-staff-and-character-catalog.md) ·
[WP10](.project/execution/wp10-logbook-and-work-log.md) ·
[WP11](.project/execution/wp11-project-adrs.md) ·
[WP12](.project/execution/wp12-pixel-art-and-assets.md) ·
[WP13](.project/execution/wp13-office-engine.md) ·
[WP14](.project/execution/wp14-office-renderer-and-view.md) ·
[WP15](.project/execution/wp15-agent-runtime.md) ·
[WP16](.project/execution/wp16-note-intake.md) ·
[WP17](.project/execution/wp17-orchestrator-and-assignment.md) ·
[WP18](.project/execution/wp18-pm-chat.md) ·
[WP19](.project/execution/wp19-project-workspaces.md) ·
[WP20](.project/execution/wp20-executor-agents.md) ·
[WP21](.project/execution/wp21-support-triage.md) ·
[WP22](.project/execution/wp22-qa-review-gate.md) ·
[WP23](.project/execution/wp23-polish-and-preferences.md) ·
[WP24](.project/execution/wp24-hardening-and-release.md)

## Claude Code commands (`.claude/commands/`)

Slash commands that run the story workflow end to end. They are user-invoked only.

| Command | What it does |
| ------- | ------------ |
| [`/feature-impl [US-NN.MM]`](.claude/commands/feature-impl.md) | Picks the next unchecked story (or the given one), opens `feat/us-NN-MM-<slug>`, implements it test-first with Conventional Commits |
| [`/feature-review`](.claude/commands/feature-review.md) | Reviews the current feature branch and writes the findings to `.project/execution/wpNN-<slug>.review.md` |
| [`/feature-rework [R1 …]`](.claude/commands/feature-rework.md) | Fixes the open review findings test-first and marks them resolved |
| [`/feature-close`](.claude/commands/feature-close.md) | Runs the quality gate, writes the story ADR (and WP closing ADR), ticks the story, updates the WP status, opens the PR |
| [`/feature-auto [US-NN.MM]`](.claude/commands/feature-auto.md) | Runs impl → review → rework → close and merges the PR |

## Skills index (`.agents/skills/`)

Skills live only in [`.agents/skills/`](.agents/skills/), one folder per skill with a
`SKILL.md` (Agent Skills format: YAML frontmatter `name` + `description`, then instructions).

| Skill | When to use it |
| ----- | -------------- |
| [`delivering-features`](.agents/skills/delivering-features/SKILL.md) | At the start of every coding task: context, slicing, TDD, gates, docs, commits |
| [`enforcing-kanban-workflow`](.agents/skills/enforcing-kanban-workflow/SKILL.md) | Columns, transitions, WIP limit, review gate, assignment, board UI behavior |
| [`authoring-office-agents`](.agents/skills/authoring-office-agents/SKILL.md) | Roles, prompts, Pydantic AI agents, toolsets, memory, PM chat, staff |
| [`tracing-events`](.agents/skills/tracing-events/SKILL.md) | Domain events, projections, work log, LLM/tool tracing, realtime |
| [`building-office-scene`](.agents/skills/building-office-scene/SKILL.md) | Office canvas, tile map, sprites, pathfinding, choreographies |
| [`designing-amiga-ui`](.agents/skills/designing-amiga-ui/SKILL.md) | Any Vue UI, palette, typography, components, assets, accessibility |
| [`writing-adrs`](.agents/skills/writing-adrs/SKILL.md) | Repository ADRs, ADR registry, Constitution amendments, Project ADRs |
