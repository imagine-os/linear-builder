---
identifier: "PAP-662"
title: "Surface and feedback components: Card, Accordion, InlineAlert, Callout, Progress, Spinner, ScrollArea, Toolbar, SegmentedControl and HoverCard"
project: "design-system"
projectName: "Design System"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Component library covers app shell needs"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-72", "PAP-238"]
blocks: ["PAP-234", "PAP-386", "PAP-618"]
key: "r4/design-system/surface-and-feedback-components"
url: "https://linear.app/paperos/issue/PAP-662/surface-and-feedback-components-card-accordion-inlinealert-callout"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:30.349Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-662: Surface and feedback components: Card, Accordion, InlineAlert, Callout, Progress, Spinner, ScrollArea, Toolbar, SegmentedControl and HoverCard

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Every design system in the benchmark set (shadcn, Radix Themes, Material 3, Polaris, Carbon) ships these ten; PaperOS pages would otherwise compose them from divs. They are what dashboards, settings pages, record panels and the view toolbar are built from.

**Scope**

In: `packages/ui/src/surfaces/{Card,Accordion,InlineAlert,Callout,Progress,Spinner,ScrollArea,Toolbar,SegmentedControl,HoverCard}.tsx` with `meta.ts` spec ids and stories.

Out: Toast (PAP-237), banners tied to page states (PAP-234 `OfflineBanner`), Tabs (PAP-238), data display (PAP-71 children).

**Spec**

* `Card` with `header`, `media`, `footer` slots, `interactive` variant (whole card focusable with one action), `tone`, elevation from PAP-66 shadows; `Accordion` single or multiple, `Collapse` animation from PAP-72, `Home/End` and arrows per APG, `lazy` panels.
* `InlineAlert` tones `info|success|warning|danger` with icon, title, body, actions and optional dismiss (`role="alert"` only for danger, `role="status"` otherwise, never auto-dismissed); `Callout` is the muted documentation variant with an accent bar.
* `Progress` linear and circular, determinate (`value`, `max`, `aria-valuenow`) and indeterminate, `size`, `tone`, label slot; `Spinner` sizes `xs..lg` with `aria-label`, hidden under 300 ms delay to avoid flashes (`delayMs`).
* `ScrollArea` custom scrollbars on the primitive library's `ScrollArea` with `type: 'auto'|'always'|'scroll'`, RTL and touch native fallback, shadow hints at edges; `Toolbar` `role="toolbar"` with roving tabindex, `orientation`, overflow into a Menu when children exceed the width (`ResizeObserver`), `ToolbarSeparator`.
* `SegmentedControl` (toggle group) single or multiple selection, icon-only mode with tooltips, keyboard per radio group semantics; `HoverCard` for previews (record, user) with 300 ms delay, focusable trigger fallback (`Enter` opens), never for essential content.

**Interface contract**

Provides: components with spec ids `ui.card`, `ui.accordion`, `ui.inlineAlert`, `ui.callout`, `ui.progress`, `ui.spinner`, `ui.scrollArea`, `ui.toolbar`, `ui.segmentedControl`, `ui.hoverCard`. Consumes: Menu, Tooltip, Popover (PAP-237), Button (PAP-236), `Collapse` and `useReducedMotion` (PAP-72), tokens (PAP-66), roving tabindex (PAP-152, soft). Consumed by PAP-234 states, PAP-386 block chrome, the view toolbar issue, PAP-333 record panel, PAP-62 and PAP-63 shells, PAP-76 guideline embeds.

**Definition of done**

* Ten components merged with stories for every variant; `play` tests for Accordion keyboard, Toolbar overflow and SegmentedControl; `vitest-axe` clean.
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark; RTL story; `docs/design/components.md` entries with when-to-use lines; changelog.

**Test plan**

* Unit: Accordion state modes; Toolbar overflow computation; Progress clamp and aria values; Spinner delay with fake timers; SegmentedControl selection modes.
* Interaction: Accordion arrows and Home/End; Toolbar roving and overflow menu; HoverCard opens on focus and closes on Escape.
* E2E: none (Storybook).

**Demo**

Reviewer opens Storybook `Surfaces/Gallery`, shrinks the Toolbar story until items overflow into the menu, tabs through an Accordion, and hovers a HoverCard by keyboard. Under one minute.

**Edge cases**

* Card with an interactive variant containing buttons: nested interactive content warned in dev, inner buttons stop propagation.
* InlineAlert inside a live region: `role="status"` avoids double announcement.
* ScrollArea on touch: native scrolling, custom bars hidden.
* Toolbar in RTL: overflow menu anchors to the start edge.

**Dependencies**

PAP-238 (hard, primitives complete), PAP-72 (hard, `Collapse`). Soft: PAP-152. Blocks PAP-234, PAP-386 and the view toolbar issue.

**Agent**

Builder: Iris (Component Crafter). Reviewer: Sentinel (Visual Inspector, Code Reviewer).

**Size**

M: one session.
