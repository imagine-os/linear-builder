---
identifier: "PAP-654"
title: "Dictation targets and voice UI: DictationTarget adapters for inputs and Tiptap, spoken punctuation, VoiceButton with push-to-talk, listening indicator, chooser and confirmation"
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
blockedBy: ["PAP-142", "PAP-290", "PAP-604", "PAP-653"]
blocks: ["PAP-158"]
key: "r4/input/dictation-targets-and-voice-ui"
url: "https://linear.app/paperos/issue/PAP-654/dictation-targets-and-voice-ui-dictationtarget-adapters-for-inputs-and"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:23.460Z"
model: "claude-sonnet-5"
effort: "high"
estimate: 3
dueDate: "2026-09-30"
cycle: null
---

# PAP-654: Dictation targets and voice UI: DictationTarget adapters for inputs and Tiptap, spoken punctuation, VoiceButton with push-to-talk, listening indicator, chooser and confirmation

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / high — Build M

**Goal**

Second half of PAP-159: what the user sees and types with. Dictation into any field with spoken punctuation and undo, the push-to-talk button and indicator, the chooser when two commands tie, confirmation for risky commands and the palette entry.

**Scope**

In: `packages/input/src/voice/{VoiceProvider,useVoice,DictationTarget,adapters/{input,tiptap},VoiceButton,ListeningIndicator,VoiceChooser}.tsx`; command extension `voice: { phrases?, confirm? }` behaviour; palette entries "Start dictation", "Voice commands help"; settings toggles; docs browser matrix.

Out: backend and matching (sibling), TV hold-space mode (PAP-158 consumes), TTS.

**Spec**

* `DictationTarget { insert(text), deleteLast(n), getContext() }` with adapters for `<input>`/`<textarea>` (selection-aware insert) and `RichTextEditor` (PAP-142 insertion API); spoken punctuation table ("comma", "period", "new line", "question mark", localised via PAP-27); auto-capitalisation after sentence ends; "undo that" removes the last utterance through PAP-641.
* `VoiceButton`: push-to-talk on `mod+shift+v` (hold) or click-to-toggle; states idle, listening, processing, denied, unsupported (tooltip names supported browsers); listening indicator uses icon, text and a waveform (`Presence` from PAP-72, static under reduced motion); partial transcript chip; state announced via PAP-152 announcer.
* Command flow: `final` → `matchCommand` → one candidate runs and toasts "Ran: Open inbox"; several open `VoiceChooser` (a listbox, also keyboard-operable); `confirm: true` commands ask "Say yes or click Confirm"; `needsArgs` opens the palette's argument prompt (PAP-290) pre-filled.
* Dictation mode is entered from the palette or by saying "start dictation" while a target is focused; commands are not matched while dictating except "stop dictation" and "undo that".
* Everything voice does is possible by keyboard; the button hides when `voice.enabled=false`; microphone entitlement for Tauri mobile through PAP-260.

**Interface contract**

Provides: `VoiceProvider`, `useVoice()`, `DictationTarget` and adapters (reused by PAP-158 `SpatialKeyboard`), `VoiceButton`, `ListeningIndicator`, `VoiceChooser`, palette entries, `voice` command extension semantics. Consumes: backend and matcher (sibling), `RichTextEditor` insertion API (PAP-142), palette argument prompts (PAP-290), undo manager (PAP-641, soft), motion presets (PAP-72), announcer (PAP-152), microphone entitlement (PAP-260, soft). Consumed by PAP-158.

**Definition of done**

* "Open inbox", "create record", "assign to Bo" and "mark done" run on the sample pages in Chrome; dictation into a form field and a Tiptap comment with punctuation works; demo video attached.
* Screenshots of indicator, chooser and denied state at 375 and 1280 in three themes; axe clean; `docs/platform/input/voice.md` UI and browser matrix; changelog; Linear comment.

**Test plan**

* Unit: punctuation and capitalisation rules; adapter insert and deleteLast on inputs and a Tiptap doc; mode transitions (idle, listening, dictating); chooser selection.
* Component: `VoiceButton` states with axe; reduced-motion story has no waveform animation.
* E2E: with `MockBackend` injected at 375 and 1280: commands run and toast, chooser appears for near ties, confirmation blocks until "yes", dictation inserts into an input and a comment with "comma" and "new line", "undo that" removes the last utterance, out-of-scope command refused with "Not available here".

**Demo**

Reviewer holds `mod+shift+v`, says "open inbox", releases and watches navigation; clicks into a comment, chooses "Start dictation" and dictates a sentence with punctuation, then says "undo that". Under two minutes.

**Edge cases**

* Permission denied: disabled state with instructions, no re-prompt loop.
* Focus moves during dictation: target follows focus only to another editable; otherwise dictation pauses.
* Noisy finals with low scores: toast with the transcript and a "Search commands" action.
* WebKitGTK (Tauri Linux) lacks `SpeechRecognition`: button shows unsupported; tested.

**Dependencies**

Sibling backend (hard), PAP-142 (hard for the Tiptap adapter; input adapter may land first), PAP-290 (hard, argument prompts). Soft: PAP-641, PAP-72, PAP-152, PAP-260. Blocks PAP-158 (`DictationTarget` reuse).

**Agent**

Builder: Nova (Product Systems Engineer) with Iris on the indicator. Reviewer: Sentinel (Visual Inspector, Edge Case Hunter).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/input/undo-manager` = PAP-641.
