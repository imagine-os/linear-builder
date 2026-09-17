---
identifier: "PAP-107"
title: "Hook every session's prompts, responses and tool calls into the prompt-log store"
project: "agents"
projectName: "Agent Characters & Orgs"
phase: "P0"
type: "Build"
priority: 1
surfaces: ["Agent"]
milestone: "Roster defined and installed"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-129"]
blocks: []
key: "agents/prompt-logging-hook"
url: "https://linear.app/paperos/issue/PAP-107/hook-every-sessions-prompts-responses-and-tool-calls-into-the-prompt"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:06:17.836Z"
---

# PAP-107: Hook every session's prompts, responses and tool calls into the prompt-log store

**Goal**

Record how the product was built: every prompt, response, tool call and tool result from every character session, with session, character, issue, tokens and cost, flows into the prompt-log store with secrets redacted before leaving the machine. This is the audit trail, the eval training set and the raw material for character memory.

**Scope**

* In: Claude Code hooks in the character bundles, the local spool, the shipper, transcript ingestion, redaction, the orchestrator's direct SDK path writing the same event shape, `docs/agents/prompt-logging.md`.
* Out: the store itself (PAP-129 ingest, dedupe, storage), curation into memory (PAP-109), the agent console UI (PAP-125 example page).

**Spec**

* Hooks `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `SubagentStop`, `PreCompact`, `Stop`, `SessionEnd` run `packages/agents/hooks/log-event.ts`, which reads hook JSON from stdin and appends one normalised event to `~/.paperos/spool/<session_id>.ndjson` in under 500 ms; heavy work (transcript parsing, shipping) runs on `Stop`/`SessionEnd` or in a detached shipper.
* Transcript ingestion parses the JSONL at `transcript_path` for assistant messages and `usage` so token counts are exact.
* Redaction `redact.ts`: patterns for API keys, JWTs, `sk-`, `ghp_`, connection strings, plus values from the secret map (PAP-106); URLs keep host and path, lose credential segments.
* Blobs over 64 KB go to MinIO (PAP-37) with a URL in the event, else truncated with `truncated: true`.
* Env: `PAPEROS_ISSUE`, `PAPEROS_CHARACTER`, `PAPEROS_SESSION` from the orchestrator; branch-name fallback.

**Interface contract**

* Provides: Zod `LogEvent = { v: 1, sessionId, parentSessionId?, seq, at, character, issue?, event: "session.start" | "prompt" | "tool.pre" | "tool.post" | "subagent.stop" | "compact" | "stop" | "session.end" | "session.killed" | "scope-denied", payload, usage? }` in `@paperos/agents/log`, `redact(text): string`, `shipSpool(sessionId)` posting NDJSON batches to PAP-129 `POST /api/prompt-log/ingest`, the synthetic `session.killed` writer used by PAP-111.
* Consumers: PAP-129 (ingest schema), PAP-98 (token counts for hook sessions), PAP-106 (`scope-denied` events), PAP-109 (source for memory proposals), PAP-110 (`issueKey: EVAL` runs), PAP-288 (heartbeats piggyback on `tool.post`).
* Requires: PAP-129 ingest endpoint (spool works without it), PAP-106 bundle `hooks.json`, PAP-96 SDK stream for direct writes.

**Definition of done**

* Redaction: 30 secret-like fixtures, zero false negatives, false positives listed.
* A 20-turn test session yields a complete ordered event set; token totals within 1 percent of the SDK `result`.
* Hook latency p95 under 500 ms (numbers in the comment).
* Shipped spool scan shows no raw key material.
* Docs page; changelog; Linear comment with integration results.

**Test plan**

* Unit: redaction table, `seq` monotonicity across resume, schema validation, transcript parser on three real transcripts.
* Integration: hooks invoked with recorded hook JSON; shipper against a mocked ingest with 429 backoff and 500 MB cap.
* e2e: 20-turn session on the toy repo with the spool compared to the SDK stream.
* Bench: `hyperfine` on `log-event.ts` cold start.
* No visual breakpoints.

**Demo**

Run a two-turn `claude -p` session with the bundle, `cat ~/.paperos/spool/<id>.ndjson | jq .event` to see the ordered events, then `pnpm log:ship <id>` and open the session in the prompt-log store. One minute.

**Edge cases**

* Store unreachable for hours: spool grows to 500 MB cap; oldest ships first.
* Killed by PAP-111: `SessionEnd` may not fire; orchestrator writes `session.killed`.
* Binary tool output: hash and size only.
* Resume shares a `transcript_path`: `seq` continues from stored max.
* Compaction: `PreCompact` logged so replays show the summary point.

**Dependencies**

Blocked by PAP-129 (ingest; may land up to 2026-09-21, spool-only until then). Integrates with PAP-106, PAP-96.

**Agent**

Built by Forge (Ops Runner) with Quill (Prompt Logger) defining the schema; reviewed by Sentinel (Security Auditor).

**Size**

M
