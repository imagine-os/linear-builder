---
identifier: "PAP-72"
title: "Define the motion system (durations, easings, reduced-motion) and shared transition components"
project: "design-system"
projectName: "Design System"
phase: "P1"
type: "Build"
priority: 3
surfaces: ["Customer"]
milestone: "Component library covers app shell needs"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-66"]
blocks: []
key: "design-system/motion"
url: "https://linear.app/paperos/issue/PAP-72/define-the-motion-system-durations-easings-reduced-motion-and-shared"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T04:18:12.495Z"
model: "claude-sonnet-5"
effort: "medium"
---

# PAP-72: Define the motion system (durations, easings, reduced-motion) and shared transition components

**Goal**

Define how things move: a small vocabulary of durations and easings as tokens, rules for when motion is allowed, and shared transition components so agents never hand-write animations and every animation disappears cleanly under reduced motion.

**Scope**

* In: finalise motion tokens (PAP-66 defines `duration.*` and `ease.*`; this issue owns their values and presets), `packages/ui/src/motion/` with `Presence`, `Fade`, `SlideIn`, `Collapse`, `Stagger`, `useReducedMotion`, `useMotionSafe`, CSS utilities `animate-in`/`animate-out`, `startViewTransition` helper, a lint rule, motion guidelines page, retrofit of PAP-237 overlays to the presets.
* Out: canvas animations, chart transitions (PAP-170), skeleton shimmer (PAP-71), Lottie or video.

**Spec**

* Tokens: `duration.instant 0, fast 120ms, base 200ms, slow 320ms, deliberate 480ms`; `ease.standard, enter (decelerate), exit (accelerate), spring` as `cubic-bezier` plus a `linear()` spring approximation.
* Runtime: `motion@12` only, imported from `motion/react` and `motion/react-m`; `Presence` API `<Presence present={open} enter="fade-up" exit="fade-down" duration="base">` with presets in `presets.ts` mapped to token variables.
* `Collapse` measures with `ResizeObserver`, animates height and opacity, `overflow: hidden` only during animation, `inert` when collapsed; distance capped at 5 000 px with a fade for the rest.
* `useReducedMotion` combines `prefers-reduced-motion` with the user setting `pos.settings.motion` (`system | always | never`), exposed as a `SettingRow` for PAP-62; under reduced motion durations become `instant`, transforms are removed, 80 ms opacity fades remain.
* Route transitions: `startViewTransition` on TanStack Router `onBeforeNavigate` with `view-transition-name` on `main`; disabled on WebKitGTK until verified.
* Performance rule: animate only `transform` and `opacity`; a Stylelint (or Biome custom) rule fails `transition: all` and animating `width|height|top|left` outside `Collapse`.

**Interface contract**

* Provides: components with spec IDs `ui.presence`, `ui.collapse`, `ui.stagger`; `useReducedMotion()`, `useMotionSafe(value, fallback)`, `startViewTransition(cb)`; preset names `fade`, `fade-up`, `fade-down`, `slide-start`, `slide-end`, `scale`; the lint rule package `ops/lint/motion`; token values consumed by PAP-66's `tokens.css`.
* Requires: PAP-66 tokens (hard). Soft: PAP-237 overlays (retrofit targets), PAP-16 router hook, PAP-75 (themes may override durations).
* Consumers: PAP-154 gestures, PAP-144 conflict banners, PAP-136 toasts and inbox, PAP-70 drawers, PAP-83 (motion evidence videos).

**Definition of done**

* Tokens merged; presets and five components with stories showing each preset and the reduced-motion toggle.
* Vitest: `useReducedMotion` matrix (media × setting); `Collapse` height math with a mocked observer; preset-to-token mapping.
* Playwright videos of Dialog open/close and Drawer slide at 375 and 1280, and the same with `reducedMotion: 'reduce'` proving no transforms (PAP-83 format once available).
* Lint rule fails a seeded `transition: all` commit.
* `docs/design/motion.md` with the duration and distance table; changelog entry; Linear comment with Storybook link.

**Test plan**

* Unit: hook matrix, interrupted exit reverses without flash (fake timers), nested `Presence` waits for children unless `immediate`, low-end device downgrade (`hardwareConcurrency <= 4`).
* Interaction: open/close a preset story ten times without leaked nodes.
* Visual and video: Dialog and Drawer at two widths, normal and reduced.
* Lint: rule fixture with passing and failing CSS.

**Demo**

Open Storybook "Motion/Presets", cycle the preset control, flip the reduced-motion toolbar toggle and watch transforms vanish while fades stay; open a Dialog story to see the retrofit. Under one minute.

**Edge cases**

* Exit interrupted by re-open: cancel and reverse.
* Tab hidden: pause non-essential animations.
* Forced colours: focus rings stay visible mid-animation.
* Very tall `Collapse`: capped distance.

**Dependencies**

PAP-66 (hard). Soft: PAP-237, PAP-16, PAP-75.

**Agent**

Iris (Motion and Input Stylist). Reviewed by Sentinel (Visual Inspector via videos, Edge Case Hunter on reduced-motion paths).

**Size**

S.
