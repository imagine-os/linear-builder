---
identifier: "PAP-643"
title: "Clipboard port: typed copy and paste with a PaperOS MIME payload, plain-text and TSV fallbacks, Tauri clipboard plugin and permission handling"
project: "input"
projectName: "Multi-Input Control & Accessibility"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer"]
milestone: "Keyboard and command system"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-289"]
blocks: ["PAP-132", "PAP-331", "PAP-342"]
key: "r4/input/clipboard-port"
url: "https://linear.app/paperos/issue/PAP-643/clipboard-port-typed-copy-and-paste-with-a-paperos-mime-payload-plain"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:35.179Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-23"
cycle: null
---

# PAP-643: Clipboard port: typed copy and paste with a PaperOS MIME payload, plain-text and TSV fallbacks, Tauri clipboard plugin and permission handling

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Grid ranges (PAP-342), canvas nodes (PAP-132), kanban cards and cross-window drags (PAP-331) all need copy and paste, and each would call `navigator.clipboard` differently. Provide one `ClipboardPort` with a typed PaperOS payload, sensible fallbacks and the Tauri plugin behind it so paste between windows, apps and devices behaves the same everywhere.

**Scope**

In: `packages/input/src/clipboard/{port,web,tauri,payload}.ts`; `ClipboardPort { write(payload), read(): Promise<ClipboardPayload> }`; payload `{ kind, version, items, text, html?, tsv? }` under MIME `web application/x-paperos+json` plus `text/plain` and `text/html`; commands `edit.copy|cut|paste` with `allowInInput: false`; permission and unsupported-browser handling.

Out: rich text clipboard inside Tiptap (PAP-142 owns), file paste to uploads (PAP-37 hook only), OS clipboard history.

**Spec**

* `write(payload)` uses `ClipboardItem` with the custom `web ` MIME when supported (Chromium), else writes `text/plain` (TSV or plain) and stores the typed payload in an in-memory `lastCopied` cache keyed by a hash embedded in the text as a trailing zero-width marker; `read()` prefers the custom MIME, then matches the marker to `lastCopied`, then falls back to parsing `text/plain` as TSV.
* Tauri: `@tauri-apps/plugin-clipboard-manager` adapter reads and writes text and HTML; the typed payload rides in HTML as a `data-paperos-payload` attribute; the same marker scheme covers cross-window paste within one app instance through PAP-145 `WindowBus` `clipboard.sync`.
* Permission: `read()` requires a user gesture; denied or unsupported reads reject with `CLIPBOARD_UNAVAILABLE` and the caller shows a paste field fallback (grid opens a textarea to paste into); Firefox and WebKitGTK paths tested.
* Payload kinds registered with `defineClipboardKind({ kind, schema, toText, fromText? })`: `records` (PAP-342), `canvasNodes` (PAP-132), `cards`; `version` allows upcasting; cut records `write` then run the consumer's delete on successful paste only.
* Security: pasted payloads are validated with Zod before use; HTML is never injected; a payload from another tenant (embedded `tenantId`) is refused with a toast.

**Interface contract**

Provides: `ClipboardPort`, `useClipboard()`, `defineClipboardKind`, `ClipboardPayload` (in `contract-input`), commands `edit.copy|cut|paste`, `PasteFallbackField`. Consumes: commands (PAP-289), Tauri plugin capability (PAP-19, PAP-260 for mobile), `WindowBus` (PAP-145, soft), `Zod` schemas from consumers. Consumed by PAP-342 (TSV ranges become the `records` kind), PAP-331 (cross-window transfer fallback), PAP-132, PAP-167.

**Definition of done**

* Copy and paste of grid ranges between two tabs and between the web app and a Tauri window recorded; fallback field proven on Firefox; screenshots of the fallback at 375 and 1280.
* `docs/platform/input/clipboard.md`; changelog; Linear comment on PAP-342 and PAP-132 with the kind registration recipe.

**Test plan**

* Unit: payload encode and decode with marker; kind registry validation; TSV fallback parse (quotes, newlines); tenant refusal; version upcast hook.
* Integration: Playwright Chromium grants clipboard permissions and round-trips the custom MIME; Firefox project exercises the marker fallback; Tauri Linux smoke via `tauri-driver`.
* E2E: copy three grid rows, paste into a second tab's grid (typed), paste into a textarea (TSV), paste a spreadsheet range into the grid (parsed), deny permission and use the fallback field.

**Demo**

Reviewer copies a range in `/demo/grid`, pastes it into a second window as typed records and into a plain text field as TSV, then denies clipboard permission and pastes through the fallback. Under two minutes.

**Edge cases**

* Payload over 1 MB: text carries a reference id and the full payload stays in `lastCopied` (same session only), documented.
* Cut then paste fails validation: nothing deleted.
* Paste of `text/html` from Excel: parsed as TSV via the HTML table.
* Clipboard read on iOS Safari without gesture: fallback field.

**Dependencies**

PAP-289 (hard), PAP-19 (soft: the Tauri adapter lands after the web adapter). Soft: PAP-145, PAP-260. Blocks PAP-342, PAP-331, PAP-132.

**Agent**

Builder: Nova (Product Systems Engineer) with Forge (Tauri Smith). Reviewer: Sentinel (Security Auditor).

**Size**

S: half a session.
