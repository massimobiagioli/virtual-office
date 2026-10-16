---
name: enforcing-kanban-workflow
description: Rules and implementation guidance for the Virtual Office Kanban domain - columns BACKLOG/TODO/DOING/REVIEW/DONE, the TODO WIP limit of 3, the QA review gate, rework loop, blocking, role permissions, Definition of Ready/Done, and PM pull/assignment scoring. Use when implementing or changing cards, board transitions, the Orchestrator tick, assignment logic, or board UI behavior.
---

# Enforcing the Kanban workflow

Authoritative source: Constitution Articles VIII and IX, permission matrix §5.9. This skill is
the implementation guide; if they disagree, the Constitution wins.

## Golden rules

1. Rules live in `services/core/src/virtual_office/domain/kanban`. Prompts may remind agents, but the domain rejects
   violations (Principle P2).
2. A forbidden command produces **no event** and returns a typed domain error; the
   application logs a `CommandRejected` diagnostic.
3. The reviewer is never the assignee. No card reaches DONE without `CardApproved`.

## Allowed transitions

| From → To        | Command            | Actor                         | Guards                                               |
| ---------------- | ------------------ | ----------------------------- | ---------------------------------------------------- |
| ∅ → BACKLOG      | `CreateCard`       | PM, user                      | schema valid; estimate ∈ {1,2,3,5,8}                 |
| BACKLOG → TODO   | `PullCard`         | PM, user                      | `count(TODO) < todoLimit`; card Ready; assignee eligible |
| TODO → BACKLOG   | `UnassignCard`     | PM, user                      | —                                                    |
| TODO → DOING     | `StartWork`        | assignee, user                | assignee has no card in DOING                        |
| DOING → REVIEW   | `SubmitWork`       | assignee, user                | ≥ 1 deliverable                                      |
| DOING → TODO     | `HandBackWork`     | assignee, PM, user            | reason required                                      |
| REVIEW → DONE    | `ApproveCard`      | QA / fallback reviewer, user  | reviewer ≠ assignee; DoD satisfied                   |
| REVIEW → TODO    | `RejectCard`       | QA / fallback reviewer, user  | reviewer ≠ assignee; ≥ 1 `blocker`/`major` note      |
| DONE → TODO      | `ReopenCard`       | user only                     | reason required                                      |

Everything else → `TransitionNotAllowed`.

## Error codes (use exactly these names)

`TransitionNotAllowed`, `WipLimitReached`, `CardNotReady`, `NoEligibleAssignee`,
`AgentAlreadyBusy`, `NotAssignee`, `ReviewerIsAssignee`, `RejectionRequiresMajorNote`,
`DefinitionOfDoneNotMet`, `DeliverableRequired`, `ReasonRequired`, `ActorNotPermitted`,
`ConcurrencyConflict`.

## WIP semantics (easy to get wrong)

- The limit (default 3, range 1–5, per project) applies to **pulls only**.
- Rework (`RejectCard`), hand-backs and user reopens are **always allowed**, even if TODO
  goes over the limit. While `count(TODO) ≥ limit`, no pulls happen.
- Blocked cards in TODO still count.
- Validate the limit against the Project aggregate version inside one transaction
  (optimistic concurrency) — two simultaneous pulls must not both succeed.

## Definition of Ready (pull guard)

title, description, ≥ 1 acceptance criterion, estimate, priority, ≥ 1 competence tag; all
`blocks` dependencies DONE; not blocked; an eligible assignee exists.

## Definition of Done (approve guard)

All criteria `pass` (or justified `not-verifiable`); deliverable attached; code checks green;
architecture cards have an `Accepted` Project ADR; no open blocker/major notes.

## Pull selection and assignment

Card order: priority → number of dependents → rank → createdAt.

```
score = 3*competenceMatch + 2*availability + 1*continuity - 1*load
```

Ties → least recently assigned. Card type → role: story/task/bug/chore → developer;
architecture/spike → architect; design → designer. Fallback executors:
developer → architect → designer (`fallback-assignee` badge).
Review fallback when QA disabled: architect → PM → user (`isFallback: true`).

Implement scoring as a **pure function** returning the full breakdown; store it in the
`CardPulled` payload so the PM can explain the decision.

## Rework loop

- Rejected card keeps its assignee; `reworkCount += 1`.
- Rework cards are picked up before new cards by that assignee.
- At `reworkCount === 3` emit `CardEscalated` and a proactive PM chat message.

## Testing requirements

- One test per allowed transition, one per forbidden pair (generate the matrix).
- Property test (Hypothesis stateful testing): random command sequences keep invariants — pulls never exceed
  the limit, every DONE has a non-assignee approval, per-agent DOING ≤ 1.
- Scenarios E1–E4, E8–E13, E17 of Constitution Appendix E.

## Board UI

- Forbidden drag-and-drop snaps back with a requester explaining the rule (use the error
  code's human message).
- Header shows `TODO n/limit`; orange when `n ≥ limit`.
- Every drag action has a keyboard alternative ("Move to…" cycle gadget).
