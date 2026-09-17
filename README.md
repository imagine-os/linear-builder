# PaperOS Core Platform plan

PaperOS Core Platform is the reusable foundation every future PaperOS app is generated from: one spec-driven TypeScript monorepo template that ships to web, desktop and mobile with a shared data layer, design system, multiplayer, table/views engine, identity for every audience, business modules and a documented ten-minute path from a one-paragraph idea to a deployed app. It is built by parallel Claude Code sessions that pick issues from a Linear queue (team **PAP**) under nine agent characters, with Justin Massion (imagine-os) as the only human in the loop. This repository is the plan: every issue spec, the platform documents, the schedule, the pending backlog, the blueprint page and the scripts that put all of it into Linear.

* Linear workspace: https://linear.app/paperos (team PAP)
* Blueprint page: https://claude.ai/artifact/M8PdehTznioG49QJUnkWTU (mirrored in `site/`)
* Session brief for a Claude Code session picking up a PAP issue: [`CLAUDE.md`](CLAUDE.md)

## Read first

In this order, before touching an issue:

1. [Blueprint](docs/blueprint.md): vision, decisions, phases, budget, project index.
2. [Interface & Data Contracts](docs/interface-and-data-contracts.md): the shapes every project codes against.
3. Your project's `Contract` section: the project content in Linear (summaries in `plan/plan.json` under `projects[].description`).
4. [Agent Roster](docs/agent-roster.md) and your [character sheet](docs/characters/).
5. [Security & Threat Model](docs/security-and-threat-model.md).
6. [Execution Schedule](docs/execution-schedule.md): start days, milestone dates, Needs Justin table.
7. [New App in Ten Minutes: the golden path](docs/new-app-in-ten-minutes.md).

## Repository map

| Path | What it holds |
|---|---|
| `CLAUDE.md` | Brief for a Claude Code session working a PAP issue: read order, pipeline states, rules. |
| `plan/plan.json` | The master plan: vision, 15 decisions, 3 phases, budget, 9 agents, labels, states, 17 projects with 206 round-1 issues. |
| `plan/linear-ids.json` | Linear ids and URLs for the team, states, labels, projects, milestones and every round-1 issue. |
| `plan/specs/` | Canonical round-1 spec JSON (`bucket-*.json`, `gaps.json`): the source text of `specs/`. |
| `plan/critique-round1.md`, `plan/linear-summary-round1.md` | Round-1 self-critique and Linear build log. |
| `plan/round2/` | Round-2 audit, critique, gap analysis, per-project digests, schedule model outputs, and `changes/` (one log per agent and per fix FIX-1..FIX-8, with every Linear mutation). |
| `plan/linear-snapshot-live.json` | The latest full snapshot of team PAP (every non-archived issue with description, state, labels, project, milestone, parent, children, blockedBy, blocks, URL, updatedAt); `specs/` is generated from it. |
| `specs/` | One markdown file per canonical PAP issue (420: PAP-13..PAP-432 minus duplicates), grouped by project key, with frontmatter (identifier, project, phase, type, priority, state, relations, URL, updatedAt) and the live Linear description as body. Index in `specs/README.md`. |
| `docs/` | The platform documents as published to Linear: Blueprint, Contracts, Security, Schedule, Roster, nine character sheets, Golden Path. Index with Linear URLs in `docs/README.md`. |
| `docs/pending/` | Historical spec text of the 156 round-2 issues held back by the Free plan cap; all 153 were created as PAP-280..PAP-432 on 2026-09-17 (3 folded into live issues). Key-to-identifier table in `docs/pending/README.md`. |
| `site/` | The blueprint page (`index.html`), served by GitHub Pages from the `gh-pages` branch. |
| `tools/linear/` | The Python scripts that built and fixed the plan in Linear (idempotent, `LINEAR_API_KEY` via the proxy). `tools/blueprint/` builds the page. |
| `.github/workflows/pages.yml` | Publishes `site/` to `gh-pages` on every push to `main`. |

## Status (2026-09-17)

* **428 issues** in Linear team PAP (420 canonical, PAP-13..PAP-432, plus PAP-5, Justin's original brief, and 7 duplicates), across 17 projects and 3 phases, deadline 2026-10-01. The workspace is on **Linear Basic** (upgraded 2026-09-17, NJ-1 / [PAP-91](https://linear.app/paperos/issue/PAP-91) approved).
* **28 Ready for Claude** with zero open blockers; the rest are Backlog behind dependency edges. PAP-91 is back in Ready for Claude.
* **All 153 pending issues created on 2026-09-17** as PAP-280..PAP-432 (109 children of existing umbrellas, 36 new umbrellas, 379 new `blocks` relations); the 3 folded entries stay work packages of their live issues. `docs/pending/` keeps the historical text with a key-to-identifier table; `specs/` holds the live spec of every issue.
* Round 2 (audit, contracts, security, schedule, characters, golden path, fixes FIX-1..FIX-8) is complete; the change logs are in `plan/round2/changes/`.

Linear is the system of record. Where this repository and Linear disagree, Linear wins and the file here is a snapshot to be refreshed.
