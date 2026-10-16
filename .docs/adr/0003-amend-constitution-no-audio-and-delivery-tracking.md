# ADR-0003: Amend Constitution: no audio, delivery tracking and ADR cadence

- Status: Accepted
- Date: 2026-10-16
- Deciders: Project owner
- Related: [CONSTITUTION.md](../CONSTITUTION.md) §12.5, §14.10, Article XXII, Amendment Log 3.0.0 and
  3.1.0; [ROADMAP.md](../../.project/ROADMAP.md); [AGENTS.md](../../AGENTS.md) rules 7, 12–14;
  skill `writing-adrs`

## Context

During the first planning session the project owner gave three explicit instructions:

1. Virtual Office must **never use sound** — not even optional or "off by default" sounds that the
   first draft of the Constitution and roadmap contained.
2. Every work-package file under `.project/execution/` must carry a status (`READY`,
   `PROCESSING`, `DONE`) and every user story must be a checklist that starts unchecked and is
   checked as it is worked.
3. An ADR must be written **after every user story or work package**.

The Constitution is the supreme reference, so these rules must be part of it, and per Article XX
amendments require an ADR.

## Decision

We will:

1. Add §14.10 "No audio (absolute rule)": no audio files, libraries, APIs, settings or "optional"
   sounds; every Amiga "beep" is the visual DisplayBeep. Remove all sound references from the
   Constitution, STACK.md (`@pixi/sound` dropped), DESIGN.md, FRONTEND.md, skills and the roadmap.
   Constitution version 3.0.0 (MAJOR: a rule reversed).
2. Track delivery in `.project/ROADMAP.md` (milestones, work packages, deliverables) and in one
   execution file per work package with status `READY` → `PROCESSING` → `DONE` and stories as
   checklists; Article XXII delegates the detailed plan to the roadmap.
3. Require a repository ADR after every completed user story (story ADR, or a reference to the WP
   closing ADR when the story took no decision) and a WP closing ADR after every completed work
   package (§12.5, AGENTS.md rule 14, skill `writing-adrs`). Constitution version 3.1.0 (MINOR).

## Alternatives Considered

1. Keep optional sounds off by default — rejected by the owner.
2. Track progress only in an external issue tracker — invisible to coding agents and detached from
   the repository; rejected.
3. ADRs only for "significant" decisions — lighter, but the owner wants a complete decision trail;
   the "reference the WP closing ADR" rule avoids empty ADRs.

## Consequences

- Positive: a silent, fully visual product; progress and decisions traceable in the repository
  at story granularity.
- Negative: more ADR files over time; contributors must update checkboxes and statuses in every
  PR.
- Risks and mitigations: ADR noise → story ADRs only when a decision was taken, otherwise a
  reference; forgotten updates → PR template and review checklists include them.

## Compliance

- Lint rules forbid audio APIs/libraries; the asset check rejects audio file types (WP01, WP12).
- Review checklists in every WP section of the roadmap include the ADR and checkbox steps.
- The ADR registry and AGENTS.md documentation index list every ADR.
