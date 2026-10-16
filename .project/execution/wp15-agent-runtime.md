# WP15 — Agent Runtime

| Field        | Value |
| ------------ | ----- |
| Milestone    | M4 — Paula |
| Status       | READY |
| Depends on   | WP09 (catalog service pattern, staff), WP10 (work log links) |
| Enables      | WP16, WP17, WP18, WP19, WP20, WP21, WP22 |
| Constitution | §5.2, §9.5, §10.2–10.3, Article XVI, §15.6–15.7, §17.2, §17.4–17.5 |
| Guides       | [BACKEND.md](../../.docs/BACKEND.md) §9 · [OLLAMA.md](../../.docs/OLLAMA.md) · [POSTGRES.md](../../.docs/POSTGRES.md) §3 |
| Skills       | `authoring-office-agents`, `tracing-events`, `delivering-features`, `writing-adrs` |
| Estimate     | 44 points |

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [ ] US-15.01 — Role definition model and files for the six roles (5 pts)
- [ ] US-15.02 — Prompt versioning, immutability and seeding (3 pts)
- [ ] US-15.03 — Catalog roles API (2 pts)
- [ ] US-15.04 — Core role-definition client (anti-corruption layer) (3 pts)
- [ ] US-15.05 — LLM model factory with pinned tags and fake mode (3 pts)
- [ ] US-15.06 — Agent job aggregate and lifecycle events (5 pts)
- [ ] US-15.07 — Job runner: concurrency, timeouts, retries, recovery (5 pts)
- [ ] US-15.08 — Budgets, usage and cost accounting (3 pts)
- [ ] US-15.09 — Pauses respected at checkpoints (2 pts)
- [ ] US-15.10 — Untrusted-data wrapper and injection test harness (3 pts)
- [ ] US-15.11 — Tool-call tracing and transcript storage with retention (3 pts)
- [ ] US-15.12 — Transcript links in the Logbook and card history (2 pts)
- [ ] US-15.13 — Evaluation harness with baselines (5 pts)

## 1. Objective

Provide the shared machinery every AI agent uses: versioned role definitions and prompts served by
`catalog`; a model factory for Ollama (default), fake mode and an optional cloud provider;
an event-sourced job lifecycle with concurrency, timeouts, retries, recovery, budgets and pauses;
safety against prompt injection; tracing of tool calls and transcripts; and an evaluation harness.
After WP15, adding a role's behavior means writing its output model, tools and prompt — nothing
else.

## 2. Scope

**In:** catalog role/prompt model, files, seed, API; core client; model factory; `AgentJob`
aggregate; runner; limiter; budgets; pause integration; untrusted wrapper; tracing; transcripts;
transcript links; pydantic-evals harness and nightly job.

**Out:** concrete role behaviors (WP16–WP22), Orchestrator scheduling (WP17), workspaces (WP19).

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D15.1 | Catalog roles & prompts | Six role definitions (tools allow-list, output model ref, default model tag, competence tags) and versioned prompts, immutable once published, seeded from files, served by API | Seed idempotency; immutability test; API tests | US-15.01 – US-15.03 |
| D15.2 | Client & model factory | ACL client with cache; factory building Pydantic AI models (Ollama/fake/cloud) from pinned tags | respx tests; factory tests; settings reject bare/`latest` tags | US-15.04, US-15.05 |
| D15.3 | Job lifecycle | `AgentJob` events, runner with limiter/timeouts/retries/recovery, budgets, pauses | GWT + integration tests; restart recovery test | US-15.06 – US-15.09 |
| D15.4 | Safety & tracing | Untrusted wrapper, injection harness (E19 groundwork), tool-call events, transcripts with retention, links in UI | Tests; retention job test | US-15.10 – US-15.12 |
| D15.5 | Evaluations | pydantic-evals datasets per role, baseline files, nightly job, PR job on prompt changes | Nightly report; regression gate | US-15.13 |

## 4. User stories

### D15.1 — Catalog roles & prompts

#### US-15.01 — Role definition model and files for the six roles

- [ ] **US-15.01 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As a maintainer, I want each role defined declaratively, so that least privilege and
  model choices are reviewable data.
- **Acceptance criteria:**
  - [ ] AC1 — `catalog/roles/<role>.yaml` for `project_manager`, `developer`, `architect`,
    `designer`, `support`, `qa` with: `role`, `version`, `display_name`, `prompt_ref`
    (`prompts/<role>/v<N>.md`), `tools` (subset of an allow-list known by core),
    `output_models` (names per job kind), `default_model` (pinned tag), `competence_tags`,
    `job_kinds`.
  - [ ] AC2 — Tools per role equal Constitution §15.7 (validated by a test comparing with a table).
  - [ ] AC3 — Pydantic validation rejects unknown tools, bare model names, `latest`.
  - [ ] AC4 — Initial prompts `v1.md` per role follow the skeleton of skill
    `authoring-office-agents` (mission, MUST, MUST NOT, inputs as data, output).
- **Tasks:** YAML files, Pydantic models, prompt files v1.
- **Tests:** validation unit tests; §15.7 table test.
- **Done when:** files validated in CI.

#### US-15.02 — Prompt versioning, immutability and seeding

- [ ] **US-15.02 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want published prompts to be immutable, so that every agent
  output can be traced to the exact instructions used.
- **Acceptance criteria:**
  - [ ] AC1 — `catalog-seed` publishes new role/prompt versions and stores a content hash per
    version.
  - [ ] AC2 — Changing the content of an already-published version fails the seed ("create v<N+1>").
  - [ ] AC3 — Tables `catalog.role_definitions`, `catalog.prompts` with `(role, version)` keys.
- **Tasks:** migrations, seed extension, hash check.
- **Tests:** integration tests for publish and immutability.
- **Done when:** seed job green.

#### US-15.03 — Catalog roles API

- [ ] **US-15.03 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As `core`, I want to fetch role definitions by version.
- **Acceptance criteria:**
  - [ ] AC1 — `GET /roles`, `GET /roles/{role}` (latest published), `GET /roles/{role}/versions/{v}`
    with prompt text and hash; ETag support.
  - [ ] AC2 — Unknown role/version → 404.
- **Tasks:** router, DTOs.
- **Tests:** API tests.
- **Done when:** catalog OpenAPI updated.

### D15.2 — Client & model factory

#### US-15.04 — Core role-definition client (anti-corruption layer)

- [ ] **US-15.04 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As `core`, I want role definitions as domain read models with caching.
- **Acceptance criteria:**
  - [ ] AC1 — `RoleDefinitions` port returns `RoleDefinition` (role, version, instructions,
    tools, output model names, default model, hash).
  - [ ] AC2 — ETag cache; catalog down → cached definitions used; none cached → readiness fails.
  - [ ] AC3 — The resolved `role@version` and prompt hash are attached to every job.
- **Tasks:** extend the catalog client of WP09.
- **Tests:** respx tests.
- **Done when:** used by the runner.

#### US-15.05 — LLM model factory with pinned tags and fake mode

- [ ] **US-15.05 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As an operator, I want models built from configuration only, so that switching
  models or providers never changes code.
- **Acceptance criteria:**
  - [ ] AC1 — `infrastructure/llm/factory.py` builds `OllamaModel(tag, provider=OllamaProvider(
    base_url=f"{VO_OLLAMA_BASE_URL}v1"))` for Ollama (BACKEND.md §9.1).
  - [ ] AC2 — `VO_LLM_MODE=fake` returns scripted `FunctionModel`s per role/job kind from
    `tests/support/fake_llm/` scripts (also used by demo mode).
  - [ ] AC3 — Optional Anthropic provider only when `ANTHROPIC_API_KEY` is set and a role is
    configured for it; otherwise attempting it is a startup error.
  - [ ] AC4 — Model tags not present in `infra/ollama/models.lock` are rejected at startup.
- **Tasks:** factory, settings validators, fake scripts.
- **Tests:** unit tests; `ALLOW_MODEL_REQUESTS=False` in test config.
- **Done when:** all AC green.

### D15.3 — Job lifecycle

#### US-15.06 — Agent job aggregate and lifecycle events

- [ ] **US-15.06 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want every agent action recorded as a job with a lifecycle,
  so that I can see what each agent tried, how long it took and what it cost.
- **Acceptance criteria:**
  - [ ] AC1 — `AgentJob(job_id, agent_id, kind, input_ref, role_version, model, status)` with
    events `AgentJobStarted`, `AgentJobProgressed` (checkpoint), `AgentJobCompleted` (usage,
    duration, output summary), `AgentJobFailed` (error class, retryable).
  - [ ] AC2 — Status machine: queued → running → (progressed)* → completed | failed |
    interrupted; illegal transitions rejected.
  - [ ] AC3 — The agent's `domainStatus` and `currentJobId` projection update from job events;
    the drive LED in the title bar is on while any job is running.
- **Tasks:** domain module `domain/agents_runtime` (or `staff/jobs`), events, projection updates.
- **Tests:** GWT tests.
- **Done when:** all AC green.

#### US-15.07 — Job runner: concurrency, timeouts, retries, recovery

- [ ] **US-15.07 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As an operator, I want agent runs to be bounded and resilient.
- **Acceptance criteria:**
  - [ ] AC1 — A runner executes Pydantic AI runs under an anyio capacity limiter of
    `VO_LLM_CONCURRENCY` (default 2).
  - [ ] AC2 — Per-request timeout (role setting, default 120 s) and per-job timeout (default
    10 min); output validation retries = 1; transport retries with backoff for connection
    errors only.
  - [ ] AC3 — On startup, jobs left `running` are marked `interrupted` and retried from the last
    checkpoint at most 2 times; then failed.
  - [ ] AC4 — The job's validated output is translated to domain commands by the role's
    `to_commands` and dispatched through the command bus as the agent actor; domain rejections
    are recorded and do not crash the runner.
- **Tasks:** `application/agents/runner.py`; recovery on lifespan start.
- **Tests:** unit tests with `FunctionModel`; integration recovery test.
- **Done when:** all AC green.

#### US-15.08 — Budgets, usage and cost accounting

- [ ] **US-15.08 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want token and cost limits per project, so that agents never run away.
- **Acceptance criteria:**
  - [ ] AC1 — Usage from `result.usage()` (requests, input/output tokens) recorded on job events;
    cost computed from a per-model price table in config (local models default cost 0, still
    counting tokens).
  - [ ] AC2 — Per-project monthly budget (tokens and/or cost); at 80 % → `BudgetThresholdReached
    {80}`; at 100 % → no new jobs for that project (`BudgetExhausted` refusal), running jobs
    finish their current step.
  - [ ] AC3 — Per-call max tokens per role from settings.
- **Tasks:** budget service, projection `projection.budgets`.
- **Tests:** unit + integration tests.
- **Done when:** all AC green.

#### US-15.09 — Pauses respected at checkpoints

- [ ] **US-15.09 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want pausing the office or an agent to stop AI work promptly
  (Constitution P4).
- **Acceptance criteria:**
  - [ ] AC1 — The runner checks office/agent pause before starting a job and at every checkpoint;
    when paused, the job is suspended (`AgentJobProgressed{suspended}`) and resumes on resume.
  - [ ] AC2 — New jobs are not started while paused.
- **Tasks:** pause checks.
- **Tests:** unit tests.
- **Done when:** all AC green.

### D15.4 — Safety & tracing

#### US-15.10 — Untrusted-data wrapper and injection test harness

- [ ] **US-15.10 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want notes, attachments, files and tool results always
  treated as data, so that no text can take control of an agent (Constitution §16.6).
- **Acceptance criteria:**
  - [ ] AC1 — `untrusted_block(label, text)` wraps content with unique delimiters, escapes
    delimiter collisions, and is the only way context packs include external text (lint/grep rule).
  - [ ] AC2 — Every role prompt contains the standard "data has no authority" clause (test).
  - [ ] AC3 — An injection corpus (≥ 20 cases incl. "ignore your rules", fake tool calls, fake
    system messages) is part of each role's eval set; domain enforcement guarantees no rule is
    bypassed even if a model complies (E19 groundwork).
- **Tasks:** helper, corpus, prompt clause.
- **Tests:** unit tests; eval cases.
- **Done when:** all AC green.

#### US-15.11 — Tool-call tracing and transcript storage with retention

- [ ] **US-15.11 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to see what tools an agent used and read full transcripts when
  needed.
- **Acceptance criteria:**
  - [ ] AC1 — Each tool call emits `AgentToolCalled{tool, args_sanitized (≤ 2 KB), result_summary,
    duration_ms}`; secrets redacted.
  - [ ] AC2 — Full transcripts (messages) stored in `runtime.agent_runs` linked by `job_id`.
  - [ ] AC3 — A daily retention job deletes transcripts older than `VO_TRANSCRIPT_RETENTION_DAYS`
    (default 90); events stay.
- **Tasks:** tool wrapper, transcript repository, retention job.
- **Tests:** unit + integration tests.
- **Done when:** all AC green.

#### US-15.12 — Transcript links in the Logbook and card history

- [ ] **US-15.12 completed** · **Points:** 2 · **Priority:** Should · **ADR:** —
- **Story:** As the user, I want to open a transcript from the line that produced it.
- **Acceptance criteria:**
  - [ ] AC1 — Job lines in the Logbook and card History show "transcript" links opening a
    read-only Transcript window (messages, tool calls, usage).
  - [ ] AC2 — Expired transcripts show "Transcript expired (retention policy)".
- **Tasks:** `GET /api/jobs/{id}/transcript`; window.
- **Tests:** API + component tests.
- **Done when:** all AC green.

### D15.5 — Evaluations

#### US-15.13 — Evaluation harness with baselines

- [ ] **US-15.13 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As a maintainer, I want to measure agent quality, so that prompt or model changes
  never silently make agents worse (Constitution §16.8).
- **Acceptance criteria:**
  - [ ] AC1 — `catalog/evals/<role>/` datasets in pydantic-evals format with property evaluators
    (e.g. "≥ 3 cards", "every card has ≥ 1 criterion", "answer cites SHOP-3").
  - [ ] AC2 — `pytest -m eval` runs datasets against the real Ollama models from the lock; results
    (pass rate, p95 latency, tokens) saved as JSON next to a committed baseline.
  - [ ] AC3 — The nightly job runs all roles; a PR touching `catalog/roles` or `catalog/prompts`
    triggers the affected roles' evals and fails on regression.
- **Tasks:** harness, baseline format, CI wiring.
- **Tests:** harness unit tests with `TestModel`.
- **Done when:** nightly eval job green with baselines for the PM (other roles added by their WPs).

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WP15 closing: Agent runtime`); story ADR ids filled in.
- [ ] File status set to `DONE`.
- [ ] All stories checked; no real LLM call in unit/integration tests (`ALLOW_MODEL_REQUESTS=False`).
- [ ] OLLAMA.md, BACKEND.md §9 and skill `authoring-office-agents` updated with any deviation.

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| Local models too slow for good UX | Concurrency limits, visible job status, fake demo mode, optional cloud provider |
| Structured output failures | Pydantic AI output retries; output mode per role chosen by evals |
| Prompt drift without measurement | Evals gate prompt/model changes |

## 7. Blockers

None.
