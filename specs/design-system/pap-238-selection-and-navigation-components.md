---
identifier: "PAP-238"
title: "Selection and navigation components: Select, Combobox, Tabs, Avatar, Separator"
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
blockedBy: ["PAP-236", "PAP-237"]
blocks: ["PAP-69", "PAP-70", "PAP-71", "PAP-73", "PAP-74", "PAP-151", "PAP-164", "PAP-233", "PAP-289", "PAP-290", "PAP-338", "PAP-339", "PAP-461", "PAP-616", "PAP-655", "PAP-659", "PAP-661", "PAP-662", "PAP-663", "PAP-664", "PAP-669"]
key: "design-system/primitives/selection-navigation"
url: "https://linear.app/paperos/issue/PAP-238/selection-and-navigation-components-select-combobox-tabs-avatar"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:56:19.558Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-22"
cycle: null
---

# PAP-238: Selection and navigation components: Select, Combobox, Tabs, Avatar, Separator

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Complete the twenty-component set with Select, Combobox (virtualised, async), Tabs, Avatar and Separator, and close PAP-67 with the bundle check, the barrel and the "All components" screenshot story.

**Scope**

* In: five components, `@tanstack/react-virtual` list over 200 items, async `loadOptions` with loading and empty states, Tabs with automatic and manual activation, Avatar with fallback initials and deterministic colour, final `index.ts` barrel, `size-limit` config for the whole package, "All components" story.
* Out: Combobox multi-select chips (PAP-164 `multiSelect` editor), data cells (PAP-71).

**Spec**

* Select: native-like keyboard model, typeahead, groups, `placeholder`, `invalid`; renders in a Popover; mobile uses a sheet under 768 px.
* Combobox: `options | loadOptions(query)`, debounce 250 ms, virtualised beyond 200 items, `allowCustomValue`, `aria-activedescendant` managed, `role="combobox"`.
* Tabs: `orientation`, `activation: 'automatic' | 'manual'`, overflow scroll with fade, `value` controlled or not, `lazy` panels.
* Avatar: `src`, `name`, `size`, deterministic fallback colour from a name hash over the accent ramp; `AvatarStack` lives in PAP-71.
* Separator: horizontal and vertical, `decorative` default.

**Interface contract**

* Provides: spec IDs `ui.select`, `ui.combobox`, `ui.tabs`, `ui.avatar`, `ui.separator`; `Option<T>` type shared with PAP-164 select fields and PAP-166 filter values; complete `@paperos/ui` barrel.
* Requires: sibling children (Popover, Field, `cn`); PAP-66 tokens.

**Definition of done**

* Five components merged; `play` tests for Select, Combobox and Tabs.
* Combobox with 10 000 options scrolls at 60 fps (Playwright trace) and reports under 40 DOM rows.
* "All components" story screenshotted at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark.
* `size-limit` passes for the package; `docs/design/components.md` completed for all twenty.

**Test plan**

* Interaction: typeahead, async load with loading state, Tabs arrow keys and Home/End, manual activation with Enter.
* Unit: option filtering, custom value, avatar colour determinism.
* Visual: seven widths; Select sheet mode at 375.

**Demo**

Open Storybook "Selection/Combobox async": type "inv", watch loading then results, arrow down and Enter; then open "All components" and flip themes. Under one minute.

**Edge cases**

* Options with duplicate labels: keys by value, labels disambiguated by `description`.
* Tabs with 30 items at 320 px: horizontal scroll with visible affordance.
* Avatar image fails to load: initials fallback without layout shift.

**Dependencies**

Both sibling children (hard).

**Agent**

Built by Iris (Component Crafter). Reviewed by Sentinel (Code Reviewer) and Nova (Option contract).

**Size**

M.
