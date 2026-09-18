---
identifier: "PAP-666"
title: "Typography components: Text, Heading with decoupled level and size, Prose for MDX and rich text, Code and inline Kbd styling on the type tokens"
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
blockedBy: ["PAP-66", "PAP-236"]
blocks: ["PAP-76", "PAP-142", "PAP-603"]
key: "r4/design-system/typography-components-and-prose"
url: "https://linear.app/paperos/issue/PAP-666/typography-components-text-heading-with-decoupled-level-and-size-prose"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:25.584Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-25"
cycle: null
---

# PAP-666: Typography components: Text, Heading with decoupled level and size, Prose for MDX and rich text, Code and inline Kbd styling on the type tokens

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

PAP-66 defines the type scale but nothing turns it into components, so agents write `text-xl font-semibold` by hand and headings drift. Ship `Text`, `Heading` and `Prose` so pages, docs (PAP-128) and rich text (PAP-142) share one typographic system, and `Code` so snippets and inline keys look the same everywhere.

**Scope**

In: `packages/ui/src/typography/{Text,Heading,Prose,Code}.tsx` with `meta.ts` spec ids; `prose.css` scoped styles for MDX and Tiptap output; `useHeadingLevel` context; stories with the full scale.

Out: fonts and tokens (PAP-66), the `Kbd` component (navigation issue; `Prose` styles `<kbd>`), `RichTextEditor` chrome (PAP-142), reading-width guidelines prose (PAP-76).

**Spec**

* `Text { size: 'xs'..'xl', weight, tone: 'default'|'muted'|'subtle'|'danger'|..., truncate?, lineClamp?, as }` maps to PAP-66 type tokens only; tabular numerals option; `Heading { level: 1..6, size?: 'sm'..'4xl', as? }` decouples semantic level from visual size, and `HeadingLevelProvider` auto-increments levels in nested sections so codegen never emits skipped levels.
* `Prose` applies a scoped stylesheet (`.pos-prose`) for headings, paragraphs, lists, tables, blockquotes, code, images, `<kbd>`, links and footnotes rendered by MDX (PAP-128) and Tiptap JSON (PAP-142); measure 65ch, vertical rhythm on the 4 px grid, `size: 'sm'|'md'|'lg'`, dark and hc variants, RTL-safe (logical margins), print styles.
* `Code { inline?, language?, wrap? }` for inline and block code with tokens for background and border; block mode integrates with the highlighter the docs engine chooses (Shiki via PAP-128, soft) through a `highlight` prop, defaulting to plain.
* Fluid display sizes use PAP-66 `clamp()` tokens; `--pos-font-scale` (from PAP-647) multiplies the scale; text never below 12 px.
* Lint hook: the design lint issue flags raw `text-*`/`font-*` utilities outside `packages/ui` in favour of these components.

**Interface contract**

Provides: components with spec ids `ui.text`, `ui.heading`, `ui.prose`, `ui.code`; `HeadingLevelProvider`, `useHeadingLevel`; `prose.css`. Consumes: type tokens and fluid sizes (PAP-66), `cn` and conventions (PAP-236), `--pos-font-scale` (a11y preferences, soft), highlighter (PAP-128, soft). Consumed by PAP-128 docs engine, PAP-142 rich text rendering, PAP-76 guideline pages, PAP-234 states, PAP-120 codegen headings.

**Definition of done**

* Four components merged with stories (full scale, nested heading levels, Prose sample document in three sizes and RTL); `vitest-axe` clean including heading order.
* Screenshots at 375, 768, 1280 light, dark and hc; `docs/design/typography.md`; changelog; Linear comment on PAP-128 and PAP-142.

**Test plan**

* Unit: size and tone class mapping; heading level auto-increment and clamp at 6; line clamp; `Prose` size variants snapshot.
* Docs: an MDX fixture and a Tiptap JSON fixture render through `Prose` with identical computed styles for matching elements.
* E2E: none (Storybook).

**Demo**

Reviewer opens Storybook `Typography/Prose`, switches size and RTL, then opens `Heading/Nested sections` and inspects that levels increment automatically. Under one minute.

**Edge cases**

* Heading level beyond 6: clamped with a dev warning.
* Prose inside a card at 320 px: measure collapses to container width.
* Font scale 1.5: display sizes clamp to viewport.
* Forced colours: links keep underline.

**Dependencies**

PAP-66 (hard), PAP-236 (hard). Soft: a11y preferences, PAP-128. Blocks PAP-142 output styling and PAP-76 pages; PAP-128 adopts `Prose` when it lands (soft).

**Agent**

Builder: Iris (Component Crafter). Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/input/accessibility-input-preferences` = PAP-647.
