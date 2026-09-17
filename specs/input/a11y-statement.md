---
identifier: "PAP-160"
title: "Publish an accessibility statement and conformance report template per app"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P2"
type: "Docs"
priority: 3
surfaces: ["Customer"]
milestone: "Voice and accessibility certification"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-117", "PAP-156"]
blocks: []
key: "input/a11y-statement"
url: "https://linear.app/paperos/issue/PAP-160/publish-an-accessibility-statement-and-conformance-report-template-per"
source: "plan/specs/bucket-5.json (round-1 canonical spec JSON)"
---

# PAP-160: Publish an accessibility statement and conformance report template per app

**Goal**

Give every PaperOS app compliance evidence out of the box: a public accessibility statement page and a conformance report (WCAG 2.2 AA, in VPAT 2.5 / ACR structure) generated from real test results rather than written by hand, updated on every release so it never drifts from the product. Customers asking "is this accessible?" get a link, and Justin gets a one-page view of remaining gaps.

**Scope**

In:
- Templates in `packages/spec/templates/a11y/`: `statement.mdx` (commitment, conformance status, known limitations, feedback channel, compatibility list, assessment method, date) and `acr.mdx` (WCAG 2.2 A/AA criteria table with Supports / Partially Supports / Does Not Support / Not Applicable and remarks), with placeholders filled from app.spec.yaml (`spec-builder/app-level-spec`: name, contact, audiences) and from test data.
- Generator `pnpm a11y:report` in `packages/input/scripts/` that reads: axe results from `design-system/a11y-audit` and `quality/playwright-matrix`, screen-reader matrix from `input/screen-reader`, focus-order audit from `input/focus-management`, contrast results from `quality/screenshot-annotation`, and open Linear issues labelled `a11y` (via `pm-linear/linear-sync` read API); it maps each data source to WCAG success criteria through `criteria-map.json` and writes `docs/a11y/statement.mdx`, `docs/a11y/acr.mdx` and `docs/a11y/report.json`.
- Rendering: the docs engine (`collab/docs-engine`) serves `/accessibility` publicly in the customer portal shell and staff console; PDF export of the ACR via the PDF pipeline from `business-core/invoicing` (reuse) for procurement requests.
- Release hook: `quality/release-train` runs the generator per release candidate; the digest (`quality/review-report`) includes the conformance delta (criteria that changed status).
- Feedback channel: the statement links to a form (`tables/gallery-list-form` form view) creating a Linear issue with the `a11y` label through `pm-linear/webhooks`.

Out: legal review wording (flagged for Justin), EN 301 549 and Section 508 chapters beyond the WCAG table (template leaves sections stubbed), third-party audit procurement.

**Spec**

- `criteria-map.json` entries: `{ criterion: '2.1.1', sources: [{ type: 'axe', rules: ['keyboard'] }, { type: 'sr-matrix', flows: ['*'] }, { type: 'manual', note }], defaultStatus: 'Not Evaluated' }`; status resolution: any failing automated rule → Partially Supports (or Does Not Support if all fail), all pass and manual confirmed → Supports, no data → Not Evaluated (shown, never hidden).
- Every non-Supports row must link the tracking Linear issue; the generator fails if a failing criterion has no issue, forcing one to be filed.
- Known limitations section is generated from open `a11y` issues with customer-facing summaries (field `publicSummary` in the issue contract from `pm-linear/issue-contract`).
- Statement page itself must pass axe, have a plain-language reading level (Flesch-Kincaid grade ≤ 9, checked with `text-readability`), and be translatable (strings in MDX frontmatter).
- Versioning: report files carry `generatedAt`, app version from `forge/release-tags`, and a hash; the page shows "Last reviewed" and "Next review by" (90 days).
- A template app with no test data renders a statement marked "Not yet assessed" instead of failing the build.

**Definition of done**

- `pnpm a11y:report` runs in CI on the template app and commits `docs/a11y/*`; all 55 WCAG 2.2 A/AA criteria appear with a status and source.
- `/accessibility` renders in the customer portal at 320, 768 and 1280 px; screenshots attached; axe clean; readability check passes.
- ACR PDF export attached to the PR.
- Release-train integration shown in one RC digest with a conformance delta section.
- Feedback form creates a labelled Linear issue (test issue linked, then closed).
- Docs `docs/platform/a11y/statement-and-acr.md` explaining how to keep the map current; changelog entry; Linear comment with the page link, routed to Needs Justin for wording approval.

**Edge cases**

- A criterion covered only by manual testing with no record yet: shown as Not Evaluated with an owner, not silently Supports.
- Tenant white-labels the app (`design-system/theming`): statement uses the tenant's name and contact but the same test data; theming contrast results are per-tenant, so contrast criteria are evaluated per theme and the worst status is shown.
- Test suite skipped in a hotfix release: the generator reuses the last full results and marks the report "based on version X".
- Linear API unavailable during generation: fall back to the last cached issue list with a warning banner in the report.
- Criteria not applicable (no audio/video content): `Not Applicable` requires a justification string in the map.
- Very long known-limitations list (over 20): grouped by area with a collapsed view.

**Dependencies**

- `input/screen-reader` (matrix), `design-system/a11y-audit`, `quality/playwright-matrix`, `quality/screenshot-annotation`, `input/focus-management` (focus audit), `spec-builder/app-level-spec`, `collab/docs-engine`, `quality/release-train`, `quality/review-report`, `pm-linear/linear-sync`, `pm-linear/issue-contract`, `forge/release-tags`.

**Agent**

Builder: Quill (Changelog Scribe sub-agent for the templates, Page Spec Writer for the docs page) with Sentinel providing the data sources. Reviewer: Sentinel (Visual Inspector) verifies the mapping against results; Justin approves wording.

**Size**

S: templates and a generator over existing data; the discipline is in the criteria map.
