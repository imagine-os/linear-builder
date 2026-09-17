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
children: ["PAP-237", "PAP-236", "PAP-238"]
blockedBy: ["PAP-212", "PAP-66"]
blocks: ["PAP-151", "PAP-164", "PAP-233", "PAP-69", "PAP-70", "PAP-71", "PAP-73", "PAP-74"]
key: "design-system/primitives"
url: "https://linear.app/paperos/issue/PAP-67/adopt-base-uiradix-primitives-with-tailwind-v4-and-build-20-core"
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-67: Adopt Base UI/Radix primitives with Tailwind v4 and build 20 core components (Button, Input, Select, Dialog, Menu, Tabs, Toast, Tooltip, Popover...)

**Goal**

Ship the 20 core interactive components every PaperOS page is built from, on top of the headless primitive library chosen in `libraries/ui-landscape` (default: Base UI `@base-ui-components/react` 1.x, Radix as fallback), styled only with Tailwind v4 utilities bound to design tokens. Each component is accessible, themable, tested and documented with a story.

**Scope**

In:
- Components in `packages/ui/src/components/<name>/` : Button, IconButton, Input, Textarea, Select, Combobox, Checkbox, Radio, Switch, Slider, Dialog, AlertDialog, Popover, Tooltip, Menu (dropdown and context), Tabs, Toast, Field (label, description, error), Avatar, Separator.
- Variant API via `class-variance-authority` (`variant`, `size`, `tone`) with `data-*` state attributes exposed for styling.
- `cn()` helper (`clsx` + `tailwind-merge`), `Slot`/`render` prop pass-through for polymorphism.
- One `*.stories.tsx` and one `*.test.tsx` per component (Vitest + Testing Library + `vitest-axe`).
- `packages/ui/src/index.ts` barrel with tree-shakeable exports; `sideEffects: false`.

Out: layout frames (`design-system/layout-components`), data display (`design-system/data-display`), motion presets (`design-system/motion`), form state management, date pickers.

**Spec**

- Folder shape: `button.tsx`, `button.stories.tsx`, `button.test.tsx`, `meta.ts` (exports `specId: 'ui.button'`, Zod props schema placeholder consumed later by `design-system/component-spec-mapping`).
- Sizes `sm|md|lg` mapping to 32/40/48px hit targets; `md` default; touch targets never under 44px on coarse pointers via `@media (pointer: coarse)`.
- Every component accepts `className`, forwards refs, and exposes `data-state`, `data-disabled`, `data-invalid`.
- Focus ring: `outline: 2px solid var(--pos-color-focus)` with 2px offset, visible only on `:focus-visible`.
- Toast: `ToastProvider` with a queue (max 3 visible), `useToast().push({ title, tone, action })`, auto-dismiss 6s, pauses on hover and focus, `role="status"`.
- Dialog: focus trap, `Escape` closes unless `preventClose`, scroll lock, returns focus to trigger; full-screen sheet under `md`.
- Select and Combobox: typeahead, virtualised list over 200 items (`@tanstack/react-virtual`), async `loadOptions`.
- Menu: keyboard navigation, submenus, checkbox and radio items, `shortcut` display slot.
- Input states: default, hover, focus, invalid, disabled, read-only, loading (Button only).
- Bundle budget: importing Button alone under 6 KB gzipped, checked with `size-limit`.

**Definition of done**

- 20 components merged with stories covering every variant and state.
- Vitest passes; `vitest-axe` reports zero violations per component.
- Storybook interaction tests (`play` functions) for Dialog, Menu, Select, Combobox, Tabs, Toast.
- Screenshots of the "All components" story at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark via `quality/playwright-matrix` (or a local script until it exists).
- `size-limit` check in CI; `docs/design/components.md` lists each component and when to use it.
- CHANGELOG entry; Linear comment with Storybook or Pages preview link.

**Edge cases**

- Right-to-left layouts: use logical properties (`ps-`, `pe-`, `ms-`) so `dir="rtl"` works without extra CSS.
- Very long labels in Button and Tabs: truncate with `title` tooltip rather than wrap unless `wrap` prop set.
- Nested Dialog inside Popover inside Menu: stacking contexts and dismiss layers must not close parents.
- Portals inside Tauri multi-window: portal root resolves per document, not `document.body` of the opener.
- Reduced motion: no transitions beyond opacity when `prefers-reduced-motion: reduce`.
- Controlled and uncontrolled props both work; warn once in dev when switching.

**Dependencies**

`design-system/tokens` (hard), `libraries/ui-landscape` (hard, decides Base UI vs Radix; if not merged by 2026-09-19 proceed with Base UI and note in ADR). Unblocks `design-system/storybook`, `design-system/layout-components`, `design-system/data-display`, `input/command-registry`, `identity/better-auth` pages.

**Agent**

Built by Iris (Component Crafter sub-agent). Reviewed by Sentinel (Code Reviewer, Visual Inspector) with Scout confirming the primitive library decision.

**Size**

L: twenty components with stories, tests and states is the largest single chunk of UI work in P0.
