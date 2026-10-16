# ADR-0007: Amend Constitution: rename the `agents-catalog` service to `catalog`

- Status: Accepted
- Date: 2026-10-16
- Deciders: Project owner (direct instruction during US-01.03: "rename agents-catalog to
  catalog everywhere")
- Related: Constitution §15.1, §15.2, §15.3, §15.6, Article XVI;
  [ADR-0002](0002-technology-stack.md); [ADR-0004](0004-per-service-python-projects.md);
  [ADR-0006](0006-us-01-02-core-settings-and-app-factory.md); US-01.03

## Context

The registry of agent definitions, prompts, characters and eval sets was named
`agents-catalog` in the Constitution, the guides, the roadmap and the first scaffold of
US-01.03 (folder `services/agents-catalog`, package `agents_catalog`, compose service and image
`agents-catalog`). The project owner asked for the shorter name `catalog` everywhere, while the
service had just been scaffolded and nothing outside this repository depended on the old name.
Its database (`catalog`), roles (`catalog_owner`, `catalog_app`) and jobs (`migrate-catalog`,
`catalog-seed`) already used the short name.

## Decision

We will name the service `catalog` everywhere:

1. Folder and Docker build context `services/catalog/`; uv project `virtual-office-catalog`;
   import package `catalog` (`src/catalog/`); compose service `catalog`, image
   `virtual-office/catalog`; `core` reaches it at `http://catalog:8001/`.
2. Constitution amended (PATCH, v3.1.1 → v3.1.2, no rule changed). Exact text changes:

   | § | Old | New |
   | - | --- | --- |
   | §15.1 | `` `frontend`, `core`, `agents-catalog`, `ollama`, `postgres` `` | `` `frontend`, `core`, `catalog`, `ollama`, `postgres` `` |
   | §15.2 table | `` `agents-catalog` `` (service row) | `` `catalog` `` |
   | §15.2 tree | `│   └── agents-catalog/` | `│   └── catalog/` |
   | §15.3 diagram | `Ports --> CAT[agents-catalog]` | `Ports --> CAT[catalog]` |
   | §15.6 | "resolved from `agents-catalog`" | "resolved from `catalog`" |
   | Art. XVI | `services/agents-catalog/catalog/…` (prompts, evals) | `services/catalog/catalog/…` |

3. Guides, skills, roadmap, execution files, commands and Proposed ADRs (0002, 0005, 0006) are
   updated to the new name. Accepted ADR-0004 is not rewritten (skill `writing-adrs`): its
   mentions of `agents-catalog` are to be read as `catalog`.

## Alternatives Considered

1. **Keep `agents-catalog`** — no churn, but the owner prefers the short name, which also
   matches the database, roles and jobs already named `catalog`.
2. **Rename the service but keep the import package `agents_catalog`** — avoids the package
   having the same name as the `catalog/` source-definitions folder, but leaves the old name
   in every import and in the uvicorn entrypoint, against the "everywhere" instruction.

## Consequences

- Positive: one name for the service, its folder, image, package, database and jobs.
- Negative: inside `services/catalog/` the import package `src/catalog/` and the definitions
  folder `catalog/` share a name. Imports are unaffected (the installed regular package wins
  over the folder, which has no `__init__.py`), but a bare `--cov=catalog` resolves to the
  folder and measures nothing.
- Risks and mitigations: coverage must target the package by path (`--cov=src/catalog`) or
  through `[tool.coverage.run] source_pkgs = ["catalog"]` when US-01.04 configures coverage.

## Compliance

- `git grep -E "agents[-_]catalog"` finds only accepted ADR-0004, this ADR (file, registry and AGENTS.md
  entries) and the Amendment
  Log row.
- `make up` → `make status` shows `catalog` running next to `core`; the catalog tests import
  `catalog.*`.
