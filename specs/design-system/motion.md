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
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-72: Define the motion system (durations, easings, reduced-motion) and shared transition components

**Goal**

Define how things move in PaperOS: a small vocabulary of durations and easings as tokens, rules for when motion is allowed, and shared transition components so agents never hand-write animations and every animation disappears cleanly under reduced motion.

**Scope**

In:
- Motion tokens in `design-system/tokens` finalised: `duration.instant 0, fast 120ms, base 200ms, slow 320ms, deliberate 480ms`; `ease.standard, enter (decelerate), exit (accelerate), spring` as `cubic-bezier` plus `linear()` spring approximation.
- `packages/ui/src/motion/`: `Presence` (mount/unmount with enter/exit classes, built on `motion/react` 12.x `AnimatePresence`), `Fade`, `SlideIn` (direction), `Collapse` (height auto), `Stagger` (children delay), `useReducedMotion()`, `useMotionSafe(value, fallback)`.
- CSS utilities `animate-in`, `animate-out` and view transitions helper `startViewTransition(cb)` guarded by feature detection for route changes.
- Motion guidelines page: purpose (orientation, feedback, continuity), forbidden motion (looping decorative, parallax), max concurrent animations, distance-to-duration table.
- Retrofit primitives (Dialog, Popover, Toast, Menu, Drawer) to use these presets.

Out: canvas animations, chart transitions (`tables/map-chart-views`), skeleton shimmer (already in data-display), Lottie or video.

**Spec**

- Install `motion@12` as the only animation runtime; tree-shake by importing from `motion/react` and `motion/react-m` for the lightweight `m` components.
- `Presence` API: `<Presence present={open} enter="fade-up" exit="fade-down" duration="base">`; presets are named objects in `presets.ts` mapping to token variables so themes can override durations.
- `Collapse` measures with `ResizeObserver`, animates `height` and `opacity`, sets `overflow: hidden` only during animation, `inert` when collapsed.
- `useReducedMotion` combines `prefers-reduced-motion` with a user setting stored under `pos.settings.motion` (`system|always|never`), exposed in a settings row spec for the portal.
- Under reduced motion: durations become `instant`, transforms removed, opacity fades of 80ms kept for orientation.
- Route transitions: `startViewTransition` on TanStack Router `onBeforeNavigate` with `view-transition-name` on `main`; disabled on Tauri WebKitGTK until support verified.
- Performance rule: animate only `transform` and `opacity`; a Biome custom lint (or Stylelint rule in CI) flags `transition: all` and animating `width|height|top|left` outside `Collapse`.

**Definition of done**

- Tokens merged, presets and five components with stories showing each preset and reduced-motion toggle.
- Vitest: `useReducedMotion` matrix (media true/false x setting), `Collapse` height math with mocked observer.
- Playwright: video of Dialog open/close and Drawer slide at 375 and 1280, plus the same with `reducedMotion: 'reduce'` proving no transforms (`quality/video-replays` format once available).
- Lint rule fails on a seeded `transition: all` commit.
- `docs/design/motion.md` with the duration table; CHANGELOG entry; Linear comment with Storybook link.

**Edge cases**

- Exit animation interrupted by re-open: `Presence` must cancel and reverse without a flash.
- Tab hidden (`visibilitychange`): pause non-essential animations to save battery on mobile.
- Low-end devices (`navigator.hardwareConcurrency <= 4` or `deviceMemory <= 4`): downgrade `spring` to `standard`.
- Nested `Presence` unmounting parent before child exit: parent waits for children unless `immediate`.
- Very tall `Collapse` (5000px): cap animated distance, fade the remainder.
- Forced colours or Windows high contrast: keep motion but ensure focus rings remain visible mid-animation.

**Dependencies**

`design-system/tokens` (hard). Soft: `design-system/primitives` (retrofit targets), `app-shell/router-layouts` (view transitions). Consumed by `input/touch-gestures`, `realtime/conflict-ux`, `collab/notifications`.

**Agent**

Built by Iris (Motion and Input Stylist sub-agent). Reviewed by Sentinel (Visual Inspector via video replays, Edge Case Hunter for reduced-motion paths).

**Size**

S: a handful of wrappers around one library; the value is in the rules and the lint.
