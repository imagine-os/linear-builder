---
identifier: "PAP-656"
title: "Data display components: Badge, Tag, AvatarStack, Timeline, EmptyState, Skeleton, Stat, KeyValue, RelativeTime and Money"
project: "design-system"
projectName: "Design System"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Tokens and primitives"
state: "Backlog"
parent: "PAP-71"
children: []
blockedBy: ["PAP-68", "PAP-655"]
blocks: ["PAP-164", "PAP-165", "PAP-234", "PAP-333", "PAP-338", "PAP-341", "PAP-386", "PAP-627", "PAP-629"]
key: "r4/design-system/data-display-components"
url: "https://linear.app/paperos/issue/PAP-656/data-display-components-badge-tag-avatarstack-timeline-emptystate"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:23.584Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-22"
cycle: null
---

# PAP-656: Data display components: Badge, Tag, AvatarStack, Timeline, EmptyState, Skeleton, Stat, KeyValue, RelativeTime and Money

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Second half of PAP-71: the ten shared read-only components dashboards, feeds and detail pages compose, built on the formatters and cells from the sibling so numbers, dates, users and statuses look identical everywhere.

**Scope**

In: `packages/ui/src/data/{Badge,Tag,AvatarStack,Timeline,EmptyState,Skeleton,Stat,KeyValue,RelativeTime,Money}.tsx` with `meta.ts` spec ids and stories; shared 30 s ticker for `RelativeTime`; `Data/Gallery` story.

Out: cells and formatters (sibling), the other page states (PAP-234), charts and sparklines (PAP-665 provides `Sparkline` for `Stat`'s slot).

**Spec**

* `Badge` tones `neutral|accent|success|warning|danger|info`, sizes `sm|md`, optional dot and count; `Tag` removable with keyboard (`Backspace` and a button), colour from the option palette, `maxWidth` truncation.
* `AvatarStack` max 4 visible, `+N` overflow with a Tooltip listing 20 then "and N more"; deterministic fallback colour from PAP-238 Avatar; `size` inherits.
* `Timeline` groups `{ id, at, actor, icon?, title, body?, href? }` by local day with sticky day headers, `RelativeTime` per item, virtualised beyond 200 items; `EmptyState` variants `empty|noResults|success` with illustrations (PAP-68) and primary and secondary actions; `error|offline|noPermission` delegate to PAP-234.
* `Skeleton` shapes `text|avatar|block|tableRow|card`, shimmer respects reduced motion (PAP-72 `useReducedMotion`), wrapper `aria-busy`; `Stat` label, value, delta with direction and tone, `sparkline` slot, `size`; `KeyValue` definition list with copy buttons and `columns` 1 or 2; `RelativeTime` on one shared interval with absolute time in `title` and `<time dateTime>`; `Money` component wraps `formatMoney` with tabular numerals and negative styling.
* All components forward refs, accept `className`, expose `data-tone`, use logical properties for RTL.

**Interface contract**

Provides: components with spec ids `ui.badge`, `ui.tag`, `ui.avatarStack`, `ui.timeline`, `ui.emptyState`, `ui.skeleton`, `ui.stat`, `ui.keyValue`, `ui.relativeTime`, `ui.money`; `useTicker(30_000)` shared hook. Consumes: formatters and `Truncate` (sibling), Avatar, Tooltip, Button (PAP-238, PAP-237, PAP-236), illustrations (PAP-68), reduced motion (PAP-72, soft), `Sparkline` (PAP-665, soft slot). Consumed by PAP-234 states, PAP-333 activity timeline, PAP-386 `NumberBlock`, PAP-62 portal, PAP-41 data dictionary, PAP-186.

**Definition of done**

* Ten components merged with stories for every variant; `play` tests for Tag remove and AvatarStack overflow tooltip; `vitest-axe` clean.
* Gallery screenshots at 375, 768, 1280, 1920 light and dark; RTL story; perf assertion that 1,000 `RelativeTime` share one interval; `docs/design/data-display.md`; changelog; Linear comment.

**Test plan**

* Unit: Badge and Tag variants snapshot; AvatarStack slicing and tooltip list; Timeline day grouping across DST; Stat delta sign and tone; KeyValue copy.
* Interaction: Tag remove by keyboard; AvatarStack overflow tooltip lists 20 then "and N more"; Timeline virtualisation keeps under 60 DOM items.
* E2E: none (Storybook).

**Demo**

Reviewer opens Storybook `Data/Gallery`, switches to compact density and dark, hovers a 6-person AvatarStack, removes a Tag by keyboard and watches RelativeTime tick. Under one minute.

**Edge cases**

* 500 avatars: slice first `max`, tooltip capped.
* Timeline item without actor: icon only, no empty avatar.
* Stat with a null delta: no arrow, muted placeholder.
* Skeleton inside a live region: `aria-busy` prevents announcement floods.

**Dependencies**

Sibling cells (hard), PAP-68 (hard, illustrations). Soft: PAP-72, dataviz issue. Blocks PAP-234, PAP-333, PAP-386.

**Agent**

Builder: Iris (Component Crafter). Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/design-system/dataviz-tokens-and-microcharts` = PAP-665.
