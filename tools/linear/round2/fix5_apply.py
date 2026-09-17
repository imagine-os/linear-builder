"""FIX-5: make the issue-cap ask visible (PAP-91 -> Needs Justin, comment on PAP-5) and fold the
12 hard dependencies on pending issues into the citing issues as work packages (Plan B).
Idempotent through the changes file; --dry writes previews to _fix5_preview/ and touches nothing."""
import json, os, re, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
KEY = os.environ.get("LINEAR_API_KEY", "placeholder")
DRY = "--dry" in sys.argv
CH = "changes-fix-FIX-5 issue-cap-needs-justin-plan-b.json"
ch = json.load(open(CH)) if os.path.exists(CH) else {
    "fix": "FIX-5 issue-cap-needs-justin-plan-b", "startedAt": "2026-09-17T06:40Z",
    "issuesUpdated": [], "stateChanges": [], "comments": [], "documentsUpdated": [],
    "relationsCreated": [], "created": [], "localFilesEdited": [], "notes": []}
def save():
    json.dump(ch, open(CH, "w"), indent=1)

def gql(q, v=None):
    for attempt in range(6):
        body = json.dumps({"query": q, "variables": v}).encode()
        req = urllib.request.Request("https://api.linear.app/graphql", data=body,
                                     headers={"Authorization": KEY, "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.load(r)
        except urllib.error.HTTPError as e:
            txt = e.read().decode()
            if e.code == 429 or "RATELIMITED" in txt:
                print("rate limited, sleeping 60s"); time.sleep(60); continue
            print("HTTP", e.code, txt[:800]); sys.exit(1)
        time.sleep(0.3)
        if d.get("errors"):
            if any(er.get("extensions", {}).get("code") == "RATELIMITED" for er in d["errors"]):
                print("RATELIMITED, sleeping 60s"); time.sleep(60); continue
            print("GQL errors:", json.dumps(d["errors"])[:2000]); sys.exit(1)
        return d["data"]
    sys.exit("retries exhausted")

NEEDS_JUSTIN = "b8037cb1-0718-412f-b913-82b5e4f19555"
TARGETS = ["PAP-5", "PAP-91", "PAP-198", "PAP-187", "PAP-180", "PAP-174", "PAP-114",
           "PAP-200", "PAP-202", "PAP-203", "PAP-204", "PAP-206", "PAP-191", "PAP-193"]
q = "{ " + " ".join(f'i{n}: issue(id: "{k}") {{ id identifier title description updatedAt state {{ id name }} }}'
                    for n, k in enumerate(TARGETS)) + " }"
live = {v["identifier"]: v for v in gql(q).values()}
json.dump(live, open("_fix5_live_at_apply.json", "w"), indent=1)

def must(text, old, new, who):
    if old not in text:
        print(f"ANCHOR MISSING in {who}: {old[:120]!r}"); sys.exit(1)
    return text.replace(old, new, 1)

def drop_footer_if_clean(text, who):
    """Remove the '**Pending issues**' footer when no bracketed pending key remains."""
    if re.search(r"\\?\[[a-z0-9-]+/[a-z0-9/-]+\\?\]", text):
        return text
    text2 = re.sub(r"\n+\*\*Pending issues\*\*\n\n[^\n]*(\n(?!\*\*)[^\n]*)*\s*$", "\n", text)
    if text2 != text:
        print(f"  {who}: removed pending-issues footer (no bracket keys remain)")
    return text2.rstrip() + "\n"

NEW = {}

# ---------------------------------------------------------------- PAP-91 (NJ-1 section, DoD line)
NJ1 = """**Needs Justin — NJ-1: upgrade the Linear workspace plan**

Upgrade the Linear workspace plan (Basic is enough) so ~165 specified issues can be created; until then the plan runs on the 275 that exist. Reply `/approve` on this issue.

* Why: every `issueCreate` since 2026-09-17 04:20Z returns `USAGE_LIMIT_EXCEEDED` (free-plan cap; team PAP holds 275 active issues). About 165 fully specified issues (Goal through Size) wait in the twelve "Round 2 pending issues" documents: children of PAP-96, PAP-101, PAP-104, PAP-110, PAP-119, PAP-120, PAP-124; 22 collab, realtime and input; 48 tables, business-core and growth; 29 migration and libraries; 14 app-shell, data-layer and forge gaps; 11 security; 4 contracts; 8 golden path; `agents/runtime-sandbox` and `agents/session-observability`. 49 live issues cite them as `[project/key]`.
* Nothing waits on the answer (Plan B, applied 2026-09-17 in round-2 FIX-5): the 12 hard dependencies on pending issues were folded into the citing issues as work packages. `migration/test-accounts` is now PAP-198 work package 2 (its sign-ups are a separate Needs Justin ask, NJ-13, filed from PAP-198); `gap/growth/consent-centre` is PAP-187 work package 0 (PAP-191 and PAP-193 depend on it there); `gap/business-core/recurring-dunning` is PAP-180 work package 4 (PAP-174 no longer cites it); `spec-builder/spec-versioning` is an explicit non-goal of PAP-114, which ships only a `migrate/` skeleton. No Dependencies section in a live issue names a pending key as a hard dependency any more.
* On `/approve` (plan upgraded): the session that reads the reply creates, in this order and nothing else first, (1) `agents/runtime-sandbox` (P0 safety) and (4) `agents/session-observability` via `round2/agent2/create_new.py`, (2) PAP-96's three children and (3) PAP-104's four children via the same script, then the rest by phase with `round2/agent3/create_issues.py`, `agent4/create_issues.py`, `agent5/create_issues.py`, `agent6/create_issues.py`, `apply_golden_path.py` and `create_contracts.py`, and adds the `blocks` relations each document lists. Run them only after round-2 FIX-6 (duplicate pending entries) is finished; every script is idempotent on title-in-project and the four folded keys above are skipped (`round2/folded-into-live-issues.json`). Then move this issue back to Ready for Claude.
* On `/reject <reason>`: the plan stays at 275 issues; the pending documents remain the spec of record for the uncreated work, and the builder of each parent builds its work packages on branches `<parent>/wp<n>-<slug>` as the documents describe. Move this issue back to Ready for Claude.

This issue sits in Needs Justin for NJ-1 only. The configuration work below has no human dependency and is claimable the moment the issue returns to Ready for Claude, so a `/approve` or `/reject` is all it needs.

"""
t = live["PAP-91"]["description"]
if not t.startswith("**Needs Justin"):
    t = NJ1 + t
t = must(t, "* Changelog entry and a Linear comment with the diff table before and after.",
         "* Changelog entry and a Linear comment with the diff table before and after.\n"
         "* NJ-1 answered on this issue: workspace plan upgraded (and the create order above started) or Justin declined.", "PAP-91 DoD")
NEW["PAP-91"] = t

# ---------------------------------------------------------------- PAP-5 comment
PAP5_COMMENT = """**Needs Justin — NJ-1: upgrade the Linear workspace plan** (filed on PAP-91, which now sits in Needs Justin)

Upgrade the Linear workspace plan (Basic is enough) so ~165 specified issues can be created; until then the plan runs on the 275 that exist. Reply `/approve` on PAP-91.

Every `issueCreate` since 2026-09-17 04:20Z returns `USAGE_LIMIT_EXCEEDED` (free-plan cap, 275 active issues). The uncreated work is fully specified in the twelve "Round 2 pending issues" documents and in `round2/*/pending-issues*.json`. Nothing waits on the decision: the 12 hard dependencies on pending issues were folded into PAP-198 (work package 2, importer test accounts), PAP-187 (work package 0, consent centre), PAP-180 (work package 4, recurring invoices and dunning) and PAP-114 (spec versioning declared out of scope, `migrate/` skeleton only). On `/approve` the pending issues are created in the order PAP-91 lists (`agents/runtime-sandbox` first); on `/reject <reason>` the parents build the work packages on branches as the documents describe. Either reply returns PAP-91 to Ready for Claude."""

# ---------------------------------------------------------------- PAP-198 (work package 2 = migration/test-accounts)
WP2 = """**Work package 2: importer test accounts and fixture workspaces (was the pending issue `migration/test-accounts`, folded in on 2026-09-17, round-2 FIX-5)**

Create the external state every migration integration test assumes and no other issue provisions: a PaperOS demo Airtable base, a Notion test workspace, a ClickUp workspace, a Stripe test-mode account, a QuickBooks Online sandbox company, access to the Xero demo company and a Google Cloud OAuth app for Sheets and Drive, each seeded with the fixture content work package 1 produces, with credentials stored where CI and agents can reach them. Build it on branch `PAP-198/wp2-test-accounts` after work package 1 (the nine sheets, matrix and fixtures) is In Review, and report it in a comment on this issue.

* Seed scripts `packages/import/fixtures/seed/<source>.ts` populate each workspace from the anonymised fixtures (Airtable: 8 tables, relations, lookups, rollups, 3 formulas, 40 attachments, 6 views; Notion: 3 databases, 25 pages 4 deep, 30 images, inline database, synced block; ClickUp: 3 lists, 150 tasks, subtasks, 5 custom fields, 40 comments, 10 attachments; Stripe: 50 customers, 3 products, 40 subscriptions, 120 invoices, 10 refunds; QuickBooks: sandbox chart plus 30 journals). Seeding is idempotent: rerunning updates rather than duplicates (each API's upsert or a stable external key). Every workspace name starts with `PaperOS Test`, contains only fictional data and carries a banner doc saying so.
* Secrets: names registered in the PAP-17 env schema (`AIRTABLE_TEST_PAT`, `NOTION_TEST_TOKEN`, `CLICKUP_TEST_TOKEN`, `STRIPE_TEST_KEY`, `QBO_TEST_CLIENT_ID|SECRET|REALM`, `XERO_TEST_CLIENT_ID|SECRET`, `GOOGLE_TEST_CLIENT_ID|SECRET`), values in the Forgejo and GitHub secret stores following PAP-48 conventions and in the Scout bot's vault; tokens belong to the Scout bot user where possible so rotation is one place. No value in the repo (the PAP-80 secret scan passes).
* `docs/migration/test-accounts.md`: what exists, who owns the login, how to reseed, token rotation dates. Xero has no persistent sandbox: use the demo company and pin recorded fixtures because it resets monthly. The Google OAuth app stays in testing mode with test users listed; the consent screen is not submitted for verification in this build.
* Weekly `import-fixtures-health.yml` workflow runs each connector's `discover` against the real account and posts drift (counts changed, token expired, "no access") as a comment on this issue; `pnpm fixtures seed <source>` and `pnpm fixtures health` are the commands.
* Interface: the integration tests of PAP-200, PAP-202, PAP-203, PAP-204 and PAP-206 read only the env names above and skip with `skipped: no-credentials` when they are unset; their recorded-fixture tests must pass regardless, so those issues are not blocked by this work package.
* Edge cases: Airtable free tier lacks attachment API access (Team trial, cost noted in the ask below); Notion integration not granted to a page (health lists it as "no access"); Stripe fixtures avoid test clocks so counts stay stable; QuickBooks sandbox resets after inactivity (reseed step documented); Google testing-mode refresh tokens expire after 7 days (health warns 2 days before); a provider consent-screen change fails the workflow loudly, never silently green.
* Done when: all seven accounts exist and `pnpm fixtures health` reports green counts for each; seed scripts committed and rerunnable with the counts above; secrets present in both forges' stores; docs page merged; CHANGELOG entry; Linear comment listing counts per source. Tests: Vitest for the seed scripts against recorded API responses (idempotence on the second run); health workflow dry run on recorded responses, then one live run once credentials land; manual check of each workspace banner.

**Needs Justin — NJ-13: importer test-account sign-ups (only a human can do these)**

The builder who claims this issue posts the list below as a comment on the day it is claimed, with the defaults, and moves this issue to Needs Justin only when work package 1 is In Review and work package 2 waits on nothing but the sign-ups. Justin replies `/approve` (defaults) or edits the list; the builder then finishes work package 2. Waiting on sign-ups is the long part, so file it on day one.

1. Airtable: create a workspace `PaperOS Test`, start a Team trial (attachment API needs it; if it lapses, document the plan cost or accept UI-export fixtures) and issue a personal access token with `data.records:read|write`, `schema.bases:read|write` scoped to that workspace.
2. Notion: create workspace `PaperOS Test`, an internal integration, and share the root test page with it.
3. ClickUp: free workspace `PaperOS Test`; personal API token from Settings > Apps.
4. Stripe: enable test mode on the existing account (already NJ-10 for PAP-177); a restricted key with read and write on customers, products, subscriptions, invoices and refunds.
5. QuickBooks Online: developer account, one sandbox company; app keys (client id, secret) and the sandbox realm id.
6. Xero: developer account; the demo company is enough, no paid org.
7. Google Cloud: project `paperos-test`, OAuth client (web) in testing mode with the Scout bot address as a test user, Sheets and Drive APIs enabled (also NJ-10 for PAP-224 and PAP-200).

Default if no reply by 2026-09-24: proceed with Stripe, Google and ClickUp (already needed elsewhere or free), record the others as `skipped: no-credentials` and keep the recorded-fixture path as the only test for Airtable, Notion, QuickBooks and Xero.

"""
t = live["PAP-198"]["description"]
t = must(t, "Out: connectors, mapping UI, sources beyond the list.",
         "* Work package 2 (below): the test accounts and fixture workspaces those sheets and fixtures seed, formerly the pending issue `migration/test-accounts`.\n\n"
         "Out: connectors, mapping UI, sources beyond the list, production customer accounts, live-mode keys.", "PAP-198 scope")
t = must(t, "* Fixtures are the seed content for `[migration/test-accounts]` (pending issue, spec in the project document), so counts match its numbers:",
         "* Fixtures are the seed content for work package 2 (test accounts), so counts match its numbers:", "PAP-198 spec")
t = must(t, "\n**Interface contract**\n", "\n" + WP2 + "**Interface contract**\n", "PAP-198 wp2 insert")
t = must(t, "* CHANGELOG entry; Linear comment linking the index and notifying PAP-199, PAP-202, PAP-203, PAP-204, PAP-206.",
         "* CHANGELOG entry; Linear comment linking the index and notifying PAP-199, PAP-202, PAP-203, PAP-204, PAP-206.\n"
         "* Work package 2 done as listed above, or its NJ-13 comment posted and the default (recorded fixtures only) applied after 2026-09-24.", "PAP-198 DoD")
t = must(t, "None; ready now. Blocks PAP-199 (interface design) and `[migration/test-accounts]` (seed content). Informs every importer.",
         "None; ready now. Blocks PAP-199 (interface design). Work package 2 gates only the live integration tests of PAP-200, PAP-202, PAP-203, PAP-204 and PAP-206, which skip with `skipped: no-credentials` until it lands; soft for work package 2: PAP-17 (env schema), PAP-48 (secret conventions), PAP-80 (secret scan). Informs every importer.", "PAP-198 deps")
t = must(t, "Researched by Scout (Import Mapper). Reviewed by Atlas for completeness and Quill for the docs template.",
         "Researched by Scout (Import Mapper); work package 2 built by Scout with Forge (Ops Runner) for the secret stores, sign-ups by Justin (NJ-13). Reviewed by Atlas for completeness, Quill for the docs template and Sentinel (Security Auditor) for work package 2.", "PAP-198 agent")
t = must(t, "M: nine sources at 45 minutes plus fixtures and the matrix.",
         "M: nine sources at 45 minutes plus fixtures and the matrix (work package 1); work package 2 is S of scripting, the waiting on sign-ups is the long part.", "PAP-198 size")
NEW["PAP-198"] = t

# ---------------------------------------------------------------- PAP-200/202/203/204/206 (test-accounts -> PAP-198 WP2)
WP2REF = "PAP-198 work package 2 (importer test accounts; integration tests read only its env names and skip with `skipped: no-credentials` when unset)"
t = live["PAP-200"]["description"]
t = must(t, "PAP-199 (hard). PAP-37, PAP-57, PAP-165 (soft), `[migration/test-accounts]` for the live Sheets test.",
         f"PAP-199 (hard). PAP-37, PAP-57, PAP-165 (soft); {WP2REF} for the live Sheets test only.", "PAP-200 deps")
t = must(t, "live against the `[migration/test-accounts]` Google app.", "live against the Google OAuth app from PAP-198 work package 2 when `GOOGLE_TEST_CLIENT_ID` is set, otherwise `skipped: no-credentials`.", "PAP-200 test")
NEW["PAP-200"] = t

t = live["PAP-202"]["description"]
t = must(t, "PAP-199 (hard), PAP-201, PAP-164, PAP-161, PAP-198, `[migration/test-accounts]` (integration). Soft: PAP-171, PAP-168, PAP-37.",
         f"PAP-199 (hard), PAP-201, PAP-164, PAP-161, PAP-198 (fixtures). Soft: PAP-171, PAP-168, PAP-37; {WP2REF} for the live Airtable run.", "PAP-202 deps")
t = t.replace("`[migration/test-accounts]`", "PAP-198 work package 2 (test accounts)")
NEW["PAP-202"] = t

t = live["PAP-203"]["description"]
t = must(t, "PAP-199 and PAP-128 (hard), PAP-202 WP2 (shared pass), PAP-201, PAP-164, `[migration/test-accounts]`. Soft: PAP-142, PAP-37.",
         f"PAP-199 and PAP-128 (hard), PAP-202 WP2 (shared pass), PAP-201, PAP-164. Soft: PAP-142, PAP-37; {WP2REF} for the live Notion run.", "PAP-203 deps")
t = t.replace("`[migration/test-accounts]`", "PAP-198 work package 2 (test accounts)")
NEW["PAP-203"] = t

t = live["PAP-204"]["description"]
t = must(t, "PAP-199 and PAP-100 (hard). PAP-201, PAP-164, PAP-37, PAP-102, `[migration/test-accounts]`. Coordinate with PAP-101 on `pm_external_ref`.",
         f"PAP-199 and PAP-100 (hard). PAP-201, PAP-164, PAP-37, PAP-102; {WP2REF} for the live ClickUp run. Coordinate with PAP-101 on `pm_external_ref`.", "PAP-204 deps")
t = t.replace("`[migration/test-accounts]`", "PAP-198 work package 2 (test accounts)")
NEW["PAP-204"] = t

t = live["PAP-206"]["description"]
t = must(t, "PAP-199 and PAP-179 (hard). PAP-175, PAP-177, PAP-180, PAP-183, PAP-187, PAP-201, `[migration/test-accounts]`.",
         f"PAP-199 and PAP-179 (hard). PAP-175, PAP-177, PAP-180, PAP-183, PAP-187, PAP-201; {WP2REF} for the live Stripe, QuickBooks and Xero runs.", "PAP-206 deps")
t = t.replace("`[migration/test-accounts]`", "PAP-198 work package 2 (test accounts)")
NEW["PAP-206"] = t

# ---------------------------------------------------------------- PAP-187 (work package 0 = gap/growth/consent-centre)
WP0 = """**Work package 0: consent and marketing compliance centre (was the pending issue `gap/growth/consent-centre`, folded in on 2026-09-17, round-2 FIX-5)**

Numbered 0 because it defines the consent semantics this schema stores; build it after the tables above on branch `PAP-187/wp0-consent-centre`, open the PR as soon as `canContact` and `consent.record` exist, and report it in a comment on this issue. PAP-191 (hard, suppression) and PAP-193 (consent writes) import from that branch and are not blocked by its merge. Replaces three partial implementations (this issue stores it, PAP-191 checks it, PAP-193 writes it) with one: a consent record per contact and channel, a shared suppression list, a public preference and unsubscribe centre, double opt-in, and the rule set that decides whether a message may go out under GDPR, CAN-SPAM and TCPA.

* Tables: `consent_record (contact_id, channel: email|sms|push, purpose: marketing|transactional|product_updates, status: granted|denied|pending_double_opt_in|withdrawn, source, evidence jsonb { ip_hash, user_agent_class, form_id, text_shown, timestamp }, version, granted_at, withdrawn_at)`, append-only with the current row per `(contact, channel, purpose)` exposed through a view; `suppression_entry (tenant_id, kind: email|phone|domain, value_hash, reason: unsubscribe|complaint|hard_bounce|manual|legal, source, created_at)`, global per tenant across sequences, notifications and forms, `suppression.check(values[])` batched; `consent_purpose`. `crm_contact.consent jsonb` becomes a denormalised cache of the current rows.
* `canContact(contactId, channel, purpose)` returns `{ ok, reason }` combining consent, suppression, `do_not_contact`, SMS quiet hours (TCPA) and the purpose rules: transactional allowed without marketing consent, marketing requires `granted`, SMS marketing requires explicit opt-in with evidence.
* Public routes with a signed per-contact token and no login: `/c/:token` preference centre (per channel and purpose toggles, "unsubscribe from all", tenant branding via PAP-74), `/u/:token` one-click unsubscribe (RFC 8058 POST), double opt-in confirm route; changes write consent records and suppression entries. Double opt-in: forms (PAP-169, PAP-193) create `pending_double_opt_in` and send the confirm email through PAP-136 core; unconfirmed after 30 days expires.
* `List-Unsubscribe` and `List-Unsubscribe-Post` headers supplied to PAP-191 and PAP-136 through `unsubscribeHeaders(contactId, channel)`; STOP keywords from PAP-191 write suppression here. Exports: per-contact consent history for DSAR (PAP-221) and a tenant compliance report dataset `growth.compliance`. Staff pages under `_app/marketing/compliance`.
* Interface: `canContact`, `consent.record|withdraw|history`, `suppression.add|check|list`, `preferenceLink(contactId)`, `unsubscribeHeaders`, events `consent.changed`, `suppression.added`. Consumes PAP-136 core, PAP-169 and PAP-193 (write through `consent.record`), PAP-267 rate limiting on the public routes, PAP-74 theming, PAP-43 jobs. Consumed by PAP-191 (hard), PAP-193, PAP-136, PAP-221 exports and PAP-180 work package 4 (reminder consent).
* Edge cases: contact merged (records re-pointed, most restrictive status wins); withdrawal then re-grant (new record with fresh evidence, history intact); suppressed domain refuses every contact at it; leaked token shows no PII beyond a masked email and rotates via `preferenceLink`; `reason: legal` suppression cannot be removed by staff.
* Done when: unit decision table for `canContact` (channel by purpose by status by suppression), token signing and expiry, double opt-in expiry and header generation green; integration: an unsubscribe POST suppresses across a running PAP-191 sequence and a PAP-136 digest in the same test, a form submission with consent goes `pending_double_opt_in` then `granted` on confirm, STOP writes suppression, history export matches records; Playwright: open the preference link, toggle SMS marketing off, confirm the sequence skips the SMS step, one-click unsubscribe from an email header; screenshots at 320, 375, 768, 1024, 1280, 1536, 1920 in light and dark for the preference centre (two brands) and the staff compliance page, axe clean; `docs/growth/consent.md` with the rule table per jurisdiction; CHANGELOG; Linear comment with a live preference link on the demo tenant. Demo: open a contact's preference link from the CRM page, turn off marketing email, enrol the contact in a sequence and watch `canContact` refuse with the reason, then one-click unsubscribe from a test email and see the suppression entry; under two minutes.

"""
t = live["PAP-187"]["description"]
t = must(t, "Out: UI (PAP-189), sequences, segment evaluation (PAP-195), importers, the consent centre (\\[gap/growth/consent-centre\\] owns preference and suppression semantics; this issue only stores `consent jsonb`).",
         "Also in: work package 0 (below), the consent and marketing compliance centre, formerly the pending issue `gap/growth/consent-centre`, folded into this issue on 2026-09-17 because PAP-191 and PAP-193 depend on it hard and Linear cannot create it (issue cap).\n\n"
         "Out: UI (PAP-189), sequences, segment evaluation (PAP-195), importers, cookie banners for the marketing site (PAP-221 owns privacy pages), consent for agent data access (PAP-60).", "PAP-187 scope")
t = must(t, "\n**Interface contract**\n", "\n" + WP0 + "**Interface contract**\n", "PAP-187 wp0 insert")
t = must(t, "Consumed by PAP-189 to PAP-197, PAP-202, PAP-206.",
         "Consumed by PAP-189 to PAP-197, PAP-202, PAP-206; work package 0 additionally provides `canContact`, `consent.*`, `suppression.*`, `preferenceLink`, `unsubscribeHeaders`, the public routes `/c/:token` and `/u/:token` and dataset `growth.compliance` to PAP-191, PAP-193, PAP-136, PAP-221 and PAP-180 work package 4.", "PAP-187 contract")
t = must(t, "* CHANGELOG; ADR `docs/adr/00xx-crm-model.md`; Linear comment linking doc and migration.",
         "* CHANGELOG; ADR `docs/adr/00xx-crm-model.md`; Linear comment linking doc and migration.\n* Work package 0 done as listed above (its PR may merge after the schema PR; the issue closes when both are merged).", "PAP-187 DoD")
t = must(t, "* Consent revoked mid-sequence: checked at send time by PAP-191.",
         "* Consent revoked mid-sequence: checked at send time by PAP-191 through work package 0's `canContact`.", "PAP-187 edge")
t = must(t, "Blocks PAP-189, PAP-190, PAP-191, PAP-193, PAP-194, PAP-195, PAP-197, \\[gap/growth/consent-centre\\].",
         "Blocks PAP-189, PAP-190, PAP-191, PAP-193, PAP-194, PAP-195, PAP-197. Work package 0 additionally needs PAP-43 (jobs, hard for double opt-in expiry), PAP-136 core, PAP-169, PAP-74, PAP-267 (soft); PAP-191 and PAP-193 import its `canContact` and `consent.record` from the `PAP-187/wp0-consent-centre` branch, so open that PR early.", "PAP-187 deps")
t = must(t, "Builder: Beacon (CRM Builder) with Forge (Schema Wright) on migrations and RLS. Reviewer: Sentinel (Security Auditor), Atlas for fit with finance and PM models.",
         "Builder: Beacon (CRM Builder) with Forge (Schema Wright) on migrations and RLS; work package 0 by Beacon with Quill on the jurisdiction rule table. Reviewer: Sentinel (Security Auditor, also for the public routes and PII of work package 0; Edge Case Hunter), Atlas for fit with finance and PM models.", "PAP-187 agent")
t = must(t, "M: twelve tables whose shape drives five downstream issues and two importers.",
         "L: twelve tables whose shape drives five downstream issues and two importers (M), plus work package 0, a decision function, two public pages and append-only tables (M). The Type label stays Spec because the schema contract is the deliverable other issues wait on; work package 0 is Build work carried here only because of the issue cap.", "PAP-187 size")
t = drop_footer_if_clean(t, "PAP-187")
NEW["PAP-187"] = t

# ---------------------------------------------------------------- PAP-191 / PAP-193 (consent-centre -> PAP-187 WP0)
t = live["PAP-191"]["description"]
t = must(t, "PAP-187 (hard), \\[gap/growth/consent-centre\\] (hard for suppression; stub with `do_not_contact` if absent), PAP-43 (hard),",
         "PAP-187 (hard, including its work package 0, the consent centre: hard for suppression and `canContact`; import from branch `PAP-187/wp0-consent-centre` if not merged and stub with `do_not_contact` only if that branch does not exist yet), PAP-43 (hard),", "PAP-191 deps")
t = t.replace("the suppression list from \\[gap/growth/consent-centre\\] are checked at send time", "the suppression list from PAP-187 work package 0 (`canContact`) are checked at send time")
t = t.replace("suppression and preference API (\\[gap/growth/consent-centre\\])", "suppression and preference API (PAP-187 work package 0)")
t = t.replace("\\[gap/growth/consent-centre\\]", "PAP-187 work package 0 (consent centre)")
NEW["PAP-191"] = t

t = live["PAP-193"]["description"]
t = must(t, "PAP-136 core, PAP-155, \\[gap/growth/consent-centre\\] (soft), Webflow account (Needs Justin).",
         "PAP-136 core, PAP-155, PAP-187 work package 0 (consent centre; soft: write consent through its `consent.record` when it exists, else store on `crm_contact.consent jsonb` and migrate), Webflow account (Needs Justin).", "PAP-193 deps")
t = t.replace("write consent through \\[gap/growth/consent-centre\\] when the consent box is ticked", "write consent through PAP-187 work package 0 (`consent.record`, double opt-in when the tenant requires it) when the consent box is ticked")
t = t.replace("`crm_lead` and consent (PAP-187, \\[gap/growth/consent-centre\\])", "`crm_lead` and consent (PAP-187 and its work package 0)")
t = t.replace("\\[gap/growth/consent-centre\\]", "PAP-187 work package 0 (consent centre)")
t = drop_footer_if_clean(t, "PAP-193")
NEW["PAP-193"] = t

# ---------------------------------------------------------------- PAP-180 (work package 4 = gap/business-core/recurring-dunning)
WP4 = """**Work package 4: recurring tenant invoices and dunning (was the pending issue `gap/business-core/recurring-dunning`, folded in on 2026-09-17, round-2 FIX-5)**

Give a clinic, agency or landlord billing its own customers monthly a recurring path in this document model: schedules that generate and send invoices, a dunning ladder with reminders and optional late fees, and payment retry for saved cards on the connected account. Tenant-to-customer billing, distinct from platform subscriptions (PAP-177). Build it after the three children on branch `PAP-180/wp4-recurring-dunning` (M) and report it in a comment on this issue.

* Tables `fin_recurring_schedule (party_id, template_document_id, cadence: weekly|monthly|quarterly|yearly, day_of_period, next_run_at, timezone, auto_send, auto_charge, status: active|paused|ended, ends_at?, occurrences?)` and `fin_dunning_policy (name, steps jsonb [{ offset_days, action: remind|late_fee|retry|escalate, template_id?, fee: { pct | fixed_minor, cap_minor } }], default)` with per-party override; the template is a draft document whose lines are copied with `{{period.start}}` and `{{period.end}}` substitutions.
* Generation job (PAP-43, hourly) creates the invoice from the template, issues it, sends it when `auto_send`, charges the saved method when `auto_charge` through a PaymentIntent on the connected account (PAP-181) or platform test mode; idempotent per `(schedule_id, period_start)`. The daily dunning job walks the steps for overdue documents and records each action as `crm_activity` and `document.event`; late fees create a `fee` line on a new document or the original (setting) posting through the rules above; retries follow Stripe smart-retry windows, capped at four; the pay page offers "save for future invoices" (Stripe SetupIntent) stored as `stripe_payment_method_id` on `fin_customer`, never raw.
* Interface: `recurring.create|update|pause|resume|preview`, `dunning.policies.*`, `dunning.run(documentId)`, events `recurring.generated`, `dunning.step_applied`, dataset `finance.recurring`, `/finance/recurring` page and per-party schedule editor, portal "Upcoming" list. Automations (PAP-174) may call `recurring.pause|resume`; escalations notify finance via PAP-136 core; reminder consent through PAP-187 work package 0 (soft: a party opted out of reminders still receives fees, sends nothing, and is flagged for manual contact).
* Edge cases: 31st-of-month cadence uses the last day of shorter months; template edits apply to future occurrences only; a payment during the retry window cancels pending retries; a restricted connected account skips charges but still generates invoices with bank instructions.
* Done when: unit tests for next-run computation across month ends and DST, substitution, idempotency key, late-fee maths with caps and retry windows; integration on a Stripe test clock: a monthly schedule generates three invoices over three simulated months, the second is left unpaid and receives remind, late fee and retry on the right days, a paused schedule skips a period, a saved-card charge succeeds and fails (`4000000000000341`); Playwright: create a schedule from an invoice, preview the next three dates, open the portal upcoming list, edit the dunning policy; screenshots at 375, 1024, 1920 in three themes for the schedule editor, dunning policy and portal list; `docs/finance/recurring-dunning.md`; CHANGELOG; Linear comment with demo link. Demo: turn a seeded invoice into a monthly schedule, preview three dates, advance the test clock a month, see the generated invoice, advance past due and watch the reminder and late fee appear in the activity; under two minutes. Out: usage-based tenant billing, proration, contracts and e-signature.

"""
t = live["PAP-180"]["description"]
t = must(t, "Out: recurring invoices and dunning (\\[gap/business-core/recurring-dunning\\]), inventory, multi-language templates beyond locale formatting.",
         "Work package 4 (below, M, built after the children on its own branch): recurring invoices and dunning, formerly the pending issue `gap/business-core/recurring-dunning`, folded into this issue on 2026-09-17 because Linear cannot create it (issue cap).\n\n"
         "Out: inventory, multi-language templates beyond locale formatting, usage-based tenant billing, proration, contracts and e-signature.", "PAP-180 scope")
t = must(t, "\n**Interface contract**\n", "\n" + WP4 + "**Interface contract**\n", "PAP-180 wp4 insert")
t = must(t, "Consumed by PAP-183, PAP-185, PAP-196 statements, \\[gap/business-core/recurring-dunning\\].",
         "Consumed by PAP-183, PAP-185, PAP-196 statements and work package 4 (which adds `recurring.*`, `dunning.*`, `finance.recurring` on top).", "PAP-180 contract")
t = must(t, "* All three children Done.", "* All three children Done and work package 4 merged.", "PAP-180 DoD")
t = must(t, "PAP-181 and PAP-182 (optional), PAP-136 core, PAP-64. Blocks PAP-182, PAP-183, \\[gap/business-core/recurring-dunning\\].",
         "PAP-181 and PAP-182 (optional), PAP-136 core, PAP-64. Work package 4 additionally needs PAP-43 (hard, jobs and test clock), PAP-177 Stripe client, PAP-181 (optional) and PAP-187 work package 0 (soft, reminder consent); PAP-174 automations call `recurring.pause|resume` (soft, PAP-174 does not depend on it). Blocks PAP-182, PAP-183.", "PAP-180 deps")
t = must(t, "L, split into three M children.", "L, split into three M children plus work package 4 (M) on branch `PAP-180/wp4-recurring-dunning`.", "PAP-180 size")
NEW["PAP-180"] = t

# ---------------------------------------------------------------- PAP-174 (drop recurring-dunning; fix garbled footer)
t = live["PAP-174"]["description"]
t = must(t, "Consumed by PAP-208, PAP-195, PAP-180 and \\[gap/business-core/recurring-dunning\\].",
         "Consumed by PAP-208, PAP-195 and PAP-180 (its work package 4, recurring invoices and dunning, exposes `recurring.pause|resume` as automation actions; soft, nothing here waits on it).", "PAP-174 deps")
t = re.sub(r"Their specs live in the project document\(s\) .*? once the workspace plan is upgraded\.",
           "Their specs live in the project document [tables](<https://linear.app/paperos/document/round-2-pending-issues-tables-24-86486d9b99cc>) and they are created as issues by `round2/agent4/create_issues.py` once the workspace plan is upgraded (see PAP-91, NJ-1).", t, count=1, flags=re.S)
NEW["PAP-174"] = t

# ---------------------------------------------------------------- PAP-114 (spec-versioning -> explicit non-goal + migrate/ skeleton)
t = live["PAP-114"]["description"]
t = must(t, "the validator CLI (PAP-115); versioning tooling (\\[spec-builder/spec-versioning\\]); i18n of copy (\\[spec-builder/spec-i18n\\]).",
         "the validator CLI (PAP-115); i18n of copy (\\[spec-builder/spec-i18n\\]); versioning tooling, explicitly: codemods, `x-deprecated` metadata, rule `SPEC_DEPRECATED`, `paperos-spec migrate` and the 300-fixture rehearsal are not built here. They were the pending issue `spec-builder/spec-versioning`, which Linear cannot create (issue cap, PAP-91 NJ-1) and which nothing in this build requires; this issue ships only the `migrate/` skeleton in Spec so that follow-up has a fixed home when it is created.", "PAP-114 scope")
t = must(t, "* YAML anchors and merge keys resolved before validation; errors carry `line` and `col` of the merged document.",
         "* YAML anchors and merge keys resolved before validation; errors carry `line` and `col` of the merged document.\n"
         "* `packages/spec/src/migrate/` skeleton (the whole versioning deliverable of this issue): `versions.ts` exporting `CURRENT_SPEC_VERSION = 1` and `SPEC_VERSIONS = [{ version: 1, schema: PageSpecSchema, codemodsFrom: {} }]`; an exported `Codemod` interface type (`{ id, description, apply(doc: YAML.Document): Change[] }`) with no implementations; `migrateSpec(doc, to = CURRENT_SPEC_VERSION)` that returns the document unchanged for `specVersion: 1` (missing treated as 1 with the warning above) and throws a `SpecIssue` with code `SPEC_UNSUPPORTED_VERSION` for any other version; `docs/spec/versioning.md` stub naming the follow-up scope (version registry, codemod helpers `renameKey|moveKey|mapEnum|wrapValue`, `paperos-spec migrate --dry-run`, `x-deprecated` and `SPEC_DEPRECATED`, weekly 300-fixture rehearsal). Unit tests: identity for v1, error for v2, `x-*` keys untouched.", "PAP-114 spec")
t = must(t, "Blocks PAP-115, PAP-116, PAP-117, PAP-119, PAP-120, PAP-121, PAP-123, PAP-124, PAP-132, PAP-85, PAP-74, \\[spec-builder/spec-versioning\\].",
         "Blocks PAP-115, PAP-116, PAP-117, PAP-119, PAP-120, PAP-121, PAP-123, PAP-124, PAP-132, PAP-85, PAP-74. The future spec-versioning tooling issue depends on this `migrate/` skeleton; nothing live depends on that tooling.", "PAP-114 deps")
NEW["PAP-114"] = t

# ---------------------------------------------------------------- previews
os.makedirs("_fix5_preview", exist_ok=True)
for k, v in NEW.items():
    open(f"_fix5_preview/{k}.md", "w").write(v)
    left = sorted(set(re.findall(r"\\?\[[a-z0-9-]+/[a-z0-9/-]+\\?\]", v)))
    print(f"{k}: {len(live[k]['description'])} -> {len(v)} chars; remaining bracket keys: {left}")
open("_fix5_preview/PAP-5.comment.md", "w").write(PAP5_COMMENT)
if DRY:
    print("dry run: nothing written to Linear"); sys.exit(0)

# ---------------------------------------------------------------- apply issue updates (batched, idempotent)
done = {u["identifier"] for u in ch["issuesUpdated"]}
todo = [k for k in NEW if k not in done]
for i in range(0, len(todo), 4):
    batch = todo[i:i + 4]
    parts, vars_ = [], {}
    for n, k in enumerate(batch):
        inp = {"description": NEW[k]}
        if k == "PAP-91" and live["PAP-91"]["state"]["id"] != NEEDS_JUSTIN:
            inp["stateId"] = NEEDS_JUSTIN
        vars_[f"in{n}"] = inp
        parts.append(f'u{n}: issueUpdate(id: "{live[k]["id"]}", input: $in{n}) {{ success issue {{ identifier state {{ name }} }} }}')
    qm = "mutation(" + ", ".join(f"$in{n}: IssueUpdateInput!" for n in range(len(batch))) + ") { " + " ".join(parts) + " }"
    res = gql(qm, vars_)
    for n, k in enumerate(batch):
        r = res[f"u{n}"]
        print("update", k, r["success"], r["issue"]["state"]["name"])
        if r["success"]:
            ch["issuesUpdated"].append({"id": live[k]["id"], "identifier": k, "fields": list(vars_[f"in{n}"].keys()), "chars": len(NEW[k])})
            if "stateId" in vars_[f"in{n}"]:
                ch["stateChanges"].append({"id": live[k]["id"], "identifier": k, "from": live[k]["state"]["name"], "to": r["issue"]["state"]["name"]})
    save()

# ---------------------------------------------------------------- comment on PAP-5
if not any(c["issue"] == "PAP-5" for c in ch["comments"]):
    res = gql("mutation($input: CommentCreateInput!) { commentCreate(input: $input) { success comment { id url } } }",
              {"input": {"issueId": live["PAP-5"]["id"], "body": PAP5_COMMENT}})
    c = res["commentCreate"]
    print("comment PAP-5", c["success"], c["comment"]["url"])
    if c["success"]:
        ch["comments"].append({"issue": "PAP-5", "issueId": live["PAP-5"]["id"], "id": c["comment"]["id"], "url": c["comment"]["url"], "subject": "NJ-1"})
    save()
print("issues done")
