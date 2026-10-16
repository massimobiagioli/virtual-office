# ADR-0001: Record architecture decisions and ratify the Constitution

- Status: Accepted
- Date: 2026-10-16
- Deciders: Project owner
- Related: [CONSTITUTION.md](../CONSTITUTION.md) Articles XII and XX

## Context

Virtual Office is built by humans and AI coding agents. Without a written record, decisions
get lost, re-litigated, or silently contradicted. The product itself is about traceability,
so the codebase must practice what it preaches.

## Decision

We will:

1. ratify `.docs/CONSTITUTION.md` v1.0.0 as the supreme reference of the project;
2. record every significant decision about this codebase as a repository ADR in `.docs/adr/`,
   named `NNNN-kebab-case-title.md`, numbered sequentially, using
   [`0000-adr-template.md`](0000-adr-template.md);
3. never rewrite an accepted ADR; supersede it with a new one;
4. amend the Constitution only through an ADR titled `Amend Constitution: <topic>`.

## Alternatives Considered

1. No formal records (decisions in commit messages) — cheap, but not discoverable.
2. A wiki outside the repository — drifts from code, invisible to coding agents.

## Consequences

- Positive: decisions are discoverable by every contributor and agent; history is preserved.
- Negative: small overhead per decision.
- Risks and mitigations: ADRs forgotten → the `writing-adrs` skill and PR checklist require them.

## Compliance

PR reviews check that changes listed in Constitution §12.5 include an ADR; `AGENTS.md`
references every ADR.
