---
identifier: "PAP-318"
title: "Comment panel, pins and composer UI"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P1"
type: "Build"
priority: 1
surfaces: ["Staff"]
milestone: "Comments and canvas"
state: "Backlog"
parent: "PAP-131"
children: []
blockedBy: ["PAP-70", "PAP-317"]
blocks: ["PAP-319"]
key: "collab/comments/panel-pins-composer"
url: "https://linear.app/paperos/issue/PAP-318/comment-panel-pins-and-composer-ui"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:30:59.972Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-29"
cycle: null
---

# PAP-318: Comment panel, pins and composer UI

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Build the visible half of comments (PAP-131): a provider that makes any page commentable, pins positioned on anchored elements, a panel listing threads for the current page or entity, and a composer with mentions built on the shared editor.

**Scope**

In:

* `packages/collab/comments/`: `CommentableRoot` provider, `data-comment-anchor` handling (codegen's `data-spec-key` doubles as the element anchor), pin overlay positioned from `getBoundingClientRect` and re-anchored on resize and scroll, clustering above 12 pins per viewport.
* `CommentsPanel` for the inspector slot (drawer under `lg`), `ThreadView`, `ResolveButton`, `CreateIssueButton` slot (wired by the sibling), reactions.
* Composer: `RichTextEditor` (PAP-142) in local `comment` variant with `MentionSource` for users, agents and entities; `Cmd+Enter` sends; attachments via PAP-37 signed uploads.
* Keyboard: command `comment.new` on `c` (PAP-151) targeting the focused element.

Out: data layer and procedures (sibling 1), live refresh and deep links (sibling 3).

**Spec**

* Pins are `button`s with `aria-label="Comment thread, 3 replies, open"`; panel lists open first then resolved.
* Storybook stories: pin states, cluster, panel empty and populated, composer with mention popup, at 320, 768 and 1280.
* Uses TanStack Query over the sibling's procedures; optimistic insert of the author's own comment.

**Interface contract**

Exposes `CommentableRoot`, `useThreads(anchor)`, `useComposer()`, `CommentsPanel`, `CommentPin`, `ThreadView`, DOM attribute `data-comment-anchor`. Consumes `comments.*` procedures and `CommentAnchor` (sibling 1), `RichTextEditor` and `MentionSource` (PAP-142), `Inspector` slot and `Drawer` (PAP-70, PAP-237), `defineCommand` (PAP-151), `AvatarStack` (PAP-71), signed uploads (PAP-37).

**Definition of done**

* Sample page is commentable end to end against the sibling's API; screenshots at 320, 375, 768, 1024, 1280, 1536 and 1920 in light and dark.
* axe clean; composer keyboard-only; Storybook published; Linear comment with screenshots.

**Test plan**

* Vitest: pin position math on resize and scroll fixtures, clustering threshold, optimistic insert and rollback.
* Component: composer mention popup opens on `@`, `Cmd+Enter` sends, empty body blocked; axe on every story.
* Playwright: press `c` on a focused field, type, send, see the pin and panel entry; resolve and reopen; drawer behaviour at 375.
* Visual: Gate 3 baselines for pins, panel and drawer.

**Demo**

Open the sample records page, press `c` on a field, type a comment mentioning @Bo, send, watch the pin appear; open the panel, resolve it, reopen it. Under two minutes.

**Edge cases**

* Element removed after mount: pin hidden, thread listed under Unanchored.
* 50 pins: clusters with a count.
* Composer offline: pending state via PAP-148.

**Dependencies**

Sibling 1 (schema and procedures), PAP-142, PAP-70 (hard). PAP-151, PAP-37 (soft). Blocks sibling 3.

**Agent**

Built by Iris (Component Crafter) with Nova. Reviewed by Sentinel (Visual Inspector).

**Size**

M: several components plus positioning and composer integration.
