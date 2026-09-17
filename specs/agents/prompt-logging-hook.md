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
source: "plan/specs/bucket-3.json (round-1 canonical spec JSON)"
---

# PAP-107: Hook every session's prompts, responses and tool calls into the prompt-log store

**Goal**

Record how the product was built: every prompt, response, tool call and tool result from every character session, with session, character, issue, tokens and cost, flows into the prompt-log store with secrets redacted before they leave the machine. This is the audit trail, the training set for evals and the memory source for characters.

**Scope**

In:
- Claude Code hooks in the generated character bundles (`agents/tool-scopes`): `SessionStart`, `UserPromptSubmit`, `PreToolUse`, `PostToolUse`, `SubagentStop`, `Stop`, `SessionEnd`, each running `packages/agents/hooks/log-event.ts` which reads the hook JSON from stdin (`session_id`, `transcript_path`, `cwd`, `hook_event_name`, `tool_name`, `tool_input`, `tool_response`) and appends a normalised event to a local spool `~/.paperos/spool/<session_id>.ndjson`.
- Transcript ingestion on `Stop`/`SessionEnd`: parse the JSONL at `transcript_path` for assistant messages and their `usage` (input, output, cache read, cache creation tokens) so token counts are exact even when hooks miss a turn.
- Orchestrator path: sessions launched through the Agent SDK also stream messages directly; `pm-linear/orchestrator` writes the same event shape, so the store sees one format regardless of launch method.
- Shipper `packages/agents/hooks/ship.ts`: batches spool files and POSTs NDJSON to the store's ingest endpoint defined by `collab/prompt-log-store` (`POST /api/prompt-log/events`, bearer token per character), with retry and at-least-once delivery; the store dedupes on `(session_id, seq)`.
- Redaction before spooling: regexes for API keys (`sk-ant-`, `lin_api_`, `ghp_`, `sk_live`, AWS, JWTs), `.env` file contents, and any value present in the character's secrets map; replaced with `[REDACTED:<kind>]` and counted.
- Event schema `packages/agents/src/log-event.ts` (Zod): `sessionId`, `seq`, `ts`, `character`, `issueKey`, `event`, `role`, `content` (truncated to 64 KB with `truncated: true`), `toolName`, `toolInput`, `toolOutput`, `usage`, `costUsd`, `model`, `redactions`.

Out: the store's schema and UI (`collab/prompt-log-store`, `collab/prompt-log-ui`), curation into knowledge (Quill's Prompt Logger routine), metering arithmetic (`pm-linear/credit-metering` reads from the store).

**Spec**

- Hook scripts must finish under 500 ms so they do not slow the session; heavy work (transcript parsing, shipping) happens in `Stop`/`SessionEnd` or in a detached shipper process.
- Sequence numbers are monotonic per session from a local counter file; `seq` gaps are reported by the store.
- Issue key and character come from env (`PAPEROS_ISSUE`, `PAPEROS_CHARACTER`) set by the orchestrator, or from the worktree branch name as a fallback.
- Tool outputs above 64 KB are stored as a blob in `data-layer/file-storage` (MinIO) with a URL in the event when available; otherwise truncated.
- A `--dry-run` mode prints events to stderr for local debugging; hook failures never block the session (exit 0 with stderr note) except for the scope hook which is separate.

**Definition of done**

- Unit tests for redaction (30 secret-like fixtures, zero false negatives on the fixture set, false positives listed), schema validation, transcript parsing on three real transcripts.
- Integration: a 20-turn test session produces a complete, ordered event set in the store; token totals match the SDK `result` message within 1 percent.
- Hook latency measured under 500 ms p95 (numbers in the comment).
- Secrets scan of a shipped spool shows no raw key material.
- `docs/agents/prompt-logging.md` (what is logged, retention, how to inspect a session locally); changelog entry; Linear comment with the integration results.

**Edge cases**

- Store unreachable for hours: spool grows; shipper caps at 500 MB per host and pages the orchestrator log; oldest sessions ship first.
- Session killed by the kill switch (`agents/cost-controls`): `SessionEnd` may not fire; the orchestrator writes a synthetic `session.killed` event.
- Sub-agent transcripts (Task tool): captured via `SubagentStop`, linked by `parentSessionId`.
- Binary tool output (screenshots read via Read): store a hash and size, not bytes.
- Redaction removes something needed for debugging (a URL with a token): keep the host and path, redact only the credential segment.
- Two sessions share one `transcript_path` after a resume: `seq` continues from the stored max for that session id.
- Compaction rewrites history: log the `PreCompact` event so replays show where context was summarised.

**Dependencies**

- `collab/prompt-log-store` (ingest endpoint, dedupe, storage).
- Integrates with `agents/tool-scopes` bundles and `pm-linear/orchestrator` SDK stream.

**Agent**

Built by Forge (Ops Runner) with Quill (Prompt Logger) defining the event content; reviewed by Sentinel (Security Auditor for redaction) and Code Reviewer.

**Size**

M: several small hooks, but redaction and delivery guarantees need care.
