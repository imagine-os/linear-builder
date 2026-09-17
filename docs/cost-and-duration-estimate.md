# PaperOS build: cost and duration estimate (Claude Code sessions)

Snapshot: `plan/linear-snapshot-live.json`, takenAt 2026-09-17T13:11:39Z, 428 issues. Raw numbers: `plan/estimate-results.json`; per-issue assignments: `plan/model-effort.json` (the `estimate.py` script that produced them lives in the planning session, not in this repository). In Linear the assignments are the `Model` and `Reasoning effort` label groups plus the `**Model / Effort:**` line at the top of every issue description.

## 1. Pricing (read 2026-09-17 from the `claude-api` skill, not from memory)

Sources: `SKILL.md` -> "Current Models (cached: 2026-06-24)" table (input/output); `shared/prompt-caching.md` line 144 and `shared/models.md` line 73 (cache read = 0.1x input, **0.025x = $0.25/MTok on Fable 5.1**; cache write = 1.25x input for 5-minute TTL). All four requested models are present.

| Model | Input | Output | Cache write (5m) | Cache read |
|---|---|---|---|---|
| claude-fable-5-1 | $10 | $50 | $12.50 | $0.25 |
| claude-opus-5 | $5 | $25 | $6.25 | $0.50 |
| claude-sonnet-5 | $2 | $10 | $2.50 | $0.20 |
| claude-haiku-4-5 | $1 | $5 | $1.25 | $0.10 |

$/MTok. Haiku 4.5 has a 200K context window; a QA session's per-turn context must stay under that.

## 2. Work inventory (PAP-13..PAP-432, Duplicates excluded)

- In scope: 420 issues (7 Duplicates PAP-6..12 and PAP-5 fall outside the range).
- Umbrellas (have children): 52, all Size L, built only via their children (each has 3-4 children).
- Buildable leaves: 368. Deferred (own `Deferred` label or child of a deferred umbrella): 42 leaves + 7 umbrellas -> **326 buildable, non-deferred issues** (298 Backlog, 28 Ready for Claude).
- Size parsed from the `**Size**` line (420/428 have one; the 8 without are PAP-5 and the Duplicates, so the M default was never needed).

| Size \ Type | Build | Infra | Spec | Research | Docs | Review | Total |
|---|---|---|---|---|---|---|---|
| S | 25 | 9 | 11 | 8 | 7 | 1 | 61 |
| M | 198 | 23 | 19 | 12 | 4 | 8 | 264 |
| L | 0 | 0 | 1 | 0 | 0 | 0 | 1 |
| Total | 223 | 32 | 31 | 20 | 11 | 9 | 326 |

Phase: P0 109, P1 150, P2 67. Deferred set (42 leaves) is priced separately below. Dependency graph among the 326: 1,148 blockedBy edges after mapping umbrella edges onto their children; no cycles.

## 3. Token model per issue (assumptions)

Builder session (reads spec + contracts + code, writes code and tests, runs them, opens PR):

| Size | Input tokens | of which cache reads (80%) | Cache writes (20%) | Output |
|---|---|---|---|---|
| S | 1.5M | 1.2M | 0.3M | 60K |
| M | 4.0M | 3.2M | 0.8M | 150K |
| L | 10.0M | 8.0M | 2.0M | 400K |

The uncached 20% is billed at the cache-write rate (in an agent loop every new turn is written to cache); this is slightly conservative versus billing it as plain input.

Formula per issue:

```
builder(size, model) = 0.8*I*p_cache_read + 0.2*I*p_cache_write + O*p_output
issue = k_type * builder * (1 + 0.40[reviewer] + 0.25[QA gate, Build/Infra only]) * 1.25[contingency]
k_type = 1.0 for Build/Infra, 0.60 for Spec/Research/Docs/Review
```

Reviewer = 40% of builder tokens (all types; docs PRs are reviewed too). QA/visual gate = 25% (code PRs only). Contingency 25% for retries and re-review.

Reconciliation with `docs/execution-schedule.md` section 4: its allowances (S $10 / M $22 / L $50 per builder session) sit just above this model priced on Fable 5.1 (builder-only S $7.05 / M $18.30 / L $47.00), so the schedule's allowances are effectively Fable 5.1 prices with headroom; its $8,345 plan line covered 166 Build/Infra units, the live snapshot has 255 Build/Infra + 71 other buildable leaves (Round 2 landed since). **This estimate uses the explicit token model, not the allowances**; the allowances are quoted only as a cross-check and agree within ~20% on mix A.

Totals across the 326 issues (all roles, before contingency): 1,730M input tokens, 65M output tokens.

## 4. Cost by model mix (326 non-deferred issues, contingency included)

| Mix | Builders | Reviewer | QA | Total | + the 42 deferred |
|---|---|---|---|---|---|
| A | Fable 5.1 | Fable 5.1 | Fable 5.1 | **$9,910** | +$1,516 |
| B | Opus 5 (90% of tokens) | Fable 5.1 = 10% of all tokens (planning + final review) | Opus 5 | **$6,035** | +$923 |
| C | Sonnet 5 | Opus 5 | Sonnet 5 | **$3,073** | +$468 |
| D | Sonnet 5 | Sonnet 5 | Haiku 4.5 | **$2,090** | +$317 |
| E | per-task rule (section 4b): Sonnet 230 / Opus 88 / Fable 8 issues | Opus 5 high after Opus/Fable builders, Sonnet 5 high after Sonnet | Haiku 4.5 low; + 4 RC reviews on Fable 5.1 high ($275) | **$3,490** | +$295 |

By phase (A / B / C / D / E): P0 $2,880 / 1,753 / 896 / 611 / 1,283; P1 $4,844 / 2,950 / 1,500 / 1,020 / 1,341; P2 $2,187 / 1,332 / 677 / 460 / 591 (E's phase figures exclude the $275 RC reviews).


### 4b. Scenario E: per-task model and effort assignment

Full per-issue list: `plan/model-effort.json` (420 rows: identifier, model, effort, reason; umbrellas carry `null`). Rule precedence per issue: umbrella -> Deferred label (Sonnet 5 / low) -> keystone spec (Fable 5.1 / high: PAP-114, 55, 161, 279, 93, 92, 103, 79) -> PAP-13 and the three children of the PAP-96 umbrella (Opus 5 / high; PAP-96 itself is an umbrella so the rule is applied to PAP-281/282/283) -> security keyword in title (deny list, credential broker, prompt injection, break-glass, encryption, RLS, auth -> Opus 5 / high) -> Type rules (Spec P0 Opus/high, Spec P1-P2 Sonnet/high; Research S Sonnet/medium, M-L Opus/medium; Build S Sonnet/medium, Build M Sonnet/high except P0 in data-layer, identity, pm-linear, realtime -> Opus/medium, Build L Opus/high; Infra S Sonnet/medium, M-L Opus/medium; Review Opus/high; Docs S Sonnet/low, M-L Sonnet/medium). Effort scales output tokens only: low x0.6, medium x1.0, high x1.4, max x2.0. Reviewer session = 40% of builder tokens on Opus 5 / high when the builder was Opus or Fable, Sonnet 5 / high when Sonnet. QA gate = 25% on Haiku 4.5 / low (code issues). Release-candidate reviews: 4 x full L-size session (10M in, 400K out x1.4) on Fable 5.1 / high = $220, $275 with contingency.

Counts (all 420 in-scope issues; the 326 active ones in parentheses):

| Model | low | medium | high | Total |
|---|---|---|---|---|
| claude-fable-5-1 | - | - | 8 (8) | 8 |
| claude-opus-5 | - | 42 (42) | 46 (46) | 88 |
| claude-sonnet-5 | 46 (4) | 43 (43) | 183 (183) | 272 |
| null (52 umbrellas) | | | | 52 |

The 42 Sonnet/low that are not active are the deferred leaves. Fully loaded per-issue: Build M on Sonnet/high = $8.85, Build M on Opus/medium = $19.42 (vs $37.74 on mix A).

Scenario E total for the Oct-1 scope: **$3,490** (issues $3,215 + RC reviews $275, contingency included), +$295 for the deferred set. It is 42% cheaper than B ($6,035) and $417 more than C, buying Opus 5 on the 88 structurally or security-critical issues and Fable 5.1 on the 8 keystone specs that every downstream spec reads.

Per-issue fully loaded (build + review + QA + contingency), Build type, mixes A-D:

| Size | A | B | C | D |
|---|---|---|---|---|
| S | $14.54 | $8.83 | $4.47 | $3.03 |
| M | $37.74 | $22.99 | $11.64 | $7.89 |
| L (not used; umbrellas are split) | $96.94 | $58.88 | $29.81 | $20.21 |

### $400 pilot

| Mix | S-only | M-only | Mixed at the live S:M ratio (19:81) |
|---|---|---|---|
| A (all Fable 5.1) | 27 | 10 | **~11 issues** |
| C (Opus review, Sonnet build/QA) | 89 | 34 | **~38 issues** |
| E (per-task rule) | - | - | **~30-35 issues** if drawn from P0 (P0 averages $11.8/issue under E; more of P0 lands on Opus than later phases) |

Mix C's $400 buys roughly a third of P0 (109 issues); mix A's buys the first dependency layer only.

## 5. Duration

Per-session wall-clock: S 30 min, M 75 min, L 180 min; reviewer 20 min; QA 15 min (code only). Each issue = build + review (+ QA) in sequence; non-code issues use the same size times (conservative).

- (a) Fully serial: 32,155 min = **536 h = 22.3 days at 24h/day, 44.7 days at 12h/day**.
- (b) Critical path over blockedBy edges (longest chain, 21 issues): 2,205 min = **36.8 h**. Chain: PAP-13 -> 42 -> 32 -> 33 -> 34 -> 227 -> 229 -> 335 -> 336 -> 337 -> 341 -> 342 -> 343 -> 332 -> 347 -> 348 -> 349 -> 201 -> 420 -> 421 -> 422 (repo template -> shell -> billing/data chain -> late P2 surfaces).

List scheduling (ready-first by longest remaining tail, dependencies respected):

| Concurrency | Wall-clock | Days @24h | Days @12h | Mean builders busy |
|---|---|---|---|---|
| 1 (serial) | 536 h | 22.3 | 44.7 | 1.0 |
| 8 | 67.5 h | 2.8 | 5.6 | 7.9 |
| 16 | 37.4 h | 1.6 | 3.1 | 14.3 |
| Unlimited | 36.8 h (= critical path) | 1.5 | 3.1 | - |

16 concurrent sessions already sit on the critical path; more buys nothing. What the model omits: `Needs Justin` approval gates (NJ-1..NJ-20 in the execution schedule, one of which, the Linear plan upgrade, currently blocks issue creation for the pending Round 2 set), merge-queue conflicts on shared files, and the 30% re-review bounce; these add calendar days, not tokens. The execution schedule's 15-day plan is therefore governed by human gates and daily PR-landing limits, not by session throughput.

## 6. Rate limits

Linear's ~1,500 requests/hour is not binding (16 sessions x ~20 issue/comment/state calls x ~1.5 issues/hour each is ~500 req/h); the binding limits are the org's Claude concurrent-session cap and output-tokens-per-minute (16 builders generate ~30-35K output tok/min; cache reads do not count toward input TPM on these models).

## 7. Recommendation

Run scenario E (per-task assignment) at 8-16 concurrent sessions: **$3,490 for the 326-issue Oct-1 scope** (about $3.8K with the deferred set), 3-6 operating days of session time, with the human-gate schedule as the real calendar constraint. It is cheaper than B by $2.5K while keeping Opus 5 / high on the scaffold, orchestrator, security-titled and P0 data/identity/realtime/pm-linear work and Fable 5.1 / high on the 8 keystone specs and the 4 release-candidate reviews; the $417 premium over C is the price of that coverage. Start with the $400 pilot under the E rule on P0's first dependency layers (~30-35 issues): it exercises all three builder models and gives real per-size token burn to re-baseline these assumptions before the rest is committed.

## 8. Discounted terms (2026-09-17, round 3)

Justin's credit terms changed after this estimate was written: he pays **$50 for every $2,500 of list-price Claude spend** (x0.02), and sessions run 24/7. Under those terms the token-saving of scenario E is worth about $150 to Justin, so the plan switches to spending list dollars where the build is most fragile. `docs/build-chunks.md` re-prices the same 326 issues with the same token model, prices and scheduler, keeps per-issue Effort as labeled, adds the four release-candidate reviews, and cuts the 16-builder schedule into consecutive **$2,500 list chunks ($50 each)** with, per chunk, the issues by project, umbrellas and milestones completed, release candidates reached, start and end times from 2026-09-17T14:23Z and the `Needs Justin` items that must be answered first.

| Mix | Builders / QA | Fable 5.1 on | Chunks | List | To Justin | Wall-clock at 16 builders 24/7 |
|---|---|---|---|---|---|---|
| A | Fable 5.1 | everything | 5 | $11,166 | **$223.32** (5 x $50 billed whole) | 37.3 h |
| B (recommended) | Opus 5 | Spec and Research issues, every reviewer session, the 4 RC reviews | 4 | $7,909 | **$158.17** (4 x $50 billed whole) | 37.3 h |

The 42 deferred issues are an optional final chunk: +$1,387 list ($27.75) on A, +$983 ($19.66) on B, +5.5 h. Per-issue models for mix B: `round3/model-effort-B.json` (planning session; Linear labels are updated by the verify stage, not by this document). The 37 hours are session time only; the `Needs Justin` gates and merge conflicts listed in section 5 still set the calendar.
