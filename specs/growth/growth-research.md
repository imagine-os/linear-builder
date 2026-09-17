---
identifier: "PAP-188"
title: "Survey open-source CRM and marketing stacks (Twenty, Postiz, Listmonk, Dub) for reuse vs build; write ADR"
project: "growth"
projectName: "Growth: Marketing, Outreach & CRM"
phase: "P1"
type: "Research"
priority: 2
surfaces: ["Staff"]
milestone: "CRM core"
state: "Ready for Claude"
parent: null
children: []
blockedBy: []
blocks: ["PAP-190"]
key: "growth/growth-research"
url: "https://linear.app/paperos/issue/PAP-188/survey-open-source-crm-and-marketing-stacks-twenty-postiz-listmonk-dub"
source: "plan/specs/bucket-7.json (round-1 canonical spec JSON)"
---

# PAP-188: Survey open-source CRM and marketing stacks (Twenty, Postiz, Listmonk, Dub) for reuse vs build; write ADR

**Goal**

Decide, before any growth code is written, which parts of the marketing stack PaperOS borrows and which it builds: evaluate Twenty (CRM), Postiz (social scheduling), Listmonk (email campaigns), Dub (links and attribution), plus Chatwoot (support inbox) and Umami/PostHog (analytics) against the library rubric, and record the outcome as an ADR that every growth issue then follows without re-litigating.

**Scope**

In:
- Rubric from `libraries/eval-rubric` extended with growth-specific criteria: multi-tenant model, embeddability (API, iframe, or fork), data ownership and export, deliverability tooling, license under `libraries/license-policy` (all six candidates are AGPL-3.0 or similar; document exactly what "review AGPL" means for a self-hosted, network-exposed service).
- Three integration shapes scored per product: (a) run as a Docker service on the VPS and integrate via API, (b) fork and embed components, (c) reimplement the relevant subset on the tables engine.
- Spike folder `spikes/growth-stack/` with Coolify compose files that stand each candidate up on staging for a day; screenshots of each product's core screen; API smoke scripts (create a contact, schedule a post, send a test email, create a short link).
- Written mapping of each candidate's data model to `growth/crm-model` fields, reused by `migration/format-research` for HubSpot and by the importers.
- ADR `docs/adr/00xx-growth-stack.md` with per-product decisions and the re-open criteria; registry entries drafted for `libraries/registry`.

Out: production deployment of any candidate, writing adapters (follow-on issues), evaluating paid SaaS beyond a one-line note.

**Spec**

- Time-box: 1.5 agent-days total, maximum 3 hours per product; unknowns become rubric penalties.
- Default hypothesis to confirm or reject: build CRM and segments on the tables engine (because views, permissions and RLS are already ours), borrow Postiz's platform adapters as reference or run it as a service behind an approval queue we own, use Listmonk only if Resend's broadcast API proves insufficient, use Dub for short links via API, and reject running Twenty because it duplicates the tables engine.
- Each product scored 1-5 on: license fit, self-host effort, API completeness, tenant isolation, TypeScript quality, community velocity (commits last 90 days), cost of exit.
- Deliverables per product: score table, "what we would take", "what we would never take", hours estimate for each integration shape.
- Deliverability section: compare Resend, Postmark and SES for transactional plus marketing volume, warmup features and inbound parsing, feeding `growth/outreach-sequences` and `growth/support-inbox`.
- Analytics section: Umami vs PostHog self-hosted vs a hand-rolled event table for `growth/attribution`; must respect the privacy-first requirement (no third-party cookies, EU hosting possible).

**Definition of done**

- Spikes committed under `spikes/growth-stack/` (excluded from `turbo build`), compose files runnable on staging.
- ADR approved by Atlas and Beacon via PR comment; decisions cross-referenced in the descriptions of `growth/social-scheduler`, `growth/outreach-sequences`, `growth/attribution`, `growth/support-inbox` (comment on each).
- Screenshots of each candidate's core screen at 1280 and 1920 attached, plus a one-page comparison table rendered from `results.json`.
- License review for every AGPL candidate written up and approved by Sentinel (Security Auditor).
- `libraries/registry` entries or a Linear comment for Scout to add them.
- CHANGELOG entry; Linear comment with the ADR link and table.

**Edge cases**

- Product requires its own Postgres or Redis: score the operational cost, do not share our primary database.
- API needs an OAuth app review that takes weeks (LinkedIn, TikTok): note lead time so `growth/social-scheduler` starts applications immediately.
- Candidate license changed recently (Dub moved parts to a commercial license): record the exact version evaluated.
- Self-hosted docs incomplete: score self-host only on what was actually achieved in the spike.
- Two candidates overlap (Postiz and Listmonk both send email): pick one owner per capability.
- Justin prefers a paid tool: capture as an open question in the ADR, not a blocker.

**Dependencies**

None (can start now). Informs `growth/social-scheduler` (hard, listed dependency), `growth/outreach-sequences`, `growth/attribution`, `growth/support-inbox`, `migration/format-research`. Uses `libraries/eval-rubric` and `libraries/license-policy` if merged; otherwise apply their draft rubric.

**Agent**

Researched by Scout (Library Evaluator) paired with Beacon for the growth judgement. Reviewed by Atlas (decision) and Sentinel (Security Auditor) for license.

**Size**

M: six spikes with real installs is a day and a half of strictly time-boxed work.
