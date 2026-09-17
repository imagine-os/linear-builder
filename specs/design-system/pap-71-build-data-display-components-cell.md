---
identifier: "PAP-71"
title: "Build data display components: cell renderers, Badge, AvatarStack, Timeline, EmptyState, Skeleton"
project: "design-system"
projectName: "Design System"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Tokens and primitives"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-67", "PAP-238", "PAP-302"]
blocks: ["PAP-164", "PAP-165", "PAP-234", "PAP-338", "PAP-341"]
key: "design-system/data-display"
url: "https://linear.app/paperos/issue/PAP-71/build-data-display-components-cell-renderers-badge-avatarstack"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:04:56.488Z"
---

# PAP-71: Build data display components: cell renderers, Badge, AvatarStack, Timeline, EmptyState, Skeleton

**Goal**

Provide the shared read-only visuals tables, dashboards, feeds and detail pages need: a registry of cell renderers for every field type plus Badge, Tag, AvatarStack, Timeline, EmptyState, Skeleton, Stat, KeyValue, RelativeTime, Money and Truncate, so numbers, dates, users and statuses look identical everywhere. Milestone moved to "Tokens and primitives" because PAP-165 needs it by 2026-09-23.

**Scope**

* In: `packages/ui/src/data/` components, cell renderer registry `data/cells/` for 20 types, `Intl` formatting utilities on `LocaleProvider`, `meta.ts` spec IDs, gallery story.
* Out: editable cells (PAP-165 editors), charts (PAP-170), tables, avatar upload, the other page states (PAP-234 builds ErrorState, DeniedState, OfflineBanner and friends; `EmptyState` stays here).

**Spec**

* Registry: `registerCell(type, renderer)`, `getCell(type)`; types `text, longText, number, currency, percent, date, dateTime, boolean, select, multiSelect, user, relation, url, email, phone, rating, attachment, progress, json, formula` aligned with PAP-164 names (agreed in that issue's thread).
* `Cell` signature `({ value, field, row, density: 'compact'|'default'|'comfortable' }) => ReactNode`; single line at `compact`; overflow via `Truncate` with tooltip; exports `{ Cell, align, defaultWidth }`.
* `Money` takes `{ amountMinor: bigint | number | string, currency }` (the canonical `Money` type lives in `packages/core`; minor units, never floats) with `currencyDisplay: 'narrowSymbol'`; `RelativeTime` on a shared 30 s ticker with absolute time in `title` and `<time dateTime>`.
* `AvatarStack` max 4 visible, `+N` overflow tooltip listing 20 then "and N more"; deterministic fallback colour from PAP-238 Avatar.
* `EmptyState` variants `empty | noResults | success` (illustrations from PAP-68); `error`, `offline`, `noPermission` variants delegate to PAP-234 components.
* `Skeleton` shapes text, avatar, block, table row; shimmer respects reduced motion; `aria-busy` on wrapper. `Timeline` groups `{ id, at, actor, icon?, title, body? }` by local day. `Stat` with label, value, delta and sparkline slot; `KeyValue` definition list with copy buttons.

**Interface contract**

* Provides: components with spec IDs `ui.badge`, `ui.tag`, `ui.avatarStack`, `ui.timeline`, `ui.emptyState`, `ui.skeleton`, `ui.stat`, `ui.keyValue`, `ui.relativeTime`, `ui.money`, `ui.truncate`; `registerCell`, `getCell`, `CellRenderer` type, `CellType` union; `formatMoney`, `formatDate`, `formatNumber` utilities.
* Requires: PAP-238 Avatar, PAP-237 Tooltip, PAP-236 Button; PAP-68 illustrations (soft); PAP-27 `LocaleProvider` (soft: fallback `en-US`); `Money` type from `packages/core` (agree with PAP-175: `amountMinor` bigint at runtime, string on the wire).
* Consumers: PAP-165 grid, PAP-164 field types, PAP-41 data dictionary, PAP-54 in-app git, PAP-62, PAP-183 reports, PAP-234, PAP-186 dashboard.
* Contract source: [Interface & Data Contracts](<https://linear.app/paperos/document/paperos-interface-and-data-contracts-d40e6a4d227c>) §1 (`Money = { amountMinor: bigint, currency }` at runtime and a decimal string such as `"1999"` on the wire; the earlier `number` form in this issue is superseded by PAP-175's shape); `formatMoney` and `ui.money` accept exactly that type, and `formatDate` takes the ISO-8601 UTC strings of §1; §6 row "Shared value types" (provider: pending contracts issue A `contracts/shared-value-types` in `@paperos/core/types`; until it exists import `Money` from PAP-175's `moneySchema`).

**Definition of done**

* All components and 20 cell renderers merged with stories at compact, default and comfortable densities.
* Vitest: formatting for en-US, en-GB, de-DE, ja-JP, ar-EG with negative, zero and huge values; registry behaviour.
* axe clean; `play` tests for Tag remove and AvatarStack overflow tooltip.
* "Data display gallery" screenshots at 375, 768, 1280 and 1920 light and dark.
* `docs/design/data-display.md` documents the renderer contract; changelog entry; Linear comment with Storybook link.

**Test plan**

* Unit: every formatter × five locales; bigint-as-string inputs; date-only fields do not shift across zones; null/undefined/empty render an em dash.
* Interaction: Tag remove, AvatarStack overflow tooltip lists 20 then "and N more".
* Visual: gallery at four widths × two themes; RTL (`ar-EG`) story for Money placement.
* Perf: 1 000 `RelativeTime` instances share one interval (single timer assertion).

**Demo**

Open Storybook "Data/Gallery", switch density to compact, then locale to `ar-EG` and watch numerals and currency placement change; hover a 6-person AvatarStack. Under one minute.

**Edge cases**

* Values beyond `MAX_SAFE_INTEGER` arrive as strings and format correctly.
* 500 avatars: slice first `max`, tooltip capped.
* Unbroken URLs wrap with `overflow-wrap: anywhere` inside `Truncate`.
* Unknown cell type: `text` renderer with a dev warning.

**Dependencies**

PAP-67 children (hard). Soft: PAP-68, PAP-27, PAP-175 (`Money` agreement).

**Agent**

Iris (Component Crafter) with Nova (Views Engineer) agreeing the renderer contract. Reviewed by Sentinel (Code Reviewer, Visual Inspector).

**Size**

M.
