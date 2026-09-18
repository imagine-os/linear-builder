---
identifier: "PAP-837"
title: "Build the staff assistant panel: inspector slot, command palette \"Ask\", citations, suggested follow-ups, history and feedback"
project: "assistant"
projectName: "Tenant AI Assistant & Business Agents"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Staff"]
milestone: "Assistant contract and grounded chat"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-70", "PAP-142", "PAP-290", "PAP-333", "PAP-604", "PAP-833", "PAP-835", "PAP-836"]
blocks: ["PAP-839", "PAP-846"]
key: "r4/assistant/staff-chat-panel"
url: "https://linear.app/paperos/issue/PAP-837/build-the-staff-assistant-panel-inspector-slot-command-palette-ask"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:51:34.463Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-10-01"
cycle: null
---

# PAP-837: Build the staff assistant panel: inspector slot, command palette "Ask", citations, suggested follow-ups, history and feedback

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Give staff one place to ask: an assistant panel in the inspector slot that knows the current page and record, opens from the command palette with `?` or the `assistant.open` command, streams answers with citation chips, offers follow-ups, and keeps a searchable history per user.

**Scope**

In: `packages/assistant/src/ui/`: `<AssistantPanel/>` filling `shell.inspector` and `record.panel.tabs.assistant` (PAP-333) with context = current route spec key, selected record `EntityRef`, active view id; composer on the PAP-142 editor in local mode with `@` mentions of records and people. Command palette integration: `assistant.open`, `assistant.ask` (prefilled with the palette query when no command matches, PAP-290 fallback slot), `assistant.explain-page` (uses spec `purpose`, PAP-380). Message list: streaming text, citation chips (open record panel or doc), tool-call cards (confirm, deny, view diff), `pending_approval` cards linking to the approval inbox, feedback thumbs; suggested follow-ups from the model as buttons. History drawer: conversations by surface and anchor, search through PAP-39 registration `assistant_conversation` (owner-only), delete (soft, PAP-355 retention). Page spec `specs/pages/assistant/panel.page.spec.yaml`; a11y: live region for deltas throttled to sentence boundaries, focus stays in the composer, Escape closes.

Out: Portal widget (own issue). Action definitions. Voice (PAP-159 routes into `assistant.ask`).

**Spec**

* Panel opens in under 100 ms with the last conversation for this anchor; first token p95 under 1.5 s on staging (dashboard in PAP-40)
* Context chips at the top show what the assistant can see (page, record, view) and can be removed before sending, which narrows grounding scopes
* Citation chips render title, entity type icon (PAP-68) and hover preview; keyboard: Tab cycles chips, Enter opens
* Empty state (PAP-234) offers three page-specific starter questions derived from the spec `purpose` and dataset names
* Multi-window (PAP-262): the panel can detach; conversation state syncs through the window bus (PAP-145)

**Interface contract**

Provides: `<AssistantPanel/>`, commands `assistant.open|ask|explain-page`, slot fill for `record.panel.tabs.assistant`, `assistant_conversation` search registration. Consumes: `assistant.*` procedures and live deltas (runtime), retrieval citations, `AppFrame`/`Inspector` (PAP-70), command palette (PAP-290), editor (PAP-142), record panel tabs (PAP-333), help panel purpose (PAP-380). Consumed by: PAP-839 (renders view drafts in the panel), PAP-840, growth support inbox (reply drafting card).

**Definition of done**

* Panel works on console pages, record panels and views in the demo tenant; Storybook stories for every message part kind; axe clean
* Playwright: ask, stream, click citation, confirm a read tool, give feedback; screenshots at 375 (panel becomes a sheet), 1024, 1920
* Every new page has a `page.spec.yaml` (PAP-114) that passes the validator, declared loading, empty, error and denied states, and Gate 3 screenshots at 375, 768, 1024 and 1920 in light and dark themes.
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Unit: delta reducer with out-of-order `seq`; context chip removal narrows the `scopes` argument; follow-up buttons send the exact text.
* E2E: command palette fallback routes an unmatched query into the panel; detach and re-dock keeps the conversation; screen reader announces one sentence per update (PAP-156 matrix).
* Isolation: the PAP-34 cross-tenant harness auto-enrols every new table; one negative case per new oRPC procedure proves `NOT_FOUND` on a foreign tenant row.

**Demo**

On a CRM contact record, open the assistant tab, ask "what did we last promise them and when is their next invoice due?", click both citations, then give a thumbs up.

**Edge cases**

* Very long answer (tables of 200 rows): rendered as a collapsed block with "open as view" (hands off to `nl-to-views`) instead of inline
* Tenant with assistant disabled: the tab and command are hidden by the `assistant.enabled` flag; deep links show `DeniedState` with the reason
* Module disabled for the tenant (PAP-266): routes return `MODULE_DISABLED` (409), slot fills unmount and the manifest declares the dependency so consumers fail closed rather than half-render.

**Dependencies**

PAP-836 and PAP-835 (hard), PAP-70, PAP-290 (hard), PAP-142 and PAP-333 (soft, fallbacks exist).

**Agent**

Builder: Nova. Reviewer: Sentinel (Visual Inspector).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 4 round-4 file keys in this description to Linear identifiers: `r4/assistant/conversation-runtime` = PAP-836, `r4/assistant/nl-to-views` = PAP-839, `r4/assistant/retrieval-grounding` = PAP-835, `r4/assistant/summaries-and-drafting` = PAP-840.
