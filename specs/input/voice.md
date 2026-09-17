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
blockedBy: ["PAP-151"]
blocks: []
key: "input/voice"
url: "https://linear.app/paperos/issue/PAP-159/integrate-voice-commands-and-dictation-web-speech-with-whisper"
source: "plan/specs/bucket-5.json (round-1 canonical spec JSON)"
---

# PAP-159: Integrate voice commands and dictation (Web Speech with Whisper fallback) routed through the command registry

**Goal**

Let people talk to the app: say a command ("open inbox", "assign to Bo", "mark done") and it runs through the command registry; dictate into any text field with punctuation; and do it privately, using the browser's Web Speech API when available and a self-hosted Whisper endpoint when it is not (Linux WebKitGTK, Firefox, kiosk). Voice is another input to the same command surface, not a separate assistant.

**Scope**

In:
- `packages/input/src/voice/`: `VoiceProvider` with a `SpeechBackend` interface (`start/stop/onPartial/onFinal/onError`) and two implementations: `WebSpeechBackend` (`SpeechRecognition` with `continuous`, `interimResults`) and `WhisperBackend` streaming 16 kHz PCM chunks over WebSocket to `apps/voice-server/` (Python `faster-whisper` 1.x, `small.en` default, running on the VPS behind Caddy at `wss://voice.<domain>`, auth via Better Auth session).
- Intent matching over the command manifest (`input/command-registry`): normalise transcript → match against command titles, keywords and user keymap aliases with a fuzzy scorer; disambiguate with a spoken/visible chooser when top two scores are close; argument extraction for simple slots (person names via the mention source, status values, numbers, dates via `chrono-node` 2.x).
- Dictation mode: inserts text at the caret in any `<input>`, `<textarea>` or Tiptap editor (`realtime/collab-text`) through a `DictationTarget` adapter; spoken punctuation ("comma", "new line"), auto-capitalisation, undo of the last utterance.
- UI: `VoiceButton` (push-to-talk with `mod+shift+v` and hold-space in spatial/TV mode), listening indicator with waveform, live partial transcript chip, confirmation toast "Ran: Assign to Bo"; entry in the command palette ("Start dictation").
- Privacy: microphone permission flow with explanation, visible indicator whenever audio is captured, no audio stored, transcripts logged only with an explicit tenant setting (`voice.logTranscripts`), Whisper server keeps nothing on disk.

Out: wake words, text-to-speech responses, natural-language questions to Claude (that belongs to future assistant work), non-English models beyond configuration.

**Spec**

- Backend selection: `WebSpeech` if `window.SpeechRecognition || webkitSpeechRecognition` exists and the tenant allows cloud recognition (Chrome sends audio to Google); otherwise or if the tenant sets `voice.backend: 'self-hosted'`, use Whisper. Setting lives in tenant settings (`data-layer/core-entities`).
- Command matching: score = 0.6 × token similarity (Jaro-Winkler on normalised title/keywords) + 0.4 × phonetic match (`double-metaphone`); threshold 0.75; exactly one candidate above threshold runs immediately; several within 0.05 open the chooser; none → toast "Did not catch a command" with the transcript.
- Registry contract: commands opt in with `voice: { phrases?: string[], confirm?: boolean }`; destructive commands (`confirm: true`) require "yes" or a click.
- Whisper protocol: `{ type: 'start', lang, sampleRate }`, binary PCM frames every 250 ms, `{ type: 'partial'|'final', text, ts }`; server VAD (Silero) segments utterances; end-to-end partial latency under 800 ms on the VPS CPU with `small.en`.
- Audio capture via `AudioWorklet` at 16 kHz mono; Tauri mobile needs microphone entitlements added in `app-shell/tauri-mobile` capabilities.
- Accessibility: listening state announced; everything voice can do is also possible by keyboard; the indicator uses icon, text and motion (motion disabled under reduced motion).

**Definition of done**

- "Open inbox", "create record", "assign to Bo" and "mark done" run correctly on the sample pages in Chrome (Web Speech) and Firefox (Whisper); demo video attached.
- Dictation into a form field and a Tiptap comment with spoken punctuation works; Playwright tests inject transcripts through a `MockBackend` at 375 and 1280 px, screenshots of indicator and chooser attached.
- Vitest tests for normalisation, scoring thresholds, slot extraction and punctuation handling.
- `apps/voice-server` deployed with `/healthz`, metrics, and a load check of 20 concurrent streams.
- Security review confirms no audio persistence and correct auth on the WebSocket.
- Docs `docs/platform/input/voice.md` (backend matrix, privacy statement text); changelog; Linear comment with links.

**Edge cases**

- Noisy environment yields garbage partials: only finals trigger commands; partials are display-only.
- Homophones ("Bo" vs "Beau" among members): chooser lists both with avatars.
- Microphone permission denied: button shows a disabled state with instructions; never re-prompt in a loop.
- Network drops mid-dictation with Whisper: buffered audio up to 10 s is sent on reconnect; beyond that, the user is told what was lost.
- Web Speech stops after ~60 s silence in Chrome: auto-restart while push-to-talk is held.
- Command matched while a Dialog is open but the command is out of scope: refused with "Not available here".

**Dependencies**

- `input/command-registry` (manifest, execution, `voice` contract), `realtime/collab-text` (dictation target), `identity/better-auth` (WebSocket auth), `app-shell/tauri-mobile` (mic entitlements), `data-layer/core-entities` (tenant settings), `input/keymaps` (aliases). Deployed by Forge patterns from `realtime/yjs-server`.

**Agent**

Builder: Nova, with Forge (Ops Runner) deploying the Whisper server. Reviewer: Sentinel (Security Auditor for audio privacy and auth, Edge Case Hunter for noisy input).

**Size**

M: two backends and a server, but each piece is small and the matching logic is testable offline.
