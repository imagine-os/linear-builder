---
identifier: "PAP-750"
title: "Page spec templates: `paperos-spec new --template dashboard|wizard|report|settings|kiosk|landing|detail-tabs` with filled examples and a template lint"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P2"
type: "Docs"
priority: 3
surfaces: ["Developer"]
milestone: "Spec editor UI"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-114", "PAP-125"]
blocks: []
key: "r4/spec-builder/page-spec-templates"
url: "https://linear.app/paperos/issue/PAP-750/page-spec-templates-paperos-spec-new-template"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:36.649Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-750: Page spec templates: `paperos-spec new --template dashboard|wizard|report|settings|kiosk|landing|detail-tabs` with filled examples and a template lint

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Docs S

**Goal**

PAP-361 derives CRUD pages and PAP-125 documents three examples. Everything else an agent writes (a dashboard, a multi-step wizard, a report, a kiosk screen, a landing page, a tabbed detail) starts from a blank YAML file. Backstage software templates exist for this reason. Ship seven starting points that validate, generate and screenshot, plus the CLI that copies them.

**Scope**

In: `packages/spec/templates/pages/<template>.spec.yaml` with `{{placeholders}}` and explanatory comments, `paperos-spec new <id> --template <t> [--entity <e>] [--surface <s>]` in PAP-115's CLI filling placeholders from `app.spec.yaml`, a Vitest lint that every template renders to a strict-valid spec for the clinic fixture, generated screenshots of each at 375 and 1280 for `docs/spec/templates.mdx`. Out: business seed packs (PAP-207, PAP-427), CRUD derivation (PAP-361), the editor's 'new spec' dialog (PAP-376 may call the CLI).

**Spec**

* Templates: `dashboard` (`ui.dashboardBlocks` with three aggregate queries and cross-filter params), `wizard` (multi-step with `logic.actions` per step, search-param step state, `states.saving`), `report` (date range params, `ui.dataGrid` with aggregates, print state, export action), `settings` (sections, `access` staff.admin, audit reason), `kiosk` (`layout.template: kiosk`, large targets, idle reset event, PAP-158 spatial focus hints), `landing` (`public: true`, `seo`, hero and CTA components, form capture to PAP-193 when enabled), `detail-tabs` (record header, tabs from relations, comments anchor, activity).
* Placeholders: `{{id}}`, `{{entity}}`, `{{Entity}}`, `{{plural}}`, `{{surface}}`, `{{audience}}`; unfilled placeholders fail validation with `SPEC_TEMPLATE_PLACEHOLDER`.
* Each template includes five edge cases across empty, huge, offline, denied and concurrent edit, matching PAP-118's drafting rules, and a `help` section (v1.1) pointing at its docs page.
* Templates use registered component ids only; missing components (dashboard blocks before PAP-173) fall back to `ui.responsiveGrid` with a callout comment naming the blocking key, as PAP-125 does.
* `docs/spec/templates.mdx` lists when to use which, with screenshots and the CLI line for each.

**Interface contract**

Provides: seven templates, `paperos-spec new`, rule `SPEC_TEMPLATE_PLACEHOLDER`, docs page. Consumes: `PageSpecSchema` (PAP-114), CLI (PAP-115), examples conventions (PAP-125), `app.spec.yaml` (PAP-117), component ids (PAP-74, soft), v1.1 `help` and `seo` (soft), kiosk template (PAP-23, deferred; falls back to `focus`). Consumed by: PAP-118 skill (offers a template first), PAP-376 editor new-spec flow, PAP-363 starter kit (landing, settings), PAP-29 drill.

**Definition of done**

* Seven templates render strict-valid specs for the clinic fixture and pass `gen:page`, `gen:tests`; screenshots at 375 and 1280 in light and dark embedded in the docs page.
* PAP-118 skill lists templates in its question bank (comment there); CHANGELOG entry; Linear comment with the docs link.

**Test plan**

* Unit: placeholder filling, lint rule, template validity per fixture app.
* Integration: full generator chain on each template in CI as part of the drift job.
* E2E: Playwright captures the screenshots.

**Demo**

Run `paperos-spec new therapist-dashboard --template dashboard --entity appointment`, validate, `gen:page`, open the route and see the three tiles with mocked data. Under two minutes.

**Edge cases**

* Entity without aggregatable fields: dashboard template uses counts only and comments why.
* Surface `agent`: templates emit `deny: [customer.*]` and read-only actions.
* Template id collides with an existing page: CLI refuses without `--force`.

**Dependencies**

Hard: PAP-114, PAP-125. Soft: PAP-115, PAP-117, PAP-74, PAP-173, PAP-23, PAP-118, PAP-376, PAP-740.

**Agent**

Builder: Quill (Page Spec Writer). Reviewer: Sentinel (Code Reviewer) with Nova on codegen fit.

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/spec-builder/schema-v1-1-extensions` = PAP-740.
