# ADR-0005: US-01.01: Root docker-compose.yml and Makefile from the first story

- Status: Proposed
- Date: 2026-10-16
- Deciders: Project owner
- Related: [ADR-0004](0004-per-service-python-projects.md) §Decision 3 (timing amended);
  [DOCKER.md](../DOCKER.md) §6, §8; [ROADMAP.md](../../.project/ROADMAP.md) WP01, WP02;
  Constitution §15.2

## Context

ADR-0004 decided that the repository root holds only `docker-compose*.yml` and a `Makefile`,
and planned to create the Makefile together with the base compose file in WP02 (US-02.04). The
roadmap likewise kept every Dockerfile and compose file out of WP01.

After US-01.01 merged as a docs-only story, the project owner expected to see
`docker-compose.yml` and the `Makefile` at the root already, with each subproject bringing its
own Dockerfile. WP01 was restarted from scratch with that expectation.

Docker Compose rejects `docker compose up` on a file without services ("no service selected"),
while `config`, `ps`, `logs` and `down` succeed.

## Decision

We will drive the repository with `make` from the first story:

1. US-01.01 creates `docker-compose.yml` (`name: virtual-office`, no services) and the
   `Makefile` (`help` default goal; `up`, `down`, `logs`, `status`, each a single
   `docker compose` call).
2. Each story that scaffolds a subproject adds its `Dockerfile`, `.dockerignore` and compose
   service in the same change: `core` (US-01.02), `catalog` (US-01.03), `frontend`
   (US-01.05). `make up` is verified from US-01.02, when the first service exists.
3. WP02 keeps hardening: healthchecks, security defaults, resource limits, Postgres, Ollama,
   one-off jobs, dev/GPU overlays. It extends the files instead of creating them.

This amends only the *timing* in ADR-0004 §Decision 3; the layout decision stands.

## Alternatives Considered

1. **Keep the plan of ADR-0004 (create both files in WP02)** — one coherent compose story,
   but the root shows no way to run anything for ten stories, and Dockerfiles arrive long after
   the code they package. Rejected by the project owner.
2. **Create compose, Makefile and all Dockerfiles in US-01.01** — everything visible at once,
   but Dockerfiles would package code that does not exist yet and could not be built or tested.
3. **Root files now, Dockerfiles with each subproject (chosen)** — every file is created when
   it can be verified; `make up` becomes meaningful from the first service.

## Consequences

- Positive: the root shows the entry points from the start; each subproject is runnable via
  `make up` the moment it is scaffolded; WP02 shrinks to hardening.
- Negative: `make up` fails with "no service selected" until US-01.02 merges; WP01 stories
  US-01.02, US-01.03, US-01.05 grow by a Dockerfile and a compose entry each.
- Risks and mitigations: early Dockerfiles skip the WP02 hardening → they still follow
  STACK.md §2.3 and DOCKER.md §4 (tag + digest, multi-stage, non-root), and WP02 reviews them
  against DOCKER.md §8.

## Compliance

- `docker compose config` valid; `make` prints the help; `make status|logs|down` exit 0
  (US-01.01).
- `make up` builds and starts each scaffolded service (US-01.02 AC6, US-01.03 AC5,
  US-01.05 AC4).
- DOCKER.md §8 review item: Makefile targets only wrap `docker compose`.
