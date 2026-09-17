---
identifier: "PAP-67"
title: "Adopt Base UI/Radix primitives with Tailwind v4 and build 20 core components (Button, Input, Select, Dialog, Menu, Tabs, Toast, Tooltip, Popover...)"
project: "design-system"
projectName: "Design System"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Tokens and primitives"
state: "Backlog"
parent: null
children: ["PAP-236", "PAP-237", "PAP-238"]
blockedBy: ["PAP-66", "PAP-212"]
blocks: ["PAP-69", "PAP-70", "PAP-71", "PAP-73", "PAP-74", "PAP-151", "PAP-164", "PAP-233", "PAP-289", "PAP-338"]
key: "design-system/primitives"
url: "https://linear.app/paperos/issue/PAP-67/adopt-base-uiradix-primitives-with-tailwind-v4-and-build-20-core"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:54:17.190Z"
model: null
effort: null
---

# PAP-67: Adopt Base UI/Radix primitives with Tailwind v4 and build 20 core components (Button, Input, Select, Dialog, Menu, Tabs, Toast, Tooltip, Popover...)

**Model / Effort:** set on children (umbrella is never claimed)

**Goal**

Ship the twenty core interactive components every PaperOS page is built from, on the headless primitive library chosen by PAP-212 (default Base UI, Radix fallback), styled only with Tailwind v4 utilities bound to tokens, each accessible, themable, tested and documented with a story. This issue is the umbrella for three children.

**Children**

1. PAP-236 Component infrastructure and form controls (M): `cn()`, variants, `meta.ts`, Button, IconButton, Input, Textarea, Checkbox, Radio, Switch, Slider, Field - blocks the other two.
2. PAP-237 Overlay components (M): Dialog, AlertDialog, Popover, Tooltip, Menu, Toast.
3. PAP-238 Selection and navigation components (M): Select, Combobox, Tabs, Avatar, Separator, plus the barrel and package `size-limit`.

**Scope**

* In (across children): the twenty components with stories and tests, the `meta.ts` convention PAP-74 fills, portal root resolution for multi-window, focus-ring and touch-target rules, RTL logical properties, bundle budgets.
* Out: layout frames (PAP-70), data display (PAP-71), motion presets (PAP-72), state components (PAP-234), date pickers and form state (PAP-233).

**Spec**

Details live in the children. Cross-child rules:

* Folder shape `components/<name>/{name.tsx, name.stories.tsx, name.test.tsx, meta.ts}`; every component forwards refs, accepts `className`, exposes `data-state`, `data-disabled`, `data-invalid`.
* Sizes `sm|md|lg` = 32/40/48 px; 44 px minimum on coarse pointers; focus ring `2px solid var(--pos-color-focus)` on `:focus-visible` only.
* Library decision: proceed with Base UI if PAP-212 has not merged by 2026-09-19 and note it in the ADR; the public API is ours, so a swap touches imports only.
* Reduced motion: opacity only until PAP-72 presets exist.

**Interface contract**

* Provides (`@paperos/ui`): the twenty components, `cn`, `defineComponentMeta`, `getPortalRoot(doc)`, `ToastProvider` and `useToast`, types `Size`, `Tone`, `Option<T>`; spec IDs `ui.button`, `ui.iconButton`, `ui.input`, `ui.textarea`, `ui.checkbox`, `ui.radio`, `ui.switch`, `ui.slider`, `ui.field`, `ui.dialog`, `ui.alertDialog`, `ui.popover`, `ui.tooltip`, `ui.menu`, `ui.toast`, `ui.select`, `ui.combobox`, `ui.tabs`, `ui.avatar`, `ui.separator`; `can` prop hook point for PAP-229.
* Requires: PAP-66 tokens (hard), PAP-212 decision (soft), PAP-68 `Icon` (soft placeholder).
* Consumers: PAP-69 stories, PAP-70, PAP-71, PAP-74 registry, PAP-151 palette, PAP-224 auth pages, PAP-58 dialogs, PAP-233 pickers, everything else.

**Definition of done**

* All three children Done; twenty components exported from the barrel.
* Integration checks below green; `size-limit` in CI (Button under 6 KB gzipped, package budget documented).
* "All components" story screenshotted at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark via PAP-246 (or the local script).
* `docs/design/components.md` lists each component and when to use it; changelog entry; Linear comment with the Storybook link.

**Test plan**

Umbrella checks in `packages/ui/test/umbrella.test.ts` and Storybook:

* Every exported component has `meta.ts` with a valid spec ID and a story; `vitest-axe` zero violations across all stories in `storybook:test`.
* Nested Dialog inside Popover inside Menu dismisses innermost first (PAP-237) and portals resolve per document (PAP-238 Combobox inside a detached window fixture).
* Keyboard traversal story: tab order through one of each component with focus rings visible (video via PAP-83 once available).
* RTL story of the full set at 1280.

**Demo**

Open Storybook "All components", toggle theme and RTL in the toolbar, then tab through the page watching focus rings; open "Overlays/Nested" and press Escape three times. Under one minute.

**Edge cases**

Cross-child: portals inside Tauri multi-window resolve to the trigger's document; long labels truncate with `title`; controlled/uncontrolled switching warns once in dev; the twenty spec IDs are reserved even before PAP-74 fills the schemas.

**Dependencies**

PAP-66 (hard), PAP-212 (soft, dated fallback). Unblocks PAP-69, PAP-70, PAP-71, PAP-73, PAP-74, PAP-151, PAP-233.

**Agent**

Iris (Component Crafter) builds all children. Reviewed by Sentinel (Code Reviewer, Visual Inspector); Scout confirms the primitive library decision.

**Size**

L, split into 3 children (M, M, M).

**Module boundary**

This umbrella is the Design System half of the PaperOS Module System (`docs/module-system.md`). The `design-system` module implements `@paperos/contract-design-system` (component id registry with props schemas, DTCG token set, theme, icon and motion ports). Other modules reference components only by registered `ui.<name>` id through the contract and codegen; they never import `packages/ui` internals. The module imports `@paperos/core` and its own packages only. Its manifest declares `provides: [{ contract: '@paperos/contract-design-system', version: '0.1.0' }]`, `owner: { agent: 'Iris', project: 'design-system' }` and `swapRisk: 'high'`. The contract package is published by `PAP-459`, proven by `PAP-460` and bound into `@paperos/kernel` by `PAP-461`; children of this issue inherit this boundary and may not add a dependency the manifest does not declare (lint rules R7 to R11).
