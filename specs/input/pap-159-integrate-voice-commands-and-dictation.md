---
identifier: "PAP-159"
title: "Integrate voice commands and dictation (Web Speech with Whisper fallback) routed through the command registry"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P2"
type: "Build"
priority: 2
surfaces: ["Customer", "Staff"]
milestone: "Voice and accessibility certification"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-151", "PAP-291", "PAP-476"]
blocks: []
key: "input/voice"
url: "https://linear.app/paperos/issue/PAP-159/integrate-voice-commands-and-dictation-web-speech-with-whisper"
source: "Linear snapshot 2026-09-17T15:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T14:58:05.711Z"
model: "claude-sonnet-5"
effort: "high"
---

# PAP-159: Integrate voice commands and dictation (Web Speech with Whisper fallback) routed through the command registry

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Let people talk to the app: say a command (“open inbox”, “assign to Bo”) and it runs through the command registry; dictate into any text field with punctuation. This build uses the browser's Web Speech API only; a self-hosted Whisper backend is recorded as a reopen criterion, not built (keeps the TypeScript-only monorepo and the VPS RAM budget from PAP-214).

**Scope**

In:

* `packages/input/src/voice/`: `VoiceProvider` with a `SpeechBackend` interface (`start/stop/onPartial/onFinal/onError`) and one implementation `WebSpeechBackend` (`SpeechRecognition`, `continuous`, `interimResults`); a `MockBackend` for tests.
* Intent matching over `commands.manifest.json` (PAP-151): normalise transcript, fuzzy match titles, keywords and PAP-153 aliases, chooser when the top two are close, slot extraction (people via `MentionSource`, status values, numbers, dates via `chrono-node` 2.x).
* Dictation into `<input>`, `<textarea>` and `RichTextEditor` (PAP-142) via a `DictationTarget` adapter: spoken punctuation, auto-capitalisation, undo last utterance.
* UI: `VoiceButton` (push-to-talk `mod+shift+v`, hold-space in TV mode), listening indicator with waveform, partial transcript chip, confirmation toast; palette entry "Start dictation".
* Privacy: permission flow with explanation, visible capture indicator, no audio stored, transcripts logged only with tenant setting `voice.logTranscripts`; tenant setting `voice.enabled` (Chrome sends audio to Google, so tenants can disable).
* ADR note: Whisper backend reopens when a tenant requires on-premise recognition or when Firefox and WebKitGTK usage exceeds 20 percent.

Out: Whisper server, wake words, text-to-speech, natural-language questions, non-English beyond configuration.

**Spec**

* Score = 0.6 × Jaro-Winkler token similarity + 0.4 × double-metaphone; threshold 0.75; one candidate runs, several within 0.05 open the chooser, none → toast with transcript.
* Commands opt in with `voice: { phrases?, confirm? }`; `confirm: true` requires "yes" or a click.
* Only finals trigger commands; partials are display only.
* Unsupported browser: button disabled with a tooltip naming the supported browsers; everything voice does is possible by keyboard.
* Listening state announced; indicator uses icon, text and motion (motion off under reduced motion).

**Interface contract**

Exposes: `SpeechBackend` interface (the seam a future Whisper backend implements), `VoiceProvider`, `useVoice()`, `matchCommand(transcript, manifest, aliases) -> { command, score, args }[]`, `DictationTarget { insert(text), deleteLast(n), getContext() }` with adapters for inputs and Tiptap (PAP-158's `SpatialKeyboard` reuses it), command extension `voice` on `defineCommand`, tenant settings keys `voice.enabled`, `voice.logTranscripts`. Consumes: manifest, `execute(id, args, 'voice')` and `voice` option (PAP-151), effective aliases (PAP-153), `RichTextEditor` insertion API (PAP-142), `MentionSource` (PAP-142), tenant settings (PAP-33), microphone entitlement for Tauri mobile (PAP-260), palette registration (PAP-151).

**Definition of done**

* "Open inbox", "create record", "assign to Bo" and "mark done" run on the sample pages in Chrome; demo video attached.
* Dictation into a form field and a Tiptap comment with spoken punctuation works; screenshots of indicator and chooser at 375 and 1280.
* Security review confirms no audio persistence and settings gating; `docs/platform/input/voice.md` with the browser matrix, privacy statement text and the Whisper reopen criteria; changelog; Linear comment with links.

**Test plan**

* Vitest: transcript normalisation, scoring thresholds with fixtures (exact, near, homophones "Bo"/"Beau", none), slot extraction for people, status, numbers and dates, punctuation and capitalisation rules, undo of last utterance.
* Component: `VoiceButton` states (idle, listening, denied, unsupported) with axe; reduced-motion story has no waveform animation.
* Playwright with `MockBackend` injected via `window.__paperosVoice.inject(transcript)` at 375 and 1280: commands run and toast, chooser appears for near ties, dictation inserts into an input and a Tiptap comment, out-of-scope command refused with "Not available here".
* Manual: Chrome desktop and Android Chrome real microphone run recorded.

**Demo**

In Chrome, hold `mod+shift+v`, say “open inbox”, release, watch it navigate and toast “Ran: Open inbox”; click into a comment, choose “Start dictation” from the palette and dictate a sentence with “comma” and “new line”. Under two minutes.

**Edge cases**

* Noisy finals: only finals trigger; low score → toast.
* Permission denied: disabled state with instructions, no re-prompt loop.
* Chrome stops after \~60 s silence: auto-restart while held.
* Tenant disables voice: button hidden, command unregistered.

**Dependencies**

PAP-151 (hard, encoded). Soft: PAP-153, PAP-142, PAP-33, PAP-260, PAP-158.

**Agent**

Builder: Nova. Reviewer: Sentinel (Security Auditor for privacy gating, Edge Case Hunter for noisy input).

**Size**

M: one backend plus matching and dictation; the matching logic is testable offline.
