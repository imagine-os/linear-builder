---
identifier: "PAP-275"
title: "OIDC auth source preparation, upgrade procedure and Forgejo runbook"
project: "forge"
projectName: "Version Control & Forge Independence"
phase: "P0"
type: "Docs"
priority: 1
surfaces: ["Developer"]
milestone: "Forgejo live and mirrored"
state: "Backlog"
parent: "PAP-45"
children: []
blockedBy: ["PAP-274"]
blocks: ["PAP-54", "PAP-276"]
key: "child/PAP-45/20"
url: "https://linear.app/paperos/issue/PAP-275/oidc-auth-source-preparation-upgrade-procedure-and-forgejo-runbook"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T13:56:11.952Z"
model: "claude-opus-5"
effort: "high"
estimate: 2
dueDate: "2026-09-20"
cycle: null
---

# PAP-275: OIDC auth source preparation, upgrade procedure and Forgejo runbook

**Model / Effort:** Opus 5 (`claude-opus-5`) / high — security-sensitive title keyword: auth

**Goal**

Prepare the Better Auth OIDC login path in Forgejo (auth source `paperos`, auto-registration, group mapping to teams) so PAP-57 can switch it on with one command, and write `docs/runbooks/forgejo.md` covering deploy, upgrade with pre-snapshot, backup, restore, SSO switch and monitoring.

**Scope**

In: `ops/forgejo/oidc.sh` creating or updating the auth source via `forgejo admin auth add-oauth`, expected issuer and scopes documented, team mapping JSON, runbook, metrics scrape hint for PAP-40.

Out: the identity provider itself (PAP-57).

**Spec**

* Issuer `https://app.PAPEROS_DOMAIN/api/auth`; scopes `openid email profile groups`; `group_claim_name: groups`; mapping `paperos:staff` to `agents`, `paperos:owner` to `owners`.
* Script idempotent; `--disable` flag for rollback.

**Interface contract**

Provides: auth source name, expected claims, `oidc.sh`. Consumes: stack (child 1). Consumed by PAP-57 (OIDC provider child).

**Definition of done**

* `oidc.sh --dry-run` prints the planned auth source; real run against staging creates a disabled source.
* Runbook merged with all six sections; Sentinel reviews the SSO section.

**Test plan**

* Unit: `bats` for script flags.
* Integration: source appears in admin UI disabled; `--disable` removes login button.
* Docs: `docs:check` link validation.

**Demo**

Reviewer reads the runbook's SSO section, runs `oidc.sh --dry-run` and sees the exact `forgejo admin auth` command that PAP-57 will enable. Under a minute.

**Edge cases**

* Claims missing `groups`: users land in no team; documented.
* Upgrade requiring migration: pre-snapshot step mandatory.

**Dependencies**

Child 1 (hard). Soft: PAP-57, PAP-40.

**Agent**

Written by Forge with Quill. Reviewed by Sentinel (Security Auditor).

**Size**

S
