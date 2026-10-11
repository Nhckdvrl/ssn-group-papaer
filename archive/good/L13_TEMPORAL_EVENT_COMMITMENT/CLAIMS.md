# L13 — Claim Ledger (calibrated 2026-09-11)

Scope decisions and the evidence licensing each wording are in `CLAIM_CALIBRATION.md`.
Status: `hypothesis` / `supported` / `weakened` / `rejected`.

> **Two wordings are banned.** "Timeline construction is not truth-preserving"
> (E12 falsifies it) and any headline that uses the *plain*-instruction instantiation
> rate as an error rate (the plain instruction says "events described", so listing is
> defensible). Headlines use the strict-instruction rate and the downstream propagation.

---

## C-A — Dissociation between judgement and emitted structure · **supported**

> Asked directly, LLMs judge the subordinate event of an unmarked `before`-clause as not
> guaranteed (P(NOT DETERMINED) 0.52–0.88 across models and both word orders, 80
> scenarios). Asked to emit an event structure from the same sentence, they emit it as
> realized at 0.875–1.000 in the natural post-posed order, against 0.138 for a matched
> non-temporal control. Under an instruction that **explicitly excludes unresolved
> events** the rate stays at 0.63–1.00 for three of four models, while the same
> instruction removes explicitly negated events in all four (0.23–0.90 → 0.03–0.43).

Evidence: E01, E04, E16. The Qwen3-8B exception recorded earlier was a **word-order
artifact**: on the fronted order it complies (0.338), on the natural post-posed order it
is at ceiling (1.000).

## C-B — The emitted event inventory governs the model's own belief · **supported**

> Emitting an event inventory raises realization commitment on identical text and an
> identical probe: +0.075 to +0.332 across 9 checkpoints and 4 families on v1, replicated
> on 80 scenarios at +0.114 to +0.398, against a form-matched paraphrase control and ~0
> on the matched non-temporal passage. A non-generative ordering demand moves it by
> ≤0.07, so the effect requires emission.

Evidence: E02, E05, v2 replication.

## C-C — Temporal order and event realization are independent · **supported**

> Enabling reasoning during structure construction takes emitted chronological order
> from 0.344 to 1.000 correct and instantiation of the unresolved event from 0.450 to
> 1.000 (Qwen3-8B); Qwen3-32B goes 0.925 → 1.000 order at 1.000 instantiation
> throughout. Across models the two are uncorrelated (Llama: order 0.150, instantiation
> 0.975).

Evidence: E09. **This is the title claim.**

## C-H — The trigger is enumeration, not ordering · **supported**

> The same failure occurs when the model is asked to list the events "in any order":
> instantiation 0.775 / 1.000 / 0.950 against a chronological 0.450 / 0.975 / 0.925, with
> the non-temporal control at ~0.10. Ordering is not required and removing it makes the
> failure slightly worse.

Evidence: E16. **This reframes the study from timeline construction to event extraction.**

## C-D — Scope: only where the construction alone carries non-veridicality · **supported**

> The failure does not extend to non-veridical events whose non-realization is marked,
> nor to unmarked non-veridicality outside the `before`-clause. On 80 scenarios:
> aspectual marking (*"was about to … when …"*) 0.200–0.212; a purpose infinitive
> (*"was there to … when …"*) 0.150–0.325; modal marking (*"before X could Y"*)
> 0.013–0.250 — against 0.875–1.000 for the unmarked `before`-clause. The decisive
> figure is the one-word pair `before Maya submitted` vs `before Maya could submit`,
> which moves instantiation by ≈0.8 with everything else held constant.

Evidence: E08, E12, E15, E16. Must appear in the abstract, not only in limitations.

## C-E — Downstream propagation · **supported**

> A reader consuming only the model's own emitted timeline inherits the false event:
> P(YES) on `before_neutral` rises +0.256 to +0.734, while `after` and the non-temporal
> control are preserved in both Qwen checkpoints.

Evidence: E13.

## C-F — Three natural prompt-level repairs fail · **supported**

> An explicit prohibition, an explicit three-state schema, and a status-first pipeline
> each nearly eliminate ghosting for explicitly negated events (0.35–0.90 → 0.00–0.08)
> and fail for unresolved ones.

Evidence: E04, E06, E10. Never state as "cannot be fixed".

## C-G — Not plausibility, not scale-fragile · **supported**

> No monotone dependence on item pragmatic bias (in the two models with headroom the
> rate is highest on items where non-occurrence is most plausible). Instantiation rises
> across the Qwen3 ladder, 0.450 (8B) → 0.975 (14B) → 1.000 (32B), with the control flat
> at 0.100 across all six checkpoints.

Evidence: E07, E11. Carry the n=4 caveat on `yes_leaning`.

---

## Rejected / weakened

| id | status | why |
|---|---|---|
| C1 direct over-commitment | **rejected** | models defer correctly when asked |
| C3 update asymmetry | **weakened** | floor-confounded; the floor-aware version is model-dependent |
| C4 representational coupling without generation | **rejected** | E05 |

## Open

1. **Independent annotation** of gold, naturalness and a ghost-node sample. Blocking.
2. **A second positive construction** (E15, purpose infinitives, running). One positive
   and two negative constructions licenses a mechanism-with-boundary paper, not a
   general claim about structure building.
