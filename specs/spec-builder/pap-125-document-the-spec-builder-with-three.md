---
identifier: "PAP-125"
title: "Document the spec builder with three fully specified example pages (customer list, staff dashboard, agent console)"
project: "spec-builder"
projectName: "Spec Builder"
phase: "P1"
type: "Docs"
priority: 2
surfaces: ["Developer"]
milestone: "Spec editor UI"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-115"]
blocks: []
key: "spec-builder/spec-docs"
url: "https://linear.app/paperos/issue/PAP-125/document-the-spec-builder-with-three-fully-specified-example-pages"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:50:30.931Z"
---

# PAP-125: Document the spec builder with three fully specified example pages (customer list, staff dashboard, agent console)

**Goal**

Document the spec builder end to end and ship three fully specified, generated and screenshotted example pages (customer invoice list, staff dashboard, agent console) that agents copy when writing new specs. The examples are executable: they validate, generate, pass conformance and render in the template app.

**Scope**

* In: `specs/pages/examples/{customer-invoices,staff-dashboard,agent-console}.spec.yaml` with explanatory comments under 150 lines each, their generated artifacts committed, `docs/spec/` pages (`workflow.mdx`, `page-spec`, `app-spec`, `access`, `data`, `integrations`, `codegen`, `conformance`, `flow-graph`, `editor`, `faq`, glossary) with `_meta.yaml` reading order.
* Out: the generators themselves, docs engine features (PAP-128), the authoring skill (PAP-118, exercised here).

**Spec**

* `customer-invoices`: surface customer, live query on `invoice`, `payInvoice` via Stripe in mock mode, five edge cases. `staff-dashboard`: `ui.dashboardBlocks` (PAP-173) or `ui.responsiveGrid` fallback, three aggregate queries, `staff.*` wildcard access with a condition. `agent-console`: lists prompt sessions from PAP-129, actions for `agent.builder` and `staff.admin`, `deny` customers, offline and denied states.
* Docs use the PAP-128 frontmatter and `<FileRef path lines>` includes so code never goes stale; `pnpm docs:lint` fails on missing paths; screenshots come from Playwright artifacts stored under `docs/spec/examples/<id>/` in light and dark.
* Language: second person, short sentences, one concept per heading; glossary defines spec, surface, audience, slot, state, transition; FAQ entries cite the spec version.
* Examples live under the `examples/` namespace and `/_app/examples/*` routes, excluded from production navigation; seeds use fixed dates.

**Interface contract**

* Provides: the three example specs as the canonical copy sources, `docs/spec/workflow.mdx` as the single onboarding page for spec writers, `docs/spec/examples/<id>/{access-matrix.md, flow-graph.json, *.png}`, glossary anchors linked from validator hints (`docs/spec/validator.md#<code>`).
* Consumers: PAP-105 `page-from-spec` and PAP-118 `author-spec` reference `workflow.mdx`; PAP-116, PAP-120, PAP-122 use the examples as fixtures; PAP-24 template docs link here; PAP-110 Quill golden task; PAP-29 drill.
* Requires: PAP-115 (hard); PAP-120, PAP-119, PAP-122, PAP-116, PAP-128, PAP-82 expected but each has a documented fallback.

**Definition of done**

* Three examples pass `paperos-spec validate --strict`, `gen:page`, `gen:data`, `gen:tests` and their suites in CI.
* Screenshots of each example in success, empty and denied states at 375 and 1280 px, light and dark, embedded.
* Docs render in the docs engine or Pages fallback with working includes and zero lint errors.
* A fresh session given only `workflow.mdx` writes a valid spec for a fourth page in one attempt (transcript linked).
* Changelog; Linear comment with docs link, screenshots and transcript.

**Test plan**

* Unit: docs lint (paths, frontmatter, glossary anchors), line-count limit on examples.
* Integration: full generator chain on the examples in CI as part of the drift job.
* e2e: Playwright captures the nine state screenshots per theme.
* Visual: docs pages at 375 and 1280 px; example pages at 375 and 1280 px through gate 3.

**Demo**

Open `docs/spec/workflow.mdx`, follow its five steps against `staff-dashboard`, then run `pnpm spec:validate --strict specs/pages/examples` and open `/_app/examples/staff-dashboard` in the template app to see the generated page. Two minutes.

**Edge cases**

* Dependency not merged (dashboard blocks): fallback component with a callout naming the blocking key.
* Generators change: examples are in the drift job, so generator PRs regenerate them.
* Docs engine unavailable: same MDX builds to Pages with a minimal Vite MDX setup.
* Example ids collide with real pages later: namespaced routes.
* Screenshot flake from dates: fixed seeds.

**Dependencies**

Blocked by PAP-115. Soft: PAP-116, PAP-119, PAP-120, PAP-122, PAP-128, PAP-82.

**Agent**

Built by Quill (Page Spec Writer, Changelog Scribe); reviewed by Nova for codegen accuracy and Sentinel for test claims.

**Size**

M
