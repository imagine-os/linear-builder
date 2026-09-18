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
blockedBy: ["PAP-66", "PAP-212"]
blocks: ["PAP-69", "PAP-237", "PAP-238", "PAP-501", "PAP-538", "PAP-553", "PAP-659", "PAP-660", "PAP-666"]
key: "design-system/primitives/infra-form-controls"
url: "https://linear.app/paperos/issue/PAP-236/component-infrastructure-and-form-controls"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:56:18.517Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-22"
cycle: null
---

# PAP-236: Component infrastructure and form controls

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

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

*Round 4 amendment (2026-09-18):*

* Round 4: a component token layer `--pos-<component>-<prop>` (for example `--pos-button-radius`, `--pos-control-height-md`) defined in `packages/ui/tokens/components.tokens.json` with values aliased to core tokens, so tenants (PAP-75) and density modes can retune components without touching classes; components reference these instead of literal sizes. All user-visible strings inside components (Close, Clear, Loading, Show password) come from `useUiStrings()` with an `en` default so PAP-27 catalogs can override them. Inputs set `autocomplete`, `inputmode` and `enterkeyhint` from a `purpose` prop (`email`, `tel`, `otp`, `search`, `decimal`).

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
