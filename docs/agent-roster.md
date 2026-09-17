# PaperOS Agent Roster

Index of the nine lead characters and their 28 sub-characters, with the org chart, the routing rules that decide who picks up an issue, the shared rules every session obeys, and the links to each character sheet. Generated from the round-2 snapshot of team PAP (2026-09-17T03:30Z, 275 issues including the 61 created earlier today) and the specs of PAP-103, PAP-104, PAP-106, PAP-108, PAP-109 and PAP-111. The character sheets are the source text for the lead prompts in PAP-104 (`agents/roster-v1/lead-prompts`) and the handbook pages in PAP-112.

## Org chart

```
Justin (only human; approves Needs Justin cards, nothing else)
└── Atlas — Chief Architect and Orchestrator          [https://linear.app/paperos/document/character-sheet-atlas-chief-architect-and-orchestrator-b4725358adc1]
    ├── Dispatcher · Decomposer · Merger
    ├── Forge — Platform Engineer                       [https://linear.app/paperos/document/character-sheet-forge-platform-engineer-6b19c5679dd0]
    │   └── Tauri Smith · Schema Wright · Ops Runner
    ├── Iris — Design Systems Lead                      [https://linear.app/paperos/document/character-sheet-iris-design-systems-lead-43ca4e29d4a9]
    │   └── Token Keeper · Component Crafter · Motion and Input Stylist
    ├── Quill — Spec and Documentation Lead             [https://linear.app/paperos/document/character-sheet-quill-spec-and-documentation-lead-1ba00329d4c8]
    │   └── Page Spec Writer · Changelog Scribe · Prompt Logger
    ├── Sentinel — Quality Lead (no merge rights)       [https://linear.app/paperos/document/character-sheet-sentinel-quality-lead-fc3ada07f9e3]
    │   └── Code Reviewer · Security Auditor · Visual Inspector · Edge Case Hunter
    │       (+ Calibration Auditor, proposed in PAP-241)
    ├── Nova — Product Systems Engineer                 [https://linear.app/paperos/document/character-sheet-nova-product-systems-engineer-a736fa0dc023]
    │   └── CRDT Engineer · Views Engineer · Canvas Cartographer
    ├── Ledger — Business Systems Lead                  [https://linear.app/paperos/document/character-sheet-ledger-business-systems-lead-b876b4a0d809]
    │   └── Payments Integrator · Bookkeeper · Payroll Adapter
    ├── Beacon — Growth Lead                            [https://linear.app/paperos/document/character-sheet-beacon-growth-lead-12b0b4eda18b]
    │   └── Campaign Composer · CRM Builder · Outreach Sequencer
    └── Scout — Library and Migration Researcher        [https://linear.app/paperos/document/character-sheet-scout-library-and-migration-researcher-44cef400dbbc]
        └── Library Evaluator · Import Mapper · Template Packager
```

Two rules the chart encodes. Sentinel reports to Atlas but Atlas cannot overrule a blocking finding; a disputed finding goes to Justin. Justin approves cards; he does not receive questions a spec, ADR or rubric already answers (PAP-94).

## Leads at a glance

| Lead | Remit | Model / effort / mode | Budget share | Owns | Reviews or consults | Sheet |
| -- | -- | -- | -- | -- | -- | -- |
| Atlas | Plan, dispatch, dependencies, budget, merges | Fable 5.1 / xhigh / acceptEdits (orchestrator repo only) | 8% | 32 | 64 | [Atlas](<https://linear.app/paperos/document/character-sheet-atlas-chief-architect-and-orchestrator-b4725358adc1>) |
| Forge | Monorepo, shells, data layer, identity, forge, hosting | Fable 5.1 / xhigh / acceptEdits | 20% | 110 | 41 | [Forge](<https://linear.app/paperos/document/character-sheet-forge-platform-engineer-6b19c5679dd0>) |
| Iris | Tokens, components, themes, Storybook, shells | Fable 5.1 / high / acceptEdits | 8% | 30 | 42 | [Iris](<https://linear.app/paperos/document/character-sheet-iris-design-systems-lead-43ca4e29d4a9>) |
| Quill | Specs, rubrics, playbook, docs, memory, digests | Fable 5.1 / high / acceptEdits in specs, docs, .claude | 10% | 24 | 55 | [Quill](<https://linear.app/paperos/document/character-sheet-quill-spec-and-documentation-lead-1ba00329d4c8>) |
| Sentinel | Four gates, security, evals, calibration | Fable 5.1 / high / plan (reviewers), no merge | 30% | 19 | 237 | [Sentinel](<https://linear.app/paperos/document/character-sheet-sentinel-quality-lead-fc3ada07f9e3>) |
| Nova | Views engine, realtime, canvas, input, CRM and support surfaces | Fable 5.1 / xhigh / acceptEdits | 12% | 30 | 58 | [Nova](<https://linear.app/paperos/document/character-sheet-nova-product-systems-engineer-a736fa0dc023>) |
| Ledger | Stripe, ledger, invoicing, reports, payroll adapter | Fable 5.1 / xhigh / acceptEdits | 4% (12% in P2) | 12 | 11 | [Ledger](<https://linear.app/paperos/document/character-sheet-ledger-business-systems-lead-b876b4a0d809>) |
| Beacon | CRM integrations, outreach, social, Webflow, content agent | Fable 5.1 / high / acceptEdits, plan for sends | 3% (8% in P2) | 4 | 11 | [Beacon](<https://linear.app/paperos/document/character-sheet-beacon-growth-lead-12b0b4eda18b>) |
| Scout | Library evaluation, registry, importers, templates | Fable 5.1 / high; Sonnet 5 / medium for scans / plan | 5% | 6 | 28 | [Scout](<https://linear.app/paperos/document/character-sheet-scout-library-and-migration-researcher-44cef400dbbc>) |

"Owns" counts issues whose Agent line names the lead first (267 canonical issues PAP-13 to PAP-279, excluding PAP-5 to PAP-12). Budget shares are daily allowance defaults for `roster.yaml`; the daily allowance is roughly $700 (about $10,000 over 14 days with a 5 percent reserve held for release week, PAP-111). Atlas reweights weekly as phases open: Ledger and Beacon rise in P2, Scout falls after the surveys close.

## Load and parallelism

A character is a role, not a worker. Forge's 110 issues are not a bottleneck as long as PAP-99 lets several Forge sessions run at once (default six, kept apart by file-lock hints and package ownership). The real constraint is serial dependency: the P0 chain PAP-13 → PAP-42 → PAP-32 → PAP-33 → PAP-57 → PAP-140 is 6.5 agent-days against a four-day P0 window (audit section 5), so Forge sessions should start PAP-13 and PAP-42 before anything else in the org, and Iris, Quill, Scout and Sentinel spend P0 on the issues that need no repo: PAP-66, PAP-92, PAP-79, PAP-114, PAP-209, PAP-56, PAP-212, PAP-239, PAP-219.

Sentinel's 237 review touch points are handled by review sessions spawned per PR by the harness (PAP-243), not by one long-lived session; the 30 percent budget pool is sized for that.

## Routing: who picks up an issue

Today the router is the Agent line in each spec ("Built by Forge (Tauri Smith). Reviewed by Sentinel (Security Auditor)."). The `Character` label group that PAP-91 and PAP-93 assume does not exist in the live workspace (audit item 1); until PAP-91 adds it (the former `pm-linear/workspace-reconcile` is merged into PAP-91), the orchestrator parses the Agent line and the sub-character in parentheses becomes the session's bundle (PAP-106). Defaults when an Agent line is missing:

| Project | Research | Spec | Build | Review | Infra | Docs |
| -- | -- | -- | -- | -- | -- | -- |
| app-shell, data-layer, identity, forge | Scout with Forge | Forge (Quill for audience and access formats) | Forge | Sentinel | Forge (Ops Runner) | Forge with Quill |
| design-system | Iris with Scout | Iris | Iris | Sentinel (Visual Inspector) | Forge (Storybook infra) | Iris |
| quality | Sentinel | Sentinel with Atlas | Sentinel (gates), Forge (CI plumbing) | Sentinel | Sentinel with Forge | Quill |
| pm-linear, agents | Atlas | Atlas | Atlas (Dispatcher), Forge for hooks and sandbox | Sentinel (evals) | Atlas | Quill |
| spec-builder | Scout | Quill | Quill (schema, validator, tests), Iris (codegen UI, editor), Nova (graph) | Sentinel | Forge | Quill |
| collab, realtime, input, tables | Nova with Scout | Quill (view model), Iris (conflict UX), Nova (input) | Nova; Iris for comment UI and field renderers; Forge for servers and stores | Sentinel | Forge | Quill |
| business-core | Ledger | Ledger | Ledger; Forge for expenses; Nova for dashboards | Sentinel (Security Auditor) | Forge | Ledger with Quill |
| growth | Beacon | Forge (CRM model) | Beacon (integrations), Nova (views) | Sentinel | Forge | Beacon |
| migration | Scout | Scout | Nova (framework, Airtable), Scout (CSV, ids), Quill (Notion, templates, agent), Ledger (finance), Atlas (ClickUp, Linear) | Sentinel | Forge (test accounts) | Quill |
| libraries | Scout with Iris or Forge | Scout | Quill (registry), Atlas (MCP catalog, Renovate, scan routine) | Sentinel | Forge (license CI) | Scout |

Cross-character work is always one owner plus named consultants; the owner posts the handoff and the consultant reviews the part in their lane.

## Sub-character index

| Sub | Lead | One-line remit | Anchor issues |
| -- | -- | -- | -- |
| Dispatcher | Atlas | Claims, spawns, moves states, budget holds | PAP-96, PAP-99, PAP-111 |
| Decomposer | Atlas | Contract-valid issues from briefs and Justin's notes | PAP-93, PAP-95, PAP-103, inbound triage (pending) |
| Merger | Atlas | Rebase, merge green PRs, tag, promote | PAP-52, PAP-254 |
| Tauri Smith | Forge | Desktop and mobile targets, windows, updater | PAP-19, PAP-20, PAP-21, PAP-255 to PAP-263 |
| Schema Wright | Forge | Drizzle, migrations, RLS, encryption | PAP-32, PAP-33, PAP-34, PAP-228 |
| Ops Runner | Forge | VPS, Docker, backups, runners, nightly | PAP-25, PAP-26, PAP-45, PAP-50, PAP-253 |
| Token Keeper | Iris | DTCG tokens, themes, branding, print theme | PAP-66, PAP-75, PAP-235 |
| Component Crafter | Iris | Components, stories, axe, shells | PAP-67, PAP-236 to PAP-238, PAP-62, PAP-63 |
| Motion and Input Stylist | Iris | Motion, focus, input states, TV navigation | PAP-72, PAP-152, PAP-158 |
| Page Spec Writer | Quill | Specs, prompts, migration agent definition | PAP-114, PAP-118, PAP-125, PAP-208 |
| Changelog Scribe | Quill | Changelogs, release digest | PAP-133, PAP-89, PAP-52 |
| Prompt Logger | Quill | Log schema, redaction, memory curation | PAP-107, PAP-109, PAP-135 |
| Code Reviewer | Sentinel | Correctness and spec conformance | PAP-244, PAP-240, PAP-64 |
| Security Auditor | Sentinel | Auth, RLS, secrets, threat model, DAST | PAP-219, PAP-245, PAP-80 |
| Visual Inspector | Sentinel | Screenshots, video, vision annotation | PAP-246 to PAP-248, PAP-83, PAP-84, PAP-137 |
| Edge Case Hunter | Sentinel | Adversarial scenarios, load, flake triage | PAP-249 to PAP-251, PAP-147, PAP-90 |
| Calibration Auditor (proposed) | Sentinel | Weekly verdict spot check, recall trend | PAP-241 |
| CRDT Engineer | Nova | Yjs rooms, presence, editor, offline | PAP-139, PAP-141, PAP-142, PAP-148, PAP-149 |
| Views Engineer | Nova | Compiler, grid, view kinds, formulas, dashboards | PAP-163, PAP-165 to PAP-173, PAP-102 |
| Canvas Cartographer | Nova | UX-flow canvas, org chart, overlays | PAP-127, PAP-132, PAP-123, PAP-113 |
| Payments Integrator | Ledger | Stripe Billing, Connect, Tax, webhooks | PAP-177, PAP-178, PAP-181, PAP-182 |
| Bookkeeper | Ledger | Ledger, posting rules, reports | PAP-179, PAP-183, PAP-180 |
| Payroll Adapter | Ledger | Provider interface and first adapter | PAP-176, PAP-184 |
| Campaign Composer | Beacon | Approval-gated posts, emails, landing copy | PAP-192, PAP-190, PAP-193 |
| CRM Builder | Beacon | CRM models, segments, consent | PAP-187, PAP-189, PAP-195 |
| Outreach Sequencer | Beacon | Sequences, warmup, compliance | PAP-191, consent centre (pending) |
| Library Evaluator | Scout | Rubric scoring, ADRs, weekly scan | PAP-209, PAP-212 to PAP-215, PAP-218 |
| Import Mapper | Scout | Mapping, dry runs, id mappings, importers | PAP-198, PAP-200, PAP-201, PAP-199 |
| Template Packager | Scout | Business seed packs and demo data | PAP-207 |

## Shared rules every session obeys

* Read first (PAP-92): the issue body, linked specs, `CLAUDE.md`, the character's memory file, the two most recent comments, touched ADRs.
* Report (PAP-92): `Session started`, at most one progress note per 30 minutes, `Session ended` with the `paperos-session` footer (`sessionId`, `character`, `costUsd`, `turns`, `pr`, `status`, `playbookVersion`).
* Hand off (PAP-108): `HANDOFF.md` plus a footer `handoff` object of kind `build-to-review`, `review-to-build`, `spec-to-build`, `research-to-decision`, `split` or `escalate`; every open question carries a default; `pnpm handoff lint` before ending.
* Deny list (PAP-106), identical for all: `git push` to `main`, `rm -rf`, `curl | sh`, writing `.claude/settings.json` or `ops/secrets/**`, disabling TLS, disabling a gate, deleting or archiving anything in Linear, changing another issue's state except through the orchestrator. Extended by `security/agent-deny-list` (pending).
* Least privilege (PAP-106): each session runs with its character's bundle (`settings.json`, `.mcp.json`, `hooks.json`); a sub-character spawned by Task gets its own, narrower bundle; temporary extra scope needs a `scope:+<name>` label and expires with the session.
* Memory (PAP-109): global 1000 tokens, project 2000, character 3000, one bullet per entry with `(PAP-n, date)` provenance; Quill curates, Atlas alone also writes `global.md`.
* Budget (PAP-111): per-issue caps S $60, M $180, L $450; warning at 80 percent of a session cap, abort with `wip:` commit at 100; `KILL`, `KILL <character>`, `KILL ALL` from Justin stop sessions within five seconds; reviewers draw from a separate pool.
* Models (PAP-104): leads on `claude-fable-5-1`; read-mostly subs (Library Evaluator facts, Prompt Logger, Changelog Scribe, Token Keeper, Motion Stylist, CRM Builder, Template Packager) on `claude-sonnet-5`; reviewers on `claude-fable-5-1` at high in `plan` mode. Prompts never name a model; the orchestrator config holds the fallback.

## Escalation matrix

| Situation | Goes to |
| -- | -- |
| Dependency cycle, phase inversion, two sessions on the same files, contract conflict between projects, split proposal, third-round review dispute, research time box exceeded | Atlas |
| Irreversible external action (DNS, domain, live keys, data deletion), spend from the reserve, reversing an architecture decision, hiring or retiring a character, release candidate, legal, tax or PCI posture, security incident with real data, any public publication or live send channel | Needs Justin, via an Atlas decision card (PAP-94), batched, max five open |
| Credential and account asks: Apple Developer, Windows certificate, Android keystore, GitHub App install, Hetzner, Stripe live and Connect KYC, payroll sandbox, Twilio, Resend, Webflow, social platform app reviews, Airtable, Notion, ClickUp, QuickBooks, Xero, Google OAuth | One consolidated Needs Justin card filed on day one (audit item 5) |
| Anything a spec, ADR, rubric or this roster already decides | Nobody; record the default in the handoff and proceed |

## How to summon a character

1. From Linear: set the Agent line in the spec (or, once PAP-91 is reconciled, the Character label), move the issue to `Ready for Claude`; the orchestrator (PAP-96) claims it with the character's bundle.
2. Locally: `pnpm agents run <name> --issue PAP-123` (PAP-104 build output).
3. For an opinion: `@atlas` … `@scout` in a Linear comment from a human spawns a read-only reply session capped at $3 (PAP-112).
4. New character: YAML plus a label; no code change (PAP-104 edge case). A new lead requires a Needs Justin approval (project non-goal).

## Pending work that changes this roster

The workspace is at the free-plan issue cap, so these fully specified issues live in project documents until it lifts: `agents/roster-v1/yaml`, `agents/roster-v1/lead-prompts` (this roster and the nine sheets are its input), `agents/roster-v1/sub-prompts`, `agents/roster-v1/build`, `agents/runtime-sandbox`, `agents/session-observability`, `agents/eval-harness/*` (Round 2 pending issues: agents), `security/agent-deny-list`, `security/prompt-injection`, `security/credential-broker` (Round 2 pending issues: security), `pm-linear/workspace-reconcile`, `pm-linear/inbound-triage` (Round 2 pending issues: pm-linear). When they are created, each sheet's Sources line gains the identifier and the Calibration Auditor row becomes a real sub.

## Sources

plan.json `agents[]`; PAP-92, PAP-93, PAP-94, PAP-96, PAP-99, PAP-103, PAP-104, PAP-105, PAP-106, PAP-108, PAP-109, PAP-110, PAP-111, PAP-112, PAP-113; round-2 audit sections 2, 3a, 5, 6; the ownership table computed from every Agent line in the snapshot and the 61 issues created earlier today.
