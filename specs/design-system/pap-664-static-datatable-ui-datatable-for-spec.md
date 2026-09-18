---
identifier: "PAP-664"
title: "Static DataTable (ui.dataTable) for spec pages and settings lists: sortable columns, selection, sticky header, responsive card collapse, no compiler or virtualisation"
project: "design-system"
projectName: "Design System"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Component library covers app shell needs"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-238", "PAP-655"]
blocks: ["PAP-64", "PAP-120", "PAP-125"]
key: "r4/design-system/static-data-table"
url: "https://linear.app/paperos/issue/PAP-664/static-datatable-uidatatable-for-spec-pages-and-settings-lists"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:24.275Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-664: Static DataTable (ui.dataTable) for spec pages and settings lists: sortable columns, selection, sticky header, responsive card collapse, no compiler or virtualisation

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Codegen and the example specs (PAP-120, PAP-125) emit `ui.dataTable`, and the round-2 audit flagged that neither design-system nor tables owns it. The views grid (PAP-165) is the heavy, compiler-bound engine; settings lists, permission matrices, API key tables and small admin lists need a light static table over an in-memory array. Build it with an explicit boundary so nobody reaches for the wrong one.

**Scope**

In: `packages/ui/src/data/table/{DataTable,columns,useTableSort,useRowSelection,ResponsiveRows}.tsx`; `meta.ts` `ui.dataTable`; `@tanstack/react-table` 8.x core only (sorting, selection, column sizing), no virtualiser; stories and docs with the "when to use DataTable vs GridView" table.

Out: server pagination, filtering UI, grouping, inline editing, virtualisation (all PAP-165 and the views engine), CSV export (consumers call the export issue's writers).

**Spec**

* `DataTable<T> { columns: ColumnDef<T>[], rows: T[], getRowId, sort?, onSortChange?, selection?, onSelectionChange?, density, caption, emptyState?, maxRows = 500 }`; above `maxRows` it renders the first 500 with a banner pointing at `GridView` (dev warning); cells render via `getCell(type)` when a column declares `type`, else a custom `cell`.
* Semantics: `<table>` with `<caption>` (visually hidden allowed), `<th scope="col">` with `aria-sort`, sticky header inside a `ScrollArea`, row selection checkboxes with a header tri-state and `Shift+click` ranges, keyboard sort on `Enter|Space`, focusable rows when `onRowClick`.
* Responsive: below the `md` container width rows collapse into cards (`ResponsiveRows`) using the first column as the title and the rest as `KeyValue` pairs; `priority` on columns hides low-priority columns first before collapsing.
* Densities `compact|default|comfortable` share tokens with the grid (PAP-341) so mixed pages look consistent; zebra optional; column `align` and `width` (px or fr); `loading` renders `Skeleton` rows; empty renders `EmptyState`.
* Spec mapping: `meta.ts` props schema lets `page.spec.yaml` declare columns `{ key, label, type, sortable }` bound to a data section array (PAP-119); codegen emits `DataTable` for `list` layouts under 500 rows without a view spec and `GridView` otherwise, documented in PAP-120's template.

**Interface contract**

Provides: `DataTable`, `ColumnDef` helper `col()`, `useTableSort`, `useRowSelection`, spec id `ui.dataTable` with props schema, docs decision table. Consumes: cells and formatters (PAP-655), Checkbox, Menu (PAP-236, PAP-237), `ScrollArea`, `KeyValue`, `Skeleton`, `EmptyState` (surface and data-display issues, soft: plain fallbacks), tokens shared with the grid (PAP-341, agreement only). Consumed by PAP-120 codegen, PAP-125 examples, PAP-64 permission matrix pages, PAP-222 API keys page, PAP-63 admin lists.

**Definition of done**

* Component merged with stories (sortable, selectable, responsive collapse, loading, empty, 500-row cap banner); `play` tests for sort and selection; `vitest-axe` clean including `aria-sort` and header scope.
* Screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 light and dark; `docs/design/data-display.md` "DataTable vs GridView" table; changelog; Linear comment on PAP-120 and PAP-125.

**Test plan**

* Unit: sort comparators per cell type (numbers, dates, strings with locale collation, nulls last); selection reducer with shift ranges; priority-based column hiding; cap banner.
* Interaction: keyboard sort toggles `aria-sort`; header checkbox tri-state; cards mode at a narrow container.
* E2E: none (Storybook; consumers cover pages).

**Demo**

Reviewer opens Storybook `Data/DataTable`, sorts by amount, selects three rows with Shift, shrinks the container and watches rows become cards, then loads the 600-row story and reads the GridView banner. Under one minute.

**Edge cases**

* Column type `currency` with mixed currencies: sorted by minor amount within currency, then currency code.
* Rows change while selected: selection keyed by `getRowId`, orphans dropped.
* RTL: sticky header shadow and alignment flip.
* Print: cards mode disabled, full table with repeated header.

**Dependencies**

PAP-655 (hard), PAP-238 (hard). Soft: surface and data-display issues, PAP-341 (token agreement). Blocks PAP-120, PAP-125, PAP-64.

**Agent**

Builder: Iris (Component Crafter) with Nova agreeing the GridView boundary. Reviewer: Sentinel (Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/design-system/cell-renderer-registry-and-cells` = PAP-655.
