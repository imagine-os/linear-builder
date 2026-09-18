# Linear features used by PaperOS (team PAP)

Written 2026-09-18 (planning round 4) after Justin asked to "use more features of Linear if possible". Workspace `paperos`, team **PAP**, plan **Basic**. Every mutation made for this document is logged in `plan/round4/changes/linear-initiatives-templates-views.json` (137 mutations; sibling log for team settings: `linear-team-features.json`). Rules that still hold: nothing is deleted or archived, no issue changes state by hand, PAP-1..PAP-12 and the six original views are never touched.

## Feature table

| Feature | Used? | Since | How PaperOS uses it |
| -- | -- | -- | -- |
| Issues | Yes | Round 1 (09-16) | 497 issues on team PAP (485 canonical, 4 without a project); one issue per claimable unit of work with the eleven-section spec (`specs/<project>/`). |
| Sub-issues | Yes | Round 1 | 158 issues have a parent; 52 umbrellas. Umbrella rule: never claimable, the last finished child moves the umbrella to In Review. View: Umbrellas. |
| Relations (blocks, duplicate) | Yes | Round 1 | 1,215 `blocks` relations form the dependency graph the orchestrator promotes from (branch-start rule); 7 duplicate relations from the app-shell dedupe. View: Blocked. |
| Labels and label groups | Yes | Round 1; groups round 2; Chunk labels round 4 | Groups `Type` (Spec, Build, Review, Research, Docs, Infra), `Model`, `Reasoning effort`; flat labels P0/P1/P2, surfaces (Customer, Staff, Developer, Agent), `Deferred`, `Chunk 1..5`; workspace labels Bug, Feature, Improvement. |
| Priorities | Yes | Round 1 | Urgent = zero-slack chains and P0 milestones, High = the rest of v0.1, Low = Deferred. Projects carry priority since round 4 (Urgent for P0 projects, High otherwise). |
| Estimates | Yes | Round 4 (sibling worker) | Fibonacci points per issue mapped from Size S/M/L; feeds cycle capacity and the burn model (`docs/cost-and-duration-estimate.md`). |
| Due dates | Yes | Round 4 (sibling worker) | Set from the Execution Schedule start half-day plus size, so the orchestrator's least-slack ordering is visible in Linear. |
| Cycles | Yes | Round 4 (sibling worker) | One-week cycles, cycle 1 active; the orchestrator moves claimed issues into the active cycle. View: Current cycle. |
| Projects | Yes | Round 1 | 18 projects, one per module; project `content` holds the Contract section (provides / consumes) every session reads. Lead = Justin since round 4. |
| Milestones | Yes | Round 1 | 54 milestones, three per project, with the dates from Execution Schedule section 7; 492 issues carry one. |
| Project updates and health | Yes | Round 4 | One update per project signed by Atlas: counts by state, next milestone, Ready for Claude issues, top risk, Needs Justin items. Health `onTrack`, `atRisk` for business-core, growth and migration (P2, credential asks). Ledger posts the daily burn report here from 09-20. |
| Project links (resources) | Yes | Round 4 | Three `entityExternalLink`s per project: the spec folder `specs/<key>` on GitHub, the Blueprint artifact, the Pages site. |
| Initiatives | Yes | Round 4 | Four initiatives (below) own the 18 projects; owner Justin, target 2026-10-01, status Active, content = outcome, why, done criteria, reading list. Team-scoped (`leadTeamId`) initiatives are Business plan only, so they are workspace initiatives. |
| Triage | Yes | Round 4 (sibling worker) | Triage state on; inbound issues from Slack, GitHub and agents land there. View: Triage inbox. |
| Templates | Yes | Round 1 (PaperOS Spec); six more plus a project template round 4 | Issue templates: Sub-feature child, Gap issue, Research spike + ADR, Needs Justin card, Gate failure / bug report (Sentinel), Release candidate. Project template: PaperOS module project. |
| Views | Yes | Round 1 (6 views); 12 more round 4 | Shared team views for every pipeline question (below). Ready for Claude is grouped by project through `viewPreferencesCreate`. |
| Documents | Yes | Round 2 | 27 project documents: Blueprint, Contracts, Module System, Roster and nine character sheets, Security, Execution Schedule, Golden path, ten Round 2 pending-issue documents. Mirrored under `docs/`. |
| Comments | Yes | Round 2 | 78 comments on 55 issues: promotion comments (`promoted:`, `BASE_BRANCHES`), fix logs, deferral notes; ADR status changes and the daily burn report are comments by convention. |
| Attachments | Not yet | Build (PAP-52, PAP-97) | PR links, gate artifacts and recordings attach to the issue when the orchestrator and the GitHub integration go live. 0 today. |
| GitHub integration | Not yet | Build (PAP-47, PAP-97) | Linked once the `imagine-os` GitHub App exists (NJ-3): PR title `PAP-n` moves the issue to In Review, merge moves it to Done. |
| Slack integration | Not yet | Build (PAP-136, NJ-13) | Project-update and Needs Justin notifications into Slack once the incoming webhook is provided. |
| API and webhooks | Yes (API) / build (webhooks) | Round 1 / PAP-97 | Everything in this repo was built through the GraphQL API (`tools/linear/`); webhooks into the orchestrator arrive with NJ-5. |
| Agents (Linear agent sessions) | Not yet | v0.2 | The orchestrator acts through a personal API key today; a Linear agent identity per character is a v0.2 item once the roster is hired (NJ-9). |
| SLAs | Not on Basic | - | Instead: due dates from the Execution Schedule and the Blocked view; the stop-loss rules in `docs/execution-schedule.md` section 5 are the SLA. |
| Customer requests | Not on Basic | - | Instead: the `Customer` surface label plus the Gap issue template; PAP-189 (support inbox) builds intake inside PaperOS. |
| Insights | Not on Basic | - | Instead: the daily burn report (PAP-98, Ledger, 09:00Z) and the Pages site dashboards built from `plan/*.json`. |
| Asks | Not on Basic | - | Instead: the Needs Justin state, view and card template, capped at five open cards (PAP-94). |

## Initiatives

| Initiative | Projects | URL |
| -- | -- | -- |
| A new app in ten minutes (the golden path) | app-shell, spec-builder, design-system, forge, data-layer, libraries | https://linear.app/paperos/initiative/a-new-app-in-ten-minutes-the-golden-path-6d4646bb9417 |
| The agent org runs the build | pm-linear, agents, quality, module-system | https://linear.app/paperos/initiative/the-agent-org-runs-the-build-2f494ac9b62e |
| Product surfaces for every audience | tables, collab, realtime, input, identity | https://linear.app/paperos/initiative/product-surfaces-for-every-audience-17c2a65800ac |
| Business-ready for any business | business-core, growth, migration | https://linear.app/paperos/initiative/business-ready-for-any-business-668c8232feef |

## Views added in round 4

| View | Filter | URL |
| -- | -- | -- |
| Needs Justin | state = Needs Justin | https://linear.app/paperos/view/864a71f16607 |
| Ready for Claude by project | state = Ready for Claude, grouped by project, ordered by priority | https://linear.app/paperos/view/6fb3e1fe30aa |
| Umbrellas | `children.length > 0`, open | https://linear.app/paperos/view/1138c1f90480 |
| Deferred (v0.2) | label Deferred | https://linear.app/paperos/view/7061d0ef9835 |
| Blocked | `hasBlockedByRelations`, open | https://linear.app/paperos/view/20c293455d40 |
| Current cycle | `cycle.isActive` | https://linear.app/paperos/view/15fe8dd46a4e |
| Chunk 1 | label Chunk 1 | https://linear.app/paperos/view/d80864023d14 |
| Chunk 2 | label Chunk 2 | https://linear.app/paperos/view/95cf7e7a2728 |
| Chunk 3 | label Chunk 3 | https://linear.app/paperos/view/323ae246b7bc |
| Chunk 4 | label Chunk 4 | https://linear.app/paperos/view/07c52b9369e6 |
| Chunk 5 | label Chunk 5 | https://linear.app/paperos/view/8f49eb37bf25 |
| Triage inbox | state type = triage | https://linear.app/paperos/view/e78588883cab |

The six round-1 views (Recently Completed, In Progress, Triage: Unassigned or No Priority, My Work, Bugs, High Priority) are unchanged.

## Templates

| Template | Type | Prefill |
| -- | -- | -- |
| Sub-feature child | issue | Backlog, High, label Build; eleven-section skeleton with `**Model / Effort:**` first line and `Parent: PAP-___` under Goal |
| Gap issue | issue | Backlog, High, label Build; skeleton plus `Gap found by / Benchmark` line |
| Research spike + ADR | issue | Backlog, High, label Research; Question, Candidates, Rubric, Time box, ADR output path `docs/adr/NNNN-*.md`, Decision |
| Needs Justin card | issue | state Needs Justin, Urgent; NJ-n, what to decide or create, default after 48 h, consuming issues, secret name, lead time |
| Gate failure / bug report (Sentinel) | issue | Backlog, High, labels Review + Bug; gate, failing check, repro, evidence links, severity S0-S3, owning issue |
| Release candidate | issue | Backlog, Urgent, label Review; RC0-RC3 checklist from Execution Schedule section 3 and the Justin decision line |
| PaperOS module project | project | name, description, `## Contract` (provides / consumes, module trio), three milestone placeholders, lead Justin, team PAP |

`templateData` carries both `description` (Markdown) and `descriptionData` (ProseMirror doc, the shape the existing PaperOS Spec template uses) so the body renders whichever field the client reads; the project template carries `content` and `contentData` the same way, plus `projectMilestones`. Linear accepted the JSON as given; whether the milestone placeholders materialise on "new project from template" is unverified from the API.

## What Linear refused

* `initiativeCreate` with `leadTeamId`: `FEATURE_NOT_ACCESSIBLE`, "Subscribe to the Business plan to access team initiatives in your workspace." Initiatives were created without a lead team.
* `icon` values `Bot`, `Layout`, `Briefcase`, `Loop` on initiatives and views: `INVALID_INPUT`, "icon is not a valid icon". Created without icons where a name failed (`Rocket`, `Alert`, `Tree`, `Calendar`, `Lock` were accepted).
