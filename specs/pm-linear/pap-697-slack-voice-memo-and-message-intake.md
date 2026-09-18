---
identifier: "PAP-697"
title: "Slack voice memo and message intake: transcribe audio posted in `#paperos-inbox`, create a Triage issue with the transcript and audio attachment, and reply in the thread with the drafted issue link"
project: "pm-linear"
projectName: "Project Management & Claude Pipeline"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Staff"]
milestone: "PM module syncs both ways"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-97", "PAP-325", "PAP-696"]
blocks: []
key: "r4/pm-linear/slack-voice-memo-intake"
url: "https://linear.app/paperos/issue/PAP-697/slack-voice-memo-and-message-intake-transcribe-audio-posted-in-paperos"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:28.346Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-697: Slack voice memo and message intake: transcribe audio posted in `#paperos-inbox`, create a Triage issue with the transcript and audio attachment, and reply in the thread with the drafted issue link

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Justin steers from his phone and already sends voice memos; today someone transcribes them by hand. A Slack app listening on one channel turns each voice memo or message into a Triage issue with the transcript, the audio as an attachment and the Slack permalink, then the Decomposer (PAP-307) drafts it and the bot replies in the thread with the issue link and the one question, if any.

**Scope**

* In: `apps/orchestrator/src/intake/slack.ts` (Slack Events API `message` and `file_shared` in `#paperos-inbox`, signature verification), audio download through the broker (PAP-300), transcription adapter `transcribe(audio): { text, segments, language }` with a Whisper-compatible provider behind a port (local `whisper.cpp` on the VPS first, hosted API second, chosen by config), issue creation in `Triage` via `PmSourcePort` with the transcript, `attachmentCreate` for the Slack permalink and audio file (MinIO signed URL, PAP-37), thread reply with the issue link, `docs/pm/intake.md`.
* Out: Linear's native Slack integration for notifications (PAP-325 owns tenant Slack config), Slack decision buttons for Needs Justin (cross-project suggestion to collab), non-audio attachments beyond images.

**Spec**

* Slack app scopes `channels:history`, `files:read`, `chat:write`, `reactions:write`; events verified with the signing secret and a 60 s timestamp window (PAP-97 pattern); only members listed in `operatorSlackUserIds` (Justin) create issues; others get a reaction and no issue.
* Audio: `.m4a`, `.mp3`, `.ogg`, `.wav`, `.webm` up to 25 MB; downloaded with the bot token injected by the broker; transcribed with a 90 s timeout; language detected; transcript stored under `Original request` verbatim with timestamps every 30 s; a text message becomes the same issue shape without the audio.
* Issue: title = first sentence of the transcript truncated to 80 characters, description = `Source: slack:<permalink>` footer plus the transcript, state `Triage`, label `source:slack`; audio attached as a MinIO URL (30-day lifecycle) and the Slack permalink as a second attachment; PAP-307 drafts as for any Triage issue.
* Thread reply within two minutes: issue link, `triaged` status, and the Decomposer's one `ask:` question if present; a `:white_check_mark:` reaction on accept.
* Idempotency by Slack `event_id` and `file_id`; retries safe.

**Interface contract**

* Provides: Slack intake handler, `TranscriptionPort` with two adapters, `source:slack` label, attachment convention (permalink plus audio), thread-reply template.
* Consumes: PAP-97 receiver framework, Triage state and intake contract, PAP-307 drafting, PAP-300 broker for Slack and provider tokens, PAP-37 MinIO, PAP-325 Slack app registration (shared app; scopes added here).

**Definition of done**

* A 45 s voice memo in `#paperos-inbox` becomes a Triage issue with transcript and two attachments and is drafted; the thread shows the link within two minutes (recording).
* Transcription accuracy check on five memos: Justin confirms the transcripts are usable in a comment.
* Non-operator message creates nothing; duplicate event delivery creates one issue (tests).
* Docs; changelog; Linear comment with the recording; Needs Justin card for the transcription provider only if the local model is too slow (default: local).

**Test plan**

* Unit: signature verification, event dedupe, title derivation, transcript formatting with segments.
* E2E: recorded Slack events through the handler with a fixture audio file; live memo on the staging channel.

**Demo**

Post a voice memo in `#paperos-inbox`, wait for the thread reply, open the Triage issue: transcript, audio attachment, drafted contract, one question. Under two minutes.

**Edge cases**

* Two memos in one minute about the same thing: PAP-307's duplicate detection labels `possible-duplicate`; no merge without Justin.
* Transcription fails or times out: issue still created with `transcript: unavailable` and the audio attached; retried once in the background.
* Memo is a decision reply ("approve the RC"): the handler recognises the PAP-94 grammar in the transcript and asks Justin to confirm in Linear; voice never approves directly (T1 requires the Linear actor id, PAP-299).
* Channel archived or bot removed: health check posts to the Plan audit issue.

**Dependencies**

Hard: PAP-97, PAP-696, PAP-325. Soft: PAP-307, PAP-300, PAP-37, PAP-299, PAP-94.

**Agent**

Builder: Atlas (Dispatcher) with Forge (Ops Runner) for the transcription container. Reviewer: Sentinel (Security Auditor).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/pm-linear/linear-triage-enable-and-intake-state-machine` = PAP-696.
