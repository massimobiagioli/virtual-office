---
name: writing-adrs
description: How to write, number, accept, supersede and reference Architecture Decision Records in Virtual Office, including Constitution amendments, and how repository ADRs differ from in-app Project ADRs. Use when making a significant or hard-to-reverse decision about this codebase (library, framework, schema strategy, state machine, security, persistence, assets licensing), when amending the Constitution, or when implementing the Project ADR feature.
---

# Writing ADRs

Authoritative source: Constitution Article XII (§12.4–12.6) and Article XX.

## Two families — do not mix them

| Family          | Where                              | About                                  | ID              |
| --------------- | ---------------------------------- | -------------------------------------- | --------------- |
| Repository ADR  | `.docs/adr/NNNN-kebab-title.md`    | How Virtual Office itself is built     | `ADR-0003`      |
| Project ADR     | In-app, event-sourced              | Decisions office agents make for user projects | `ADR-SHOP-0003` |

This skill's workflow covers **repository ADRs**. For Project ADRs (feature code), the same
template and status lifecycle apply, implemented as the `Adr` aggregate with events
`AdrProposed/Accepted/Rejected/Deprecated/Superseded`.

## When a repository ADR is mandatory

**Always after every completed user story and every completed work package** (AGENTS.md
rule 14):

- *Story ADR* — title `US-NN.MM: <decision>`; records the decisions the story took
  (libraries, patterns, schemas, trade-offs). If the story took none, do not invent one:
  reference the WP closing ADR on the story line instead.
- *WP closing ADR* — title `WPNN closing: <work package name>`; summarizes the decisions of the
  WP, deviations from the roadmap, consequences and follow-ups.
- Write the ADR id on the story line in `.project/execution/wpNN-*.md`
  (`- [x] **US-05.03** … · ADR: ADR-0012`).

In addition, an ADR is mandatory for:

- choosing/replacing a library or framework; changing event schema strategy; changing the card
or agent state machine; changing any Constitution rule; adding an external service or
dependency of framework level; changing persistence; changing security posture; changing
asset licensing approach.

## Workflow

1. Read the registry `.docs/adr/index.md` and take the next number (4 digits, zero-padded).
2. Copy `.docs/adr/0000-adr-template.md` to `.docs/adr/NNNN-<kebab-title>.md`.
3. Fill every section. "Alternatives Considered" needs ≥ 2 real options. "Compliance" must
   name a verifiable check (test, lint rule, review item).
4. Status starts as `Proposed`. Only the project owner moves it to `Accepted` or `Rejected`.
5. Add a row to the ADR registry `.docs/adr/index.md` **and** to the "Documentation index" in
   `AGENTS.md`. Every status change (Accepted, Rejected, Superseded…) is mirrored in the
   registry in the same change.
6. Reference the ADR in the commit body: `Refs: ADR-NNNN`.

## Superseding

Never rewrite an accepted ADR. Create a new ADR with `Related: supersedes ADR-XXXX`, and edit
only the old ADR's status line to `Superseded by ADR-YYYY`.

## Amending the Constitution

1. ADR titled `Amend Constitution: <topic>` containing the exact old and new text.
2. After acceptance, edit `.docs/CONSTITUTION.md` in the same change:
   - bump version (MAJOR: rule removed/reversed; MINOR: new rule/article; PATCH: clarification);
   - update the header status line version;
   - append a row to the Amendment Log.

## Writing style

- English, active voice: "We will use PixiJS for the office renderer."
- Context explains forces, not the solution. Consequences include negatives honestly.
- One decision per ADR.
