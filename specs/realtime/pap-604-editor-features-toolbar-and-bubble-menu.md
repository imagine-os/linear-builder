---
identifier: "PAP-604"
title: "Editor features: toolbar and bubble menu on design-system primitives, `editor.*` commands with shortcuts, mentions of users, agents and entities through `MentionSource`, markdown round-trip, image upload and the comment-variant stories"
project: "realtime"
projectName: "Multiplayer & Realtime"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Yjs server and presence"
state: "Backlog"
parent: "PAP-142"
children: []
blockedBy: ["PAP-603"]
blocks: ["PAP-131", "PAP-317", "PAP-379", "PAP-627", "PAP-654", "PAP-737", "PAP-837", "PAP-856"]
key: "r4/realtime/editor-features"
url: "https://linear.app/paperos/issue/PAP-604/editor-features-toolbar-and-bubble-menu-on-design-system-primitives"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:15.251Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-25"
cycle: null
---

# PAP-604: Editor features: toolbar and bubble menu on design-system primitives, `editor.*` commands with shortcuts, mentions of users, agents and entities through `MentionSource`, markdown round-trip, image upload and the comment-variant stories

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Second half of PAP-142: what makes the editor pleasant. A toolbar and bubble menu built from the design system, every action registered as a command with a shortcut, `@` and `#` mentions of people, agents and entities, markdown in and out, and images uploading through the file service, with the `comment` and `inline` variants ready for PAP-131.

**Scope**

In: `packages/collab/src/editor/{Toolbar,BubbleMenu,mentions,markdown,images}.tsx`, commands `editor.bold|italic|link|heading|list|task|table|code|image|mention` registered with PAP-151 (soft: local registry until it lands), roving tabindex on the toolbar (PAP-152), `MentionSource { search(q, kinds) -> Mention[] }` with `Mention { kind: user|agent|entity, id, label, avatarUrl? }` rendering `ActorBadge` for agents (PAP-60, soft), `markdownToRichText()` and `richTextToMarkdown()` via `prosemirror-markdown`, image node uploading through `uploadFile` (PAP-37) with a placeholder and retry, Storybook `comment` and `inline` variants plus dense and RTL, docs section.

Out: Core binding and schema (sibling), anchoring and threads (PAP-131), AI assistance, version history.

**Spec**

* Toolbar uses PAP-236 to PAP-238 primitives (`Button`, `Menu`, `Tooltip`, `Dialog`); hidden in `inline` variant; bubble menu on selection in all variants; every action appears in the command palette with its shortcut.
* Mentions: `@` opens the people and agents list, `#` the entity list from the dataset registry (PAP-161, soft: users only); a mentioned user who loses access renders as plain text with a tooltip; mentions serialise as `{ type: 'mention', attrs: { kind, id, label } }` and `richTextToPlain` renders `@label`.
* Markdown: paste detection converts lists, headings, code and links; export round-trips the fixtures in the unit suite; unsupported nodes degrade to text.
* Images: paste or drop uploads through PAP-37 with progress, a placeholder node with retry on failure, and alt text prompt for accessibility; SVG refused (PAP-37 sandbox rule).
* Comment variant: single toolbar row, submit on `mod+enter`, 10,000 character cap with a counter; inline variant: no chrome, bubble menu only.

**Interface contract**

Provides: `Toolbar`, `BubbleMenu`, command ids `editor.*`, `MentionSource` interface and `Mention` type, `markdownToRichText`, `richTextToMarkdown`, image node, variant stories.

Consumes: Editor core (sibling), primitives (PAP-236 to PAP-238), command registry (PAP-151, soft), roving tabindex (PAP-152, soft), file uploads (PAP-37), `ActorBadge` (PAP-60, soft), dataset registry for entity mentions (PAP-161, soft). Consumed by PAP-131, PAP-318, PAP-379, PAP-411.

**Definition of done**

* Toolbar actions appear in the palette with shortcuts; mention of a user and an agent inserts and serialises; markdown paste converts a list (Playwright).
* Image upload with a forced failure shows the placeholder and retries successfully; markdown round-trip fixtures pass.
* Stories for four variants at 320, 768, 1280 with axe passing; docs; changelog; Linear comment with the Storybook link.

**Test plan**

* Unit: markdown round-trip fixtures, mention insertion and serialisation, command registration table, image placeholder state machine, character cap.
* E2E: Playwright: run Bold from the palette, insert a mention, paste markdown, drop an image; RTL story capture.

**Demo**

Press `mod+k`, run Bold, type `@` and pick Forge (agent badge), paste a markdown list and see it convert, drop an image and watch it upload. Under two minutes.

**Edge cases**

* Mention source slow: list shows a skeleton and cancels stale queries.
* Very long link pasted: rendered as a link, not converted to an embed.
* Toolbar in a 320 px comment box: overflow menu.

**Dependencies**

Blocked by PAP-603 (hard). Soft: PAP-236 to PAP-238, PAP-151, PAP-152, PAP-37, PAP-60, PAP-161. Consumed by PAP-131, PAP-318, PAP-379, PAP-411.

**Agent**

Builder: Nova (CRDT Engineer); Iris reviews toolbar styling. Reviewer: Sentinel (Visual Inspector; Code Reviewer).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/realtime/editor-core` = PAP-603.
