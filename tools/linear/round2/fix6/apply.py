"""FIX-6: de-duplicate the pending-issue documents and JSON files, fix cross-references.
Usage: python3 apply.py [--dry]   (local file edits always run; Linear mutations only without --dry)
Idempotent: every replacement checks its expected count; already-applied replacements are skipped when the
new text is present and the old one is gone."""
import sys, os, re, json, importlib.util
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *
DRY = "--dry" in sys.argv
ch = load_changes()
NOW = "2026-09-17"

class Rep:
    """Collects replacement problems instead of raising, so a dry run reports everything."""
    problems = []
    @staticmethod
    def do(text, old, new, where, count=1):
        n = text.count(old)
        if n == count:
            return text.replace(old, new)
        if n == 0 and new in text:
            return text  # already applied
        Rep.problems.append(f"{where}: expected {count} of {old[:90]!r}, found {n}")
        return text

def doc_form(s):
    """canonical [a/b] -> Linear-escaped \\[a/b\\]"""
    return re.sub(r"(?<!\\)\[([a-z][a-z0-9-]*/[A-Za-z0-9_./-]+)\]", r"\\[\1\\]", s)
def curly_form(s):
    """canonical [a/b] -> {{a/b}} (agent2/agent6 module convention)"""
    return re.sub(r"(?<!\\)\[([a-z][a-z0-9-]*/[A-Za-z0-9_./-]+)\]", r"{{\1}}", s)
def curly_security_only(s):
    return re.sub(r"(?<!\\)\[(security/[A-Za-z0-9_./-]+)\]", r"{{\1}}", s)

def read(p): return open(p, encoding="utf-8").read()
def write(p, s):
    open(p, "w", encoding="utf-8").write(s)
    if p not in ch["filesEdited"]: ch["filesEdited"].append(p)

MERGES = [
 {"dropped": "gap/data-layer/field-encryption", "keptKey": "security/field-encryption", "source": "gaps-pending-0.json / agent0/gaps.py", "reason": "same deliverable; security version cites the Threat Model and adds the leak scanner and AAD binding"},
 {"dropped": "gap/data-layer/platform-dr", "keptKey": "security/platform-dr", "source": "gaps-pending-0.json / agent0/gaps.py", "reason": "same drill; security version adds key escrow, monitoring and measured RPO/RTO"},
 {"dropped": "gap/data-layer/retention-pii", "keptKey": "security/retention-pii", "source": "gaps-pending-0.json / agent0/gaps.py", "reason": "same deliverable; security version owns pii() annotations, retention.yaml and the purge job"},
 {"dropped": "gap/data-layer/tenant-lifecycle (purge half)", "keptKey": "security/retention-pii", "source": "gaps-pending-0.json / agent0/gaps.py", "reason": "hard purge moved; tenant-lifecycle keeps states, quotas and the deletion request flow"},
 {"dropped": "gap/data-layer/event-bus", "keptKey": "contracts/domain-events", "source": "gaps-pending-0.json / agent0/gaps.py", "reason": "contracts version already declares it supersedes the gap"},
 {"dropped": "gap/data-layer/rate-limit-idempotency", "keptKey": "contracts/idempotency-rate-limits", "source": "gaps-pending-0.json / agent0/gaps.py", "reason": "contracts version already declares it supersedes the gap"},
 {"dropped": "gap/forge/template-upgrade", "keptKey": "gp/app-shell/upgrade", "source": "gaps-pending-0.json / agent0/gaps.py", "reason": "both build `paperos upgrade`; golden-path version is richer (ownership manifest, codemods, fleet mode); registry publishing folded in"},
 {"dropped": "collab/notification-core", "keptKey": "PAP-136 (work package 1)", "source": "agent3/pending-issues.json / agent3/new_collab.py", "reason": "PAP-136 owns the notification core as work package 1 after its P1 re-phase; children collab/notifications/* stay parented to PAP-136"},
 {"dropped": "pm-linear/workspace-reconcile", "keptKey": "PAP-91", "source": "agent2/new_pm.py / pm-linear pending document", "reason": "obsolete: PAP-91 and PAP-93 already treat the live workspace as correct"},
 {"dropped": "agents/runtime-sandbox (egress proxy, allowlist, secret injection)", "keptKey": "security/credential-broker; hook policy -> security/agent-deny-list", "source": "agent2/new_agents.py / agents pending document / agent6", "reason": "trio overlap: sandbox keeps container, worktree, CPU/RAM; now blocked by broker and deny list"},
]
DROPPED_KEYS = {"gap/data-layer/field-encryption", "gap/data-layer/platform-dr", "gap/data-layer/retention-pii", "gap/data-layer/event-bus", "gap/data-layer/rate-limit-idempotency", "gap/forge/template-upgrade", "collab/notification-core", "pm-linear/workspace-reconcile"}

# ----------------------------------------------------------------------------------------------------
# 1. gaps-pending-0.json and agent0/gaps.py
# ----------------------------------------------------------------------------------------------------
TL_TITLE_OLD = "Build the tenant lifecycle jobs: hard-delete purge after grace period (export first), archive schema for legal retention, per-tenant storage and row quotas"
TL_TITLE_NEW = "Build the tenant lifecycle: tenant states, deletion request and cancel flow with grace period, archive metadata, per-tenant storage and row quotas (the purge job itself is `security/retention-pii`)"
TL_REPS = [
 ("Own what PAP-33 leaves to \"a separate job\": a `tenant.purge` job that hard-deletes a soft-deleted tenant after a grace period only once a PAP-205 export has completed, an archive path for legal retention, and per-tenant storage and row counters that feed PAP-178's `storageGb` entitlement.",
  "Own the tenant state machine around PAP-33's `deleted_at`: request and cancel deletion with a grace period, the archive metadata kept for legal retention, and per-tenant storage and row counters that feed PAP-178's `storageGb` entitlement. The hard-purge job itself (`tenant.purge`: export first, delete rows, files, docs and keys, tombstone) is owned by `security/retention-pii`; this issue triggers it and displays its progress. Merged: the purge half of this gap moved to `security/retention-pii` on 2026-09-17 (FIX-6)."),
 ("* Job `tenant.purge` (PAP-43): verify export `completed` (PAP-205), snapshot metadata to `tenant_archive` (legal minimum: name, owner email, invoices references, dates), delete rows across every tenant table in dependency order using the PAP-34 table list, delete MinIO objects under the tenant prefix, revoke sessions, emit `tenant.purged`.",
  "* Deletion flow: `requestDeletion` sets `deleted_at`, enqueues the PAP-205 export and schedules `tenant.purge` (`security/retention-pii`) at the end of the grace period; `cancelDeletion` clears it; `tenant_archive` (legal minimum: name, owner email, invoice references, dates) is written before the purge runs."),
 ("Out: billing proration (PAP-177), data export format (PAP-205).",
  "Out: the purge job and tombstone (`security/retention-pii`), billing proration (PAP-177), data export format (PAP-205)."),
 ("* Purge is resumable: progress in `tenant_purge_run` per table; a crash resumes.\n* Audit events for the purge are written to a platform-level (tenant-null) partition and retained.",
  "* Purge progress is read from the `security/retention-pii` job run and shown on the staff usage page; a tenant in `purging` is inaccessible to every principal."),
 ("* Archive rows encrypted with the field-encryption helper.", "* Archive rows encrypted with the `security/field-encryption` helper."),
 ("Provides: tenant states, job `tenant.purge`, tables `tenant_archive`, `tenant_usage`, `tenant_purge_run`, helper `checkQuota`, error `QUOTA_EXCEEDED`, event `tenant.purged`, oRPC `tenants.usage|requestDeletion|cancelDeletion`. Consumes: entities and table list (PAP-33, PAP-34), jobs (PAP-43), export (PAP-205), files (PAP-37), audit (PAP-38), entitlements (PAP-178), event bus (events issue), encryption (field-encryption issue).",
  "Provides: tenant states, tables `tenant_archive`, `tenant_usage`, helper `checkQuota`, error `QUOTA_EXCEEDED`, events `tenant.deletion_requested|deletion_cancelled`, oRPC `tenants.usage|requestDeletion|cancelDeletion`. Consumes: entities (PAP-33), jobs (PAP-43), export (PAP-205), files (PAP-37), audit (PAP-38), entitlements (PAP-178), event bus (`contracts/domain-events`), encryption (`security/field-encryption`), purge job and `tenant.purged` event (`security/retention-pii`)."),
 ("* Demo tenant deleted, exported, grace period fast-forwarded in test, purged: zero rows across all tenant tables and zero objects (harness output).\n* Purge without a completed export refuses (test); paid-history tenant lands in Needs Justin.",
  "* Demo tenant deletion requested, export enqueued, grace period fast-forwarded in test, `tenant.purge` (`security/retention-pii`) invoked once and the state reaches `purged` (harness output).\n* `cancelDeletion` inside the grace period restores `active` (test)."),
 ("* Integration (CI compose): purge on the `demo` seed with a killed worker mid-way resumes and completes; PAP-34 harness confirms zero rows for the tenant.",
  "* Integration (CI compose): request, cancel, re-request; grace expiry invokes the purge job exactly once (idempotency asserted)."),
 ("runs `pnpm jobs:run tenant.purge --tenant <id> --now` with the grace override, and watches the purge run table progress to `purged` while Studio shows the tenant's rows disappear",
  "fast-forwards the grace in test, and watches the state move `deleted` to `purging` to `purged` as the `security/retention-pii` job runs"),
 ("* Tables added later without a tenant column mapping: harness fails the purge dry run.",
  "* Tables added later without a tenant column mapping: the `security/retention-pii` FK-order generator fails the purge dry run; the usage page counts them as unknown."),
 ("PAP-33, PAP-43, PAP-205 (hard). Soft: PAP-37, PAP-38, PAP-178, events issue, field-encryption issue.",
  "PAP-33, PAP-43, PAP-205 (hard). Soft: PAP-37, PAP-38, PAP-178, `contracts/domain-events`, `security/field-encryption`, `security/retention-pii` (purge job)."),
]
RF_REPS = [  # runtime-flags and code-signing prose pointing at dropped gaps
 ("event bus (data-layer events issue, soft)", "event bus (`contracts/domain-events`, soft)"),
 ("PAP-195, data-layer events issue. Consumed by", "PAP-195, `contracts/domain-events`. Consumed by"),
 ("Linux package signing (deferred to the template-upgrade issue)", "Linux package signing (deferred to `gp/app-shell/upgrade`)"),
]

def fix_gaps_pending0():
    p = os.path.join(R2, "gaps-pending-0.json"); d = json.load(open(p))
    keep = []; merged = d.get("merged", [])
    have = {m["key"] for m in merged}
    for it in d["issues"]:
        k = it["key"]
        if k in DROPPED_KEYS:
            if k not in have:
                kept = next(m["keptKey"] for m in MERGES if m["dropped"] == k)
                merged.append({"key": k, "title": it["title"], "status": "merged", "mergedInto": kept, "note": f"Merged into `{kept}` on {NOW} (FIX-6); do not create."})
            continue
        if k == "gap/data-layer/tenant-lifecycle":
            it["title"] = TL_TITLE_NEW if it["title"] == TL_TITLE_OLD else it["title"]
            it["input"]["title"] = it["title"]
            desc = it["input"]["description"]
            for o, n in TL_REPS: desc = Rep.do(desc, o, n, "gaps-pending-0 tenant-lifecycle")
            it["input"]["description"] = desc
            it["note"] = f"Narrowed on {NOW} (FIX-6): the hard-purge job moved to `security/retention-pii`; this issue keeps states, quotas and the deletion request flow."
        if k in ("gap/app-shell/runtime-flags", "gap/app-shell/code-signing"):
            desc = it["input"]["description"]
            for o, n in RF_REPS:
                if o in desc or n in desc: desc = Rep.do(desc, o, n, f"gaps-pending-0 {k}")
            it["input"]["description"] = desc
        keep.append(it)
    d["issues"] = keep; d["merged"] = merged
    d["reason"] = d["reason"].split(" FIX-6:")[0] + f" FIX-6: {len(merged)} entries merged into security/contracts/golden-path specs (see `merged`); tenant-lifecycle narrowed."
    json.dump(d, open(p, "w"), indent=1)
    if p not in ch["filesEdited"]: ch["filesEdited"].append(p)
    # module
    mp = os.path.join(R2, "agent0", "gaps.py"); s = read(mp)
    s = Rep.do(s, TL_TITLE_OLD, TL_TITLE_NEW, "gaps.py tenant-lifecycle title")
    for o, n in TL_REPS + RF_REPS: s = Rep.do(s, o, n, "gaps.py")
    marker = "# FIX-6 (2026-09-17): merged duplicates are filtered out so create_issues.py never creates them."
    if marker not in s:
        s += f"\n\n{marker}\nMERGED = {{\n" + "".join(f"    \"{k}\": \"{next(m['keptKey'] for m in MERGES if m['dropped']==k)}\",\n" for k in sorted(DROPPED_KEYS) if k.startswith("gap/")) + "}\nGAPS = [g for g in GAPS if f\"gap/{g['project']}/{g['slug']}\" not in MERGED]\n"
    write(mp, s)

# ----------------------------------------------------------------------------------------------------
# 2. agent3: notification-core
# ----------------------------------------------------------------------------------------------------
NC_REPS = [
 ("notification rows (notification core) as the main producer", "notification rows (PAP-136 work package 1, the notification core) as the main producer"),
 ("PAP-267, notification core. Consumed by PAP-136", "PAP-267, PAP-136 work package 1 (notification core). Consumed by PAP-136"),
 ("Out: notifications (notification core), screenshot crops (PAP-137).", "Out: notifications (PAP-136 work package 1), screenshot crops (PAP-137)."),
 ("all over the notification core's tables.", "all over the tables of PAP-136 work package 1 (the notification core)."),
 ("`resolvePreferences()` from the notification core,", "`resolvePreferences()` from PAP-136 work package 1 (the notification core),"),
]
def fix_agent3():
    p = os.path.join(R2, "agent3", "pending-issues.json"); d = json.load(open(p))
    out = []
    for it in d:
        if it["key"] == "collab/notification-core": continue
        desc = it["description"]
        for o, n in NC_REPS:
            if o in desc or n in desc: desc = Rep.do(desc, o, n, f"agent3 json {it['key']}")
        it["description"] = desc; out.append(it)
    json.dump(out, open(p, "w"), indent=1)
    if p not in ch["filesEdited"]: ch["filesEdited"].append(p)
    for mod in ("new_collab.py", "new_rt_input.py"):
        mp = os.path.join(R2, "agent3", mod); s = read(mp)
        for o, n in NC_REPS:
            if o in s or n in s: s = Rep.do(s, o, n, f"agent3/{mod}")
        if mod == "new_collab.py":
            marker = "# FIX-6 (2026-09-17): collab/notification-core is merged into PAP-136 work package 1; never create it."
            if marker not in s:
                s += f"\n\n{marker}\nMERGED = {{\"collab/notification-core\": \"PAP-136\"}}\nGAPS = [g for g in GAPS if g[\"key\"] not in MERGED]\n"
        write(mp, s)

# ----------------------------------------------------------------------------------------------------
# 3. agent2: workspace-reconcile (drop) and runtime-sandbox (rewrite)
# ----------------------------------------------------------------------------------------------------
RS_TITLE_OLD = "Build the agent runtime sandbox: per-session container or worktree isolation, egress allowlist, CPU/RAM limits, no production credentials inside the sandbox"
RS_TITLE_NEW = "Build the agent runtime sandbox: per-session container, worktree mount, CPU/RAM/time limits and network isolation with the credential broker's egress proxy as the only route"
RS_DESC = """**Goal**

Give every Claude session a wall it cannot talk its way through: each session runs in a per-session container that mounts only its worktree, has bounded CPU, memory, pids and wall clock, and has no network route except the egress proxy owned by [security/credential-broker]. This issue owns the container, the worktree mount and the resource limits. The proxy, the per-character allowlist and credential injection belong to [security/credential-broker]; the hook policy the image ships belongs to [security/agent-deny-list]. PAP-106 admits its hook is best-effort; this is the isolation it defers to. Split on 2026-09-17 (FIX-6) from a trio that each defined the egress allowlist and the no-secrets rule.

**Scope**

* In: `ops/sandbox/` image and runner (`Dockerfile.session`, `run-session.sh`), `runInSandbox()` in the orchestrator launcher (`launchSession` gains `sandbox: true`), the internal Docker network with the broker proxy as its only route, resource limits by Size, worktree bind mount, orphan sweep, escape probes for filesystem, network route and limits, `docs/agents/sandbox.md`.
* Out: egress proxy container, allowlist generation and credential injection ([security/credential-broker]); deny rules and the PreToolUse hook ([security/agent-deny-list], PAP-106); forge branch protection (PAP-46); VPS provisioning (PAP-25).

**Spec**

* Runtime: rootless Docker (or Podman) on the VPS; image Node 22, git, pnpm, gh, Playwright deps, the PAP-106 hooks and the compiled `agent-deny.json` from [security/agent-deny-list] (the launcher refuses to start a container whose policy digest is stale); read-only root filesystem except `/work` (the worktree bind mount), `/tmp` and the pnpm store cache; `--cap-drop ALL`, `--security-opt no-new-privileges`, seccomp default profile, `--pids-limit 512`, CPU 2, RAM 4 GB, session wall clock 3 h (configurable per Size).
* Network: containers attach to the internal `sandbox` network that has no default route; the only reachable host is the broker egress proxy (`PAPEROS_PROXY=http://egress:3128`, [security/credential-broker]); the sandbox proves the route property (a direct `curl https://example.com` fails at the network layer, not at the proxy). Which hosts the proxy allows per character and which credentials it injects is the broker's concern.
* Environment: the container receives only `broker:*` placeholders and non-secret configuration; the orchestrator's own keys, Postgres superuser, Coolify and sops keys never enter; a probe script asserts on every start that `env` contains no value matching `ghp_|lin_api_|sk-ant-|sk_test_|sk_live_`.
* Worktree: bind-mounted from `/srv/worktrees/<key>`; git pushes go through the proxy, which injects the character's forge token (PAP-48 or default bot, minted by the broker).
* Cleanup: container removed on session end; orphan sweep every 10 minutes; `SandboxHandle.kill` is what PAP-111 `kill` calls.

**Interface contract**

* Provides: `runInSandbox(spec: { worktree, character, env, limits }): SandboxHandle` with `exec`, `kill`, `stats`; image tag `paperos/session:<sha>`; network `sandbox`; events `sandbox.started`, `sandbox.killed`, `sandbox.limit_hit`.
* Consumers: [pm-linear/orchestrator/sessions] (`launchSession` wraps `query()` execution in the container), PAP-106 (hooks run inside), PAP-110 runner (`sandbox: true`), PAP-111 (`kill`), [agents/session-observability] (`stats`).
* Requires: PAP-25 VPS with Docker; [security/credential-broker] proxy image, network name and placeholder contract; [security/agent-deny-list] compiled policy; PAP-104 roster (character to Size and limits).

**Definition of done**

* Probe suite inside a running sandbox: cannot read `/srv/repos` of other issues, cannot reach `postgres:5432`, `coolify` or any host except the proxy, can reach Linear and the forge through the proxy; results table attached.
* No production credential present: `env` dump diffed against the placeholder set in CI.
* Limits enforced: a fork bomb and a 6 GB allocation are killed; timing recorded; a stale policy digest refuses to start (test).
* Orchestrator launches a real session in the sandbox and opens a PR (recording).
* Docs; changelog; Linear comment with table and recording.

**Test plan**

* Unit: limit computation by Size; policy digest check; network spec generation.
* Integration: `ops/sandbox/test/probes.sh` run in CI on a self-hosted runner (PAP-50) against a stub proxy; env-diff assertion.
* e2e: staging session through the sandbox and the real broker proxy.
* No UI.

**Demo**

Run `pnpm sandbox probe --character beacon`: watch a direct `curl https://example.com` fail with no route, a `curl` through the proxy to `api.linear.app` succeed, and `env | grep -c -E 'ghp_|lin_api_|sk-ant-'` print 0. One minute.

**Edge cases**

* Playwright needs Chromium: included in the image; `--shm-size 1g`.
* Session needs a host not on the allowlist: the proxy denies and logs `egress-denied`; the fix is the character's `access[]` in the broker rules, never a sandbox change.
* Docker daemon restart: orphan sweep reattaches or kills; claims released by the orchestrator.
* Disk pressure from images: nightly prune keeps two tags.
* Rootless Docker unavailable: fall back to a dedicated `sandbox` user with cgroups v2 limits and nftables rules that allow only the proxy; documented as degraded; the broker's degraded mode (short-lived tokens in env) applies.
* Broker not yet merged when this starts: build against a stub proxy that allows everything and injects nothing (branch-start rule); the DoD probe that needs real injection waits for the broker.

**Dependencies**

Blocked by PAP-25, [security/credential-broker] (proxy, allowlist, injection) and [security/agent-deny-list] (hook policy shipped in the image). Blocks nothing hard: PAP-106 runs its hooks inside the sandbox once it exists (soft), PAP-96 and [pm-linear/orchestrator/sessions] enable `sandbox: true` when it merges (soft). Soft: PAP-48, PAP-50, PAP-104.

**Agent**

Built by Forge (Ops Runner sub-agent); reviewed by Sentinel (Security Auditor).

**Size**

M (proxy and allowlist moved to the broker)"""

def fix_agent2():
    mp = os.path.join(R2, "agent2", "new_pm.py"); s = read(mp)
    marker = "# FIX-6 (2026-09-17): pm-linear/workspace-reconcile is obsolete (PAP-91 and PAP-93 treat the live workspace as correct); never create it."
    if marker not in s:
        s += f"\n\n{marker}\nMERGED = {{\"pm-linear/workspace-reconcile\": \"PAP-91\"}}\nGAPS = [g for g in GAPS if g[\"key\"] not in MERGED]\n"
    write(mp, s)
    mp = os.path.join(R2, "agent2", "rw_pm.py"); s = read(mp)  # sources of PAP-91/93 descriptions
    s = Rep.do(s, "reconciling issue bodies and estimates ({{pm-linear/workspace-reconcile}}), the contract validator (PAP-93)", "reconciling issue bodies and estimates (not needed: this issue treats the live workspace as correct), the contract validator (PAP-93)", "rw_pm.py PAP-91 out")
    s = Rep.do(s, "PAP-22 (`paperos create` reuses the script), {{pm-linear/workspace-reconcile}}.", "PAP-22 (`paperos create` reuses the script).", "rw_pm.py PAP-91 consumers")
    s = Rep.do(s, "bulk fixes of existing issues ({{pm-linear/workspace-reconcile}}), drafting help", "bulk fixes of existing issues (none planned: PAP-91 treats the live workspace as correct), drafting help", "rw_pm.py PAP-93 out")
    s = Rep.do(s, "Blocked by PAP-91 and {{pm-linear/workspace-reconcile}}. Soft: PAP-97.", "Blocked by PAP-91. Soft: PAP-97.", "rw_pm.py PAP-93 deps")
    write(mp, s)
    # runtime-sandbox rewrite in new_agents.py: replace the whole GAPS.append({...}) block for that key
    mp = os.path.join(R2, "agent2", "new_agents.py"); s = read(mp)
    if RS_TITLE_NEW not in s:
        start = s.index('GAPS.append({\n"key": "agents/runtime-sandbox"')
        end = s.index("GAPS.append({", start + 10)
        block = ('GAPS.append({\n"key": "agents/runtime-sandbox",\n"title": %s,\n"phase": "P0", "type": "Infra", "priority": 1, "surfaces": ["Agent", "Developer"],\n'
                 '"milestone": "Roster defined and installed", "state": "Backlog",\n"blockedBy": ["PAP-25", "security/credential-broker", "security/agent-deny-list"], "blocks": [],\n'
                 '"description": """%s""",\n})\n# FIX-6 (2026-09-17): rewritten; egress proxy, allowlist and secret injection moved to security/credential-broker, hook policy to security/agent-deny-list.\n\n') % (json.dumps(RS_TITLE_NEW), curly_form(RS_DESC))
        s = s[:start] + block + s[end:]
    write(mp, s)

# ----------------------------------------------------------------------------------------------------
# 4. agent6 security specs (module + JSON); canonical [key] form, converted per target
# ----------------------------------------------------------------------------------------------------
SEC_REPS = [
 # credential broker
 ("* In: `packages/orchestrator/src/broker/` (minting, storage, rotation, revocation), proxy credential injection rules",
  "* In: `packages/orchestrator/src/broker/` (minting, storage, rotation, revocation), the egress proxy container `ops/sandbox/egress/` (Dockerfile, per-character allowlist `ops/sandbox/egress/<character>.txt` generated from `roster.json`: Anthropic API, Linear, GitHub, Forgejo, npm registry plus the character's `access[]` connector hosts; every other host denied and logged as `egress-denied` in PAP-107 format; moved here from [agents/runtime-sandbox] on 2026-09-17), proxy credential injection rules"),
 ("* Out: the egress proxy container itself and the allowlist ([agents/runtime-sandbox]), bot account creation (PAP-48)",
  "* Out: the session container, worktree mount and resource limits ([agents/runtime-sandbox], which attaches to this proxy as its only route), bot account creation (PAP-48)"),
 ("[agents/runtime-sandbox] (proxy reads rules), PAP-105 `linear-update` skill",
  "[agents/runtime-sandbox] (attaches session containers to the proxy network; no other route), PAP-105 `linear-update` skill"),
 ("Blocks PAP-111 (kill implies revoke). Soft: [agents/runtime-sandbox], PAP-60, PAP-105.",
  "Blocks PAP-111 (kill implies revoke) and [agents/runtime-sandbox] (container, worktree and limits; needs this proxy as its only route). Soft: PAP-60, PAP-105."),
 # deny list
 ("credential broker [security/credential-broker] Linear proxy that refuses archive and delete mutations, egress allowlist [agents/runtime-sandbox]);",
  "credential broker [security/credential-broker] Linear proxy that refuses archive and delete mutations and its egress allowlist);"),
 ("Blocks PAP-96 (launcher staleness check), PAP-111 (S0 hit escalation). Soft: PAP-94, PAP-46, [agents/runtime-sandbox].",
  "Blocks PAP-96 (launcher staleness check), PAP-111 (S0 hit escalation) and [agents/runtime-sandbox] (the sandbox image ships the compiled `agent-deny.json`). Soft: PAP-94, PAP-46."),
 # absorb notes
 ("and a scanner that fails CI when a secret-shaped column is stored in the clear.\n\n**Scope**",
  "and a scanner that fails CI when a secret-shaped column is stored in the clear.\n\nMerges `gap/data-layer/field-encryption` (round-2 data-layer gap, same deliverable; merged 2026-09-17, FIX-6). From it: encrypted columns are marked `secret` in the PAP-41 data dictionary, and PAP-174 automation connector credentials and PAP-199 import connector PATs are adopters.\n\n**Scope**"),
 ("and proves them monthly with a scripted drill on a throwaway host.\n\n**Scope**",
  "and proves them monthly with a scripted drill on a throwaway host.\n\nMerges `gap/data-layer/platform-dr` (same drill; merged 2026-09-17, FIX-6). From it: the smoke suite reuses PAP-86 flows, the restore uses only images from our own registry (PAP-50; GitHub blocked as in PAP-53), and the drill proves field decryption works with keys restored from escrow ([security/field-encryption]).\n\n**Scope**"),
 ("then delete every row, file, Yjs document and key for the tenant.\n\n**Scope**",
  "then delete every row, file, Yjs document and key for the tenant.\n\nMerges `gap/data-layer/retention-pii` (same deliverable) and the hard-purge half of `gap/data-layer/tenant-lifecycle` (merged 2026-09-17, FIX-6). From them: tenant-level retention overrides within legal bounds with defaults picked by the PAP-126 compliance profile (7-year finance retention), tables tagged immutable (PAP-179, PAP-180) are never touched, the purge refuses without a completed PAP-205 export and lands in Needs Justin when the tenant has paid history in the last 90 days, and the PAP-88 digest reports rows deleted and anonymised per table. `gap/data-layer/tenant-lifecycle` keeps tenant states, quotas and the `requestDeletion`/`cancelDeletion` flow and schedules `tenant.purge` from here.\n\n**Scope**"),
]
def fix_agent6():
    p = os.path.join(R2, "agent6", "pending-issues.json"); d = json.load(open(p))
    for it in d:
        desc = it["description"]
        for o, n in SEC_REPS:
            o2, n2 = curly_security_only(o), curly_security_only(n)
            if o2 in desc or n2 in desc: desc = Rep.do(desc, o2, n2, f"agent6 json {it['key']}")
        it["description"] = desc
        if it["key"] == "security/credential-broker" and "agents/runtime-sandbox" not in it["blocks"]: it["blocks"].append("agents/runtime-sandbox")
        if it["key"] == "security/agent-deny-list" and "agents/runtime-sandbox" not in it["blocks"]: it["blocks"].append("agents/runtime-sandbox")
    json.dump(d, open(p, "w"), indent=1)
    if p not in ch["filesEdited"]: ch["filesEdited"].append(p)
    mp = os.path.join(R2, "agent6", "specs.py"); s = read(mp)
    for o, n in SEC_REPS:
        o2, n2 = curly_security_only(o), curly_security_only(n)
        s = Rep.do(s, o2, n2, "agent6/specs.py")
    s = Rep.do(s, '"blockedBy": ["PAP-96", "PAP-48", "PAP-25"], "blocks": ["PAP-111"]', '"blockedBy": ["PAP-96", "PAP-48", "PAP-25"], "blocks": ["PAP-111", "agents/runtime-sandbox"]', "specs.py broker blocks")
    s = Rep.do(s, '"blockedBy": ["PAP-106", "PAP-210"], "blocks": ["PAP-96", "PAP-111"]', '"blockedBy": ["PAP-106", "PAP-210"], "blocks": ["PAP-96", "PAP-111", "agents/runtime-sandbox"]', "specs.py deny-list blocks")
    write(mp, s)

# ----------------------------------------------------------------------------------------------------
# 5. contracts and golden path (JSON pairs + generator), agent4 growth ref
# ----------------------------------------------------------------------------------------------------
CON_REPS = [
 ("Consumed by PAP-28, PAP-97, PAP-136 and notification-core, PAP-174,", "Consumed by PAP-28, PAP-97, PAP-136 (work package 1, the notification core), PAP-174,"),
 ("* PAP-28, PAP-136 (or notification-core), PAP-174, PAP-195 and PAP-222 owners", "* PAP-28, PAP-136 (work package 1), PAP-174, PAP-195 and PAP-222 owners"),
 ("This issue supersedes the pending gap `gap/data-layer/event-bus`.", "This issue supersedes the pending gap `gap/data-layer/event-bus` (merged here 2026-09-17, FIX-6; from it: `flags.changed` for the runtime flags gap and `file.ready` for PAP-37 join the initial catalogue, and PAP-181 is a consumer)."),
 ("This issue supersedes the pending gap `gap/data-layer/rate-limit-idempotency`.", "This issue supersedes the pending gap `gap/data-layer/rate-limit-idempotency` (merged here 2026-09-17, FIX-6; from it: financial procedures in PAP-179 and PAP-180 require the `Idempotency-Key` header, and per-actor overrides exist for `kind: 'agent'` principals)."),
 ("publishing packages (forge template-upgrade gap).", "publishing packages (`gp/app-shell/upgrade`, which absorbed the forge template-upgrade gap)."),
]
GP_REPS = [
 ("This closes the template-upgrade gap the round-2 audit found in forge and app-shell.",
  "This closes the template-upgrade gap the round-2 audit found in forge and app-shell; `gap/forge/template-upgrade` was merged into this issue on 2026-09-17 (FIX-6), which adds the `@paperos/*` package registry below."),
 ("* Fleet mode `paperos upgrade --fleet imagine-os`",
  "* Package registry (from `gap/forge/template-upgrade`): publish `@paperos/*` on each template tag to the Forgejo npm registry (`git.PAPEROS_DOMAIN/api/packages/imagine-os/npm/`) with a GitHub Packages mirror; `.npmrc` template in generated apps; auth via the PAP-48 bot token in CI and the developer's Forgejo token locally; the upgrade PR bumps `@paperos/*` versions alongside the file merge.\n* Fleet mode `paperos upgrade --fleet imagine-os`"),
 ("* Fleet mode without forge credentials: falls back to GitHub org listing (PAP-22 client) and warns.",
  "* Fleet mode without forge credentials: falls back to GitHub org listing (PAP-22 client) and warns.\n* Template major bump: upgrade refuses without `--allow-major` and links the ADR.\n* Registry down: `pnpm install` falls back to the GitHub Packages mirror."),
 ("Hard: PAP-22, `paperos gen` pipeline. Soft: PAP-264, PAP-266, PAP-53, PAP-49, PAP-133, PAP-276, PAP-24.",
  "Hard: PAP-22, `paperos gen` pipeline. Soft: PAP-264, PAP-266, PAP-53, PAP-49, PAP-133, PAP-276, PAP-24, PAP-45 (Forgejo packages), PAP-48 (bot token), PAP-52 (release feed); PAP-29's drill upgrades a drill app with this command."),
]
def fix_contracts_golden_agent4():
    for f in ("contracts-issues.json", "pending-issues-contracts.json"):
        p = os.path.join(R2, f); d = json.load(open(p))
        for it in d:
            for o, n in CON_REPS:
                if o in it["description"] or n in it["description"]: it["description"] = Rep.do(it["description"], o, n, f"{f} {it['key']}")
        json.dump(d, open(p, "w"), indent=1)
        if p not in ch["filesEdited"]: ch["filesEdited"].append(p)
    for f in ("golden-path-issues.json", "pending-issues-golden-path.json"):
        p = os.path.join(R2, f); d = json.load(open(p))
        for it in d:
            if it["key"] != "gp/app-shell/upgrade": continue
            for o, n in GP_REPS: it["description"] = Rep.do(it["description"], o, n, f"{f} upgrade")
        json.dump(d, open(p, "w"), indent=1)
        if p not in ch["filesEdited"]: ch["filesEdited"].append(p)
    mp = os.path.join(R2, "golden_path_specs.py"); s = read(mp)
    for o, n in GP_REPS: s = Rep.do(s, o, n, "golden_path_specs.py")
    write(mp, s)
    # agent4 growth: field-encryption ref
    p = os.path.join(R2, "agent4", "pending-issues.json"); d = json.load(open(p))
    for it in d["issues"]:
        desc = it["input"]["description"]
        if "{{gap/data-layer/field-encryption}}" in desc or "{{security/field-encryption}}" in desc:
            it["input"]["description"] = Rep.do(desc, "{{gap/data-layer/field-encryption}}", "{{security/field-encryption}}", f"agent4 json {it['key']}")
    json.dump(d, open(p, "w"), indent=1)
    if p not in ch["filesEdited"]: ch["filesEdited"].append(p)
    mp = os.path.join(R2, "agent4", "new_growth.py"); s = read(mp)
    s = Rep.do(s, "{{gap/data-layer/field-encryption}}", "{{security/field-encryption}}", "agent4/new_growth.py")
    write(mp, s)

def write_sidecar():
    p = os.path.join(R2, "pending-merged.json")
    json.dump({"fix": "FIX-6", "at": NOW, "rule": "Before creating any pending issue, skip keys listed here; the kept spec owns the deliverable.", "merges": MERGES,
               "droppedKeys": sorted(DROPPED_KEYS), "narrowed": ["gap/data-layer/tenant-lifecycle"], "rewritten": ["agents/runtime-sandbox"]}, open(p, "w"), indent=1)
    if p not in ch["filesEdited"]: ch["filesEdited"].append(p)

# ----------------------------------------------------------------------------------------------------
# 6. Linear documents
# ----------------------------------------------------------------------------------------------------
def build_docs():
    docs = json.load(open(os.path.join(HERE, "_docs_live.json")))
    other = json.load(open(os.path.join(HERE, "_otherdocs_live.json")))
    out = {}
    # pm-linear doc: drop the workspace-reconcile section
    t = "Round 2 pending issues: pm-linear (9)"; c = docs[t]["content"]
    if "merged into PAP-91" not in c:
        lines = c.split("\n")
        i0 = next(i for i, l in enumerate(lines) if l.startswith("## Reconcile the live Linear workspace"))
        i1 = next(i for i, l in enumerate(lines) if i > i0 and l.startswith("## "))
        repl = ["## Merged: Reconcile the live Linear workspace with the round-1 import", "",
                "`pm-linear/workspace-reconcile` | merged into PAP-91 on 2026-09-17 (FIX-6) | not to be created", "",
                "Obsolete. PAP-91 and PAP-93 were rewritten to treat the live workspace as correct (existing states, ungrouped surface labels, Size in the description, `Todo` as human parking), which was this issue's whole goal. The `Files:` line convention is enforced by PAP-93's validator and consumed by PAP-99; the workspace decisions are recorded in PAP-91's `docs/pm/linear-setup.md`. `round2/agent2/new_pm.py` filters this key out, so `create_new.py` will not create it.", ""]
        lines = lines[:i0] + repl + lines[i1:]
        c = "\n".join(lines)
        c = Rep.do(c, "* `pm-linear/workspace-reconcile` - Reconcile the live Linear workspace with the round-1 import: Character label group, `Files:` scope lines, estimates vs Size, Surface multi-label rule; align PAP-91 and PAP-93 to it",
                   "* `pm-linear/workspace-reconcile` - merged into PAP-91 (obsolete; not to be created; see below)", "pm doc contents")
        c = Rep.do(c, "Until then, descriptions of existing issues reference them as `[project/key]`.\n", "Until then, descriptions of existing issues reference them as `[project/key]`. Status 2026-09-17 (FIX-6): 8 to create, 1 merged.\n", "pm doc intro")
    out[t] = (docs[t], c)
    # agents doc: rewrite the runtime-sandbox section
    t = "Round 2 pending issues: agents (9)"; c = docs[t]["content"]
    if RS_TITLE_NEW not in c:
        lines = c.split("\n")
        i0 = next(i for i, l in enumerate(lines) if l.startswith("## Build the agent runtime sandbox"))
        i1 = next(i for i, l in enumerate(lines) if i > i0 and l.startswith("## "))
        meta = "`agents/runtime-sandbox` | new issue | Phase/P0, Type/Infra, Agent, Developer | priority 1 | milestone: Roster defined and installed | state: Backlog | blocked by: PAP-25, security/credential-broker, security/agent-deny-list | blocks: none (PAP-106 and PAP-96 soft) | rewritten 2026-09-17 (FIX-6)"
        repl = [f"## {RS_TITLE_NEW}", "", meta, ""] + doc_form(RS_DESC).split("\n") + [""]
        lines = lines[:i0] + repl + lines[i1:]
        c = "\n".join(lines)
        c = Rep.do(c, f"* `agents/runtime-sandbox` - {RS_TITLE_OLD}", f"* `agents/runtime-sandbox` - {RS_TITLE_NEW}", "agents doc contents")
    out[t] = (docs[t], c)
    # security doc
    t = "Round 2 pending issues: security (11)"; c = docs[t]["content"]
    for o, n in SEC_REPS: c = Rep.do(c, doc_form(o), doc_form(n), "security doc")
    c = Rep.do(c, "priority 1 | size M | state: Backlog | blocked by: PAP-96, PAP-48, PAP-25 | blocks: PAP-111\n", "priority 1 | size M | state: Backlog | blocked by: PAP-96, PAP-48, PAP-25 | blocks: PAP-111, agents/runtime-sandbox\n", "security doc broker meta")
    c = Rep.do(c, "blocked by: PAP-106, PAP-210 | blocks: PAP-96, PAP-111\n", "blocked by: PAP-106, PAP-210 | blocks: PAP-96, PAP-111, agents/runtime-sandbox\n", "security doc deny meta")
    out[t] = (docs[t], c)
    # contracts pending doc
    t = "Round 2 pending issues: contracts (4)"; c = docs[t]["content"]
    for o, n in CON_REPS: c = Rep.do(c, o, n, "contracts pending doc")
    out[t] = (docs[t], c)
    # golden path pending doc
    t = "Round 2 pending issues: golden path (8)"; c = docs[t]["content"]
    for o, n in GP_REPS: c = Rep.do(c, o, n, "golden path pending doc")
    out[t] = (docs[t], c)
    # Roster, Atlas, Threat Model, Contracts
    t = "PaperOS Agent Roster (org chart and character index)"; c = other[t]["content"]
    c = Rep.do(c, "until `pm-linear/workspace-reconcile` adds it, the orchestrator parses", "until PAP-91 adds it (the former `pm-linear/workspace-reconcile` is merged into PAP-91), the orchestrator parses", "roster")
    out[t] = (other[t], c)
    t = "Character sheet: Atlas — Chief Architect and Orchestrator"; c = other[t]["content"]
    c = Rep.do(c, "Pending: `pm-linear/workspace-reconcile`, `pm-linear/weekly-reaudit`,", "Pending: `pm-linear/weekly-reaudit`,", "atlas")
    out[t] = (other[t], c)
    t = "PaperOS Security & Threat Model"; c = other[t]["content"]
    c = Rep.do(c, "Owned elsewhere but relied on: `[agents/runtime-sandbox]` (agents pending document) and Postgres-backed rate limiting (data-layer gaps).",
               "Owned elsewhere but relied on: `[agents/runtime-sandbox]` (agents pending document; container, worktree and limits only, since 2026-09-17 the egress proxy and allowlist live in `[security/credential-broker]`) and Postgres-backed rate limiting (`[contracts/idempotency-rate-limits]`, contracts pending document).", "threat model")
    out[t] = (other[t], c)
    t = "PaperOS Interface & Data Contracts"; c = other[t]["content"]
    c = Rep.do(c, "`deleted_at` starts a 30-day purge grace (tenant-lifecycle gap).", "`deleted_at` starts a 30-day purge grace (`gap/data-layer/tenant-lifecycle` owns the request flow; `security/retention-pii` owns the purge job).", "contracts doc tenant")
    c = Rep.do(c, "| Notification | pending collab notification-core, PAP-136 |", "| Notification | PAP-136 work package 1 (notification core) |", "contracts doc notification")
    c = Rep.do(c, "PAP-28, PAP-97, PAP-136 and notification-core, PAP-174, PAP-179, PAP-195, PAP-222, push-transport, PAP-113 |", "PAP-28, PAP-97, PAP-136 (work package 1), PAP-174, PAP-179, PAP-195, PAP-222, push-transport, PAP-113 |", "contracts doc events row")
    c = Rep.do(c, "| PAP-37, PAP-39, notification-core, PAP-190,", "| PAP-37, PAP-39, PAP-136 (work package 1), PAP-190,", "contracts doc jobs row")
    out[t] = (other[t], c)
    return out

# ----------------------------------------------------------------------------------------------------
# 7. Issues and projects (live re-fetch right before the update)
# ----------------------------------------------------------------------------------------------------
ISSUE_REPS = {
 "PAP-91": [("* Out: reconciling issue bodies and estimates (\\[pm-linear/workspace-reconcile\\]), the contract validator (PAP-93)", "* Out: reconciling issue bodies and estimates (not needed: this issue treats the live workspace as correct; the former `pm-linear/workspace-reconcile` is merged here), the contract validator (PAP-93)"),
            ("PAP-22 (`paperos create` reuses the script), \\[pm-linear/workspace-reconcile\\].", "PAP-22 (`paperos create` reuses the script).")],
 "PAP-93": [("bulk fixes of existing issues (\\[pm-linear/workspace-reconcile\\]), drafting help", "bulk fixes of existing issues (none planned: PAP-91 treats the live workspace as correct), drafting help"),
            ("Blocked by PAP-91 and \\[pm-linear/workspace-reconcile\\]. Soft: PAP-97.", "Blocked by PAP-91. Soft: PAP-97.")],
 "PAP-190": [("encrypted via [gap/data-layer/field-encryption] or PAP-17 helpers", "encrypted via [security/field-encryption] (security pending document; absorbed the data-layer gap) or PAP-17 helpers")],
}
PROJECT_REPS = {
 "Project Management & Claude Pipeline": [("Decisions record (`[pm-linear/workspace-reconcile]`): `Todo` stays", "Decisions record (PAP-91, `docs/pm/linear-setup.md`; the former `[pm-linear/workspace-reconcile]` is merged into PAP-91): `Todo` stays"),
     ("`[pm-linear/workspace-reconcile]` created and Done as soon as the issue limit is lifted.", "PAP-91 also records the workspace decisions (`pm-linear/workspace-reconcile` is merged into it and will not be created).")],
 "Data Layer & Database": [("Pending gap issues (blocked by the workspace issue cap, inputs in `round2/gaps-pending-0.json`): domain event bus and outbox, transactional email package, server-side field encryption, rate limiting and idempotency, object-storage backups and platform DR drill, tenant lifecycle and quotas, retention and PII enforcement.",
     "Pending gap issues (blocked by the workspace issue cap): transactional email package (`gap/data-layer/email-package`) and tenant states, quotas and deletion request flow (`gap/data-layer/tenant-lifecycle`) in `round2/gaps-pending-0.json`; domain event bus and outbox (`contracts/domain-events`) and rate limiting and idempotency (`contracts/idempotency-rate-limits`) in the contracts pending document; server-side field encryption (`security/field-encryption`), object-storage backups and platform DR drill (`security/platform-dr`) and retention, PII and tenant hard-purge (`security/retention-pii`) in the security pending document. The data-layer duplicates of the last five were merged on 2026-09-17 (FIX-6).")],
 "Version Control & Forge Independence": [("Pending gap issues (blocked by the workspace issue cap, inputs in `round2/gaps-pending-0.json`): non-Linux CI runners (hosted macOS, Windows VM), template upgrade path and `@paperos/*` registry.",
     "Pending gap issues (blocked by the workspace issue cap): non-Linux CI runners (hosted macOS, Windows VM; `gap/forge/non-linux-runners` in `round2/gaps-pending-0.json`); the template upgrade path and `@paperos/*` registry are owned by `gp/app-shell/upgrade` (golden path pending document; `gap/forge/template-upgrade` merged into it 2026-09-17, FIX-6).")],
}

def main():
    fix_gaps_pending0(); fix_agent3(); fix_agent2(); fix_agent6(); fix_contracts_golden_agent4(); write_sidecar()
    docs = build_docs()
    for title, (meta, new) in docs.items():
        print(f"DOC {title[:50]:50} {len(meta['content'])} -> {len(new)} chars, changed={new != meta['content']}")
    if Rep.problems:
        print("\nPROBLEMS:"); [print(" -", p) for p in Rep.problems]
    ch["merges"] = MERGES
    save_changes(ch)
    if DRY or Rep.problems:
        print("dry run or problems; no Linear mutations"); return
    # documents
    done = {d["title"] for d in ch["documentsUpdated"]}
    for title, (meta, new) in docs.items():
        if new == meta["content"] or title in done: continue
        r = gql("mutation($id: String!, $i: DocumentUpdateInput!) { d: documentUpdate(id: $id, input: $i) { success document { id title updatedAt } } }", {"id": meta["id"], "i": {"content": new}})
        assert r["d"]["success"], title
        ch["documentsUpdated"].append({"id": meta["id"], "title": title, "url": meta["url"], "chars": len(new), "updatedAt": r["d"]["document"]["updatedAt"]}); save_changes(ch); print("updated doc", title)
    # issues (re-fetch live first)
    done = {u["identifier"] for u in ch["issuesUpdated"]}
    for ident, reps in ISSUE_REPS.items():
        if ident in done: continue
        live = gql("query($id: String!) { issue(id: $id) { id identifier description updatedAt } }", {"id": ident})["issue"]
        desc = live["description"]
        for o, n in reps: desc = Rep.do(desc, o, n, f"live {ident}")
        if Rep.problems: print("PROBLEMS on", ident, Rep.problems); Rep.problems.clear(); continue
        if desc == live["description"]: print("no change", ident); continue
        r = gql("mutation($id: String!, $i: IssueUpdateInput!) { u: issueUpdate(id: $id, input: $i) { success issue { id identifier updatedAt } } }", {"id": live["id"], "i": {"description": desc}})
        assert r["u"]["success"], ident
        ch["issuesUpdated"].append({"id": live["id"], "identifier": ident, "fields": ["description"], "basedOnUpdatedAt": live["updatedAt"], "updatedAt": r["u"]["issue"]["updatedAt"], "change": "workspace-reconcile references removed" if ident != "PAP-190" else "[gap/data-layer/field-encryption] -> [security/field-encryption]"}); save_changes(ch); print("updated", ident)
    # projects
    snap = json.load(open(os.path.join(R2, "linear-snapshot-2.json")))
    pids = {p["name"]: p["id"] for p in snap["projects"]}
    done = {u["name"] for u in ch["projectsUpdated"]}
    for name, reps in PROJECT_REPS.items():
        if name in done: continue
        live = gql("query($id: String!) { project(id: $id) { id name content updatedAt } }", {"id": pids[name]})["project"]
        content = live["content"]
        for o, n in reps: content = Rep.do(content, o, n, f"live project {name}")
        if Rep.problems: print("PROBLEMS on", name, Rep.problems); Rep.problems.clear(); continue
        if content == live["content"]: print("no change", name); continue
        r = gql("mutation($id: String!, $i: ProjectUpdateInput!) { u: projectUpdate(id: $id, input: $i) { success project { id updatedAt } } }", {"id": live["id"], "i": {"content": content}})
        assert r["u"]["success"], name
        ch["projectsUpdated"].append({"id": live["id"], "name": name, "fields": ["content"], "basedOnUpdatedAt": live["updatedAt"], "updatedAt": r["u"]["project"]["updatedAt"]}); save_changes(ch); print("updated project", name)
    save_changes(ch)

if __name__ == "__main__":
    main()
