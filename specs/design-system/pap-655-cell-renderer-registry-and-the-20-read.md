---
identifier: "PAP-655"
title: "Cell renderer registry and the 20 read-only cells with Intl formatting utilities and density support"
project: "design-system"
projectName: "Design System"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Developer"]
milestone: "Tokens and primitives"
state: "Backlog"
parent: "PAP-71"
children: []
blockedBy: ["PAP-67", "PAP-238", "PAP-302"]
blocks: ["PAP-338", "PAP-341", "PAP-656", "PAP-664"]
key: "r4/design-system/cell-renderer-registry-and-cells"
url: "https://linear.app/paperos/issue/PAP-655/cell-renderer-registry-and-the-20-read-only-cells-with-intl-formatting"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:33.266Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-22"
cycle: null
---

# PAP-655: Cell renderer registry and the 20 read-only cells with Intl formatting utilities and density support

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

First half of PAP-71 and the part the grid critical path waits on (PAP-71 → PAP-338 → PAP-341): the `registerCell|getCell` registry, the twenty read-only cell renderers aligned with PAP-164's type names, and the `Intl` formatters they share, so field types and the grid can land without the rest of the data-display set.

**Scope**

In: `packages/ui/src/data/cells/{registry,types,*.tsx}`; `LocaleProvider` consumption; `formatMoney|formatDate|formatNumber|formatDuration`; `Truncate` (needed by cells); `meta.ts` for `ui.truncate`; gallery story `Data/Cells`.

Out: Badge, Tag, AvatarStack, Timeline, EmptyState, Skeleton, Stat, KeyValue, RelativeTime, Money component (sibling), editors (PAP-164), charts.

**Spec**

* Registry: `registerCell(type, renderer)`, `getCell(type)` falling back to `text` with one dev warning; types `text, longText, number, currency, percent, date, dateTime, boolean, select, multiSelect, user, relation, url, email, phone, rating, attachment, progress, json, formula`; the `CellType` union is exported and re-checked against PAP-164's `FieldType` in a contract test.
* `Cell` signature `({ value, field, row, density: 'compact'|'default'|'comfortable' }) => ReactNode` exporting `{ Cell, align, defaultWidth }`; compact renders a single line with `Truncate` and a tooltip; comfortable wraps up to three lines.
* `Money` cell and `formatMoney` accept `{ amountMinor: bigint | number | string, currency }` (PAP-302 shape, minor units, never floats) with `currencyDisplay: 'narrowSymbol'`; `formatDate` takes ISO-8601 UTC strings and date-only values without zone shift; numerals follow the locale (`ar-EG` Eastern Arabic digits).
* `select` and `multiSelect` cells render option chips with the token palette from PAP-339's option colours; `user` renders Avatar (PAP-238) plus name; `attachment` renders up to three thumbnails and `+n`; `formula` dispatches on the result type and renders `#ERROR` states; `json` pretty-prints one line with copy.
* Null, undefined and empty render an em dash; every cell sets `title` for truncated content and `data-cell-type`; RTL uses logical properties.
* Perf: rendering 1,000 cells of each type under 50 ms in a Vitest bench (no per-cell `Intl` construction; formatters cached per locale).

**Interface contract**

Provides: `registerCell`, `getCell`, `CellRenderer`, `CellType`, twenty cells, `formatMoney`, `formatDate`, `formatNumber`, `formatDuration`, `Truncate` (`ui.truncate`), `cellDensity` tokens. Consumes: Avatar and Tooltip (PAP-238, PAP-237), `Money` and ISO conventions (PAP-302; interim from PAP-175's `moneySchema`), `LocaleProvider` (PAP-27, soft: `en-US` fallback), option colours (PAP-339, soft: default palette). Consumed by PAP-338 to PAP-340, PAP-341, sibling components, PAP-183 reports.

**Definition of done**

* Twenty cells merged with stories at compact, default and comfortable; Vitest formatting for en-US, en-GB, de-DE, ja-JP, ar-EG with negative, zero and huge values; contract test against PAP-164's union.
* Gallery screenshots at 375, 768, 1280, 1920 light and dark plus RTL (`ar-EG`); axe clean; `docs/design/data-display.md` renderer contract section; changelog; Linear comment on PAP-338 and PAP-341.

**Test plan**

* Unit: every formatter × five locales; bigint-as-string inputs; date-only no zone shift; registry fallback warning once; density line clamps.
* Bench: 1,000 cells per type under 50 ms; formatter cache hit rate.
* E2E: none (Storybook interaction tests cover tooltips on truncation).

**Demo**

Reviewer opens Storybook `Data/Cells`, switches density to compact, then locale to `ar-EG` and watches numerals and currency placement change. Under one minute.

**Edge cases**

* Values beyond `MAX_SAFE_INTEGER` arrive as strings and format correctly.
* Unknown cell type: `text` renderer with a dev warning.
* Unbroken URLs wrap with `overflow-wrap: anywhere` inside `Truncate`.
* Attachment with a failed variant: broken-image placeholder, retry handled by PAP-339.

**Dependencies**

PAP-238 (hard, Avatar), PAP-302 (hard for `Money`; interim import allowed). Soft: PAP-27, PAP-339. Blocks PAP-338, PAP-341 and the sibling.

**Agent**

Builder: Iris (Component Crafter) with Nova agreeing the renderer contract. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.
