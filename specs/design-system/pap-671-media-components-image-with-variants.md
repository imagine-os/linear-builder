---
identifier: "PAP-671"
title: "Media components: Image with variants and blur-up, FilePreview for images, PDF, video, audio and office fallbacks, and an accessible Lightbox with zoom and swipe"
project: "design-system"
projectName: "Design System"
phase: "P2"
type: "Build"
priority: 3
surfaces: ["Customer"]
milestone: "Themable per tenant with docs"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-37", "PAP-154", "PAP-237", "PAP-652"]
blocks: ["PAP-137"]
key: "r4/design-system/media-preview-and-lightbox"
url: "https://linear.app/paperos/issue/PAP-671/media-components-image-with-variants-and-blur-up-filepreview-for"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:29.013Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: "2026-09-30"
cycle: null
---

# PAP-671: Media components: Image with variants and blur-up, FilePreview for images, PDF, video, audio and office fallbacks, and an accessible Lightbox with zoom and swipe

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Attachment cells (PAP-339), the record attachments tab (PAP-333) and screenshot annotation (PAP-137) each need to show a file bigger than a thumbnail. Ship one `Image`, one `FilePreview` and one `Lightbox` on PAP-37's variants so previews behave and announce the same way everywhere.

**Scope**

In: `packages/ui/src/media/{Image,FilePreview,Lightbox}.tsx` with `meta.ts` spec ids and stories; PDF via the browser viewer in an iframe with a download fallback; video and audio via native elements with tokens-styled controls; office and unknown types via an icon card with download.

Out: upload (specialised inputs `FileUpload`), ink annotation layer (PAP-157), image editing beyond crop (specialised inputs), a custom PDF renderer.

**Spec**

* `Image { fileId | src, alt, variant: 'sm'|'md'|'lg'|'original', aspectRatio?, fit, blurUp, loading }`: picks the PAP-37 variant URL, shows a blurred `sm` placeholder while `md|lg` loads, reserves space by `aspectRatio` to avoid layout shift, `alt` required (`decorative` prop for empty alt), error fallback icon.
* `FilePreview { file }` switches on MIME: images through `Image`, `application/pdf` in a sandboxed iframe (`sandbox="allow-scripts allow-same-origin"` only when same-origin signed URL) with a `Download` button and page count from metadata when available, `video/*` and `audio/*` with native controls and captions track support, everything else as a card (icon by type, name, size, Download and Open).
* `Lightbox { items, index, onClose }`: PAP-237 `Dialog` full-screen, arrows and swipe (PAP-154 `useSwipe`) between items, `PinchZoomView` (mobile gesture components) for images with `+`/`-` keys on desktop, caption from `file.name` and alt, item counter announced ("2 of 5"), download and open-in-new-tab actions, focus trap and return, `Escape` closes, reduced motion disables slide.
* Signed URLs minted per request (PAP-37) are used as-is and refreshed on 403 by a retry hook; previews never embed raw storage URLs.
* Sizes and chrome use tokens; RTL flips arrow semantics.

**Interface contract**

Provides: components with spec ids `ui.image`, `ui.filePreview`, `ui.lightbox`; `useSignedUrl(fileId, variant)`; MIME switch table. Consumes: Dialog, Tooltip (PAP-237), file rows, variants and signed URLs (PAP-37), `useSwipe` (gesture recognisers issue) and `PinchZoomView` (mobile gesture components, soft: zoom buttons only until it lands), `Icon` (PAP-68). Consumed by PAP-339 attachment cells and editor, PAP-333 attachments tab, PAP-137 screenshot annotation viewer, PAP-131 comment attachments.

**Definition of done**

* Three components merged with stories (image states, each preview type, lightbox with five mixed items); `play` tests for lightbox keyboard navigation and focus return; `vitest-axe` clean.
* Screenshots at 375, 768, 1280 light and dark; `docs/design/media.md`; changelog; Linear comment on PAP-339 and PAP-333.

**Test plan**

* Unit: variant selection; MIME switch; signed URL refresh on 403; counter announcement text; aspect ratio reservation.
* Interaction: arrows and swipe change items; Escape returns focus to the thumbnail; PDF iframe sandbox attributes asserted.
* E2E: none (Storybook; consumers cover flows).

**Demo**

Reviewer opens Storybook `Media/Lightbox`, arrows through an image, a PDF and a video, pinches the image on the touch viewport, presses Escape and sees focus return. Under one minute.

**Edge cases**

* Variant still `pending` (PAP-37 processing): blur-up placeholder with a spinner, `file.ready` event swaps it.
* PDF blocked by CSP in an embed context: download card fallback.
* Video without captions: warning in dev, `aria-describedby` notes it.
* 1,000 attachments in a lightbox: items lazy, only neighbours preloaded.

**Dependencies**

PAP-237 (hard), PAP-37 (hard), PAP-154 children (hard for swipe; keyboard-only until then). Soft: PAP-68. Blocks PAP-137 viewer; PAP-339 and PAP-333 adopt the lightbox softly (their milestones are earlier).

**Agent**

Builder: Iris (Component Crafter). Reviewer: Sentinel (Visual Inspector).

**Size**

S: half a session.
