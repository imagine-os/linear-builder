# PaperOS Execution Schedule

Plan for team PAP under the round-4 graph (2026-09-18): 901 specified issues, 105 umbrellas tracked through their children, 796 leaves of which 601 are scheduled and 195 deferred to `v0.2`. Simulated over the live `blocks` graph (3,041 relations, no cycles) with 16 builder sessions running 24/7 from 2026-09-18T14:15Z; model in `plan/round4/sched/` (round 2's 15-day half-day model stays in `round2/sched/` for history). The rules in section 1 are unchanged; the Round 4 note at the end of section 1 records what changed in Linear.

## 1. Scheduling rules

* **Sizes.** S = half a session-day, M = one, L = two; sessions start 03:30Z (am) or 15:30Z (pm). S lands the same half-day, M the next, L two days on.
* **Branch-start rule.** A dependent may start once every blocker is `In Review` with a PR open; it works against the PR branch and owns the rebase. Without it the 11-deep chains of section 2 do not fit before 10-01 at any parallelism. Implemented by the PAP-96 promotion work package (`promote()` every poll cycle; `pnpm linear:promote --dry-run` as the operator tool) and enforced by PAP-93 `BLOCKED_BY_OPEN` (error): an inbound blocker is open when it is in Backlog, Todo, Ready for Claude, In Progress or Needs Justin, or in In Review without a PR; a Backlog issue is promoted to Ready for Claude when it has no `Deferred` label, no sub-issues, no open blocker and no contract error. Promoted issues get `BASE_BRANCHES` (the In Review blockers' branches) in their session prompt and merge them before coding (PAP-92 "How your issue got to Ready"). Defined 2026-09-17 (FIX-8).
* **Claim order.** Least slack first (milestone target minus remaining critical path), then priority, then size. The orchestrator (PAP-96, live 09-20pm) refills `Ready for Claude` through its promotion pass; before that (09-17..09-20) Atlas runs `pnpm linear:promote --dry-run` from the orchestrator repo at each half-day boundary (03:30Z, 15:30Z), applies the listed promotions by hand (state to Ready for Claude, the `promoted:` comment, `BASE_BRANCHES` in the launch prompt) and launches the sessions; until the repo exists (PAP-96 claimed 09-19) the same list is produced by hand from the `blocks` graph with the four checks and recorded as a comment on PAP-96.
* **Capacity.** Peak parallel builder sessions 8, 12, 16, then 20 from 09-20 to 09-26, tapering 18, 16, 14, 10, 6. Reviewer sessions are on top of the cap.
* **Deferred to v0.2 (not claimable before 10-01):** PAP-23, 137, 149, 157, 158, 182, 185, 190, 191, 193, 194, 195, 196, 197, 203, 204, 206, 207, 218, 221, 222, 230, 231, 232, 235, 276, 277, 278 ($812 of allowances). Each carries the team label `Deferred`, priority 4 and a deferral line under Goal (FIX-4, 2026-09-17); PAP-96 never claims a `Deferred` issue and promotion skips them. Two scheduled issues used to depend on this set and both edges were made soft on 2026-09-17: PAP-235 → PAP-180 (FIX-1; invoices render PDFs with their own template until the theme lands) and PAP-190 → PAP-192 (FIX-4; the content agent drafts into its own `campaign_draft` queue and never publishes). After those two deletions no `blocks` edge runs from a deferred issue to a scheduled one; the only edges out of the set stay inside it (PAP-230/231 → 232, PAP-276 → 277 → 278).
* **Justin.** `Needs Justin` holds at most five open items (PAP-94). Conditional escalations (ADR contradictions from PAP-44 or PAP-56, S0 waivers from PAP-80, cycles from PAP-99) are not pre-scheduled.

### Round 4 (2026-09-18)

* **Scope re-planned over the expanded graph.** Team PAP now holds 901 specified issues (PAP-13 upward, Triage ideas excluded): 105 umbrellas, 796 leaves of which 195 carry `Deferred` (own label or a deferred umbrella) and 601 are scheduled. The tables in sections 2 and 4 were regenerated from `plan/round4/sched/model.py` under Justin's 24/7 terms (16 builders, $50 per $2,500 list, mix B); the rules above are unchanged, only the calendar moved from 15 days of half-day sessions to 38.6 hours of continuous sessions (2026-09-18T14:15Z to 2026-09-20T04:50Z), plus 14.3 h for the `v0.2` set. The `Needs Justin` items keep their NJ numbers; section 2 shows the block in which each is first needed.
* **Cycles hold in-flight work only.** Linear moves a Backlog issue to the default unstarted state when it joins a cycle, so planned issues never carry a cycle; `cycleIssueAutoAssignStarted` is on for team PAP and an issue joins the active cycle (C1 to 09-25, C2 to 10-02, C3 v0.2 stretch) the moment it moves to In Progress. Ready for Claude issues sit in the current cycle. Planned timing lives in due dates and Chunk labels, not in cycles.
* **Estimates are Fibonacci points**: S = 2 (half a session-day), M = 3 (one), L = 5 (two), set on every leaf; umbrellas carry none so Linear rolls up their children. The scheduler reads the estimate, not the `**Size**` text. Scheduled scope: 1609 points; deferred: 548.
* **Due dates are milestone target dates**, not the simulated landing time: every non-deferred issue's `dueDate` equals its project milestone's `targetDate` (section 7 dates; the five round-4 projects use 10-01 / 10-09 / 10-16). The simulation lands everything well before those dates; the dates stay as the commitment the burn report measures slips against.
* **Chunk labels follow mix B** of `docs/build-chunks.md`: `Chunk 1`..`Chunk 5` on the 601 scheduled leaves, `Chunk: v0.2` on the 195 deferred leaves, none on umbrellas (exactly one per leaf; round 3 had applied mix A to 326 leaves and left 46 issues that later became umbrellas labelled). Log: `plan/round4/changes/chunks-relabel.json`. The orchestrator uses the chunk order only as a tie-breaker among Ready for Claude issues.
* **Deferred set.** The 28 issues listed under *Deferred to v0.2* above grew to 195 leaves and 9 umbrellas in rounds 3-4 (label `Deferred`, priority 4, `Chunk: v0.2`, no cycle, no due date); the two FIX rules still hold: no `blocks` edge runs from a deferred issue to a scheduled one (verified 2026-09-18, `plan/round4/verify.md`) and PAP-96 never claims one.

## 2. Block by block

Identifiers omit `PAP-`. Regenerated 2026-09-18 from `plan/round4/sched/model.py` (16 builders 24/7, branch-start rule, clock start 2026-09-18T14:15Z); one row per six-hour block because the whole scheduled scope lands in 38.6 h. *Starts* = builder sessions launched in the block; *Peak* = concurrent builder sessions; *Landed* = PRs whose review and QA finish in the block (one reviewer session each, on top of the builder cap); *Chunk* = the `Chunk` label(s) of the issues starting in the block (`v0.2` = deferred set, after RC3 and NJ-14 only). Raw rows: `plan/round4/sched/days.json`.

| Block (UTC) | Starts | Peak | Landed (reviewer sessions) | Chunk | Needs Justin / checkpoint |
| -- | -- | -- | -- | -- | -- |
| 2026-09-18 12-18Z | 69: 13 14 25 46 55 56 66 127 139 150 161 209 279 302 433 555 31 91 92 114 212 295 476 644 93 103 210 292 16 17 30 42 68 255 281 556 657 32 72 236 273 284 296 44 285 286 293 305 117 256 282 447 508 691 79 198 449 33 237 274 297 666 78 94 105 219 275 564 739 | 16 | 47 | 1 | NJ-1 Linear: upgrade the workspace plan (PAP-91). Resolved: workspace is on Linear Basic. NJ-2 Infra batch (PAP-25): Hetzner account and cpx41, registrar or Cloudflare token (or accept sslip.io), Resend sign-up, sops recovery key. NJ-5 Linear: orchestrator API key and webhook signing secret (PAP-92, PAP-97). NJ-6 Code signing (PAP-256): Apple Developer Program + Azure Trusted Signing, or accept unsigned v0.1.0 installers (default after 48 h: unsigned). NJ-8 Approve docs/pm/justin-queue.md (PAP-94) and the issue contract (PAP-93). NJ-9 Hire the roster (PAP-104, PAP-210): nine leads, 28 sub-characters, tool scope classes. |
| 2026-09-18 18-24Z | 94: 121 257 283 287 436 519 520 521 665 34 238 267 97 223 448 38 239 456 503 115 258 350 704 108 264 294 526 227 268 655 659 70 224 225 226 289 537 557 74 175 259 558 438 662 713 228 229 565 656 660 269 290 578 661 37 152 641 260 270 642 643 392 459 664 140 335 338 484 768 240 291 579 663 667 678 741 271 311 645 234 265 393 714 912 312 336 603 613 616 651 177 246 314 582 | 16 | 92 | 1, 2 | NJ-3 GitHub App on org imagine-os with repo+workflow scope (PAP-47). NJ-10 Stripe test-mode account and restricted key (PAP-177); Google Cloud OAuth consent screen (PAP-224, PAP-200). **RC0.** |
| 2026-09-19 00-06Z | 78: 243 339 272 394 562 586 116 329 337 604 652 178 315 467 583 340 740 326 80 129 395 505 122 162 317 353 615 133 266 370 658 351 627 327 247 396 709 790 118 123 313 318 330 465 584 668 679 341 347 527 244 563 261 328 331 504 69 319 361 587 64 87 128 262 316 585 320 342 348 614 725 344 352 475 483 522 566 675 | 16 | 83 | 2 | Queue drains. |
| 2026-09-19 06-12Z | 92: 40 126 397 791 343 619 621 629 630 245 349 599 834 15 248 710 360 362 718 18 99 211 242 542 677 711 617 620 622 100 176 188 252 308 359 492 73 86 201 323 466 507 541 153 300 462 167 253 263 321 333 474 618 524 580 673 382 567 676 398 414 600 388 450 623 765 833 863 878 249 493 683 288 364 439 500 692 694 699 712 216 307 309 389 568 605 624 702 485 501 523 682 | 16 | 91 | 2, 3 | NJ-7 License of the template code (PAP-211): MIT, Apache-2.0 or proprietary; default Apache-2.0. NJ-11 Domain: set PAPEROS_DOMAIN or keep sslip.io for v0.1.0 (RC1). NJ-12 Payroll provider (PAP-176): sign the Check sandbox agreement (default) or Gusto Embedded. NJ-13 Airtable demo base and token (PAP-202); Slack incoming webhook (PAP-136). NJ-18 Industry list and terminology defaults (PAP-126). **RC1.** |
| 2026-09-19 12-18Z | 92: 156 324 372 437 766 767 769 531 647 280 385 451 452 457 460 463 538 625 848 468 469 98 254 495 322 61 145 332 334 345 386 420 470 847 477 478 479 486 487 488 494 183 189 376 383 399 415 421 581 674 653 835 836 862 877 893 693 250 325 429 440 453 560 561 601 703 670 716 306 310 717 722 757 144 502 606 696 729 200 680 107 125 160 373 387 539 559 631 669 672 849 84 | 16 | 87 | 3, 4 | NJ-4 Anthropic Console: orchestrator API key, hard spend limit, usage export (PAP-98). NJ-17 Accessibility statement wording (PAP-160). |
| 2026-09-19 18-24Z | 79: 83 89 109 111 134 135 346 528 543 544 369 371 454 455 458 461 464 471 472 473 480 481 482 489 490 491 496 497 509 510 511 546 548 549 569 570 588 589 590 593 594 607 608 646 697 715 728 742 102 113 138 148 181 186 217 743 756 814 192 208 377 378 384 390 391 400 416 422 432 498 654 815 864 879 894 90 375 379 431 | 16 | 83 | 4 | NJ-16 Approve the content agent (PAP-192) and migration agent (PAP-208). |
| 2026-09-20 00-06Z | 114: 626 24 130 251 628 648 695 731 749 837 895 29 76 112 444 301 446 602 896 530 753 445 512 529 532 533 534 545 754 540 547 550 551 571 572 591 592 597 609 610 612 698 705 706 720 727 748 506 681 700 701 719 721 726 744 745 758 813 746 747 755 759 760 146 374 380 499 525 552 761 762 763 792 908 553 573 574 575 595 413 596 611 649 671 684 730 732 733 734 850 41 49 95 241 685 77 750 23 182 185 194 235 276 401 404 407 410 423 426 636 778 793 851 838 | 16 | 119 | 4, 5, v0.2 | NJ-14 Stop-loss checkpoint: go or no-go on the stretch pool (deferred set). NJ-15 Release candidate v0.1.0-rc.2 from PAP-254: /approve or /reject (RC2). NJ-19 Scope freeze: deferred list becomes milestone v0.2. NJ-20 Release candidate v0.1.0: /approve promotes and tags (RC3, PAP-254). NJ-21 PAP-5: close or keep as scoreboard (PAP-95 vs PAP-29). **RC2.** **RC3.** |
| 2026-09-20 06-12Z | 75: 158 195 221 222 230 231 277 405 411 417 427 856 880 883 402 408 412 424 770 772 774 794 805 816 841 857 885 888 845 852 854 858 860 865 867 868 871 875 884 891 897 900 418 707 906 137 149 157 218 232 278 403 406 425 869 903 515 516 536 889 576 598 632 633 634 635 637 638 650 689 735 737 738 751 771 | 16 | 71 | v0.2 | Queue drains. |
| 2026-09-20 12-18Z | 97: 773 775 777 780 781 782 783 785 786 788 789 795 796 797 798 799 801 804 806 808 809 810 811 817 818 819 821 822 823 825 826 827 839 840 842 846 853 855 859 861 866 872 876 881 882 886 887 892 409 419 554 843 890 898 899 902 905 907 913 428 513 514 517 518 535 577 639 640 686 687 688 690 708 723 736 752 764 776 779 784 787 800 802 803 807 812 820 824 829 830 831 832 844 870 873 874 901 | 16 | 85 | v0.2 | Queue drains. |
| 2026-09-20 18-24Z | 6: 724 828 904 909 910 911 | 16 | 38 | v0.2 | Queue drains. |

Longest chain (branch-start, 27.8 h): 13 -> 42 -> 32 -> 33 -> 267 -> 268 -> 565 -> 37 -> 663 -> 339 -> 340 -> 627 -> 341 -> 342 -> 343 -> 617 -> 618 -> 623 -> 624 -> 625 -> 420 -> 421 -> 422. Without the branch-start rule the same chain is 40.4 h. The schedule is capacity-bound (16 builders busy 15.7 of the time), so a slipped issue moves its milestone only if it sits on this chain or on the tables / identity / realtime P1 chains; Atlas re-simulates nightly and republishes this table.

## 3. Release-candidate checkpoints

| RC | When | Cut by | Must be true | Justin |
| -- | -- | -- | -- | -- |
| RC0 | 09-21 pm | Atlas by hand | Staging on the VPS (PAP-25, 30, 269); sign-in (PAP-223, 224); seeded tenant; Gates 1-2 green; orchestrator claiming (PAP-96); PAP-29 checkpoints C1-C3 timed. | Informational comment on PAP-5. |
| RC1 | 09-24 pm | Atlas, tag `v0.1.0-rc.1` via PAP-52 | RLS-backed permissions (PAP-227-229); installers (PAP-256, 257); Yjs server (PAP-140); codegen (PAP-120); Stripe test mode (PAP-177); story baselines (PAP-246). | NJ-11. |
| RC2 | 09-28 am | PAP-254, first real cut | Gates 1-4 green; grid and compiler (PAP-163, 165); comments (PAP-131); record sync (PAP-143); ledger and invoices (PAP-179, 180); imports (PAP-199); drill C1-C5 (PAP-29). Digest by hand (PAP-89 lands 09-29). | NJ-15 `/approve` or `/reject <reason>`. |
| RC3 = v0.1.0 | 10-01 am | PAP-254 + PAP-89 digest | Every non-deferred issue Done or Canceled with a reason; evidence from PAP-112, 160, 53, 147 attached; final burn report. | NJ-20 `/approve` promotes and tags. |

Freeze: no new claims after 09-30 12:00Z except `release-blocker` issues.

## 4. Credit burn model

Round 4: list price under mix B from the token model of `docs/cost-and-duration-estimate.md` section 3 (builder tokens by Size, Effort as labeled, reviewer 40% on Fable 5.1, QA gate 25% on Opus 5 for code issues, x1.25 contingency, RC reviews $68.75 each), booked on the day a session starts. *Build $* = builder sessions of Build / Infra issues; *QA $* = every reviewer session, QA gate and RC review; *Plan $* = Spec builders; *Docs $*, *Research $* = those builders. *To Justin* is the cumulative plan line x0.02 (billed as whole $2,500 chunks: 5 x $50 = $250 for the scheduled scope, +$100 with `v0.2`). The *allowance cross-check* is the old per-session allowance (S $10, M $22, L $50) summed over the day's builder starts: it tracks the builder columns within about 15%, so PAP-98 metering and the PAP-111 2x hard stop (S $20, M $44, L $100) keep their numbers. Raw rows: `plan/round4/sched/burn.json`.

| Day | Sessions S/M/L | Build starts P0/P1/P2 | Landed | Build $ | QA $ | Plan $ | Docs $ | Research $ | Day $ | Plan line $ | To Justin (x0.02) | Allowance cross-check $ |
| -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- | -- |
| 2026-09-18 (RC0) | 51/111/1 | 62/49/4 | 139 | 891 | 1,633 | 384 | 10 | 142 | 3,060 | 3,060 | $61.20 | 3,002 |
| 2026-09-19 (RC1) | 64/276/1 | 34/174/71 | 344 | 1,945 | 4,088 | 367 | 10 | 60 | 6,470 | 9,530 | $190.59 | 6,762 |
| 2026-09-20 (RC2, RC3) | 83/14/0 | 6/46/31 | 118 | 210 | 672 | 16 | 16 | 5 | 920 | 10,450 | $209.00 | 1,138 |
| v0.2 (after RC3) | 47/143/5 | 0/0/184 | 195 | 1,185 | 2,211 | 16 | 1 | 5 | 3,418 | 13,868 | $277.35 | 3,866 |

Reconciliation to the round-2 12/45/30/8/5 split (scheduled scope, mix B, list):

| Bucket | List $ | Share | To Justin | Round-2 share |
| -- | -- | -- | -- | -- |
| Planning (59 Spec builders) | $767 | 7% | $15.33 | 12% |
| Building (477 Build / Infra builders) | $3,048 | 29% | $60.96 | 45% |
| Automated QA (601 reviewer sessions, 477 QA gates, 4 RC reviews, 28 Review builders) | $6,391 | 61% | $127.83 | 30% |
| Docs (17 Docs builders) | $36 | 0% | $0.72 | 8% |
| Research (20 Research builders) | $208 | 2% | $4.16 | 5% |
| **Total** | **$10,450** | 100% | **$209.00** | |

QA is the largest bucket because the reviewer overlay runs on Fable 5.1 behind 374 Sonnet 5 builders; the retry pool ($360), the $500 RC3 reserve and the stop-loss rules of section 5 are unchanged and sit outside these figures.

## 5. Stop-loss rules

1. **Plan line.** Ledger compares cumulative spend with the plan-line column at 09:00Z. Two consecutive days above 115 percent: no more P2 claims, stretch pool cancelled. Any day above 125 percent, or 09-27 above 110 percent: only zero-slack-chain issues may be claimed, and one `Needs Justin` item offers cut list (PAP-174, 173, 101, 102, 113, 159, 186, 208, 192, in order) or top-up.
2. **Per issue.** At 80 percent of the 2x cap the session gets a wrap-up turn (PAP-111); at 100 percent it commits `wip:`, pushes and returns the issue to `Ready for Claude` with `retry-1`. Second failure: Decomposer splits it. Third: `Needs Justin`. Retries draw on the $360 pool, flagged at 75 percent.
3. **Reserve.** $500 is locked from 09-29 for RC3 fixes; only Justin releases it.
4. **Stretch pool.** Deferred issues are claimable only after NJ-14 says go and while the plan line is under 100 percent; cheapest first, never an L. Reinstating one means Atlas removes its `Deferred` label, restores its priority and deletes the deferral line under Goal; until then PAP-96 refuses to claim it.
5. **Throughput.** Fewer than 12 PRs landing on a day from 09-20 to 09-26: Atlas re-simulates and moves milestones instead of adding sessions.

## 6. Daily burn report (Ledger, 09:00Z, comment on the PAP-98 report issue)

```
Burn report <date> (day n of 15)
Spend yesterday $x | Cumulative $x of 10,000 (plan line $y, ratio r)
By bucket: plan $ / build $ / QA $ / docs $ / research $ (shares vs 12/45/30/8/5)
Sessions: started n (S/M/L), landed n, bounced n, retried n, killed at cap n
Retry pool $x of 360 | Reserve locked/unlocked
Most expensive: PAP-a $x (size, ratio), PAP-b, PAP-c
Chains (half-days vs plan): orchestrator, API/sync, permissions, gates, tables, release
Milestones moved: <name> <before> -> <after> (why)
Needs Justin open n/5 (ids) | Stop-loss: green / amber (rule 1a) / red (rule 1b)
Tomorrow: n claims (ids), peak sessions n
```

## 7. Milestone target dates moved by this schedule

Set via `projectMilestoneUpdate` on 2026-09-17 (before -> after, last issue in brackets). Early finishers keep their dates.

* agents / Roster defined and installed: 09-20 -> 09-24 (PAP-107)
* app-shell / Desktop and mobile shells build: 09-23 -> 09-24 (PAP-263)
* app-shell / Template scaffolds and runs on web: 09-19 -> 09-20 (PAP-18)
* collab / Comments and canvas: 09-26 -> 09-29 (PAP-136)
* collab / Docs and prompt log stores: 09-20 -> 09-23 (PAP-129)
* data-layer / Local-first sync working: 09-24 -> 09-25 (PAP-272)
* data-layer / Postgres + Drizzle baseline: 09-19 -> 09-22 (PAP-269)
* design-system / Tokens and primitives: 09-20 -> 09-22 (PAP-71)
* forge / Forgejo live and mirrored: 09-19 -> 09-20 (PAP-49)
* identity / Auth works across web and desktop: 09-20 -> 09-23 (PAP-58)
* libraries / Evaluation process: 09-19 -> 09-20 (PAP-211)
* pm-linear / Linear configured for the pipeline: 09-18 -> 09-20 (PAP-93)
* quality / Gates 1 and 2 on every PR: 09-20 -> 09-25 (PAP-248)
* quality / Visual and video gates: 09-25 -> 09-26 (PAP-84)
* realtime / Record sync and conflict UX: 09-26 -> 09-28 (PAP-144)
* realtime / Yjs server and presence: 09-22 -> 09-25 (PAP-142)
* spec-builder / Spec schema and validator: 09-22 -> 09-24 (PAP-116)
* tables / Grid with sort, filter, group: 09-23 -> 09-28 (PAP-166)
* tables / All view types: 09-27 -> 09-29 (PAP-167..170; round-2 FIX-1, must follow Grid at 09-28 because PAP-163 blocks all four views)
* growth / CRM core: 09-28 -> 09-29 (PAP-189; round-2 FIX-1, the CRM kanban needs PAP-167)

Round-2 FIX-1 (2026-09-17, milestone inversions): app-shell / Template scaffolds and runs on web stays at 09-20; PAP-26 deploy pipeline alone moved to Desktop and mobile shells build (09-24) because its staging deploy needs PAP-30 Postgres (09-22). Three `blocks` relations became soft dependencies with matching Dependencies text on both ends: PAP-239 -> PAP-97 (PAP-97 ships its own `orchestrator-event.json` schema and adopts `packages/contracts` later), PAP-235 -> PAP-180 (invoices use their own PDF template until `packages/ui-print` lands), PAP-88 -> PAP-29 (the first drill run does not need the release train). After these edits no blocker sits in a milestone dated later than the issue it blocks, across all remaining `blocks` relations.

Milestones holding deferred work (identity / Agent principals and enterprise, forge / Disaster recovery proven, growth / Campaigns and social, migration / Business migrations, input / Voice and accessibility certification) are not moved; their deferred issues go to a `v0.2` milestone at NJ-19.

## 8. Risks

* The issue cap (NJ-1) blocks the pending children of PAP-96, 101, 104, 110, 163, 164, 165, 171, 173, 174, 179, 180, 184, 199, 202, 205, 213, 214, 215; until it lifts those parents run as single L sessions using the pending specs, and the retry pool goes there first.
* PAP-256 and PAP-156 need macOS and Windows runners; if NJ-6 defaults, v0.1.0 ships unsigned installers and guidepup dumps.
* NJ-10, 12 and 13 have lead times; PAP-177, 184, 200 and 202 start against mocks.