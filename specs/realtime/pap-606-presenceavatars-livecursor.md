---
identifier: "PAP-606"
title: "`PresenceAvatars`, `LiveCursor`, `SelectionHighlight` and `ViewersBadge` on `AvatarStack` with colour tokens, idle and reduced-motion rules, accessibility labels and stories in three themes"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Yjs server and presence"
state: "Backlog"
parent: "PAP-141"
children: []
blockedBy: ["PAP-605"]
blocks: ["PAP-146", "PAP-149", "PAP-481"]
key: "r4/realtime/presence-components"
url: "https://linear.app/paperos/issue/PAP-606/presenceavatars-livecursor-selectionhighlight-and-viewersbadge-on"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:15.450Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-25"
cycle: null
---

# PAP-606: `PresenceAvatars`, `LiveCursor`, `SelectionHighlight` and `ViewersBadge` on `AvatarStack` with colour tokens, idle and reduced-motion rules, accessibility labels and stories in three themes

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Second half of PAP-141: what people see. Four components in `packages/ui` render the presence data from the sibling on any page, with the overflow, truncation, idle and motion rules PAP-141 specifies, so grids, docs, canvases and the support chat all show presence the same way.

**Scope**

In: `packages/ui/src/presence/{PresenceAvatars,LiveCursor,SelectionHighlight,ViewersBadge}.tsx` on PAP-71 `AvatarStack` and `Badge`; 12 accessible colour tokens from PAP-66 chosen by `presenceColor`; `PresenceAvatars` shows 5 plus overflow with a tooltip listing 20; `LiveCursor` fades after 4 s, hidden on touch, label truncated at 24 characters; `SelectionHighlight` outlines rows or ranges in the peer's colour; `ViewersBadge` for entity rooms; idle peers dimmed; reduced motion removes animation and pulse; live region announcing joins at most once per 10 s; Storybook stories in light, dark and high contrast; docs section.

Out: Data path and privacy (sibling), agent avatar and activity chip (PAP-146), follow bar (PAP-149).

**Spec**

* `PresenceAvatars peers max=5` with `aria-label` 'Ada, Ben and 3 others are here'; overflow tooltip lists up to 20 names; `x2` badge for a peer with several windows.
* `LiveCursor` positions relative to the surface via `data-presence-surface`; hidden when the peer's `cursor` is null or the device is touch; 50 ms transition, none under reduced motion.
* `SelectionHighlight` accepts `{ entityId, fieldId? }` or `{ from, to }` and renders an outline with the peer's colour token and a name tag on hover; multiple peers on one cell stack tags.
* Colour tokens meet 3:1 against both themes; the token set is documented for PAP-146's agent palette.

**Interface contract**

Provides: Four components with props documented, `presenceTokens` list, stories.

Consumes: Presence hooks and `presenceColor` (sibling), `AvatarStack` and `Badge` (PAP-71), tokens (PAP-66), reduced-motion hook (PAP-72, soft). Consumed by PAP-146, PAP-165, PAP-132, PAP-142, PAP-411.

**Definition of done**

* Stories for the four components in three themes; axe clean; reduced-motion story has no animation; screenshots at 375, 1024 and 1920.
* 50-viewer fixture shows 5 plus `+45` and the tooltip lists 20; long names truncate; docs; changelog; Linear comment with the Storybook link.

**Test plan**

* Unit: overflow text, truncation, colour token selection, touch detection, announcement throttling.
* E2E: Playwright two contexts on the records page: avatars, cursor and selection outline render; disconnect dims then removes.

**Demo**

Move the mouse in one browser and watch the labelled cursor in the other; select a row and see the outline; hover the avatar stack to read the names. Under two minutes.

**Edge cases**

* Scrolled container: surface-relative coordinates keep cursors aligned.
* Peer without avatar: initials in the peer colour.
* High-contrast theme: outlines use the theme's focus colour with the peer colour as a dot.

**Dependencies**

Blocked by PAP-605 (hard). Soft: PAP-71, PAP-66, PAP-72. Blocks PAP-146.

**Agent**

Builder: Nova (CRDT Engineer); Iris (Component Crafter) pairs on components. Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/realtime/presence-core` = PAP-605.
