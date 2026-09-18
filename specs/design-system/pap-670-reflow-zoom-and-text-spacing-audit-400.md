---
identifier: "PAP-670"
title: "Reflow, zoom and text-spacing audit: 400 percent zoom at 320 CSS px, 200 percent text-only zoom, WCAG 1.4.12 text-spacing injection and 1.4.10 reflow over every story and template page"
project: "design-system"
projectName: "Design System"
phase: "P2"
type: "Review"
priority: 2
surfaces: ["Customer"]
milestone: "Themable per tenant with docs"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-69", "PAP-70", "PAP-73"]
blocks: ["PAP-160"]
key: "r4/design-system/reflow-zoom-text-spacing-audit"
url: "https://linear.app/paperos/issue/PAP-670/reflow-zoom-and-text-spacing-audit-400-percent-zoom-at-320-css-px-200"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:27.939Z"
model: "claude-opus-5"
effort: "high"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-670: Reflow, zoom and text-spacing audit: 400 percent zoom at 320 CSS px, 200 percent text-only zoom, WCAG 1.4.12 text-spacing injection and 1.4.10 reflow over every story and template page

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Review S

**Goal**

PAP-73's axe scan cannot see reflow and text-spacing failures: content clipped at 320 CSS px (WCAG 1.4.10), layouts that break at 200 percent text zoom (1.4.4) and components that truncate when line height and letter spacing grow (1.4.12). Run those checks over every story and template page, fix the findings and leave a CI job so they never return. PAP-160's conformance report needs these three criteria evaluated.

**Scope**

In: `pnpm --filter ui a11y:reflow` Playwright script: viewport 320 × 256 (400 percent zoom equivalent) and 1280 with `deviceScaleFactor`, text-only zoom emulation via root `font-size: 200%`, and the 1.4.12 CSS injection (`line-height: 1.5; letter-spacing: 0.12em; word-spacing: 0.16em; p { margin-bottom: 2em }`); detectors for horizontal overflow (`scrollWidth > clientWidth` on `html` and named containers), clipped text (`scrollHeight > clientHeight` with `overflow: hidden` and no truncation intent flag), overlapping boxes; fix PRs; `meta.a11y.reflowAuditedAt`; Gate 1 job on `packages/ui` changes.

Out: axe rules (PAP-73), manual AT (PAP-156), page-level app audits beyond the template's example routes.

**Spec**

* Detectors run per story from `storybook-static/index.json` (PAP-69) and per template route (PAP-86 flow list) in both themes; intentional truncation is declared with `data-truncate-intent` (set by `Truncate` and `lineClamp`) and excluded; horizontal scroll inside `data-scroll-x` containers (tables, toolbars) is allowed only when the container has a visible affordance.
* Findings map to PAP-79 severities: content unreachable or clipped is S1, overlap S2, minor spacing S3; each finding carries story id, width, theme, mode (`reflow|zoom|spacing`), selector and a screenshot crop into `reflow-report.json` (PAP-239 artefact kind `a11y`).
* Fixes land in the owning components (PAP-70 frames, PAP-238 Tabs overflow, data display, surfaces, pickers) with `min-width: 0` and `overflow-wrap` corrections, container-query breakpoints and `clamp()` typography; guidelines rule `DS-RESP-*` added to PAP-76's `rules.json`.
* Results feed PAP-160's `criteria-map.json` sources for 1.4.4, 1.4.10 and 1.4.12 as `type: reflow`; the job runs on `packages/ui` PRs under 3 minutes with story-hash caching and nightly on the template.

**Interface contract**

Provides: `a11y:reflow` script, `reflow-report.json`, `data-truncate-intent` and `data-scroll-x` DOM contracts, `meta.a11y.reflowAuditedAt`, Gate 1 job `a11y-reflow`. Consumes: Storybook index (PAP-69), frames and containers (PAP-70), severity taxonomy (PAP-79), artefact schema (PAP-239), flow routes (PAP-86), `Truncate` (cells issue). Consumed by PAP-160 (criteria 1.4.4, 1.4.10, 1.4.12), PAP-84 vision rubric, PAP-76 rules.

**Definition of done**

* Zero S1 and S2 findings across all stories and the template's example routes in both themes; fix PRs merged or linked; job green and failing on a seeded fixed-width component.
* Screenshots of five representative stories at 320 × 256 and with text-spacing injected; `docs/design/accessibility.md` reflow section; changelog; Linear comment on PAP-160 with the criteria mapping.

**Test plan**

* Unit: detector logic on fixture DOMs (overflow, clipped, overlap, intent flags); severity mapping; report schema validity.
* Seeded regressions: a `width: 600px` card and a `white-space: nowrap` label each produce the expected S1.
* E2E: the script itself over the story index and the template routes (Chromium).

**Demo**

Reviewer runs `pnpm --filter ui a11y:reflow --story ui-appframe--playground` and opens the report showing zero findings, then adds `white-space: nowrap` to a nav label, reruns and reads the S1 with a crop. Under two minutes.

**Edge cases**

* Virtualised lists report `scrollHeight` beyond viewport by design: `data-scroll-y` intent excludes them.
* Storybook decorators at 320 px: container-width decorator forced to 100 percent.
* Fonts not loaded in CI: `document.fonts.ready` awaited before measuring.
* RTL: overflow detection uses `scrollLeft` normalised.

**Dependencies**

PAP-73 (hard, shares the scan harness), PAP-70 (hard), PAP-69 (hard). Soft: PAP-79, PAP-239, PAP-86. Blocks PAP-160's evaluation of three criteria.

**Agent**

Builder: Sentinel (Visual Inspector) audits; Iris (Component Crafter) fixes. Reviewer: Sentinel (Edge Case Hunter).

**Size**

S: half a session.
