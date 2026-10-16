# Repository ADR Registry

Registry of every Architecture Decision Record about **this codebase**. Project ADRs written by
office agents for user projects live in the app, not here (Constitution §12.4).

How to add an ADR: follow the [`writing-adrs`](../../.agents/skills/writing-adrs/SKILL.md)
skill — copy the [template](0000-adr-template.md), take the next number, and add a row below
in the same change.

| ID       | Title                                                                    | Status   | Date       | Supersedes | Superseded by |
| -------- | ------------------------------------------------------------------------ | -------- | ---------- | ---------- | ------------- |
| ADR-0000 | [ADR template](0000-adr-template.md)                                     | Template | —          | —          | —             |
| ADR-0001 | [Record architecture decisions and ratify the Constitution](0001-record-architecture-decisions.md) | Accepted | 2026-10-16 | — | — |
| ADR-0002 | [Technology stack](0002-technology-stack.md)                             | Proposed | 2026-10-16 | —          | —             |
| ADR-0003 | [Amend Constitution: no audio, delivery tracking and ADR cadence](0003-amend-constitution-no-audio-and-delivery-tracking.md) | Accepted | 2026-10-16 | — | — |
| ADR-0004 | [US-01.01: Self-contained subprojects; only docker-compose.yml and Makefile at the root](0004-per-service-python-projects.md) | Accepted | 2026-10-16 | — | — |
| ADR-0005 | [US-01.01: Root docker-compose.yml and Makefile from the first story](0005-us-01-01-root-compose-and-makefile-first.md) | Proposed | 2026-10-16 | — | — |
| ADR-0006 | [US-01.02: Core settings named by env variable, uvicorn app factory, uv_build backend](0006-us-01-02-core-settings-and-app-factory.md) | Proposed | 2026-10-16 | — | — |

## Status legend

- **Proposed** — written, awaiting the project owner's decision.
- **Accepted** — in force; must be respected.
- **Rejected** — considered and declined; kept for history.
- **Deprecated** — no longer relevant, not replaced.
- **Superseded** — replaced by the ADR in "Superseded by".
