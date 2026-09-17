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
| `plan/round2/` | Round-2 audit, critique, gap analysis, per-project digests, schedule model outputs, the final Linear snapshot, and `changes/` (one log per agent and per fix FIX-1..FIX-8, with every Linear mutation). |
| `specs/` | One markdown file per canonical PAP issue (268), grouped by project key, with frontmatter (identifier, project, phase, type, priority, state, relations, URL). Index in `specs/README.md`. |
| `docs/` | The platform documents as published to Linear: Blueprint, Contracts, Security, Schedule, Roster, nine character sheets, Golden Path. Index with Linear URLs in `docs/README.md`. |
| `docs/pending/` | The 156 specified issues Linear could not hold yet (Free plan cap), one file each, with the create order from PAP-91. |
| `site/` | The blueprint page (`index.html`), served by GitHub Pages from the `gh-pages` branch. |
| `tools/linear/` | The Python scripts that built and fixed the plan in Linear (idempotent, `LINEAR_API_KEY` via the proxy). `tools/blueprint/` builds the page. |
| `.github/workflows/pages.yml` | Publishes `site/` to `gh-pages` on every push to `main`. |

## Status (2026-09-17)

* **267 spec-complete issues** in Linear team PAP (275 issues minus 7 duplicates and PAP-5, Justin's original brief), across 17 projects and 3 phases, deadline 2026-10-01.
* **25 Ready for Claude** and unblocked; the rest are Backlog behind dependency edges. PAP-91 sits in Needs Justin (NJ-1, the Linear plan upgrade).
* **156 pending issues** fully specified in `docs/pending/` (153 to create, 3 folded into live issues as work packages), held until the Linear plan upgrade requested in [PAP-91](https://linear.app/paperos/issue/PAP-91).
* Round 2 (audit, contracts, security, schedule, characters, golden path, fixes FIX-1..FIX-8) is complete; the change logs are in `plan/round2/changes/`.

Linear is the system of record. Where this repository and Linear disagree, Linear wins and the file here is a snapshot to be refreshed.
