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
source: "plan/specs/bucket-4.json (round-1 canonical spec JSON)"
---

# PAP-125: Document the spec builder with three fully specified example pages (customer list, staff dashboard, agent console)

**Goal**

Document the spec builder end to end and ship three fully specified, generated and screenshotted example pages (customer invoice list, staff dashboard, agent console) that agents copy when writing new specs. The examples are executable: they validate, generate, pass conformance and render in the template app.

**Scope**

In:
- `specs/pages/examples/customer-invoices.spec.yaml` (surface customer, `data` live query on `invoice`, `markPaid`-style mutation replaced by `payInvoice` integration with Stripe in mock mode, five edge cases), `specs/pages/examples/staff-dashboard.spec.yaml` (surface staff, `ui.dashboardBlocks` from `tables/dashboard-blocks` or `ui.responsiveGrid` fallback, three queries with aggregates, access with `staff.*` wildcards and a condition), `specs/pages/examples/agent-console.spec.yaml` (surface agent, lists prompt sessions from `collab/prompt-log-store`, actions restricted to `agent.builder` and `staff.admin`, `deny` for customers, offline and denied states).
- Each example annotated with `#` comments explaining every section, kept under 150 lines.
- Generated artifacts committed: route, view, logic stubs, data hooks, conformance tests, flow graph, access matrix (`docs/spec/examples/<id>/`).
- Docs in `docs/spec/` rendered by `collab/docs-engine`: `index.mdx` (why spec-first, lifecycle draft to built), `page-spec.md` (generated reference), `app-spec.md`, `access.md`, `data.md`, `integrations.md`, `codegen.md`, `conformance.md`, `validator.md`, `editor.md`, `workflow.mdx` (author with the skill, validate, generate, build, test, review, ship; includes a Mermaid sequence diagram), `examples/*.mdx` embedding the YAML with callouts and screenshots at 375 and 1280, `faq.md` (twelve real questions collected from sessions and Linear comments).
- A `docs/spec/checklist.md` agents paste into PR bodies (spec exists, validates, generated files current, conformance green, screenshots attached).

Out: docs for the design system or data layer beyond links; video tutorials.

**Spec**

- Pages use the docs engine frontmatter (`title`, `owner: Quill`, `audience: developer`, `tags: [spec]`, `updated`).
- Every code block referencing a file is included via the docs engine `<FileRef path=... lines=...>` component so it never goes stale; a docs lint (`pnpm docs:lint`) fails on missing paths.
- Screenshots are pulled from the Playwright artifacts of the examples and stored in `docs/spec/examples/<id>/*.png` with light and dark variants.
- Reading order and sidebar defined in `docs/spec/_meta.yaml`.
- Language rules: second person, short sentences, one concept per heading, no unexplained acronyms; a glossary section defines spec, surface, audience, slot, state, transition.

**Definition of done**

- Three examples pass `paperos-spec validate --strict`, `gen:page`, `gen:data`, `gen:tests` and their conformance suites in CI.
- Playwright screenshots of each example in success, empty and denied states at 375 and 1280, light and dark, embedded in the docs.
- Docs render in the in-app docs engine (or GitHub Pages fallback if it is not merged) with working `FileRef` includes and no lint errors; link in comment.
- A fresh Claude Code session given only `docs/spec/workflow.mdx` writes a valid spec for a fourth page in one attempt (transcript linked).
- CHANGELOG entry; Linear comment with docs link, screenshots and the transcript.

**Edge cases**

- A dependency the example uses is not merged (dashboard blocks): example falls back to the listed alternative component and notes it in a callout with the blocking issue key.
- Generated files drift when generators change: examples are part of the drift job, so generator PRs must regenerate them.
- Docs engine unavailable: the same MDX builds with a minimal Vite MDX setup to Pages.
- Example ids collide with real app pages later: examples live under `examples/` namespace and route prefix `/_app/examples/*`, excluded from production navigation.
- Screenshots flake between runs (timestamps in seeded data): seeds use fixed dates.
- FAQ answers become wrong after schema changes: each FAQ entry cites the spec version it applies to.

**Dependencies**

`spec-builder/validator` (hard). Soft but expected: `spec-builder/layout-codegen`, `spec-builder/data-section`, `spec-builder/conformance-tests`, `spec-builder/access-section`, `collab/docs-engine`, `quality/playwright-matrix`. Consumed by `agents/skills-library` `page-from-spec`, `spec-builder/spec-authoring-skill`, `app-shell/template-docs`.

**Agent**

Built by Quill (Page Spec Writer, Changelog Scribe). Reviewed by Sentinel (spec-conformance reviewer) and Nova for the examples' technical accuracy.

**Size**

M: writing is fast, but three executable examples must stay green across many generators.
