---
identifier: "PAP-823"
title: "Files import from Google Drive, Dropbox and OneDrive: folder picker, folder-to-docs and attachments mapping, hash dedupe, resumable transfer within storage quotas"
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
blockedBy: ["PAP-37", "PAP-347", "PAP-815"]
blocks: []
key: "r4/migration/drive-dropbox-files-import"
url: "https://linear.app/paperos/issue/PAP-823/files-import-from-google-drive-dropbox-and-onedrive-folder-picker"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:20:05.837Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-823: Files import from Google Drive, Dropbox and OneDrive: folder picker, folder-to-docs and attachments mapping, hash dedupe, resumable transfer within storage quotas

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Build M

**Goal**

Deferred to v0.2 by the Execution Schedule (NJ-14 stop-loss 09-27 can reinstate). Not claimable before 10-01.

Businesses keep contracts, photos and spreadsheets in a cloud drive, not in a database. Bringing folders into PaperOS files and docs, linked to records where a naming convention allows, is the migration step every vertical shares and none of the importers covers.

**Scope**

In: `connectors/{gdrive,dropbox,onedrive}/` via the connections issue (Google via `googleapis`, Dropbox SDK, Microsoft Graph); discover as a folder tree with counts and sizes; stream files with resumable download to PAP-37 multipart upload; mapping options: folder to `docs/imported/<source>/<path>` for Markdown and Google Docs (exported as Markdown through the provider), everything else to `file` rows with folder path kept as tags; record linking rule `<Table>/<record key>/...` attaching files to matching records through the PAP-164 attachment type; hash dedupe (`sha256`) against existing files; quota check against PAP-178 `storageGb` before start; Google Sheets in a folder offered to the PAP-200 connector.

Out: two-way file sync, permissions mirroring, Office document conversion beyond Google Docs to Markdown.

**Spec**

* Transfers stream provider to storage without buffering; 10 GB attachment limit per run from PAP-347 applies; resumable by file.
* Shared drives and shortcuts followed once; cycles detected.
* Files over the tenant's remaining quota are listed in dry run and the run refuses until scoped down.

**Interface contract**

Provides: three connectors, folder picker step, `docs` and `files` mapping modes, record-linking rule, dedupe report section. Consumes: framework (PAP-347, PAP-348, PAP-349), connections, storage (PAP-37), docs import path (PAP-128), attachments (PAP-164), entitlements (PAP-178), conformance harness.

**Definition of done**

* Recorded-fixture imports for all three providers (200 files, 3 levels, 20 duplicates) with counts and zero duplicate blobs; resume after a killed transfer; Playwright picker; screenshots at 375, 1024, 1920 light and dark.
* `docs/migration/files.md`; CHANGELOG.

**Test plan**

* Unit: tree walk with shortcuts, dedupe, linking rule parsing, quota arithmetic, Google Docs export mapping.
* E2E: pick two folders from the mocked Drive, map one to docs and one to attachments on `clients`, dry run, commit, open a client record with its files.

**Demo**

Reviewer connects the mocked Drive, picks a folder and sees a client record gain three attachments and a docs tree appear. Under two minutes.

**Edge cases**

* File renamed between dry run and commit: matched by provider id, path updated.
* Provider export limit for large Google Docs: kept as a link with a warning.
* Quota exceeded mid-run: run pauses, owner notified with an upgrade link.

**Dependencies**

Hard: PAP-347, connections issue, PAP-37. Soft: PAP-128, PAP-164, PAP-178, PAP-200, conformance harness.

**Agent**

Builder: Scout (Import Mapper). Reviewer: Sentinel (Security Auditor for tokens, Code Reviewer).

**Size**

M: one session.
