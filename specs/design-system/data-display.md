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
blockedBy: ["PAP-238", "PAP-67"]
blocks: ["PAP-164", "PAP-165", "PAP-234"]
key: "design-system/data-display"
url: "https://linear.app/paperos/issue/PAP-71/build-data-display-components-cell-renderers-badge-avatarstack"
source: "plan/specs/bucket-2.json (round-1 canonical spec JSON)"
---

# PAP-71: Build data display components: cell renderers, Badge, AvatarStack, Timeline, EmptyState, Skeleton

**Goal**

Provide the shared read-only visuals that tables, dashboards, feeds and detail pages need: a registry of cell renderers for every field type, plus Badge, Tag, AvatarStack, Timeline, EmptyState, Skeleton, Stat and KeyValue. The tables engine and dashboards render data through these so numbers, dates, users and statuses look identical everywhere.

**Scope**

In:
- `packages/ui/src/data/` components: `Badge` (tones, dot, count), `Tag` (removable), `AvatarStack` (overflow `+N`, tooltip listing), `Timeline` (events with actor, time, icon, grouped by day), `EmptyState` (illustration, title, body, primary and secondary actions), `Skeleton` (text, avatar, block, table row; shimmer respects reduced motion), `Stat` (label, value, delta, sparkline slot), `KeyValue` (definition list with copy buttons), `RelativeTime`, `Money`, `Truncate`.
- Cell renderer registry `packages/ui/src/data/cells/`: `text, longText, number, currency, percent, date, dateTime, boolean, select, multiSelect, user, relation, url, email, phone, rating, attachment, progress, json` each exporting `{ Cell, Editor?: undefined, align, defaultWidth }`. Editors come with `tables/grid-view`.
- Formatting utilities using `Intl` with locale and timezone from a `LocaleProvider`.

Out: editable cells, charts (`tables/map-chart-views`), tables themselves, avatar upload.

**Spec**

- Registry API: `registerCell(type, renderer)`, `getCell(type)`; types align with `tables/field-types` names (agree in that issue's comment thread; use the list above as the interim contract).
- `Cell` signature: `({ value, field, row, density: 'compact'|'default'|'comfortable' }) => ReactNode`; must render in a single line at `compact` and never exceed row height; overflow handled by `Truncate` with hover tooltip.
- `Money` uses `Intl.NumberFormat` with `currencyDisplay: 'narrowSymbol'`, minor units input (integers), never floats.
- `RelativeTime` updates on a shared 30s interval, absolute time in `title` and `<time dateTime>`.
- `AvatarStack` max 4 visible by default, sizes from primitives Avatar, deterministic fallback colour from user id hash using accent ramp.
- `EmptyState` variants `empty|error|offline|noPermission|noResults|success` mapping to illustrations from `design-system/icons-illustrations`.
- `Skeleton` accepts `lines` or explicit children shapes; `aria-busy` on the wrapper and `aria-hidden` on bones.
- `Timeline` accepts `items: {id, at, actor, icon?, title, body?}[]` and groups by local day headers.
- All components register `meta.ts` spec IDs (`ui.badge` ...) for `design-system/component-spec-mapping`.

**Definition of done**

- All components and 20 cell renderers merged with stories showing compact, default and comfortable densities.
- Vitest: formatting for 5 locales (en-US, en-GB, de-DE, ja-JP, ar-EG) and negative, zero, huge values; registry behaviour.
- axe clean; `play` tests for Tag remove and AvatarStack overflow tooltip.
- Screenshots of the "Data display gallery" story at 375, 768, 1280 and 1920 in light and dark.
- `docs/design/data-display.md` documents renderer contract; CHANGELOG entry.
- Linear comment with Storybook link.

**Edge cases**

- Null, undefined and empty string render a muted em dash, never `null` or `undefined` text.
- Numbers beyond `Number.MAX_SAFE_INTEGER` arrive as strings; formatters accept bigint-like strings.
- Dates without timezone (date-only fields) must not shift by a day across zones.
- 500 avatars in a stack: only slice the first `max`, tooltip lists 20 and "and N more".
- Right-to-left numerals and currency placement in `ar-EG`.
- Extremely long unbroken strings (URLs) break with `overflow-wrap: anywhere` inside `Truncate`.

**Dependencies**

`design-system/primitives` (Avatar, Tooltip, Button) hard; `design-system/icons-illustrations` (EmptyState art) soft. Consumed by `tables/grid-view`, `tables/field-types`, `data-layer/data-dictionary`, `forge/in-app-git`, `identity/customer-portal-shell`, `business-core/finance-reports`.

**Agent**

Built by Iris (Component Crafter) with Nova (Views Engineer) agreeing the renderer contract. Reviewed by Sentinel (Code Reviewer, Visual Inspector).

**Size**

M: many small components; formatting correctness across locales is the risk.
