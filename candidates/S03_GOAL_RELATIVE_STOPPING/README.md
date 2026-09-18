# S03 — From Document End to Task Done

**Status:** PILOT IN PROGRESS
**Opened:** 2026-09-17
**Topic authority:** `ssn-taste/S03_FROM_DOCUMENT_END_TO_TASK_DONE.md`, `ssn-taste/SELECTED_TOPICS.md`

## Frozen scientific object

> How does post-training turn pretrained document/text-ending behaviour into
> goal-relative assistant stopping?

Sharper form:

> Is the information needed for goal-relative stopping already present in
> pretrained states so that post-training mainly changes the **stop readout**,
> or must post-training change **internal computation** before goal completion
> can control termination?

Everything in this directory serves `goal information -> stop action`
acquisition. Not an EOS benchmark, not a stopping leaderboard, not an
instruction-following study, not a response-length study, not a circuit hunt.

## Layout

```
src/        experiment code
stimuli/    E01 exact-prefix identification stimuli (instrument, NOT a benchmark)
results/    raw per-item measurements + logs
docs/       research log, preregistrations, decision records
```

## Instrument (E01)

Matched pair = two conditions with a **token-for-token identical assistant
prefix** and only the user goal changed, flipping whether the replayed prefix
already satisfies the request.

Two decision positions are read from one forward pass:

* `p1` — after the last content token; competitor = the item separator
* `p2` — after the separator; competitor = first token of the correct missing
  content (this is the S03-specified primary)

```
stop_margin = logit(stop) - logit(correct_next_missing_token)
d_goal      = stop_margin(complete) - stop_margin(incomplete)
```

`stop` is the log-sum-exp over every token id that actually terminates an
assistant turn for that checkpoint, so a dual-stop-token model is not
mismeasured.

Three deliberately non-isomorphic families:

| family | goal form | cardinality stated? |
|---|---|---|
| `A_bounded_quantity` | "give the first N" | yes |
| `B_semantic_predicate` | set-membership predicate | **no** |
| `C_slot_requirement` | requested field set | implicitly |

`B` is the family that decides whether the effect is more than counting: no
number appears anywhere in either prompt, only the predicate changes.

Every run also emits, per item, the continuation-awareness control (rank and
probability of the correct missing continuation in the incomplete condition).

## Current result

**Reading and clearing are different problems with different parameter loci.**

Pretraining already makes goal completion visible to the stop action, but at a
behaviourally inactive operating point. Post-training does two separable things:

1. **Reading** — making goal completion visible to the stop action. Already
   almost fully supplied by pretraining (`dz_stop` = +8.16 at base, 47/3 items,
   while p(stop) ~ 1e-4). Either locus can sharpen it: **4,097** stop-readout
   parameters take it to +14.48 with the state frozen; **6.9B** internal
   parameters take it to +12.73 with the entire output head byte-frozen.
   Readout capacity is not the limit — a 500x larger nonlinear readout over the
   same frozen state adds nothing.
2. **Clearing** — suppressing the still-plausible continuation once the goal is
   satisfied. A stop readout *structurally cannot* do this (`dz_cont` pinned at
   +0.67); internal-state change reaches −5.00, matching full SFT and the
   released checkpoint. This is the part that keeps growing with training
   budget.

Behavioural stopping is the sum. "Reuse vs new representation" fails not because
the answer is "both", but because the two loci are not competing to do the same
job.

Established across **three lineages and two stopping architectures**: OLMo-3
reuses one native `<|endoftext|>` for both roles, while Qwen2.5 and Llama-3.1
introduce a separate end-of-turn token. The effect follows the token that
actually ends the turn — in Llama-3.1 Instruct the document-end token moves
*against* goal completion (8/42) while the turn-end token moves strongly with it
(48/2).

### Two methodological traps this project fell into and climbed out of

- **A locus comparison at one training budget is not identified.** Two different
  wrong headlines came from reading a locus conclusion off a single budget.
- **`Δ log p(stop)` carries a whole-vocabulary normalizer term** that differs
  systematically by arm and can flip the apparent sign of an effect. Locus and
  architecture claims are stated on the raw stop logit or the gauge-free margin.

Numbers: `docs/RESULTS.md` (regenerate with `src/make_results.py`).

## Research log

See `docs/RESEARCH_LOG.md` — every entry records what was observed, what it
rules out, what remains, and why the next experiment discriminates.
