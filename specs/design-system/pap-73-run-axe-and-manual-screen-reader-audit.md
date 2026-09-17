---
identifier: "PAP-73"
title: "Run axe and manual screen-reader audit on every component and fix to WCAG 2.2 AA"
project: "design-system"
projectName: "Design System"
phase: "P1"
type: "Review"
priority: 1
surfaces: ["Customer"]
milestone: "Component library covers app shell needs"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-67", "PAP-69", "PAP-238"]
blocks: ["PAP-156"]
key: "design-system/a11y-audit"
url: "https://linear.app/paperos/issue/PAP-73/run-axe-and-manual-screen-reader-audit-on-every-component-and-fix-to"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:41:11.168Z"
model: "claude-opus-5"
effort: "high"
---

# PAP-73: Run axe and manual screen-reader audit on every component and fix to WCAG 2.2 AA

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — Review

**Goal**

Audit every component in `packages/ui` against WCAG 2.2 AA with automated axe scans and ARIA snapshot checks across all seven widths and three themes, fix every finding, and leave behind a per-component accessibility record and a CI job so the library cannot regress below AA. Recast per the round-2 audit: manual NVDA, VoiceOver and TalkBack passes move to PAP-156, which owns the assistive-technology drivers and device runners; this issue is fully automatable on a Linux runner.

**Scope**

* In: `pnpm --filter ui a11y:scan` (Storybook static build, every story × 7 widths × 3 themes with `@axe-core/playwright`), `locator.ariaSnapshot()` per story committed as name/role regression baselines, contrast verification of every token pair components use (extends `tokens:check`), fix PRs grouped by severity, `meta.ts` `a11y` record, allowlist with expiry, Gate 1 job, checklist template, docs.
* Out: manual screen-reader passes (PAP-156), page-level audits of real apps (PAP-156), accessibility statement (PAP-160), AAA.

**Spec**

* Scan iterates `storybook-static/index.json` (PAP-69), opens each story at each width and theme, runs axe with tags `wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22aa, best-practice` scoped to `#storybook-root` plus the portal container, writes `packages/ui/a11y-report.json` and a Markdown summary grouped by rule and component.
* Severity mapping to PAP-79: axe `critical` and `serious` fail CI (S1); `moderate` creates a Linear issue via PAP-97; `minor` logged.
* ARIA snapshots: `__aria__/<storyId>.yml` committed; CI fails on a diff; updates through the same label flow as PAP-247.
* Checklist `docs/design/a11y-checklist.md` per component: name, role, value, keyboard operability, focus visible, announcements, target size (2.5.8), dragging alternatives (2.5.7), focus not obscured (2.4.11), consistent help (3.2.6), redundant entry (3.3.7), accessible authentication (3.3.8); the keyboard and focus rows are verified by `play` tests, the AT rows are marked "see PAP-156".
* `meta.a11y = { auditedAt, wcag: 'AA', notes, atVerified?: ['nvda' | 'voiceover' | 'talkback'] }`; `atVerified` filled by PAP-156.
* CI job `a11y` in Gate 1 on `packages/ui` changes, cached by story hash, under 4 minutes.

**Interface contract**

* Provides: `a11y-report.json` (contracts kind `a11y`: `{ violations: [{ ruleId, impact, storyId, width, theme, nodes }], summary }`), ARIA snapshot baselines, `a11y.allow.json` with expiry, `meta.a11y` shape, the checklist template PAP-156 completes.
* Requires: PAP-67 children and PAP-69 (hard), PAP-70, PAP-71 (audit whatever exists at start, re-run at end), PAP-79 severity names, PAP-78 job slot, PAP-239 artifact kind, PAP-97 (soft) for moderate issues.
* Consumers: PAP-156 (AT rows), PAP-160 (conformance report data), PAP-84 (a11y rubric items), PAP-76 (accessibility page).

**Definition of done**

* Scan reports zero `critical` or `serious` across all stories, widths and themes.
* Every exported component has `meta.a11y.auditedAt` set and a checklist entry with keyboard and focus rows verified by a `play` test.
* ARIA snapshots committed; CI fails on a seeded role change.
* Contrast check covers every token pair used by components in all themes.
* Focus-state screenshots at 375 and 1280 for Dialog, Menu, Select, Tabs, SplitPane; `docs/design/accessibility.md`; changelog entry; Linear comment with the report link and fix count.

**Test plan**

* Automated: the scan itself (21 combinations × all stories); ARIA snapshot diff; contrast assertions; allowlist expiry test.
* Interaction: keyboard operability `play` tests for every interactive component (tab, arrows, Escape, Enter/Space).
* Visual: focus-state screenshots.
* Seeded regressions: a removed `aria-label` and a 3:1 text pair each fail the job.

**Demo**

Run `pnpm --filter ui a11y:scan --story ui-select--default` and open the Markdown summary; then edit Select to drop its label, rerun and read the `serious` violation with the story id, width and theme. Under two minutes.

**Edge cases**

* Portal or hidden-story false positives: allowlist by rule and story id with justification and expiry.
* hc theme changes contrast math: scan runs per theme.
* 44 px targets at 320 px: 24 px minimum with spacing per the 2.5.8 exception, documented.
* Toast disappearing during announcement: `useToast` pauses while the live region is being read.
* Storybook chrome violations: scope excludes it.

**Dependencies**

PAP-67 children, PAP-69 (hard). Soft: PAP-70, PAP-71, PAP-79, PAP-78, PAP-239, PAP-97.

**Agent**

Sentinel (Visual Inspector and Edge Case Hunter) audits; Iris (Component Crafter) fixes. Reviewed by Iris for fixes and Atlas for sign-off.

**Size**

M.
