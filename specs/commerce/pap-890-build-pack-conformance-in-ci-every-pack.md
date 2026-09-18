---
identifier: "PAP-890"
title: "Build pack conformance in CI: every pack applies to a blank tenant, home dashboard screenshots at seven widths, terminology and audience policy checks, posting traces, and golden-path acceptance extension"
project: "commerce"
projectName: "Commerce, Operations & Vertical Packs"
phase: "P2"
type: "Review"
priority: 4
surfaces: ["Developer"]
milestone: "Operations packs, marketplace and swap"
state: "Backlog"
parent: null
children: []
blockedBy: ["PAP-239", "PAP-246", "PAP-429", "PAP-888", "PAP-889"]
blocks: []
key: "r4/commerce/pack-conformance-tests"
url: "https://linear.app/paperos/issue/PAP-890/build-pack-conformance-in-ci-every-pack-applies-to-a-blank-tenant-home"
source: "Linear snapshot 2026-09-18T14:58Z (plan/linear-snapshot-live.json)"
updatedAt: "2026-09-18T14:30:03.999Z"
model: "claude-sonnet-5"
effort: "medium"
estimate: 3
dueDate: null
cycle: null
---

# PAP-890: Build pack conformance in CI: every pack applies to a blank tenant, home dashboard screenshots at seven widths, terminology and audience policy checks, posting traces, and golden-path acceptance extension

**Model / Effort:** Sonnet 5 (`claude-sonnet-5`) / medium — Review M

**Goal**

Keep sixteen packs honest as the platform changes under them: a nightly and per-PR job that applies every pack to a blank tenant, runs the pack's own smoke flow, captures the home dashboard and three key pages at the seven-width matrix (PAP-246), checks terminology coverage and generated audience policy tests, verifies posting traces against golden ledgers, and extends the PAP-429 golden path with one canned idea per pack family.

**Scope**

In: `ops/ci/packs.yml`: sharded job (four shards) applying packs from `packs/*` to per-shard blank tenants on the compose stack; `pack.yaml` gains `smoke: [{ flow, expect }]` for a scripted Playwright flow per pack. Artefacts: `packs.json` in the PAP-239 shape (per pack: apply time, lint, coverage, smoke pass, screenshots, posting diff); contact sheet of home dashboards; failures open a Linear comment on the pack's owning issue. Golden path extension: PAP-429 gains ideas "a salon in Leeds", "a plumbing company", "a small private school" mapped to packs and asserting the pack content is present in the generated app.

Out: Pack authoring. Visual review beyond the existing vision agent (PAP-84 inspects the contact sheet).

**Spec**

* A pack that fails to apply blocks merges touching `packs/` or any contract the pack depends on (compat matrix PAP-440 lists them)
* Posting golden files per pack are versioned with the pack; a change requires a Ledger review comment
* Runtime budget: full run under 25 minutes across shards; per-PR runs only the affected packs (dependency map)

**Interface contract**

Provides: packs CI job, `packs.json` artefact, `smoke` schema, golden posting files, golden-path ideas. Consumes: packs wave 2 and 3 and PAP-427, golden path acceptance (PAP-429), Playwright matrix (PAP-246), gate artefacts (PAP-239), compat matrix (PAP-440), vision inspection (PAP-84). Consumed by: quality release digest (pack health section, PAP-89), PAP-428 gallery (screenshots), platform-ops compliance evidence.

**Definition of done**

* Nightly run green for all sixteen packs on staging; per-PR affected-pack selection proven; a deliberately broken pack fails exactly its shard; golden path asserts three new ideas
* Linear comment on the issue with the evidence links (PR, gate artefacts, recording or report) and the module docs page updated where the interface changed.

**Test plan**

* Meta: break one pack field mapping and confirm the failure names the pack and file.
* Determinism: two runs produce identical `packs.json` except timings.

**Demo**

Open the nightly contact sheet of sixteen home dashboards at 375 and 1920, then show a PR that changed the scheduling contract running only the four packs that depend on it.

**Edge cases**

* Compose stack flake: the job retries a shard once and quarantines flaky smoke flows through PAP-90 rather than blocking every pack

**Dependencies**

PAP-888 and PAP-889 (hard), PAP-429, PAP-246, PAP-239 (hard), PAP-440, PAP-84, PAP-90 (soft).

**Agent**

Builder: Sentinel. Reviewer: Scout.

**Size**

M: one session.

*Round 4 critique fix (2026-09-18):* resolved 2 round-4 file keys in this description to Linear identifiers: `r4/commerce/vertical-packs-wave2` = PAP-888, `r4/commerce/vertical-packs-wave3` = PAP-889.
