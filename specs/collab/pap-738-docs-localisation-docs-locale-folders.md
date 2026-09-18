---
identifier: "PAP-738"
title: "Docs localisation: `docs/<locale>/` folders with fallback to the default locale, language switcher, translation status page and a translation skill hook"
project: "collab"
projectName: "In-App Collaboration & Knowledge"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Customer"]
milestone: "Knowledge surfaced everywhere"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-27", "PAP-128", "PAP-504"]
blocks: []
key: "r4/collab/docs-i18n"
url: "https://linear.app/paperos/issue/PAP-738/docs-localisation-docslocale-folders-with-fallback-to-the-default"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:33.747Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-738: Docs localisation: `docs/<locale>/` folders with fallback to the default locale, language switcher, translation status page and a translation skill hook

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 (stretch pool; NJ-14 can reinstate). Not claimable before 10-01.

'One-size-fits-all software that adapts to every type of business' includes businesses that do not read English. PAP-27 localises UI strings and PAP-375 spec copy; customer docs and changelog entries have no locale path. Add locale folders with fallback, a switcher and a status page the translation skill (PAP-27) writes into.

**Scope**

In: loader change in `packages/collab/docs/` resolving `docs/<locale>/<path>.mdx` before `docs/<path>.mdx` with a `translated: false` banner on fallback; frontmatter `sourceHash` and `translatedFrom` for staleness; `LocaleSwitcher` in the docs header bound to PAP-27 negotiation; `/_app/docs/translations` status page (per locale: translated, stale, missing) and `pnpm docs:i18n status|extract --locale es`; changelog entries (PAP-133) gain `locale` with the same fallback; `llms.txt` per locale. Out: machine translation itself (PAP-27 skill), runtime docs (PAP-379) translation UI.

**Spec**

* Resolution order: requested locale, tenant default locale (PAP-126), app default; `hreflang` links on public pages.
* Staleness: a translated page whose `sourceHash` differs from the current source is `stale`; lint warns; the status page lists it first.
* Search (PAP-138) indexes each locale as its own document with a `locale` facet; customers search their locale first.
* Extraction writes a task file `docs/.generated/i18n-tasks.json` the PAP-27 translation skill consumes; a translated file is a normal PR.
* RTL locales get `dir="rtl"` on the article and mirrored TOC, reusing PAP-27's RTL flip.

**Interface contract**

Provides: locale-aware loader, `LocaleSwitcher`, status page and CLI, frontmatter fields, `i18n-tasks.json`. Consumes: docs loader and lint (PAP-128), locale negotiation and translation skill (PAP-27), business profile default locale (PAP-126), search facets (PAP-138), changelog rows (PAP-133). Consumed by: PAP-727 (per-locale `llms.txt`), PAP-363 landing pages.

**Definition of done**

* Five template docs translated to `es` (fixture), fallback banner on the rest, switcher works, status page counts match; `hreflang` present on public pages.
* Screenshots at 375 and 1280 in light and dark for `en` and `es`; axe clean; `docs/collab/docs-i18n.md`; CHANGELOG entry.

**Test plan**

* Unit: resolution order, staleness detection, task extraction, `hreflang` generation.
* Integration: search facet per locale; changelog fallback.
* E2E (Playwright): switch locale, see the translated page, open an untranslated one and see the banner.

**Demo**

Switch to Español, open the getting-started doc in Spanish, open an untranslated page and read the fallback banner, open the status page. Under one minute.

**Edge cases**

* Locale folder with a file the source no longer has: listed as orphan on the status page.
* Mixed-locale search results: locale facet defaults to the viewer's locale with a toggle.
* Tenant default locale not enabled in the app: falls back to app default with a settings hint.

**Dependencies**

Hard: PAP-128, PAP-27. Soft: PAP-126, PAP-138, PAP-133, PAP-379. Deferred: v0.2.

**Agent**

Builder: Quill (Changelog Scribe). Reviewer: Sentinel (Visual Inspector for RTL).

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 1 round-4 file key in this description to Linear identifiers: `r4/collab/agent-readable-docs` = PAP-727.
