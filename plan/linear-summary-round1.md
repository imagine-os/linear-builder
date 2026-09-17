# PaperOS Core Platform — Linear build log

Workspace **PaperOS** (`paperos`), team **PAP** (`0ee78894-89f8-4376-a829-f8685dbc1868`). Built 2026-09-17. Deadline 2026-10-01.

## Counts

| Object | Created |
| --- | --- |
| Workflow states | 3 (Ready for Claude, In Review, Needs Justin) |
| Label groups | 3 (Phase, Type, Surface) |
| Labels | 13 (3 Phase, 6 Type, 4 Surface) |
| Projects | 17 |
| Project milestones | 51 |
| Issues | 206 |
| Blocking relations | 284 |
| Issue templates | 1 (PaperOS Spec) |
| Issues updated | 8 (PAP-5 + 7 duplicates) |

All 206 issues got a full spec description (197 from `specs/bucket-*.json`, 9 from `specs/gaps.json`). No issue fell back to `oneLine`.

## Workflow

Pipeline order on team PAP: **Backlog → Todo → Ready for Claude → In Progress → In Review → Needs Justin → Done → Canceled → Duplicate**. The three new states were inserted at fractional positions (1.5, 2.5, 2.75) so the six defaults were left untouched.

- `Ready for Claude` (unstarted, #F2C94C) — spec-complete and unblocked; the orchestrator may claim it.
- `In Review` (started, #5E6AD2) — PR open, automated gates running.
- `Needs Justin` (started, #EB5757) — human decision required; keep under five.

## Projects

| Phase | Project | Issues | Milestones | Target | URL |
| --- | --- | --- | --- | --- | --- |
| P0 | Universal App Shell & Repo Template | 17 | 3 | 2026-09-29 | https://linear.app/paperos/project/universal-app-shell-and-repo-template-2a1a63307c48 |
| P0 | Data Layer & Database | 14 | 3 | 2026-09-30 | https://linear.app/paperos/project/data-layer-and-database-1eaa26bb2fa7 |
| P0 | Version Control & Forge Independence | 11 | 3 | 2026-09-30 | https://linear.app/paperos/project/version-control-and-forge-independence-b51cbdae5753 |
| P0 | Identity, Roles & Audiences | 11 | 3 | 2026-09-30 | https://linear.app/paperos/project/identity-roles-and-audiences-f5b42bf49c6f |
| P0 | Design System | 12 | 3 | 2026-09-30 | https://linear.app/paperos/project/design-system-b50d53802313 |
| P0 | Quality Pipeline | 13 | 3 | 2026-09-30 | https://linear.app/paperos/project/quality-pipeline-bafa1891cb31 |
| P0 | Project Management & Claude Pipeline | 12 | 3 | 2026-09-30 | https://linear.app/paperos/project/project-management-and-claude-pipeline-cf56ba15c065 |
| P0 | Agent Characters & Orgs | 11 | 3 | 2026-09-30 | https://linear.app/paperos/project/agent-characters-and-orgs-0e471ec523e4 |
| P1 | Spec Builder | 13 | 3 | 2026-09-30 | https://linear.app/paperos/project/spec-builder-4271fae6c995 |
| P1 | In-App Collaboration & Knowledge | 12 | 3 | 2026-09-30 | https://linear.app/paperos/project/in-app-collaboration-and-knowledge-1c66a61637ca |
| P1 | Multiplayer & Realtime | 11 | 3 | 2026-09-30 | https://linear.app/paperos/project/multiplayer-and-realtime-256a6078be1e |
| P1 | Multi-Input Control & Accessibility | 11 | 3 | 2026-09-30 | https://linear.app/paperos/project/multi-input-control-and-accessibility-59ffd5906c81 |
| P1 | Table & Views Engine | 14 | 3 | 2026-09-30 | https://linear.app/paperos/project/table-and-views-engine-85325cbcfbf2 |
| P2 | Business Core: Payments, Finance & Payroll | 12 | 3 | 2026-10-01 | https://linear.app/paperos/project/business-core-payments-finance-and-payroll-4edd57501af9 |
| P2 | Growth: Marketing, Outreach & CRM | 11 | 3 | 2026-10-01 | https://linear.app/paperos/project/growth-marketing-outreach-and-crm-5de8143467be |
| P2 | Migration & Import Tools | 11 | 3 | 2026-10-01 | https://linear.app/paperos/project/migration-and-import-tools-8736648f9a4e |
| P0 | Library Discovery & Integration | 10 | 3 | 2026-09-30 | https://linear.app/paperos/project/library-discovery-and-integration-cad7e8dc6954 |

## Ready for Claude — 21 issues unblocked right now

| Issue | Project | Title | URL |
| --- | --- | --- | --- |
| PAP-13 | Universal App Shell & Repo Template | Scaffold paperos-template monorepo with pnpm, Turborepo, strict TypeScript and a Vite React 19 web app | https://linear.app/paperos/issue/PAP-13/scaffold-paperos-template-monorepo-with-pnpm-turborepo-strict |
| PAP-14 | Universal App Shell & Repo Template | Research and document the target device matrix (phone, tablet, laptop, desktop, TV/kiosk, foldable) with breakpoints and test devices | https://linear.app/paperos/issue/PAP-14/research-and-document-the-target-device-matrix-phone-tablet-laptop |
| PAP-25 | Universal App Shell & Repo Template | Provision the Hetzner VPS with Coolify, Caddy, DNS for the PaperOS domain, object storage, sops keys and the paperos-infra repo | https://linear.app/paperos/issue/PAP-25/provision-the-hetzner-vps-with-coolify-caddy-dns-for-the-paperos |
| PAP-31 | Data Layer & Database | Evaluate Zero, ElectricSQL, PowerSync and Replicache for local-first sync and write an ADR | https://linear.app/paperos/issue/PAP-31/evaluate-zero-electricsql-powersync-and-replicache-for-local-first |
| PAP-44 | Version Control & Forge Independence | Write ADR: keep Git as the format, self-host Forgejo, mirror GitHub, defer any custom VCS | https://linear.app/paperos/issue/PAP-44/write-adr-keep-git-as-the-format-self-host-forgejo-mirror-github-defer |
| PAP-46 | Version Control & Forge Independence | Define branch protection, conventional commits and worktree-per-issue conventions for parallel agents | https://linear.app/paperos/issue/PAP-46/define-branch-protection-conventional-commits-and-worktree-per-issue |
| PAP-55 | Identity, Roles & Audiences | Specify the audience model: customer tiers, staff roles, partners, admins, agents and composable segments in between | https://linear.app/paperos/issue/PAP-55/specify-the-audience-model-customer-tiers-staff-roles-partners-admins |
| PAP-56 | Identity, Roles & Audiences | Compare Better Auth, Lucia, Clerk and Auth.js for self-hosting, organizations and passkeys; write ADR | https://linear.app/paperos/issue/PAP-56/compare-better-auth-lucia-clerk-and-authjs-for-self-hosting |
| PAP-66 | Design System | Define design tokens (color, type, space, radius, motion, elevation) in DTCG JSON compiled to CSS variables | https://linear.app/paperos/issue/PAP-66/define-design-tokens-color-type-space-radius-motion-elevation-in-dtcg |
| PAP-79 | Quality Pipeline | Write review rubrics and a severity taxonomy shared by all reviewer agents and humans | https://linear.app/paperos/issue/PAP-79/write-review-rubrics-and-a-severity-taxonomy-shared-by-all-reviewer |
| PAP-91 | Project Management & Claude Pipeline | Add pipeline states (Ready for Claude, In Review, Needs Justin), label groups and project templates to Linear team PAP | https://linear.app/paperos/issue/PAP-91/add-pipeline-states-ready-for-claude-in-review-needs-justin-label |
| PAP-92 | Project Management & Claude Pipeline | Write the session playbook: how a Claude session picks up an issue, what it must read, how it reports and ends | https://linear.app/paperos/issue/PAP-92/write-the-session-playbook-how-a-claude-session-picks-up-an-issue-what |
| PAP-103 | Agent Characters & Orgs | Define the character schema: name, role, reportsTo, tools, MCP servers, access scopes, plugins, skills, memory, escalation rules | https://linear.app/paperos/issue/PAP-103/define-the-character-schema-name-role-reportsto-tools-mcp-servers |
| PAP-114 | Spec Builder | Define the page.spec.yaml schema: purpose, logic, access, data, integrations, layout, components, states, events, edge cases | https://linear.app/paperos/issue/PAP-114/define-the-pagespecyaml-schema-purpose-logic-access-data-integrations |
| PAP-127 | In-App Collaboration & Knowledge | Evaluate tldraw vs React Flow for the canvas and Tiptap vs BlockNote for docs; write ADR | https://linear.app/paperos/issue/PAP-127/evaluate-tldraw-vs-react-flow-for-the-canvas-and-tiptap-vs-blocknote |
| PAP-139 | Multiplayer & Realtime | Benchmark Yjs vs Automerge vs Loro for document CRDT and write an ADR | https://linear.app/paperos/issue/PAP-139/benchmark-yjs-vs-automerge-vs-loro-for-document-crdt-and-write-an-adr |
| PAP-150 | Multi-Input Control & Accessibility | Design a unified input event abstraction so components handle mouse, touch, pen and gamepad uniformly | https://linear.app/paperos/issue/PAP-150/design-a-unified-input-event-abstraction-so-components-handle-mouse |
| PAP-161 | Table & Views Engine | Specify the view model: data source, fields, filters, sorts, groups, aggregations, permissions and sharing as a superset of Airtable, Notion and ClickUp | https://linear.app/paperos/issue/PAP-161/specify-the-view-model-data-source-fields-filters-sorts-groups |
| PAP-162 | Table & Views Engine | Audit Airtable, Notion, ClickUp, Baserow and NocoDB view features into a parity checklist | https://linear.app/paperos/issue/PAP-162/audit-airtable-notion-clickup-baserow-and-nocodb-view-features-into-a |
| PAP-209 | Library Discovery & Integration | Define the library evaluation rubric (license, maintenance, bundle size, a11y, TS quality, agent-friendliness) and ADR template | https://linear.app/paperos/issue/PAP-209/define-the-library-evaluation-rubric-license-maintenance-bundle-size |
| PAP-210 | Library Discovery & Integration | Catalog and configure MCP servers and connectors (Linear, GitHub, Stripe, Notion, Drive, Webflow, Miro, Gamma) for agents | https://linear.app/paperos/issue/PAP-210/catalog-and-configure-mcp-servers-and-connectors-linear-github-stripe |

## PAP-5

Updated in place (title unchanged): moved into **Universal App Shell & Repo Template**, state **Backlog**, priority **2 (High)**, description rewritten as the origin note plus links to all 17 projects. https://linear.app/paperos/issue/PAP-5/my-issue-is-that-the-startup-procedure-for-creating-new-apps-on-the

## Issue template

`templateCreate` succeeded: **PaperOS Spec** (`591f7807-8322-4bda-935e-9a73d221eec3`), an issue template whose description carries the standard spec headings — Goal, Scope (In/Out), Design / Approach, Page spec (logic, access, data, integrations, layout, components), Interfaces & contracts, Acceptance criteria, Verification, Edge cases & failure modes, Dependencies & risks, Artifacts to produce.

## Deviations, fixes and things to know

1. **Surface labels are ungrouped.** Linear enforces one label per group, but 53 of 206 issues legitimately span two or three surfaces (e.g. Customer + Staff). `Customer`, `Staff`, `Developer` and `Agent` were therefore moved out of the `Surface` group to team top level so they can co-apply. The now-empty `Surface` group label remains (nothing was deleted). `Phase` and `Type` stay grouped and exclusive, which is correct for them.
2. **12 project icons from plan.json are not in Linear's icon set** (GitBranch, Palette, CheckCircle, Kanban, Bot, FileText, MessageSquare, Keyboard, Table, DollarSign, Download, Package). Those projects were created without an icon and then updated to the nearest valid Linear icon: Server, Paint, Wrench, Calendar, Robot, Search, Chat, Cursor, Spreadsheet, Dollar, Cube, Box. Rocket, Database, Shield, Users and Megaphone were accepted as-is.
3. **PAP-6 through PAP-12 are duplicates.** The first issue-import run created seven issues before crashing on the Surface-label constraint, and had not yet checkpointed them. Per the no-delete rule they were not removed: each was set to state **Duplicate**, given a description pointing at its canonical twin, and linked with a `duplicate` relation. Canonical equivalents are PAP-13..PAP-19. Team `issueCount` therefore reads 214 (206 canonical + PAP-5 + 7 duplicates).
4. **Dependencies were capped at 3 per issue** as instructed: 182 issues declare dependencies, producing 284 `blocks` relations (dependency blocks dependent). No dependency pointed at an unknown issue key.
5. **Project state**: the eight P0 projects are `started`; the nine P1/P2 projects are `planned`. All start 2026-09-17; target dates come from each project's last milestone (2026-09-29 to 2026-10-01).
6. Nothing was deleted or archived at any point.

## Files

- `<plan-dir>/linear-ids.json` — every created id and url, keyed by plan key.
- `<plan-dir>/linear-summary.md` — this file.
