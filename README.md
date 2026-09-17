# PaperOS Core Platform plan

PaperOS Core Platform is the reusable foundation every future PaperOS app is generated from: one spec-driven TypeScript monorepo template that ships to web, desktop and mobile with a shared data layer, design system, multiplayer, table/views engine, identity for every audience, business modules and a documented ten-minute path from a one-paragraph idea to a deployed app. It is built by parallel Claude Code sessions that pick issues from a Linear queue (team **PAP**) under nine agent characters, with Justin Massion (imagine-os) as the only human in the loop. This repository is the plan: every issue spec, the platform documents, the schedule, the pending backlog, the blueprint page and the scripts that put all of it into Linear.

* Linear workspace: https://linear.app/paperos (team PAP)
* Blueprint page (v4: filterable, sortable graph views of the Linear data, module map, chunk plan): https://claude.ai/artifact/M8PdehTznioG49QJUnkWTU (mirrored in `site/`, Pages copy with the WebGL views at https://imagine-os.github.io/linear-builder/)
* Session brief for a Claude Code session picking up a PAP issue: [`CLAUDE.md`](CLAUDE.md)

## Read first

In this order, before touching an issue:

1. [Blueprint](docs/blueprint.md): vision, decisions, phases, budget, project index.
2. [Interface & Data Contracts](docs/interface-and-data-contracts.md): the shapes every project codes against (its Module map section lists every contract package).
3. [Module System](docs/module-system.md): every project is a module, modules depend only on versioned contract packages, the kernel (registry, DI, event bus, gateway, UI slots, conformance runner, swap CLI) is the only place a dependency lives, and the swap playbook that lets the shell or any other module be rewritten and plugged back in.
4. Your project's `Contract` section: the project content in Linear (summaries in `plan/plan.json` under `projects[].description`).
5. [Agent Roster](docs/agent-roster.md) and your [character sheet](docs/characters/).
6. [Security & Threat Model](docs/security-and-threat-model.md).
7. [Execution Schedule](docs/execution-schedule.md): start days, milestone dates, Needs Justin table, discounted terms and the $2,500 chunks.
8. [Build in $2,500 chunks](docs/build-chunks.md) and [Cost and duration estimate](docs/cost-and-duration-estimate.md): what each chunk delivers, mix A / mix B, wall-clock at 16 builders running 24/7.
9. [New App in Ten Minutes: the golden path](docs/new-app-in-ten-minutes.md).

## Repository map

| Path | What it holds |
|---|---|
| `CLAUDE.md` | Brief for a Claude Code session working a PAP issue: read order, pipeline states, rules. |
| `plan/plan.json` | The master plan: vision, 15 decisions, 3 phases, budget, 9 agents, labels, states, 17 projects with 206 round-1 issues (the 18th project, Module System & Swap Tooling, is described in `plan/module-issues.json`). |
| `plan/module-issues.json` | Round 3: the Module System & Swap Tooling project and the 65 module-system issues (14 kernel issues PAP-433..PAP-446, one contract / conformance / wire trio per module PAP-447..PAP-497) with keys, labels, dependencies and the 18 `Module boundary` amendments to live issues. |
| `plan/chunks.json`, `plan/model-effort.json`, `plan/model-effort-B.json`, `plan/estimate-results.json` | The $2,500 chunk plan (mix A all Fable 5.1, mix B Opus 5 builders; discounted terms, 16 builders, 24/7) and the per-issue Model / Effort assignments behind the labels. |
| `plan/linear-ids.json` | Linear ids and URLs for the team, states, labels, projects, milestones and every round-1 issue. |
| `plan/specs/` | Canonical round-1 spec JSON (`bucket-*.json`, `gaps.json`): the source text of `specs/`. |
| `plan/critique-round1.md`, `plan/linear-summary-round1.md` | Round-1 self-critique and Linear build log. |
| `plan/round2/` | Round-2 audit, critique, gap analysis, per-project digests, schedule model outputs, and `changes/` (one log per agent and per fix FIX-1..FIX-8, with every Linear mutation). |
| `plan/linear-snapshot-live.json` | The latest full snapshot of team PAP (every non-archived issue with description, state, labels, project, milestone, parent, children, blockedBy, blocks, URL, updatedAt); `specs/` is generated from it. |
| `specs/` | One markdown file per canonical PAP issue (485: PAP-13..PAP-497 minus duplicates), grouped by project key (18 folders incl. `module-system/`), with frontmatter (identifier, project, phase, type, priority, state, relations, key, URL, updatedAt, model, effort) and the live Linear description as body. Index in `specs/README.md`. |
| `docs/` | The platform documents as published to Linear: Blueprint, Contracts (with Module map), Module System, Security, Schedule (with discounted terms and chunks), Roster, nine character sheets, Golden Path, plus `build-chunks.md` and `cost-and-duration-estimate.md`. Index with Linear URLs in `docs/README.md`. |
| `docs/pending/` | Historical spec text of the 156 round-2 issues held back by the Free plan cap; all 153 were created as PAP-280..PAP-432 on 2026-09-17 (3 folded into live issues). Key-to-identifier table in `docs/pending/README.md`. |
| `site/` | The blueprint page v4 (`index.html`, `data.json`; objects map, lanes skill tree, radial tree, images, icons, objects 3D and radial 3D views with filters and sorting, module map, chunk plan), served by GitHub Pages from the `gh-pages` branch. Earlier versions under `site/previous/`. |
| `tools/linear/` | The Python scripts that built and fixed the plan in Linear (idempotent, `LINEAR_API_KEY` via the proxy). `tools/blueprint/` builds the page (`build_v4.js`). |
| `.github/workflows/pages.yml` | Publishes `site/` to `gh-pages` on every push to `main`. |

## Status (2026-09-17)

* **493 issues** in Linear team PAP (485 canonical, PAP-13..PAP-497, plus PAP-5, Justin's original brief, and 7 duplicates), across **18 projects** and 3 phases, deadline 2026-10-01. The workspace is on **Linear Basic** (upgraded 2026-09-17, NJ-1 / [PAP-91](https://linear.app/paperos/issue/PAP-91) approved). Snapshot `plan/linear-snapshot-live.json` taken 2026-09-17T15:11Z; 1,224 `blocks` edges, no cycles.
* **29 Ready for Claude** with zero open blockers (28 from rounds 1-2 plus [PAP-433](https://linear.app/paperos/issue/PAP-433), the module manifest schema); the rest are Backlog behind dependency edges. 52 umbrellas, 49 Deferred.
* **Round 3 (2026-09-17, module system and chunk plan):** new project [Module System & Swap Tooling](https://linear.app/paperos/project/module-system-and-swap-tooling-8f81243eebfc) with 14 kernel issues PAP-433..PAP-446 (manifest schema, registry and DI, flag-driven swaps with shadow-run, event schema registry, gateway, UI slots, dependency lint, compatibility matrix, conformance runner, swap playbook, migration adapter kit, config port, docs generator, shell-swap drill) and one contract / conformance / wire trio per module, PAP-447..PAP-497 (51 issues across the 17 projects); 18 live issues carry a `Module boundary` amendment; document [PaperOS Module System](https://linear.app/paperos/document/paperos-module-system-8007373cc6bb) (`docs/module-system.md`); the Contracts document gained a Module map and the Execution Schedule the discounted terms. Rule: **a module depends only on contract packages, never on another module's implementation.** Change logs in the round-3 folder of the planning scratchpad, summarised in `plan/module-issues.json`.
* **Chunk plan** (`docs/build-chunks.md`, `plan/chunks.json`): at Justin's discounted terms ($50 per $2,500 of list-price Claude spend), 16 builders running 24/7, the 326 buildable non-deferred issues take **4 chunks with mix B** (Opus 5 builders, Fable 5.1 for Spec / Research, reviews and the 4 RC reviews: $7,909 list, $158 to Justin, 4 x $50 billed whole) or **5 chunks with mix A** (all Fable 5.1: $11,166 list, $223, 5 x $50), about 37 wall-clock hours either way; the 42 deferred leaves are an optional extra chunk. Mix B is the recommendation.
* **Blueprint v4** (same artifact URL, `site/index.html`): filterable, sortable views of the Linear data in the graph-gallery styles Justin picked (objects map, lanes skill tree, radial tree, images, icons, objects 3D, radial 3D), a Modules & plug points map with the kernel pieces and swap playbook, and the chunk plan.
* **All 153 pending issues created on 2026-09-17** as PAP-280..PAP-432 (109 children of existing umbrellas, 36 new umbrellas, 379 new `blocks` relations); the 3 folded entries stay work packages of their live issues. `docs/pending/` keeps the historical text with a key-to-identifier table; `specs/` holds the live spec of every issue.
* Round 2 (audit, contracts, security, schedule, characters, golden path, fixes FIX-1..FIX-8) is complete; the change logs are in `plan/round2/changes/`.

Linear is the system of record. Where this repository and Linear disagree, Linear wins and the file here is a snapshot to be refreshed.
