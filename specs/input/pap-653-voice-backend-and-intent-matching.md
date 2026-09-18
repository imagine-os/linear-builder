---
identifier: "PAP-653"
title: "Voice backend and intent matching: SpeechBackend interface, WebSpeechBackend and MockBackend, transcript normalisation, fuzzy command matching and slot extraction"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Voice and accessibility certification"
state: "Backlog"
parent: "PAP-159"
children: []
blockedBy: ["PAP-151", "PAP-153", "PAP-291", "PAP-476"]
blocks: ["PAP-654"]
key: "r4/input/voice-backend-and-intent-matching"
url: "https://linear.app/paperos/issue/PAP-653/voice-backend-and-intent-matching-speechbackend-interface"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:31.957Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-653: Voice backend and intent matching: SpeechBackend interface, WebSpeechBackend and MockBackend, transcript normalisation, fuzzy command matching and slot extraction

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

First half of PAP-159, fully testable offline: the `SpeechBackend` seam (Web Speech now, Whisper later), a `MockBackend` for tests, and the intent layer that turns a transcript into a command with arguments using the manifest, keymap aliases and fuzzy scoring.

**Scope**

In: `packages/input/src/voice/{backend,webSpeech,mock,normalize,match,slots}.ts`; `SpeechBackend { start, stop, onPartial, onFinal, onError, capabilities }`; `matchCommand(transcript, manifest, aliases, ctx)`; slot extraction for people (`MentionSource`), status values, numbers and dates (`chrono-node` 2.x); tenant settings `voice.enabled`, `voice.logTranscripts`; ADR note on the Whisper reopen criteria.

Out: UI, dictation into fields and the palette entry (sibling), wake words, text-to-speech, Whisper server.

**Spec**

* `WebSpeechBackend` wraps `SpeechRecognition` with `continuous`, `interimResults`, `lang` from PAP-27 locale, auto-restart on Chrome's \~60 s silence stop while held; `capabilities` reports `{ supported, continuous, offline: false }`; `MockBackend.inject(transcript, { final })` for tests exposed as `window.__paperosVoice` in test mode (PAP-240).
* Normalisation: lowercase, strip punctuation, number words to digits, remove fillers ("please", "um"), map spoken symbols; command phrases from `title`, `keywords`, `voice.phrases` and PAP-153 aliases.
* Score = 0.6 × Jaro-Winkler token similarity + 0.4 × double-metaphone match; threshold 0.75; exactly one candidate above threshold runs, several within 0.05 return a chooser list, none returns `{ none: true, transcript }`; only `final` transcripts are matched.
* Slots: `argsSchema` fields typed `user` resolve through `MentionSource` (PAP-142) with fuzzy name match, `enum` fields match option labels, numbers and dates via `chrono-node` in the actor timezone; missing required slots return `{ needsArgs: [...] }` for the UI to prompt.
* Privacy: no audio stored; transcripts logged (PAP-129 prompt-log kind `voice`) only when `voice.logTranscripts`; `voice.enabled=false` unregisters the provider; every matched command runs through `registry.execute(id, args, 'voice')` so audit and telemetry apply.

**Interface contract**

Provides: `SpeechBackend` interface (in `contract-input` as `VoiceRoutePort`), `WebSpeechBackend`, `MockBackend`, `normalizeTranscript`, `matchCommand`, `extractSlots`, settings keys, telemetry `voice.matched { score, chooser }`. Consumes: manifest and execute (PAP-291), aliases (PAP-153), `MentionSource` (PAP-142, soft: user list fallback), tenant settings (PAP-33), locale (PAP-27), test mode (PAP-240), prompt log (PAP-129, soft). Consumed by the sibling UI.

**Definition of done**

* Matcher fixtures (exact, near, homophones "Bo"/"Beau", none, multi-slot) green; `WebSpeechBackend` manual Chrome run recorded; `docs/platform/input/voice.md` sections on matching, privacy and the Whisper reopen criteria; changelog.

**Test plan**

* Unit: normalisation table; scoring thresholds and chooser window; slot extraction for people, enums, numbers, dates including relative ("next Friday"); auto-restart logic with fake timers; settings gating.
* Integration: `MockBackend` through the registry executes `nav.goToInbox` with source `voice` and an audit row; disabled tenant → provider unregistered.
* E2E: none (sibling).

**Demo**

Reviewer runs `pnpm tsx scripts/voice-match.ts 'assign this to bo'` and reads the matched command, score and extracted user, then repeats with a near tie to see the chooser list. Under one minute.

**Edge cases**

* Chrome sends audio to Google: documented in the privacy statement text; tenants may disable.
* Two commands with identical titles in sibling scopes: focused scope wins before scoring.
* Non-English locale without a phrase list: matching falls back to titles in that locale (PAP-27 catalogs).
* Transcript with a number word ("two"): parsed as a slot only when the schema expects a number.

**Dependencies**

PAP-291 (hard), PAP-153 (hard, aliases). Soft: PAP-142, PAP-33, PAP-27, PAP-240, PAP-129. Blocks the sibling.

**Agent**

Builder: Nova (Product Systems Engineer). Reviewer: Sentinel (Security Auditor (privacy gating), Edge Case Hunter).

**Size**

M: one session.
