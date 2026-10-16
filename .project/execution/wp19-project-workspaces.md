# WP19 — Project Workspaces

| Field        | Value |
| ------------ | ----- |
| Milestone    | M5 — Chipset |
| Status       | READY |
| Depends on   | WP15 (agent tools tracing), WP02 (compose) |
| Enables      | WP20 (developers write code), WP22 (QA runs checks) |
| Constitution | §5.4, §15.7, §15.8, Article XVII (§17.3–17.4) |
| Guides       | [BACKEND.md](../../.docs/BACKEND.md) §8–9 · [DOCKER.md](../../.docs/DOCKER.md) · [STACK.md](../../.docs/STACK.md) |
| Skills       | `authoring-office-agents`, `delivering-features`, `writing-adrs` |
| Estimate     | 28 points |

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [ ] US-19.01 — Spike: command execution isolation strategy (3 pts)
- [ ] US-19.02 — Workspace settings on projects (3 pts)
- [ ] US-19.03 — Workspace mounting in containers (2 pts)
- [ ] US-19.04 — Sandboxed file port (5 pts)
- [ ] US-19.05 — Git port: branch, commit, diff, status (5 pts)
- [ ] US-19.06 — Code deliverable from git state (2 pts)
- [ ] US-19.07 — Allow-listed command runner (5 pts)
- [ ] US-19.08 — Workspace security test suite (3 pts)

## 1. Objective

Give developer and QA agents a safe place to work on real code: a project may point to a local
git repository; agents read and write files only inside it, work on `vo/<CARD-ID>-<slug>`
branches, commit locally, produce diffs, and run only allow-listed commands with timeouts and
output limits — never pushing, merging or rewriting history (Constitution §15.8).

## 2. Scope

**In:** isolation strategy decision (spike + ADR), workspace settings, mounting, file port, git
port, code deliverable, command runner, security tests.

**Out:** pushing/PRs/deployments (non-goals v1), developer agent behavior (WP20).

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D19.1 | Strategy & settings | ADR choosing how commands are isolated; project workspace settings validated; workspaces mounted read-write only where needed | Accepted ADR; settings tests | US-19.01 – US-19.03 |
| D19.2 | File port | Read/write/list confined to the workspace root; symlinks and traversal rejected; size limits | Security tests | US-19.04 |
| D19.3 | Git port & deliverable | Branch per card, commits, diff, status; no push/merge/rebase; code deliverable assembled from git | Integration tests on a temp repo | US-19.05, US-19.06 |
| D19.4 | Command runner | Allow-listed commands with timeouts, output caps, no network by default, per the ADR | Tests incl. timeout, disallowed command, network denial | US-19.07, US-19.08 |

## 4. User stories

### D19.1 — Strategy & settings

#### US-19.01 — Spike: command execution isolation strategy

- [ ] **US-19.01 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want a deliberate decision on where agent commands run, so
  that running a project's tests never endangers my machine.
- **Acceptance criteria:**
  - [ ] AC1 — A repository ADR compares at least: (a) subprocess inside `core` with restricted
    environment, (b) ephemeral sibling containers via a restricted Docker API proxy, (c) a
    dedicated sandbox runner service (would add a sixth service — requires owner approval and an
    amendment of STACK.md).
  - [ ] AC2 — The ADR evaluates security, toolchain availability for the user's projects,
    complexity, and macOS/Linux support, and recommends one option.
  - [ ] AC3 — The owner accepts or rejects the ADR before US-19.07 starts.
- **Tasks:** time-boxed research (≤ 1 day); prototype of the recommended option.
- **Tests:** prototype smoke test.
- **Done when:** ADR accepted.

#### US-19.02 — Workspace settings on projects

- [ ] **US-19.02 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to attach a local git repository to a project, so that developers
  can work on real code.
- **Acceptance criteria:**
  - [ ] AC1 — `SetProjectWorkspace(path, default_branch, allowed_commands[])` →
    `ProjectSettingsChanged{workspace}`; path relative to `VO_WORKSPACES_ROOT`.
  - [ ] AC2 — Validation: directory exists, is a git repository, default branch exists, path
    inside the root, allowed commands match the command grammar (no shell metacharacters).
  - [ ] AC3 — Projects UI: workspace section in project settings with validation feedback.
- **Tasks:** domain extension, API, UI.
- **Tests:** GWT + API + component tests.
- **Done when:** all AC green.

#### US-19.03 — Workspace mounting in containers

- [ ] **US-19.03 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As an operator, I want workspaces mounted explicitly, so that containers see only the
  repositories I chose.
- **Acceptance criteria:**
  - [ ] AC1 — `docker-compose.yml` mounts `${VO_WORKSPACES_HOST_DIR}` to `/workspaces` in `core` only
    (read-write), documented in DOCKER.md; absent variable → no mount, workspaces disabled.
  - [ ] AC2 — The container user (10001) can read/write; files created keep the host user's
    ownership strategy documented (UID mapping note for macOS/Linux).
- **Tasks:** compose change, docs.
- **Tests:** smoke test with a sample repo.
- **Done when:** all AC green.

### D19.2 — File port

#### US-19.04 — Sandboxed file port

- [ ] **US-19.04 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want agents to touch only files inside the workspace.
- **Acceptance criteria:**
  - [ ] AC1 — `WorkspaceFiles.read(path, max_bytes)`, `write(path, content)`, `list(dir)`,
    `exists(path)` resolve paths with `realpath` and reject anything outside the root
    (`PathOutsideWorkspace`).
  - [ ] AC2 — Symlinks pointing outside are rejected; `.git/` internals are not writable.
  - [ ] AC3 — Limits: read ≤ 1 MB per call, write ≤ 512 KB per file, ≤ 200 files changed per job.
  - [ ] AC4 — Every call is traced as a tool call (path, bytes, result).
- **Tasks:** port + adapter.
- **Tests:** unit tests with tmp dirs; traversal fixtures (`../`, absolute, symlink, unicode tricks).
- **Done when:** all AC green.

### D19.3 — Git port & deliverable

#### US-19.05 — Git port: branch, commit, diff, status

- [ ] **US-19.05 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As a developer agent, I want my own branch per card and local commits, so that my work
  is isolated and reviewable.
- **Acceptance criteria:**
  - [ ] AC1 — `create_or_checkout_branch(card)` → `vo/<CARD-ID>-<slug>` from the default branch;
    re-entry on rework checks out the same branch.
  - [ ] AC2 — `commit(message)` with author `"<Agent name> (Virtual Office) <agent-id@virtual-office.local>"`;
    Conventional Commit message; returns SHA.
  - [ ] AC3 — `diff(base)` and `status()` return bounded outputs.
  - [ ] AC4 — `push`, `merge`, `rebase`, `reset --hard`, `filter-branch`, force operations are not
    exposed and are blocked if attempted through the runner.
  - [ ] AC5 — Operations run via `anyio.run_process` with a timeout; git binary pinned in the image.
- **Tasks:** port + adapter; git config isolation (`GIT_CONFIG_NOSYSTEM`, no hooks).
- **Tests:** integration tests on temp repos.
- **Done when:** all AC green.

#### US-19.06 — Code deliverable from git state

- [ ] **US-19.06 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the reviewer, I want a code deliverable with branch, commits, diff summary and
  check results.
- **Acceptance criteria:**
  - [ ] AC1 — `build_code_deliverable(card)` returns `{kind: code, branch, commits[], diffSummary,
    checks[]}` (Appendix A).
  - [ ] AC2 — The diff summary lists files changed with +/− counts and is ≤ 4 KB; the full diff is
    available through a tool call for QA.
- **Tasks:** builder.
- **Tests:** unit tests.
- **Done when:** used by WP20.

### D19.4 — Command runner

#### US-19.07 — Allow-listed command runner

- [ ] **US-19.07 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want agents to run only the commands I allowed, safely.
- **Acceptance criteria:**
  - [ ] AC1 — Implemented per the US-19.01 ADR; commands are given as argument vectors (no shell),
    matched exactly against the project's allow-list.
  - [ ] AC2 — Timeout default 5 min, output capped at 1 MB (truncated with marker), environment
    reduced to an explicit allow-list (no secrets), network disabled by default.
  - [ ] AC3 — Results `{command, exitCode, summary, durationMs}` stored as `CheckResult` and traced.
  - [ ] AC4 — Disallowed command → `CommandNotAllowed` (tool error the model can see) and a
    refused line in the Logbook.
- **Tasks:** runner adapter; environment filter; network isolation per ADR.
- **Tests:** integration tests (timeout, disallowed, output cap, env leakage, network denial).
- **Done when:** all AC green.

#### US-19.08 — Workspace security test suite

- [ ] **US-19.08 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want a dedicated security suite for workspaces.
- **Acceptance criteria:**
  - [ ] AC1 — Tests for path traversal, symlink escape, `.git` tampering, command injection via
    arguments, env-variable exfiltration, oversized outputs, fork bombs (process limit), long
    runs (timeout).
  - [ ] AC2 — Suite runs in CI (`-m security`) and nightly.
- **Tasks:** test suite.
- **Tests:** itself.
- **Done when:** suite green and required.

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WP19 closing: Project workspaces`); isolation ADR accepted; story ADR ids filled in.
- [ ] File status set to `DONE`.
- [ ] All stories checked; security suite green; DOCKER.md and Constitution §15.8 consistent.

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| Isolation choice adds complexity or a sixth service | Spike first; owner decision recorded |
| Toolchains missing for user projects | ADR addresses toolchain provisioning (e.g. per-project runner image) |
| File ownership issues on bind mounts | Documented UID mapping; tests on Linux and macOS |

## 7. Blockers

None.
