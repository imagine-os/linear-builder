---
identifier: "PAP-824"
title: "Contacts import from Google Contacts, Outlook People and vCard files into the CRM with dedupe and consent-neutral defaults"
project: "migration"
projectName: "Migration & Import Tools"
phase: "P2"
type: "Build"
priority: 4
surfaces: ["Staff"]
milestone: "Airtable, Notion, ClickUp importers"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-347", "PAP-790"]
blocks: []
key: "r4/migration/contacts-import-google-outlook-vcard"
url: "https://linear.app/paperos/issue/PAP-824/contacts-import-from-google-contacts-outlook-people-and-vcard-files"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:29:50.570Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 2
dueDate: null
cycle: null
---

# PAP-824: Contacts import from Google Contacts, Outlook People and vCard files into the CRM with dedupe and consent-neutral defaults

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build S

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

The smallest businesses keep customers in their phone. Google Contacts, Outlook People and a `.vcf` export are the on-ramp before any CRM; a small connector set over the framework makes that a two-minute job with the consent centre kept honest.

**Scope**

In: `connectors/{gcontacts,mscontacts,vcard}/`: People API and Graph via the connections issue, vCard 3.0 and 4.0 parser (`vcard4` or hand-rolled with fixtures) for files and multi-card exports; mapping to `crm_contact` and `crm_company` (organisation field), phones E.164 by default region, emails normalised, photos to PAP-37; labels and groups to `crm_tag`; dedupe via PAP-821 when present, else PAP-201 email key; consent defaults: imported contacts get no marketing consent (`consent_record` untouched) and a `source: import:<system>` note; preset in the CSV importer for Google and Outlook CSV exports too.

Out: calendar and mail (other issues), continuous sync (scheduled resync issue applies).

**Spec**

* Multiple emails and phones: primary to the contact fields, the rest into `custom.alt_emails|alt_phones` arrays.
* Duplicate people across providers: dedupe pass or email key merges them into one contact with all tags.
* The importer never writes `granted` consent; a banner in the wizard explains why marketing sends need opt-in.

**Interface contract**

Provides: three connectors, vCard parser, CSV presets `google-contacts`, `outlook-contacts`, mapping to CRM. Consumes: framework (PAP-347 to PAP-349), CRM schema (growth child), connections issue, dedupe issue (soft), PAP-201, PAP-37, consent centre (read-only expectation).

**Definition of done**

* Fixture vCard set (50 cards, both versions, photos, groups) and recorded People and Graph responses import with correct counts and E.164 phones; consent rows remain zero; Playwright; screenshots at 375, 1024 light and dark.
* `docs/migration/contacts.md`; CHANGELOG.

**Test plan**

* Unit: vCard parsing edge cases (folded lines, quoted-printable, multiple TEL types), phone normalisation by region, tag mapping.
* E2E: upload a `.vcf`, map, dry run, commit, open the contacts grid with tags applied.

**Demo**

Reviewer uploads a 50-card vCard, sees phones normalised and groups as tags, commits and opens the CRM. Under one minute.

**Edge cases**

* Card without a name: uses email or phone as the display name with a report line.
* Non-Latin names: kept as given; trigram dedupe handles transliteration poorly and says so.
* Photo over 5 MB: skipped with a note.

**Dependencies**

Hard: PAP-347, PAP-790. Soft: connections issue, dedupe issue, PAP-201, PAP-37.

**Agent**

Builder: Scout (Import Mapper). Reviewer: Sentinel (Edge Case Hunter).

**Size**

S: half a session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/growth/crm-schema-routers-page-specs` = PAP-790, `r4/migration/import-duplicate-detection-and-merge-preview` = PAP-821.
