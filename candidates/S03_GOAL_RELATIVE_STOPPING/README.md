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

Olmo-3 7B base, four parameter-locus arms on the same 12k ordinary Tülu-3
examples, verified bit-exact freezes, 2 seeds, 3 training budgets.

Goal-relative stopping is acquired through **two components with different
budget scaling**:

1. a large **readout** component available immediately from the frozen
   pretrained state — a 4,097-parameter delta on the single stop output row,
   every non-stop logit bit-exactly unchanged, reaches `d_stop` +6.70 from a
   base of +2.58, and extra readout capacity adds nothing;
2. a smaller but **growing state** component — full adaptation wins at every
   budget, by +0.80 at 250 steps and +2.34 at 2250, while the readout route
   saturates.

A locus comparison at a single budget is not identified: this project produced
two different wrong headlines that way before the budget ladder settled it.

## Research log

See `docs/RESEARCH_LOG.md` — every entry records what was observed, what it
rules out, what remains, and why the next experiment discriminates.
