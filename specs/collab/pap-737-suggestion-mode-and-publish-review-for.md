---
identifier: "PAP-737"
title: "Suggestion mode and publish review for runtime docs: tracked changes, accept or reject per change, approval before publish"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Knowledge surfaced everywhere"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-142", "PAP-379", "PAP-604"]
blocks: []
key: "r4/collab/docs-suggestion-mode"
url: "https://linear.app/paperos/issue/PAP-737/suggestion-mode-and-publish-review-for-runtime-docs-tracked-changes"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:33.587Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-737: Suggestion mode and publish review for runtime docs: tracked changes, accept or reject per change, approval before publish

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 (stretch pool; NJ-14 can reinstate). Not claimable before 10-01.

Google Docs' suggesting mode is what makes shared documents safe for agents and junior staff: propose, review, accept. Runtime docs (PAP-379) publish whatever the Yjs state holds. Add tracked changes on top of the shared editor and a publish gate for pages an admin marks `reviewed`.

**Scope**

In: Tiptap extension `suggestions` in `packages/collab/editor-ext/` storing insert and delete marks with `authorId`, `at`, `suggestionId` inside the Yjs doc (no server table); sidebar `SuggestionList` with accept, reject, accept all; `doc_page.review: none|required` and `docs.pages.publish` refusing while open suggestions exist when `required`; agents (`author_kind: agent`) always write in suggesting mode; diff view between the last published version (PAP-379 `doc_page_version`) and the current draft. Out: repo MDX docs (PRs are their review), comment threads (PAP-131 already anchors), suggestion notifications beyond `doc.suggestion_added` kind.

**Spec**

* Marks survive concurrent edits through Yjs; accepting applies the change and removes the marks in one transaction; rejecting removes the inserted text or restores the deleted text.
* Suggesting mode toggle per user per page (`Cmd+Shift+X`, PAP-151 command `editor.toggleSuggesting`); read-only render (`renderRichText`) shows the published state only.
* Kind `doc.suggestion_added` notifies the page owner (watchers through PAP-726), collapsed by PAP-324.
* Version diff uses `diff-match-patch` on `richTextToPlain` with block-level anchors so the diff opens at the first change.
* Import (PAP-203) writes directly, never as suggestions.

**Interface contract**

Provides: `suggestions` extension, `SuggestionList`, `review` column and publish gate, kind `doc.suggestion_added`, `DocDiffView`. Consumes: `RichTextEditor` and Yjs binding (PAP-142), `doc_page`, versions and publish (PAP-379), notification core, watchers (soft), commands (PAP-151), agent principals (PAP-60). Consumed by: PAP-192 content agent drafts, PAP-109 memory pages edited by agents.

**Definition of done**

* Two contexts: A suggests, B accepts one and rejects another, text matches expectation; publish blocked while a suggestion is open on a `required` page; agent edits always appear as suggestions.
* Screenshots at 768 and 1280 in light and dark; axe clean; `docs/collab/runtime-docs.md` gains Suggestions; CHANGELOG entry.

**Test plan**

* Unit: mark application and removal, accept-all ordering, publish gate, diff anchoring.
* Integration: two `Y.Doc`s through local Hocuspocus converge after concurrent accept and edit.
* E2E (Playwright, two contexts): suggest, accept, reject, publish.

**Demo**

Toggle suggesting, replace a sentence, switch browsers as the owner, accept it, publish, open the public page and see the new sentence. Under two minutes.

**Edge cases**

* Suggestion inside a suggestion: flattened to one with two authors.
* Owner rejects an agent's suggestion: `doc.suggestion_rejected` event for PAP-110 eval signal.
* Hocuspocus down: suggesting disabled with a banner; reading works.

**Dependencies**

Hard: PAP-379, PAP-142. Soft: PAP-725, PAP-726, PAP-151, PAP-60, PAP-324. Deferred: v0.2.

**Agent**

Builder: Nova (CRDT Engineer). Reviewer: Sentinel (Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/collab/notification-core` = PAP-725, `r4/collab/watchers-subscriptions` = PAP-726.
