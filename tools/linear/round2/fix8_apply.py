#!/usr/bin/env python3
"""FIX-8 promotion rule: anchor-based edits to PAP-96, PAP-93, PAP-92, the Execution Schedule and the pm-linear pending doc.
Usage: fix8_apply.py [--apply]   (default: dry run, writes previews to round2/fix8/)"""
import json, os, subprocess, sys, time, datetime
R = os.environ.get("PAPEROS_PLAN_DIR", ".") + "/round2"
CHANGES = os.path.join(R, "changes-fix-FIX-8 promotion-rule.json")
APPLY = "--apply" in sys.argv
KEY = os.environ.get("LINEAR_API_KEY") or "placeholder"

def gql(query, variables=None):
    for attempt in range(4):
        body = json.dumps({"query": query, "variables": variables or {}})
        p = subprocess.run(["curl", "-sS", "-w", "\n%{http_code}", "https://api.linear.app/graphql",
                            "-H", f"Authorization: {KEY}", "-H", "Content-Type: application/json", "-d", body],
                           capture_output=True, text=True)
        out, _, code = p.stdout.rpartition("\n")
        time.sleep(0.3)
        if code == "429":
            print("429, waiting 60s"); time.sleep(60); continue
        try:
            j = json.loads(out)
        except Exception:
            print("bad response", code, out[:300]); time.sleep(5); continue
        if j.get("errors"):
            if any((e.get("extensions") or {}).get("code") == "RATELIMITED" for e in j["errors"]):
                print("RATELIMITED, waiting 60s"); time.sleep(60); continue
            raise SystemExit("GraphQL errors: " + json.dumps(j["errors"])[:1000])
        return j["data"]
    raise SystemExit("gave up")

def ins_after(text, anchor, addition, label):
    n = text.count(anchor)
    if n != 1:
        raise SystemExit(f"anchor for {label} found {n} times: {anchor[:80]!r}")
    return text.replace(anchor, anchor + addition)

def ins_before(text, anchor, addition, label):
    n = text.count(anchor)
    if n != 1:
        raise SystemExit(f"anchor for {label} found {n} times: {anchor[:80]!r}")
    return text.replace(anchor, addition + anchor)

def repl(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"anchor for {label} found {n} times: {old[:80]!r}")
    return text.replace(old, new)

# ---------------------------------------------------------------- load changes file (idempotency)
if os.path.exists(CHANGES):
    changes = json.load(open(CHANGES))
else:
    changes = {"fix": "FIX-8 promotion-rule", "startedAt": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%MZ"),
               "issuesCreated": [], "relationsCreated": [], "labelsCreated": [],
               "issuesUpdated": [], "documentsUpdated": [], "notes": []}
done_issues = {u["identifier"] for u in changes["issuesUpdated"]}
done_docs = {u["id"] for u in changes["documentsUpdated"]}

def save():
    json.dump(changes, open(CHANGES, "w"), indent=1)

# ---------------------------------------------------------------- fetch fresh
data = gql("""{ a: issue(id:"PAP-92"){id identifier description updatedAt}
                b: issue(id:"PAP-93"){id identifier description updatedAt}
                c: issue(id:"PAP-96"){id identifier description updatedAt}
                s: document(id:"1623cb9d-9ed5-4af1-aa62-f520948fc21c"){id title content updatedAt}
                p: document(id:"929a59dd-0cd1-47ba-9c12-7bf4ddb4ae9f"){id title content updatedAt} }""")
p92, p93, p96, sched, pmdoc = data["a"], data["b"], data["c"], data["s"], data["p"]

# ================================================================ PAP-96
t = p96["description"]
if "**Promotion (Backlog → Ready for Claude).**" in t:
    print("PAP-96 already has promotion; skipping"); p96_new = None
else:
    t = ins_after(t, "the work is split into three children so cold sessions can finish each in one context window.",
        " The claim loop also owns **promotion**: it is the only thing that moves a Backlog issue to `Ready for Claude` once every blocker is Done, Canceled or In Review with a PR (the branch-start rule), so the queue refills after the 26 Ready issues drain without Atlas promoting by hand.", "96 goal")
    t = ins_after(t, "  * \\[pm-linear/orchestrator/deploy\\]: deployment, `/status` endpoint and runbook.\n",
        "  * Promotion work package (lives inside \\[pm-linear/orchestrator/claims\\] and is built in the same session as the poll loop; if that child exists, claim the child): Backlog → Ready for Claude promotion under the branch-start rule, the `promotions` table, the `promoted:` comment, the `BASE_BRANCHES` prompt variable and the `pnpm linear:promote` CLI. Spec below under \"Promotion\".\n", "96 scope")
    promo = ("\n* **Promotion (Backlog → Ready for Claude).** Every poll cycle, after the claim pass, `promote()` scans team PAP issues in `Backlog` (`state: { name: { eq: \"Backlog\" } }`, `first: 100`, paged) and moves a candidate to `Ready for Claude` only when all four checks hold:\n"
             "  1. no `Deferred` label (label id from `linear-workspace.json`; the Execution Schedule v0.2 set) and no `deferred` note under Goal (PAP-92 deferred rule);\n"
             "  2. no sub-issues (`children.nodes.length === 0`; an umbrella is never promoted, Umbrella rule above);\n"
             "  3. every inbound `blocks` relation (`inverseRelations` filtered to `type: \"blocks\"`) comes from an issue that is `Done`, `Canceled`, or `In Review` **with an open PR** (a PR attachment on the blocker, or a `gh pr list --head <branch>` hit for its branch). This is the branch-start rule from Execution Schedule §1. An `In Review` blocker without a PR counts as open. Zero inbound blockers satisfies the check, so a `readyNow` Backlog issue is promoted on the first cycle;\n"
             "  4. `validateIssue(issue)` (PAP-93) returns no `severity: \"error\"` violation; `BLOCKED_BY_OPEN` (error in PAP-93) is the same predicate as check 3 and must agree with it (a disagreement is logged as `promotion.validator_mismatch` and the issue is skipped). Until PAP-93 lands, `promote()` runs checks 1-3 plus a local `parseSections` requiring the eight PAP-93 sections and marks the report `validator: unavailable`.\n"
             "  For each promoted issue the orchestrator: (a) collects the branch name of every `In Review` blocker into `BASE_BRANCHES` (comma-separated, deterministic order by identifier; empty when every blocker is Done or Canceled) and stores it with the `promotions(issue_id, promoted_at, blockers_json, base_branches_json, dry_run)` row (unique on `issue_id` while the issue stays promoted; a PAP-93 bounce clears it so re-promotion is allowed after a blocker changes state); (b) sets `stateId` to `Ready for Claude` under the same `updatedAt` guard as claiming; (c) posts exactly one `linearComment` in the form `promoted: blockers PAP-x (Done), PAP-y (In Review, branch feat/PAP-y)` or `promoted: no blockers`, footer `status: \"promoted\"`; (d) emits `issue.promoted`. At claim time `launchSession` injects `BASE_BRANCHES=<list>` into the session prompt; the session (PAP-92 orient step) creates its worktree from `main`, merges each base branch (`git merge --no-ff origin/<branch>`; a conflict stops the session with `status: \"ended\", reason: \"base-branch-conflict\"` and `Needs Justin`), and owns the rebase when the base PRs merge. Ordering and limits: at most 20 promotions per cycle, least slack first (PAP-99 `scheduler.next()` when present; before that milestone target date, then priority, then `createdAt`). Never re-promote an issue that PAP-93 bounced (`contract_checks` row with `ok: false` newer than the last blocker state change). `Deferred` issues are also excluded from any stretch-pool promotion until the label is gone.\n"
             "* `pnpm linear:promote [--dry-run | --apply] [--limit n] [--issue PAP-n]` (`src/cli/promote.ts`) runs one promotion pass outside the loop. `--dry-run` is the default: it prints a table (issue, milestone, inbound blockers with state and PR/branch, validator result, `BASE_BRANCHES`, verdict) and writes nothing to Linear or the database (rows go to `promotions` with `dry_run: true` only when `--record` is passed). `--apply` performs (a)-(d) above. Atlas runs the dry run by hand each half-day 09-17..09-20 and applies the list manually (PAP-92 \"How your issue got to Ready\"); from 09-20 pm the loop runs `promote()` every cycle and the CLI stays as the operator tool. Exit code 0 when the pass ran, 2 when Linear was unreachable.")
    t = ins_after(t, "The same exclusion applies to promotion and to any stretch-pool claim until the label is gone.", promo, "96 spec promotion")
    t = ins_before(t, "* Consumers: PAP-97 (event bus, sessions table)",
        "* Promotion provides: `promote(opts: { dryRun: boolean; limit?: number; issue?: string }): PromotionReport` (`{ candidates: [{ issue, blockers: [{ identifier, state, pr?, branch? }], validator, baseBranches, verdict: \"promoted\" | \"skipped\" , reason? }] }`), table `promotions`, CLI `pnpm linear:promote`, event `issue.promoted`, prompt variable `BASE_BRANCHES` (read by PAP-92 orient step and PAP-104 prompt templates), comment template `templates/promoted.md`.\n", "96 iface provides")
    t = repl(t, "bot users from PAP-48 (falls back to one bot user).",
        "bot users from PAP-48 (falls back to one bot user), `validateIssue` from PAP-93 for promotion check 4 (fallback: local `parseSections` and `validator: unavailable` in the report until PAP-93 lands).", "96 iface requires")
    t = ins_after(t, "* All three children Done and their DoDs met.\n",
        "* Promotion package: on a fixture team, Backlog issues whose inbound blockers are all Done, Canceled or In Review with a PR are moved to `Ready for Claude` with the `promoted:` comment and a `promotions` row; an issue labelled `Deferred`, an umbrella with sub-issues, an issue with an In Progress blocker and an issue with an In Review blocker without a PR are left in Backlog with no comment; the promoted issue whose blocker is In Review receives `BASE_BRANCHES` in its session prompt. `pnpm linear:promote --dry-run` on the live team prints the candidate table and changes nothing (recording attached). Live: one Backlog issue on the team whose only blocker is moved to Done is in `Ready for Claude` within two poll cycles.\n", "96 dod")
    t = ins_after(t, "exactly one re-queued `umbrella-close` session.",
        "\n* Promotion fixture graph `test/fixtures/promotion-graph.json` (mocked Linear): chain A `PAP-a` Done → `PAP-b` Backlog; chain B `PAP-c` In Review with PR on `feat/PAP-c` → `PAP-d` Backlog; `PAP-e` Backlog labelled `Deferred` with every blocker Done; umbrella `PAP-f` Backlog with two Backlog children and every blocker Done; `PAP-g` Backlog with one blocker In Progress; `PAP-h` Backlog with an In Review blocker that has no PR; `PAP-i` Backlog with no blockers but a missing Definition of done (validator error). One `promote()` pass promotes exactly `PAP-b` and `PAP-d` and nothing else; the comment on `PAP-b` is `promoted: blockers PAP-a (Done)` and on `PAP-d` `promoted: blockers PAP-c (In Review, branch feat/PAP-c)`; `PAP-d`'s prompt carries `BASE_BRANCHES=feat/PAP-c` and `PAP-b`'s is empty; a second pass promotes nothing (idempotent); moving `PAP-c` back to In Progress then running PAP-93 bounces `PAP-d` and a third pass leaves it in Backlog; `--dry-run` on the same fixture lists the same two verdicts and every state and comment count is unchanged. Also: the umbrella's children are promoted when their own blockers are Done, the umbrella never.", "96 test plan")
    t = ins_after(t, "is caught by the pre-claim re-check, not by the `updatedAt` guard alone.",
        "\n* Base PR closed without merge: PAP-97's `pr.closed` event triggers PAP-93 re-validation of every dependent promoted with that branch in `BASE_BRANCHES`; they are bounced to Backlog and promotion waits for the blocker to reach In Review again.\n* Justin moves a Backlog issue to Ready for Claude by hand while `promote()` is running: the `updatedAt` guard fails, the promotion row is not written and Justin's move stands (PAP-93 will still validate it).\n* Blocker in `Needs Justin`: counts as open; the candidate stays in Backlog and the dry-run table names the Needs Justin card so Atlas can see what is holding the chain.", "96 edge")
    t = repl(t, "Blocked by PAP-91, PAP-92, PAP-46, PAP-25. Blocks PAP-97, PAP-98, PAP-99, \\[agents/session-observability\\].",
        "Blocked by PAP-91, PAP-92, PAP-46, PAP-25. Soft: PAP-93 (`validateIssue` for promotion check 4; fallback in the Interface contract). Blocks PAP-97, PAP-98, PAP-99, \\[agents/session-observability\\].", "96 deps")
    p96_new = t

# ================================================================ PAP-93
t = p93["description"]
if "`BLOCKED_BY_OPEN` (error):" in t:
    print("PAP-93 already defines BLOCKED_BY_OPEN; skipping"); p93_new = None
else:
    t = repl(t, "`BLOCKED_BY_OPEN` (warn), `READY_BUT_BLOCKED` (error)", "`BLOCKED_BY_OPEN` (error), `READY_BUT_BLOCKED` (error)", "93 codes")
    t = ins_before(t, "* `READY_BUT_BLOCKED` (error): the issue is in `Ready for Claude`",
        "* `BLOCKED_BY_OPEN` (error): at least one inbound `blocks` relation comes from an **open** issue. An inbound blocker is open exactly when it is in `Backlog`, `Todo`, `Ready for Claude`, `In Progress` or `Needs Justin`, or in `In Review` without an open PR (no PR attachment and no `gh pr list --head <branch>` hit); it is closed when it is `Done`, `Canceled`, or `In Review` with a PR (the branch-start rule, Execution Schedule §1). The check applies to an issue in any state and is the predicate PAP-96 promotion (`promote()`, `pnpm linear:promote`) evaluates on every Backlog candidate: an issue with a `BLOCKED_BY_OPEN` error is not promoted. `fix` text lists each open blocker with its state and PR status and the two remedies: wait for the blocker to reach In Review with a PR (or Done), or soften the dependency (delete the relation and write the soft dependency with its fallback into Dependencies). On the webhook path (issue moved to Ready) the error bounces the issue to `Backlog` like any other; on the promotion path it only keeps the issue in Backlog and posts nothing; `pnpm contract:audit --state Backlog` reports it per issue, and the Backlog issues with zero errors are exactly the ones PAP-96 promotes on its next cycle. Was an undefined warning; made an error and defined 2026-09-17 (FIX-8).\n", "93 define")
    t = repl(t, "* `READY_BUT_BLOCKED` (error): the issue is in `Ready for Claude` and at least one inbound `blocks` relation comes from an open issue (Backlog, Todo, Ready for Claude, In Progress, Needs Justin, or In Review without an open PR).",
        "* `READY_BUT_BLOCKED` (error): the issue is in `Ready for Claude` and `BLOCKED_BY_OPEN` holds (same definition of open: Backlog, Todo, Ready for Claude, In Progress, Needs Justin, or In Review without an open PR). Kept as a separate code so the bounce comment and the audit table distinguish \"never promoted\" (`BLOCKED_BY_OPEN` on a Backlog issue) from \"promoted or hand-moved, then blocked again\" (`READY_BUT_BLOCKED`).", "93 rbb")
    t = repl(t, "* Consumers: PAP-96 re-validates before claiming;",
        "* Consumers: PAP-96 re-validates before claiming and calls `validateIssue` on every Backlog promotion candidate (promotion requires zero errors, `BLOCKED_BY_OPEN` included; the two implementations of \"open\" must agree, PAP-96 logs `promotion.validator_mismatch` otherwise);", "93 consumers")
    t = ins_after(t, "* Fixture suite of 12 good and 20 bad issues passes; `validate.ts` coverage above 95 percent.\n",
        "* `BLOCKED_BY_OPEN` fixtures pass (six cases in the Test plan) and `pnpm contract:audit --state Backlog` prints the pre-promotion list: every Backlog issue with its error codes, so the zero-error rows are the ones PAP-96 will promote next cycle; the table for the live team is posted here.\n", "93 dod")
    t = ins_after(t, "a blocker In Review with an open PR passes (branch-start rule).",
        "\n* `BLOCKED_BY_OPEN`: a Backlog issue with a Todo blocker fails (error); with a Needs Justin blocker fails; with an In Progress blocker fails; with an In Review blocker without a PR fails; with an In Review blocker with a PR passes; with every blocker Done or Canceled passes; with no inbound blockers passes; an outbound `blocks` relation never triggers it. `isOpen(blocker)` is exported and PAP-96's promotion test imports it so the two agree by construction.", "93 test")
    t = ins_after(t, "re-validate every Ready dependent and bounce with `READY_BUT_BLOCKED`.",
        "\n* Blocker moves to Done or In Review-with-PR while the dependent sits in Backlog: nothing to do here; PAP-96 promotion picks the dependent up on its next cycle (or Atlas via `pnpm linear:promote --dry-run` before 09-20).\n* Blocker is In Review and its PR is closed without merge: it becomes open again; PAP-97's `pr.closed` event triggers re-validation of the dependents and `READY_BUT_BLOCKED` bounces the promoted ones.", "93 edge")
    t = repl(t, "Blocked by PAP-91. Soft: PAP-97. Consumed by PAP-96, PAP-99, PAP-118.",
        "Blocked by PAP-91. Soft: PAP-97. Consumed by PAP-96 (claim re-validation and promotion check 4), PAP-99, PAP-118.", "93 deps")
    p93_new = t

# ================================================================ PAP-92
t = p92["description"]
if "**How your issue got to Ready.**" in t:
    print("PAP-92 already has the section; skipping"); p92_new = None
else:
    t = repl(t, "* Structure: Purpose; lifecycle diagram (mermaid, states mirror Linear); steps claim, orient, plan, build, verify, report, hand off, end",
        "* Structure: Purpose; lifecycle diagram (mermaid, states mirror Linear, including the Backlog → Ready for Claude promotion edge); How your issue got to Ready; steps claim, orient, plan, build, verify, report, hand off, end", "92 structure")
    t = repl(t, "pr?, branch, handoff? }`. `handoff` is defined by PAP-108 and referenced by `$ref`.",
        "pr?, branch, baseBranches?, handoff? }`. `handoff` is defined by PAP-108 and referenced by `$ref`; `baseBranches` echoes the `BASE_BRANCHES` prompt variable set by PAP-96 promotion (omitted when empty).", "92 footer")
    howready = ("\n* **How your issue got to Ready.** Nobody hand-picks issues for you. An issue reaches `Ready for Claude` in exactly one of two ways: Justin moved it (rare, and PAP-93 validates it anyway), or the orchestrator's promotion pass (PAP-96, Spec \"Promotion\") moved it because all four checks held: no `Deferred` label and no deferral note; no sub-issues (umbrellas are never promoted); every inbound `blocks` issue is `Done`, `Canceled`, or `In Review` with an open PR (the **branch-start rule**, Execution Schedule §1: a dependent may start once every blocker is In Review with a PR open and works against the PR branch); and the issue contract (PAP-93) passes with no errors, `BLOCKED_BY_OPEN` included (`BLOCKED_BY_OPEN` = an inbound blocker in Backlog, Todo, Ready for Claude, In Progress or Needs Justin, or In Review without a PR). The promotion comment on your issue reads `promoted: blockers PAP-x (Done), PAP-y (In Review, branch feat/PAP-y)` and your prompt carries `BASE_BRANCHES=feat/PAP-y,...` for every blocker that is still In Review. **Orient step therefore adds:** read the `promoted:` comment; for each branch in `BASE_BRANCHES` run `git merge --no-ff origin/<branch>` into your worktree before writing code (conflict → stop with `status: \"ended\", reason: \"base-branch-conflict\"`, comment, and the orchestrator routes to Needs Justin); list the base branches in your `Session started` footer (`baseBranches`); when a base PR merges before you open yours, rebase onto `main` (you own the rebase); when a base PR is closed without merge, PAP-93 bounces your issue and you stop with `status: \"partial\"`. **Manual fallback 09-17..09-20 (before PAP-96 is live, scheduled 09-20 pm):** Atlas runs `pnpm linear:promote --dry-run` from the orchestrator repo (`imagine-os/paperos-orchestrator`, script `src/cli/promote.ts` specified in the PAP-96 promotion package) at each half-day boundary (03:30Z and 15:30Z), reads the candidate table, and applies it by hand: move each listed issue to `Ready for Claude`, post the `promoted:` comment verbatim from the table, and put the table's `BASE_BRANCHES` line into the session prompt when launching. Until the orchestrator repo exists (PAP-96 is claimed 09-19), Atlas produces the same table by hand from the Linear `blocks` graph with the four checks above and records it as a comment on PAP-96 (`manual promotion 09-17 pm: PAP-16 (PAP-13 In Review, branch feat/PAP-13), ...`). The playbook carries this paragraph verbatim and the FAQ entry \"My issue is in Backlog and its blockers are done, why is it not Ready?\" (answers: Deferred label, sub-issues, an In Review blocker without a PR, or a contract error; check the `pnpm contract:audit --state Backlog` row).", )
    t = ins_before(t, "\n\n**Interface contract**", howready[0], "92 howready")
    t = ins_after(t, "deferred (an issue with the `Deferred` label or a \"deferred\" note in its body is never claimed and never promoted until Justin removes the deferral).\n",
        "* The section \"How your issue got to Ready\" states the four promotion checks, the branch-start rule, the `BASE_BRANCHES` merge procedure in the orient step and the manual fallback for 09-17..09-20 (Atlas runs `pnpm linear:promote --dry-run` and applies the list by hand); Sentinel checks that its wording matches PAP-96 Spec \"Promotion\" and PAP-93 `BLOCKED_BY_OPEN` word for word where they define the same thing.\n", "92 dod")
    t = repl(t, "* Unit: `ajv` validation of the schema against 10 valid and 10 invalid footers; word-count test 1500-2500.",
        "* Unit: `ajv` validation of the schema against 10 valid and 10 invalid footers (including two with `baseBranches`); word-count test 1500-2500 (the promotion section counts; trim the FAQ before trimming it).", "92 test")
    t = ins_after(t, "* Justin comments mid-session: highest priority, acknowledged in the next comment.",
        "\n* Prompt carries `BASE_BRANCHES` but a branch no longer exists on origin (PR merged and branch deleted): skip the merge, note it in the `Session started` comment, continue on `main`.", "92 edge")
    p92_new = t

# ================================================================ Execution Schedule doc
t = sched["content"]
if "Implemented by the PAP-96 promotion work package" in t:
    print("schedule already updated; skipping"); sched_new = None
else:
    t = repl(t, "it works against the PR branch and owns the rebase. Without it the 11-deep chains of section 2 do not fit before 10-01 at any parallelism.",
        "it works against the PR branch and owns the rebase. Without it the 11-deep chains of section 2 do not fit before 10-01 at any parallelism. Implemented by the PAP-96 promotion work package (`promote()` every poll cycle; `pnpm linear:promote --dry-run` as the operator tool) and enforced by PAP-93 `BLOCKED_BY_OPEN` (error): an inbound blocker is open when it is in Backlog, Todo, Ready for Claude, In Progress or Needs Justin, or in In Review without a PR; a Backlog issue is promoted to Ready for Claude when it has no `Deferred` label, no sub-issues, no open blocker and no contract error. Promoted issues get `BASE_BRANCHES` (the In Review blockers' branches) in their session prompt and merge them before coding (PAP-92 \"How your issue got to Ready\"). Defined 2026-09-17 (FIX-8).", "sched branch-start")
    t = repl(t, "The orchestrator (PAP-96, live 09-20pm) refills `Ready for Claude`; before that Atlas launches sessions by hand.",
        "The orchestrator (PAP-96, live 09-20pm) refills `Ready for Claude` through its promotion pass; before that (09-17..09-20) Atlas runs `pnpm linear:promote --dry-run` from the orchestrator repo at each half-day boundary (03:30Z, 15:30Z), applies the listed promotions by hand (state to Ready for Claude, the `promoted:` comment, `BASE_BRANCHES` in the launch prompt) and launches the sessions; until the repo exists (PAP-96 claimed 09-19) the same list is produced by hand from the `blocks` graph with the four checks and recorded as a comment on PAP-96.", "sched claim order")
    sched_new = t

# ================================================================ pm-linear pending doc (claims child)
t = pmdoc["content"]
if "`promote()`" in t:
    print("pm-linear doc already updated; skipping"); pm_new = None
else:
    t = repl(t, "the `linearComment()` helper and the database tables everything else records into.",
        "the `linearComment()` helper, the database tables everything else records into, and the promotion pass that refills `Ready for Claude` from `Backlog` under the branch-start rule (PAP-96 Spec \"Promotion\"; this child owns it).", "pm goal")
    t = repl(t, "`linearComment()`, config loading.",
        "`linearComment()`, config loading, `src/promote.ts` (`promote()`), `src/cli/promote.ts` (`pnpm linear:promote --dry-run | --apply`) and the `promotions` table.", "pm scope")
    t = repl(t, "* Tables: `sessions`, `claims`, `events`; SQLite in dev",
        "* Promotion: after each claim pass, `promote()` exactly as specified in PAP-96 Spec \"Promotion\" (checks 1-4: no `Deferred` label or deferral note, no sub-issues, every inbound blocker Done/Canceled/In Review-with-PR, PAP-93 `validateIssue` zero errors with `BLOCKED_BY_OPEN` an error); writes `promotions(issue_id, promoted_at, blockers_json, base_branches_json, dry_run)`, moves the issue to `Ready for Claude` under the `updatedAt` guard, posts `promoted: blockers PAP-x (Done), PAP-y (In Review, branch feat/PAP-y)` once, emits `issue.promoted`; `BASE_BRANCHES` is handed to the sessions child at launch. At most 20 per cycle, least slack first.\n* Tables: `sessions`, `claims`, `events`, `promotions`; SQLite in dev", "pm spec+tables")
    t = repl(t, "`events.emit(\"issue.claimed\" | \"issue.released\")`.",
        "`events.emit(\"issue.claimed\" | \"issue.released\" | \"issue.promoted\")`, `promote(opts): PromotionReport`, `isOpen(blocker)` re-exported from PAP-93, CLI `pnpm linear:promote`.", "pm provides")
    t = ins_after(t, "* Claim atomicity test: 20 concurrent `claimNext()` on one issue yields one winner.\n",
        "* Promotion fixture-graph test from PAP-96's Test plan passes (exactly `PAP-b` and `PAP-d` promoted; Deferred, umbrella, In Progress-blocked, PR-less In Review-blocked and contract-failing issues untouched; idempotent second pass); `pnpm linear:promote --dry-run` on the live team prints the candidate table and changes nothing (recording).\n", "pm dod")
    pm_new = t

# ---------------------------------------------------------------- previews
os.makedirs(os.path.join(R, "fix8"), exist_ok=True)
for name, new in [("PAP-96", p96_new), ("PAP-93", p93_new), ("PAP-92", p92_new), ("schedule", sched_new), ("pm-linear-doc", pm_new)]:
    if new:
        open(os.path.join(R, "fix8", f"preview_{name}.md"), "w").write(new)
        print(f"{name}: {len(new)} chars")

if not APPLY:
    print("dry run; previews in round2/fix8/"); sys.exit(0)

# ---------------------------------------------------------------- apply (one batched request for the three issues, one for the two docs)
now = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
issue_edits = [(p96, p96_new, ["promotion-work-package", "spec-promotion", "cli-linear-promote", "dod", "fixture-graph-test", "edge-cases", "soft-dep-PAP-93"]),
               (p93, p93_new, ["BLOCKED_BY_OPEN-error-defined", "READY_BUT_BLOCKED-relation", "consumers", "dod", "test-plan", "edge-cases", "deps"]),
               (p92, p92_new, ["how-your-issue-got-to-ready", "manual-fallback-09-17..09-20", "BASE_BRANCHES-orient-step", "footer-baseBranches", "dod", "test", "edge"])]
todo = [(iss, new, ch) for iss, new, ch in issue_edits if new and iss["identifier"] not in done_issues]
if todo:
    parts, vars_ = [], {}
    for i, (iss, new, ch) in enumerate(todo):
        parts.append(f'u{i}: issueUpdate(id: "{iss["id"]}", input: {{ description: $d{i} }}) {{ success issue {{ identifier updatedAt }} }}')
        vars_[f"d{i}"] = new
    q = "mutation(" + ", ".join(f"$d{i}: String!" for i in range(len(todo))) + ") { " + " ".join(parts) + " }"
    res = gql(q, vars_)
    for i, (iss, new, ch) in enumerate(todo):
        r = res[f"u{i}"]
        print(iss["identifier"], "success" if r["success"] else "FAILED", r["issue"]["updatedAt"])
        if r["success"]:
            changes["issuesUpdated"].append({"id": iss["id"], "identifier": iss["identifier"], "fields": ["description"], "changes": ch,
                                             "chars": len(new), "previousUpdatedAt": iss["updatedAt"], "updatedAt": r["issue"]["updatedAt"], "at": now})
    save()

doc_edits = [(sched, sched_new, "https://linear.app/paperos/document/paperos-execution-schedule-1fa3d38d6795", "branch-start rule now names PAP-96 promotion package and PAP-93 BLOCKED_BY_OPEN (error); claim-order bullet documents the 09-17..09-20 `pnpm linear:promote --dry-run` manual fallback"),
             (pmdoc, pm_new, "https://linear.app/paperos/document/round-2-pending-issues-pm-linear-9-d4829fc00859", "claims child (pm-linear/orchestrator/claims) now owns promote(), pnpm linear:promote, promotions table, issue.promoted and the fixture-graph DoD")]
todo = [(d, new, url, ch) for d, new, url, ch in doc_edits if new and d["id"] not in done_docs]
if todo:
    parts, vars_ = [], {}
    for i, (d, new, url, ch) in enumerate(todo):
        parts.append(f'd{i}: documentUpdate(id: "{d["id"]}", input: {{ content: $c{i} }}) {{ success document {{ id updatedAt }} }}')
        vars_[f"c{i}"] = new
    q = "mutation(" + ", ".join(f"$c{i}: String!" for i in range(len(todo))) + ") { " + " ".join(parts) + " }"
    res = gql(q, vars_)
    for i, (d, new, url, ch) in enumerate(todo):
        r = res[f"d{i}"]
        print(d["title"], "success" if r["success"] else "FAILED", r["document"]["updatedAt"])
        if r["success"]:
            changes["documentsUpdated"].append({"id": d["id"], "title": d["title"], "url": url, "change": ch, "chars": len(new),
                                                "previousUpdatedAt": d["updatedAt"], "updatedAt": r["document"]["updatedAt"], "at": now})
    save()
changes["notes"] = list(dict.fromkeys(changes["notes"] + [
    "No issues, relations or labels created: the Deferred label (beea2f68-dbc8-4a56-8213-1aeb46d24355) already existed; the promotion package lives inside PAP-96 / pm-linear/orchestrator/claims, so no new issue was needed.",
    "No state changes. Edits were anchor-based insertions on freshly fetched content, so concurrent FIX-9/FIX-12 edits to the same issues are preserved."]))
changes["finishedAt"] = now
save()
print("changes written to", CHANGES)
