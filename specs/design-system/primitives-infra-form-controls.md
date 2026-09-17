---
identifier: "PAP-236"
title: "Component infrastructure and form controls"
project: "design-system"
projectName: "Design System"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Tokens and primitives"
state: "Backlog"
parent: "PAP-67"
children: []
blockedBy: ["PAP-212", "PAP-66"]
blocks: ["PAP-237", "PAP-238"]
key: "design-system/primitives/infra-form-controls"
url: "https://linear.app/paperos/issue/PAP-236/component-infrastructure-and-form-controls"
source: "Linear snapshot 2026-09-17T06:03Z (round-2 issue)"
---

# PAP-236: Component infrastructure and form controls

**Goal**

Lay down the conventions every component follows and ship the form controls: `cn()`, the variant API, the `meta.ts` convention, and Button, IconButton, Input, Textarea, Checkbox, Radio, Switch, Slider and Field on the chosen headless primitives with Tailwind v4 bound to tokens.

**Scope**

* In: `packages/ui` package setup (`sideEffects: false`, barrel, `size-limit`), `cn()` (`clsx` + `tailwind-merge`), `class-variance-authority` variants (`variant`, `size`, `tone`), `meta.ts` convention with `defineComponentMeta` placeholder, the nine form controls with stories and tests, focus-ring and touch-target rules, RTL logical properties.
* Out: overlays and selection components (siblings), date pickers, form state.

**Spec**

* Folder `packages/ui/src/components/<name>/{name.tsx, name.stories.tsx, name.test.tsx, meta.ts}`; every component forwards refs, accepts `className`, exposes `data-state`, `data-disabled`, `data-invalid`.
* Sizes `sm|md|lg` = 32/40/48 px; `@media (pointer: coarse)` enforces 44 px minimum hit area; focus ring `outline: 2px solid var(--pos-color-focus)` offset 2 px on `:focus-visible` only.
* `Field` wraps label, description, error with `aria-describedby` wiring; `Input` supports `startAdornment`, `endAdornment`, `loading` (Button only); `Slider` supports range and keyboard steps.
* Base UI `@base-ui-components/react` 1.x by default; if PAP-212 recommends Radix by 2026-09-19 switch imports (the API surface here is ours, not the library's).

**Interface contract**

* Provides: `cn`, `cva` presets, `defineComponentMeta`, components and their `meta.ts` with spec IDs `ui.button`, `ui.iconButton`, `ui.input`, `ui.textarea`, `ui.checkbox`, `ui.radio`, `ui.switch`, `ui.slider`, `ui.field`; `Size`, `Tone` types.
* Requires: PAP-66 tokens and `theme.css`; PAP-68 `Icon` for `IconButton` (soft, placeholder glyph until merged).

**Definition of done**

* Nine components merged with stories for every variant and state; `vitest-axe` zero violations each.
* `size-limit`: Button alone under 6 KB gzipped, checked in CI.
* Storybook "All form controls" story screenshotted at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark.
* `docs/design/components.md` started with conventions and the nine entries.

**Test plan**

* Unit: variant class output snapshots, controlled and uncontrolled behaviour, `Field` aria wiring.
* Interaction: keyboard toggles for Checkbox, Radio group arrows, Slider arrows and Home/End.
* Visual: seven widths; RTL story for Input adornments.

**Demo**

Open Storybook "Forms/All controls", tab through every control with the keyboard watching focus rings, switch to RTL and dark in the toolbar. Under one minute.

**Edge cases**

* Long Button labels: truncate with `title` unless `wrap`.
* `IconButton` without `label`: TypeScript error.
* Switching controlled to uncontrolled: one dev warning.

**Dependencies**

PAP-66 (hard). Blocks the two sibling children.

**Agent**

Built by Iris (Component Crafter). Reviewed by Sentinel (Code Reviewer).

**Size**

M.
