---
identifier: "PAP-728"
title: "Build journals: generate a docs page per issue from the prompt log with summary, decisions, files touched, cost and replay links"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Developer"]
milestone: "Knowledge surfaced everywhere"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-128", "PAP-129"]
blocks: []
key: "r4/collab/build-journals"
url: "https://linear.app/paperos/issue/PAP-728/build-journals-generate-a-docs-page-per-issue-from-the-prompt-log-with"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:19.200Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-728: Build journals: generate a docs page per issue from the prompt log with summary, decisions, files touched, cost and replay links

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Justin asked for every prompt and response to be logged 'properly in the documentation system'. PAP-129 stores them in Postgres and PAP-135 replays them, but nothing turns a finished session into a page a human or the next agent reads. Generate one journal page per issue in the docs engine, so the docs hold the memory of how each part of PaperOS was built.

**Scope**

In: job `journal.build` in `packages/collab/journal/` triggered by `agent.session.finished` and by PR merge (PAP-97); writer producing `docs/journal/<issue-key>.mdx` (committed on the issue's branch by the finishing session, or to `main` by the merge workflow for orphan sessions); template with frontmatter (`issue`, `sessions[]`, `character`, `model`, `costUsd`, `prUrl`, `status`); index page `/_app/docs/journal` with filters; `SessionLink` (PAP-135) embeds. Out: the 200-word search summary (PAP-138 writes it; reused here), character memory curation (PAP-109).

**Spec**

* Page sections: Summary (from `prompt_session.summary`, generated once by a Claude call with the Changelog Scribe prompt when absent), Decisions (assistant messages matching `decid|chose|because` heuristics plus ADR links from PAP-130 created in the session), Files touched (from `Edit|Write` tool inputs, grouped by package), Commands run (`Bash` tool inputs, deduplicated), Blockers and handoffs (PAP-108 comment format), Cost and tokens (from `promptLog.stats`), Replay (`?seq=` permalinks to the first tool error and final message).
* Redaction: journal content passes the PAP-129 second-pass redactor again; `[REDACTED:kind]` markers stay; tool outputs are never included, only inputs.
* Multiple sessions per issue append dated entries; a killed or failed session writes a stub with the failure reason.
* Journal pages carry `audience: [developer, agent]` and register as search kind `doc` with tag `journal` (PAP-138); size cap 40 KB per page with a 'see replay' link beyond it.
* Regeneration is idempotent by session id set; a manual edit below `<!-- journal:manual -->` survives regeneration.

**Interface contract**

Provides: `docs/journal/*.mdx`, `buildJournal(issueKey): MdxDocument`, job `journal.build`, `docs.journal.rebuild` procedure for staff.admin, MDX component `JournalRef`. Consumes: `prompt_session`, `prompt_event`, `promptLog.stats` (PAP-129), `renderMdx` and docs routes (PAP-128), `SessionLink` (PAP-135), `adr-index.json` (PAP-130), PR and merge events (PAP-97), Forgejo client for the commit (PAP-276, soft; PAP-134's wrapper otherwise), jobs (PAP-43). Consumed by: PAP-109 (memory loader reads Decisions), PAP-89 release digest (links), PAP-112 handbook.

**Definition of done**

* Journals generated for the 20-turn fixture session and for a real merged issue on staging; page renders at 375 and 1280 with TOC; redaction markers preserved.
* Index lists journals filterable by character and project; search finds a journal by issue key.
* `docs/collab/journals.md`; CHANGELOG entry; Linear comment with two rendered journals.

**Test plan**

* Unit: section extraction from fixture events (files, commands, decisions), idempotent regeneration, manual-section preservation, size cap.
* Integration: job run against seeded prompt log writes the file through a mocked Forgejo API; redactor invoked (spy).
* E2E (Playwright): open `/_app/docs/journal`, filter by character, open a page, click a replay link and land at `?seq=` in PAP-135.

**Demo**

Run `pnpm journal:build PAP-129` against the seeded store, open `/_app/docs/journal/PAP-129`, read Decisions, click the replay link. Under two minutes.

**Edge cases**

* Session with 10k events: extraction streams by `seq` chunks; page stays under the cap.
* Summary generation over budget: page written without Summary and flagged `needs_summary`; nightly retry.
* Issue renamed in Linear: file keyed by identifier, title refreshed from PAP-101 mirror when available.
* Sub-agent sessions (`parent_session_id`): folded into the parent's journal as a nested entry.

**Dependencies**

Hard: PAP-129, PAP-128. Soft: PAP-135, PAP-130, PAP-97, PAP-107 (real sessions), PAP-276, PAP-43, PAP-138.

**Agent**

Builder: Quill (Prompt Logger). Reviewer: Sentinel (Security Auditor for redaction) and Atlas.

**Size**

M: one session.
