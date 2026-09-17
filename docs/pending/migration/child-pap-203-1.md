---
key: "child/PAP-203/1"
title: "Notion block converter to MDX and Tiptap JSON: all block types, media upload before URL expiry, internal link rewriting"
project: "migration"
parent: "PAP-203"
phase: "P2"
type: "Build"
priority: 2
size: "M"
surfaces: ["Staff"]
milestone: "Airtable, Notion, ClickUp importers"
intendedState: "Backlog"
blockedBy: []
blocks: []
source: "round2/agent5/pending-issues.json"
linearDocument: "https://linear.app/paperos/document/round-2-pending-issues-migration-20-6cb063cc1be6"
identifier: "PAP-418"
status: "created"
createdAt: "2026-09-17"
---

# Notion block converter to MDX and Tiptap JSON: all block types, media upload before URL expiry, internal link rewriting

**Goal**

Convert Notion page content without flattening it: every block type to MDX for the docs engine and to Tiptap JSON for editable documents, media uploaded within the one-hour URL window, and links between imported pages rewritten to their new slugs.

**Scope**

In: `mapping/notion-blocks.ts` with `toMdx(blocks)` and `toTiptap(blocks)` covering paragraph, headings, lists (bulleted, numbered, to-do, toggle), quote, callout, code, divider, table, image/file/video/pdf, bookmark, embed, equation, column lists (flattened), synced blocks, child pages, child databases (embedded view reference), mentions, link previews; annotation marks; `rewriteLinks(pass)` using PAP-201; 5 MB body cap with sectioning.

Out: connector (child 1), tree picker (child 3).

**Spec**

* Callouts become `<Callout>`; equations KaTeX; colours dropped and counted.
* Images fetched immediately and stored via PAP-37; external URLs kept unless "copy external media".
* Toggles deeper than level 4 flattened with a note.

**Interface contract**

Provides: `toMdx(blocks, ctx): { mdx, report }`, `toTiptap(blocks, ctx): { doc, report }`, `ConversionReport { unsupported: [{ type, count }], droppedColours, unmatchedPeople }`, final pass `rewriteLinks`. Consumes: child 1 body refs, PAP-128 MDX component set, PAP-142 Tiptap schema (soft: MDX only until merged), PAP-201 lookups. Reused by PAP-204 for ClickUp docs later.

**Definition of done**

* Every block type converts with MDX and Tiptap snapshot fixtures; 30 images from the test workspace stored.
* Two side-by-side Notion vs PaperOS renders attached.
* Block coverage table in `docs/migration/notion.md`.

**Test plan**

* Vitest: one fixture per block type for both targets, marks, nested lists, link rewriting, body splitting at 5 MB.
* Integration: 25 nested pages converted; broken-link check over the output finds zero internal 404s.
* Visual: rendered doc screenshots at 375 and 1280 in light and dark compared to Notion.

**Demo**

Reviewer runs the converter CLI on the fixture export, opens the generated MDX in the docs engine and sees callouts, a table, an image and a link to a sibling page that resolves. Under two minutes.

**Edge cases**

* Synced block whose original is unshared: copy of visible content with a note.
* Video hosted on YouTube: kept as embed link, not downloaded.
* Code block language unknown to the highlighter: plain fenced block.

**Dependencies**

Child 1 (hard), PAP-128 (hard), PAP-142 (soft), PAP-201, PAP-37. Blocks child 3.

**Agent**

Built by Scout (Import Mapper) with Quill. Reviewed by Sentinel (Edge Case Hunter, Visual Inspector) and Nova for Tiptap validity.

**Size**

M
