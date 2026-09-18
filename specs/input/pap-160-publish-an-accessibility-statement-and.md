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
blockedBy: ["PAP-117", "PAP-156", "PAP-620", "PAP-647", "PAP-670"]
blocks: ["PAP-896", "PAP-904"]
key: "input/a11y-statement"
url: "https://linear.app/paperos/issue/PAP-160/publish-an-accessibility-statement-and-conformance-report-template-per"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:28:43.559Z"
model: "claude-sonnet-5"
effort: "low"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-160: Publish an accessibility statement and conformance report template per app

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / low — Docs S

**Goal**

Give every PaperOS app compliance evidence out of the box: a public accessibility statement and a WCAG 2.2 AA conformance report (VPAT 2.5 / ACR structure) generated from real test results and refreshed every release, so it never drifts. Customers get a link; Justin gets a one-page view of remaining gaps.

**Scope**

In:

* Templates `packages/spec/templates/a11y/statement.mdx` and `acr.mdx` filled from `app.spec.yaml` (PAP-117: name, contact, audiences) and test data.
* Generator `pnpm a11y:report` reading axe results (PAP-73, PAP-82), the screen-reader matrix (PAP-156 `sr-results.json`), focus-order audit (PAP-152), contrast results (PAP-84) and open `a11y` Linear issues (PAP-101 read API); maps sources to criteria via `criteria-map.json`; writes `docs/a11y/statement.mdx`, `acr.mdx`, `report.json`.
* Rendering at `/accessibility` in portal and console via PAP-128; ACR PDF via PAP-235's `renderPdf()`.
* Release hook: PAP-88 runs the generator per RC; PAP-89 digest shows the conformance delta.
* Feedback form (PAP-169 form view) creating an `a11y` issue through PAP-97.

Out: legal wording (Justin), EN 301 549 and Section 508 chapters (stubbed), third-party audits.

**Spec**

* Map entry `{ criterion, sources: [{ type: axe|sr-matrix|focus|contrast|manual, ... }], defaultStatus: 'Not Evaluated' }`; resolution: any failing automated rule → Partially Supports (Does Not Support if all fail); all pass plus manual confirmed → Supports; no data → Not Evaluated, shown never hidden.
* Every non-Supports row links a tracking issue or the generator fails.
* Known limitations generated from open `a11y` issues' `publicSummary` (PAP-93 contract).
* Statement passes axe and Flesch-Kincaid grade ≤ 9 (`text-readability`); report carries `generatedAt`, version (PAP-52) and hash; "Next review by" 90 days.

*Round 4 amendment (2026-09-18):*

* Round 4: the statement links `/settings/accessibility` (PAP-647) as the mechanism for criteria 2.1.4 (character key shortcuts), 2.2.1 (timing adjustable) and 1.4.4 (resize text via `fontScale`); `criteria-map.json` gains `type: 'prefs'` sources pointing at that page's Playwright evidence and `type: 'reflow'` sources from PAP-670 for 1.4.4, 1.4.10 and 1.4.12.

**Interface contract**

Exposes: `report.json` `{ generatedAt, version, criteria: [{ id, level, status, sources[], issueUrl?, remarks }] }` consumed by PAP-89; `criteria-map.json` schema; MDX templates with frontmatter strings for i18n; routes `/accessibility` and `/accessibility/acr.pdf`; CLI `a11y:report [--from-cache]`. Consumes: `a11y-report.json` (PAP-73), `visual.json` axe section (PAP-82, PAP-239), `sr-results.json` (PAP-156), focus-order JSON (PAP-152), `vision.json` contrast findings (PAP-84), Linear read API (PAP-101), `publicSummary` field (PAP-93), app spec (PAP-117), `renderMdx` (PAP-128), `renderPdf` (PAP-235), release hooks (PAP-88, PAP-89), form view (PAP-169), webhook issue creation (PAP-97).

**Definition of done**

* `pnpm a11y:report` runs in CI on the template and commits `docs/a11y/*`; all 55 WCAG 2.2 A and AA criteria appear with status and source.
* `/accessibility` renders at 320, 768 and 1280; axe clean; readability passes; ACR PDF attached.
* One RC digest shows a conformance delta; feedback form creates a labelled issue (linked, then closed).
* `docs/platform/a11y/statement-and-acr.md`; changelog; Linear comment with the page link, routed to Needs Justin for wording approval only.

**Test plan**

* Vitest: status resolution matrix (all pass + manual → Supports, one fail → Partially, all fail → Does Not, none → Not Evaluated), missing issue link fails the run, `Not Applicable` requires a justification, cache fallback when Linear is unreachable produces a warning banner, readability check on the template text.
* Integration: generator over fixture result files for all sources writes `report.json` matching a snapshot; per-theme contrast takes the worst status.
* Playwright: `/accessibility` at 320, 768 and 1280 as anonymous in the portal and as staff in the console; ACR table scrolls horizontally at 320; feedback form submits and the mocked webhook receives an `a11y`-labelled issue.
* Visual: Gate 3 captures of statement and ACR at the three widths, both themes.

**Demo**

Run `pnpm a11y:report`, open `/accessibility`, scroll the ACR to 2.1.1 and follow its tracking issue link, download the PDF, submit the feedback form and open the created Linear issue. Under two minutes.

**Edge cases**

* Manual-only criterion without a record: Not Evaluated with owner.
* Hotfix release skips tests: reuse last full results, "based on version X".
* White-labelled tenant: tenant name and contact, worst-theme contrast.
* Over 20 limitations: grouped and collapsed.

**Dependencies**

PAP-156, PAP-117 (hard, encoded). Soft: PAP-73, PAP-82, PAP-84, PAP-152, PAP-128, PAP-235, PAP-88, PAP-89, PAP-101, PAP-93, PAP-52, PAP-169, PAP-97.

**Agent**

Builder: Quill (Changelog Scribe for templates, Page Spec Writer for the docs page) with Sentinel providing data sources. Reviewer: Sentinel (Visual Inspector) verifies the mapping; Justin approves wording.

**Size**

S: templates and a generator over existing data; the discipline is in the criteria map.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/design-system/reflow-zoom-text-spacing-audit` = PAP-670, `r4/input/accessibility-input-preferences` = PAP-647.
