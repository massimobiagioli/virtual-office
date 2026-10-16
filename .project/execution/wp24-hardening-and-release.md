# WP24 — Hardening & Release

| Field        | Value |
| ------------ | ----- |
| Milestone    | M6 — Demo Scene |
| Status       | READY |
| Depends on   | WP23 (and all previous WPs) |
| Enables      | v1.0.0 |
| Constitution | §4.3.9 (data), Article XVII, §18.2, §18.6, Appendix E (E1–E20), success criteria S1–S7, Article XXII |
| Guides       | All tool guides; [PRINCIPLES.md](../../.docs/PRINCIPLES.md) |
| Skills       | `delivering-features`, `tracing-events`, `writing-adrs` |
| Estimate     | 37 points |

## 0. Story checklist

Status legend: file status `READY` → `PROCESSING` → `DONE`; check a story only when all its
acceptance criteria and tasks are checked, merged, and its ADR is written.

- [ ] US-24.01 — Export everything (3 pts)
- [ ] US-24.02 — Import into an empty office (5 pts)
- [ ] US-24.03 — Full wipe with typed confirmation (2 pts)
- [ ] US-24.04 — Performance budget suite as gates (5 pts)
- [ ] US-24.05 — Performance fixes from findings (3 pts)
- [ ] US-24.06 — Accessibility audit and fixes (3 pts)
- [ ] US-24.07 — Security review and fixes (5 pts)
- [ ] US-24.08 — Backup and restore drill (2 pts)
- [ ] US-24.09 — Complete acceptance suite E1–E20 (5 pts)
- [ ] US-24.10 — Documentation pass (2 pts)
- [ ] US-24.11 — Release v1.0.0 (2 pts)

## 1. Objective

Make Virtual Office v1.0.0 trustworthy: data portability (export, import, wipe), enforced
performance budgets, audited accessibility and security, a proven backup/restore, the complete
Appendix E acceptance suite in CI, consistent documentation, and a clean release.

## 2. Scope

**In:** data commands and UI; performance gates; audits and fixes; restore drill; E1–E20 suite;
docs pass; release process.

**Out:** new features (post-v1 backlog).

## 3. Deliverables

| ID    | Deliverable | Precise objective | Acceptance evidence | Stories |
| ----- | ----------- | ----------------- | ------------------- | ------- |
| D24.1 | Data portability | Export (events, attachments, settings), import into an empty office with validation, full wipe | Round-trip test: export → wipe → import → identical projections | US-24.01 – US-24.03 |
| D24.2 | Performance | All §18.6 budgets measured and gating; fixes | Perf suite green in CI/nightly | US-24.04, US-24.05 |
| D24.3 | Audits | Accessibility and security audits with fixes; backup/restore drill | Audit reports; drill log | US-24.06 – US-24.08 |
| D24.4 | Release | E1–E20 in CI; docs consistent; v1.0.0 tagged with notes and demo | Green suite; tag; recording | US-24.09 – US-24.11 |

## 4. User stories

### D24.1 — Data portability

#### US-24.01 — Export everything

- [ ] **US-24.01 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to export my whole office, so that I own my data.
- **Acceptance criteria:**
  - [ ] AC1 — `GET /api/export` streams a `.tar` (or zip) containing `events.ndjson` (all events,
    original envelopes), `attachments/`, `catalog-customizations.json` (role model assignments),
    and `manifest.json` (versions, counts, hash).
  - [ ] AC2 — Transcripts are excluded by default (option to include, with a warning).
  - [ ] AC3 — Preferences → Data → *Export everything* button.
- **Tasks:** streaming exporter; UI.
- **Tests:** integration tests; manifest hash verification.
- **Done when:** all AC green.

#### US-24.02 — Import into an empty office

- [ ] **US-24.02 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to restore an export on a new machine.
- **Acceptance criteria:**
  - [ ] AC1 — `POST /api/import` accepts an export only into an empty event store; validates the
    manifest hash and event schema versions (upcasters applied).
  - [ ] AC2 — Events are appended preserving ids, order and envelopes; projections rebuilt.
  - [ ] AC3 — Round-trip test: export → wipe → import → projections identical (row by row).
- **Tasks:** importer (one-off job and API), validation.
- **Tests:** round-trip integration test.
- **Done when:** all AC green.

#### US-24.03 — Full wipe with typed confirmation

- [ ] **US-24.03 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want to reset the office completely when I decide to.
- **Acceptance criteria:**
  - [ ] AC1 — Preferences → Data → *Reset office* requires typing `RESET MY OFFICE`.
  - [ ] AC2 — Wipe runs as a one-off admin job (owner role): truncates events (migration-level
    bypass of the append-only trigger, logged), projections, runtime, attachments; then the office
    is re-initialized.
  - [ ] AC3 — The UI never offers wipe from PM chat (Constitution §11.3).
- **Tasks:** admin job, UI.
- **Tests:** integration test.
- **Done when:** all AC green.

### D24.2 — Performance

#### US-24.04 — Performance budget suite as gates

- [ ] **US-24.04 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want the budgets of Constitution §18.6 enforced, not hoped for.
- **Acceptance criteria:**
  - [ ] AC1 — Measured and gated: initial JS gz ≤ 350 KB; time to interactive ≤ 2 s (local);
    event → screen p95 ≤ 500 ms; UI interaction ≤ 100 ms; office 60 fps with 7 agents; command
    handling p95 ≤ 50 ms.
  - [ ] AC2 — Results published in job summaries with trend comparison; regression > 10 % fails.
- **Tasks:** consolidate measurement harnesses from WP06/WP08/WP14; bundle-size check.
- **Tests:** itself.
- **Done when:** suite required (PR: quick subset; nightly: full).

#### US-24.05 — Performance fixes from findings

- [ ] **US-24.05 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As the user, I want a fast office.
- **Acceptance criteria:**
  - [ ] AC1 — Every budget violation found by US-24.04 is fixed or recorded in an ADR with an
    accepted exception.
  - [ ] AC2 — Decision on snapshots/async projections documented (WP04 open question).
- **Tasks:** profiling, fixes.
- **Tests:** perf suite.
- **Done when:** suite green.

### D24.3 — Audits

#### US-24.06 — Accessibility audit and fixes

- [ ] **US-24.06 completed** · **Points:** 3 · **Priority:** Must · **ADR:** —
- **Story:** As a user with disabilities, I want the whole app usable (Constitution §14.9).
- **Acceptance criteria:**
  - [ ] AC1 — Keyboard-only walkthrough of every window and the full demo flow; screen-reader
    walkthrough (VoiceOver and NVDA) of key flows; axe zero violations.
  - [ ] AC2 — Findings fixed or recorded with an ADR exception; report in `.docs/audits/` (indexed in
    AGENTS.md).
- **Tasks:** audit, fixes, report.
- **Tests:** E2E keyboard suites.
- **Done when:** report merged.

#### US-24.07 — Security review and fixes

- [ ] **US-24.07 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want v1.0.0 reviewed for security (Constitution Article XVII).
- **Acceptance criteria:**
  - [ ] AC1 — Threat model (STRIDE) covering services, ports, workspace sandbox, LLM injection,
    secrets, supply chain; report in `.docs/audits/security-v1.md`.
  - [ ] AC2 — Prompt-injection red-team run against every role with the injection corpus (E19 and
    beyond); no rule bypass possible.
  - [ ] AC3 — Zero fixable HIGH/CRITICAL in dependencies and images; all ports bound to
    `127.0.0.1`; containers non-root with dropped capabilities.
  - [ ] AC4 — Findings fixed or accepted via ADR.
- **Tasks:** review, red team, fixes.
- **Tests:** security suite extended.
- **Done when:** report merged.

#### US-24.08 — Backup and restore drill

- [ ] **US-24.08 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As an operator, I want to know restores work before I need them.
- **Acceptance criteria:**
  - [ ] AC1 — `backup` job produces dumps of `core` and `catalog`; restore script on a fresh stack
    recreates the office; projections rebuilt; demo project intact.
  - [ ] AC2 — Drill steps and timings documented in POSTGRES.md §10.
- **Tasks:** drill, docs.
- **Tests:** scripted drill in nightly.
- **Done when:** drill green.

### D24.4 — Release

#### US-24.09 — Complete acceptance suite E1–E20

- [ ] **US-24.09 completed** · **Points:** 5 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want every Constitution scenario automated and green.
- **Acceptance criteria:**
  - [ ] AC1 — A traceability table maps E1–E20 to test ids; a CI check fails if a scenario has no
    test.
  - [ ] AC2 — All scenarios green in CI (fake LLM) and the real-model subset green nightly.
  - [ ] AC3 — Success criteria S1–S7 measured and reported in the release notes.
- **Tasks:** fill gaps, mapping file `e2e/acceptance-map.json`, check script.
- **Tests:** itself.
- **Done when:** all green.

#### US-24.10 — Documentation pass

- [ ] **US-24.10 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As a new contributor, I want documentation that matches reality.
- **Acceptance criteria:**
  - [ ] AC1 — Every `.docs/` file reviewed against the code; outdated statements fixed; Constitution
    amendment log complete; ADR registry complete; AGENTS.md index complete with "when to use".
  - [ ] AC2 — `README.md` quickstart (clone, `.env`, `docker compose up`) verified on a clean machine.
- **Tasks:** review, fixes.
- **Tests:** link check; quickstart run.
- **Done when:** all AC green.

#### US-24.11 — Release v1.0.0

- [ ] **US-24.11 completed** · **Points:** 2 · **Priority:** Must · **ADR:** —
- **Story:** As the product owner, I want a clean, documented v1.0.0.
- **Acceptance criteria:**
  - [ ] AC1 — `CHANGELOG.md` complete (Keep a Changelog); release notes with S1–S7 results, known
    issues, upgrade notes.
  - [ ] AC2 — Tag `v1.0.0`; images built from the tag; demo recording attached.
  - [ ] AC3 — Final retrospective recorded; post-v1 backlog captured as notes for the PM.
- **Tasks:** release steps.
- **Tests:** release checklist.
- **Done when:** tag pushed (by the owner).

## 5. WP Definition of Done

- [ ] WP closing ADR written and registered (`WP24 closing: Hardening & release`); story ADR ids filled in.
- [ ] File status set to `DONE`; ROADMAP M6 marked done.
- [ ] All stories checked; E1–E20 green; S1–S7 reported; audits merged; `v1.0.0` tagged.

## 6. Risks and mitigations

| Risk | Mitigation |
| ---- | ---------- |
| Late discovery of perf or security issues | Budgets measured since WP06/WP08/WP14; security suite since WP19 |
| Import of old exports with older event versions | Upcasters tested in round-trip |
| Scope creep before release | Only fixes and audits; features go to the post-v1 backlog |

## 7. Blockers

None.
