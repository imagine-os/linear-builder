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
blockedBy: ["PAP-238", "PAP-67", "PAP-69"]
blocks: ["PAP-156"]
key: "design-system/a11y-audit"
url: "https://linear.app/paperos/issue/PAP-73/run-axe-and-manual-screen-reader-audit-on-every-component-and-fix-to"
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-73: Run axe and manual screen-reader audit on every component and fix to WCAG 2.2 AA

**Goal**

Audit every component in `packages/ui` against WCAG 2.2 AA with automated axe runs and manual screen-reader passes on NVDA, VoiceOver and TalkBack, fix every finding, and leave behind a per-component accessibility checklist and a CI check so the library can never regress below AA.

**Scope**

In:
- Automated pass: `storybook:test` axe results aggregated into `packages/ui/a11y-report.json`; Playwright `@axe-core/playwright` against the Storybook static build across all seven widths and three themes.
- Manual pass per component with NVDA + Firefox (Windows VM or a contractor-free recorded session by the agent using accessibility tree dumps as proxy where a real screen reader is unavailable), VoiceOver + Safari (macOS runner), TalkBack + Chrome (Android emulator via `app-shell/tauri-mobile` tooling if present).
- Checklist template `docs/design/a11y-checklist.md`: name, role, value, keyboard operability, focus visible, announcements, target size (2.5.8), dragging alternatives (2.5.7), focus not obscured (2.4.11), consistent help (3.2.6), redundant entry (3.3.7), accessible authentication (3.3.8).
- Fix PRs per component grouped by severity; component `meta.ts` gains `a11y: { auditedAt, wcag: 'AA', notes }`.
- Contrast verification of every token pair used by components in all themes (extends `tokens:check`).

Out: page-level audits of real apps (`input/screen-reader`), accessibility statement (`input/a11y-statement`), AAA targets.

**Spec**

- Script `pnpm --filter ui a11y:scan` builds Storybook, iterates `index.json`, opens each story at each width and theme with `@axe-core/playwright` 4.x, tags `wcag2a, wcag2aa, wcag21a, wcag21aa, wcag22aa, best-practice`, writes JSON and a Markdown summary grouped by rule and component.
- Manual findings recorded in `docs/design/a11y-audit-2026-09.md` as a table: component, assistive tech, issue, WCAG criterion, severity (from `quality/review-rubrics` taxonomy), fix PR.
- Severity gate: `critical` and `serious` fail CI; `moderate` creates a Linear issue automatically via the orchestrator webhook (`pm-linear/webhooks`); `minor` logged.
- CI job `a11y` added to Gate 1 running the scan on `packages/ui` changes only, cached by story hash to stay under 4 minutes.
- Accessibility tree snapshots (`page.accessibility.snapshot()` replacement: `locator.ariaSnapshot()` in Playwright 1.5x) stored per story to detect name/role regressions.

**Definition of done**

- Scan reports zero `critical` or `serious` across all stories, widths and themes.
- Manual audit doc covers all 20 primitives, 5 layout and all data-display components with at least VoiceOver and NVDA columns filled; TalkBack marked where tested.
- All fixes merged; each component `meta.a11y.auditedAt` set.
- ARIA snapshot files committed; CI fails on a seeded role change.
- Screenshots of focus states at 375 and 1280 for Dialog, Menu, Select, Tabs, SplitPane.
- `docs/design/accessibility.md` written; CHANGELOG entry; Linear comment with report link and count of fixes.

**Edge cases**

- axe false positives in portals or hidden stories: allowlist by rule and story id in `a11y.allow.json` with a justification and expiry date.
- Combobox announcements differ between NVDA and VoiceOver; document acceptable behaviours rather than forcing one.
- High-contrast theme changes contrast math; scan must run per theme, not once.
- Touch target rule at 320px width where 44px targets do not fit: allow 24px minimum with spacing per 2.5.8 exception, document.
- Toasts disappearing before screen reader finishes: extend timeout when `aria-live` region is being read (`useToast` pause on focus).
- Storybook chrome itself has violations: scope scans to `#storybook-root` and the portal container only.

**Dependencies**

`design-system/primitives`, `design-system/storybook` (hard). Soft: `design-system/layout-components`, `design-system/data-display` (audit whatever exists at start, re-run at end), `quality/review-rubrics` (severity names), `quality/ci-gate1` (job slot).

**Agent**

Built and audited by Sentinel (Visual Inspector plus Edge Case Hunter) with fixes implemented by Iris (Component Crafter). Reviewed by Iris for fixes and Atlas for sign-off.

**Size**

M: scanning is automated, but the manual passes and fix churn across 40 components take days.
