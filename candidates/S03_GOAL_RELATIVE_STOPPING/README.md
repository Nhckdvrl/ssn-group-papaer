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

## Research log

See `docs/RESEARCH_LOG.md`.
