---
identifier: "PAP-27"
title: "Add internationalisation and localisation: ICU message catalogs, locale negotiation, Intl formatting helpers, RTL layout flip, pseudo-locale testing and an agent translation skill"
project: "app-shell"
projectName: "Universal App Shell & Repo Template"
phase: "P1"
type: "Build"
priority: 2
surfaces: ["Customer", "Developer", "Staff"]
milestone: "Desktop and mobile shells build"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-13", "PAP-66", "PAP-302"]
blocks: ["PAP-126", "PAP-375"]
key: "app-shell/i18n-l10n"
url: "https://linear.app/paperos/issue/PAP-27/add-internationalisation-and-localisation-icu-message-catalogs-locale"
source: "Linear snapshot 2026-09-17T13:11Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-17T13:04:58.278Z"
---

# PAP-27: Add internationalisation and localisation: ICU message catalogs, locale negotiation, Intl formatting helpers, RTL layout flip, pseudo-locale testing and an agent translation skill

**Goal**

Make localisation a template default before pages multiply: ICU message catalogs, locale negotiation, `Intl` helpers, RTL flip, pseudo-locale testing and a translation skill agents run. Retrofitting i18n after 200 pages is the most expensive refactor in this plan, so it lands in P1.

**Scope**

In:

* `packages/i18n`: Lingui 5 with macros `t`, `Trans`, `plural`, `select`; catalogs `apps/web/src/locales/<locale>/messages.po`; `pnpm i18n:extract|compile` wired into Gate 1.
* Locale negotiation: tenant default (PAP-58 setting), user preference (PAP-57 profile), `Accept-Language`, browser; Tauri reads OS locale.
* Helpers `formatNumber`, `formatCurrency`, `formatDate`, `formatRelative`, `formatList`, `formatUnit`, `parseNumber`.
* RTL via CSS logical properties and `dir` on `<html>`; pseudo-locale `en-XA`.
* Translation skill `.claude/skills/translate` producing catalog PRs.

Out: tenant-authored content translation, machine-translation runtime.

**Spec**

* Source strings live in code; catalogs are the only translation store.
* Lint bans `toLocaleString` and `new Intl.*` outside the package.
* Auto-generated message IDs with explicit IDs for reusable terms; CI warns above 2 percent fuzzy entries, fails above 10 percent for enabled locales.
* Catalogs lazy-loaded; `en` runtime under 8 KB gzipped.
* Dates stored UTC; tenant timezone from PAP-58; formatting never guesses.
* `ar` uses Arabic-Indic digits only when the tenant opts in.

**Interface contract**

Provides (from `@paperos/i18n`):

* `useLocale(): { locale, dir, timeZone, currency }`, `LocaleProvider`, macros re-exported from Lingui, `format*` helpers taking `Money = { amountMinor: bigint; currency: string }` from `@paperos/core/money` (the canonical type; JSON wire encoding is a decimal string).
* `parseNumber(input, locale)` used by PAP-164 editors.
* Catalog file convention and `pnpm i18n:*` scripts that PAP-78 runs.
* Skill `translate` in PAP-108 format.

Consumes: tokens per script (PAP-66), tenant settings (PAP-58), user profile (PAP-57); PAP-116 later validates spec strings through the same extractor.

**Definition of done**

* Template renders in `en`, `es`, `ar`, `en-XA` with a switcher; screenshots at 375 and 1280 per locale; `ar` mirrored with no clipping.
* Adding a literal without extracting fails CI (demo PR).
* Translation skill produces an `es` PR that Quill merges.
* Currency and date table across six locales green.
* Pseudo-locale column green in PAP-82; `docs/platform/i18n.md`, ADR, CHANGELOG, Linear comment.

**Test plan**

* Unit: format helpers across `en-US`, `de-DE`, `ar-EG`, `ja-JP`, `hi-IN`, `pt-BR`; plural forms for Arabic and Polish; `parseNumber` with comma and dot decimals.
* Static: lint rule tests for banned `Intl` calls and string concatenation next to JSX text.
* Integration: negotiation order test with tenant, user and header permutations.
* E2E: Playwright switches locale, asserts `dir="rtl"` and no horizontal overflow at 375 in `ar`.
* Visual: four locales at 375 and 1280, light and dark.

**Demo**

Reviewer opens the preview, switches the locale menu to Arabic: layout mirrors, dates and currency reformat; switches to `en-XA` and sees accented, elongated strings revealing any hard-coded text. Under a minute.

**Edge cases**

* Fragment concatenation detected by lint.
* Long German compounds caught by pseudo-locale expansion.
* Mixed direction: `unicode-bidi: isolate` on data spans.
* Tenant changes default locale mid-session: applies at next navigation.
* Locale enabled without a catalog: fall back to `en` with a staff-visible warning.

**Dependencies**

PAP-13, PAP-66 (hard). Soft: PAP-57, PAP-58, PAP-116, PAP-164. Consumed by PAP-126, PAP-179, PAP-191, PAP-207.

**Agent**

Built by Forge (Platform Engineer) with Iris on RTL components. Reviewed by Quill and Sentinel.

**Size**

M: one package, a lint rule and a skill.
