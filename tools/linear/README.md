# Linear tooling

The Python scripts that built the PaperOS plan in Linear (team PAP) and applied the round-2 audit fixes. They are kept as the record of how every issue, relation, label, milestone and document got there, and as the scripts PAP-91 names for creating the pending issues once the workspace plan is upgraded.

## How they talk to Linear

* Every script POSTs GraphQL to `https://api.linear.app/graphql` with `urllib` and the header `Authorization: $LINEAR_API_KEY`. In the planning sessions the key was injected by the session's agent proxy; here it must be in the environment (`export LINEAR_API_KEY=...`). No key is stored in this repository.
* Requests are throttled (about three per second) and retried on `429` / `RATELIMITED` with a 60 s sleep.
* Every mutation script is **idempotent**: creates are keyed on title-in-project (or on a `key` recorded in the matching `changes-*.json`), relations on the `(from, type, to)` string, text edits on a marker sentence. Re-running a script after a partial failure finishes the job without duplicating anything. Most take `--dry` to print the plan without mutating.
* They never delete or archive issues, never move anything to Done or Canceled and never touch PAP-1..PAP-12 or views (Security & Threat Model §4).

## Layout and data directory

The scripts kept their original relative layout:

| Path | Purpose |
|---|---|
| `build_plan.py` | Round 1: reads `plan.json` and the spec buckets, creates team config, projects, milestones, 206 issues and relations; writes `linear-ids.json`. |
| `lin.py`, `step*.py` | Round-1 helpers and follow-up steps (duplicates, PAP-5 handling, relations). |
| `round2/snapshot*.py` | Full read-only snapshots of the team (`linear-snapshot*.json`). |
| `round2/agent0..agent6/` | Round-2 audit agents per project group: `rw_*.py` rewrite descriptions, `new_*.py` hold the specs of gap and child issues, `create_*.py` create them, `relations.py` / `push_*.py` push edges and updates, `docs.py` publishes the "Round 2 pending issues" documents when `issueCreate` hits the plan cap. |
| `round2/create_contracts.py`, `apply_golden_path.py`, `golden_path_specs.py` | Contracts and golden-path documents and their issues. |
| `round2/characters/publish.py` | Publishes the roster and nine character sheets. |
| `round2/sched/model.py`, `sim.py` | The schedule model and burn-down simulation behind the Execution Schedule. |
| `round2/fix*_apply.py`, `fix3_plan.py`, `fix4/`, `fix6/`, `fix8_apply.py` | Fixes FIX-1..FIX-8 from the round-2 audit (milestone inversions, ready-but-blocked, umbrella rule, Deferred set, issue cap Plan B, pending-doc dedupe, read-first index, promotion rule). |
| `round2/update_blueprint.py` | Rewrites the Blueprint document in Linear. |

They read and write plan data (`plan.json`, `linear-ids.json`, `specs/bucket-*.json`, `round2/linear-snapshot*.json`, `round2/changes-*.json`) from one directory. The hard-coded scratch path was replaced with `os.environ.get("PAPEROS_PLAN_DIR", ".")`, so point `PAPEROS_PLAN_DIR` at a directory laid out like the original planning directory. To rebuild one from this repository:

```
mkdir -p work/specs work/round2
cp plan/plan.json plan/linear-ids.json work/
cp plan/specs/*.json work/specs/
cp plan/round2/*.json plan/round2/*.md work/round2/
cp plan/round2/changes/*.json work/round2/   # restore the original names: spaces were replaced with '_'
export PAPEROS_PLAN_DIR=$PWD/work
```

The `sys.path.insert` lines use the same variable so sibling modules (`r2.py`, `lin.py`, `common.py`) import. Snapshot files larger than the final one (`linear-snapshot.json`, `linear-snapshot-2.json`) were not committed; take a fresh snapshot with `round2/snapshot3.py` before running anything that needs one.

## Creating the pending issues (PAP-91 Plan B)

After NJ-1 is approved, run in this order: `round2/agent2/create_new.py` (runtime sandbox first, then PAP-96 and PAP-104 children, then session observability), then `round2/agent3/create_issues.py`, `agent4/create_issues.py`, `agent5/create_issues.py`, `agent6/create_issues.py`, `apply_golden_path.py`, `create_contracts.py`. They skip the keys in `round2/folded-into-live-issues.json`. See `docs/pending/README.md`.
