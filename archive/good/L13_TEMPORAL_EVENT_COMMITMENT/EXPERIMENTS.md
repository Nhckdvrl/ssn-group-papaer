# L13 — Experiment Registry

## E01 — Commitment profile (fact_first)

- **Claim:** C1, C3.
- **Question:** under an unresolved `before`-clause, does realization commitment exceed
  a matched non-temporal unresolved control, and is later resolution symmetric?
- **Why necessary:** it is the cheapest measurement that can separate "the model holds
  the event open" from "the model treats mention-in-a-temporal-relation as occurrence",
  and the non-temporal control is what makes a low `NOT_DETERMINED` rate interpretable.
- **Data:** `data/stimuli_v1.jsonl`, 40 bases × 5 conditions, paired within base.
- **Models:** `configs/pilot_v1.json` (qwen3-8b, llama3.1-8b-instruct, olmo3-7b-instruct-dpo,
  gemma3-12b-it, qwen3-32b) — 4 families plus one within-family scale contrast.
- **Metric:** normalised label probability mass, averaged over all 6 option
  permutations; paired bootstrap over bases (10k, 95% percentile CI).
- **Controls:** option-order permutation (position/letter bias), `nontemporal_neutral`
  (middle-label availability), P2 likelihood (strict vs pragmatic channel).
- **Interpretation / kill:** `PILOT_CARD.md`.
- **Command:** `scripts/run_pilot.sh <slug> <gpu>` then `scripts/summarize_commitment.py`.
- **Status:** running 2026-09-11.

## E02 — Timeline-induced actualization

- **Claim:** C2.
- **Question:** does forcing an explicit chronological timeline before the identical
  realization probe raise commitment on the unresolved event?
- **Why necessary:** it converts a correlational profile into a task-level causal
  statement and is the part no factuality benchmark can produce.
- **Design:** same items and same probe under `fact_first` / `timeline_first` /
  `paraphrase_first`. The paraphrase arm is load-bearing: it matches "the model
  generated something about the passage first" without asking for a timeline, so the
  timeline effect is not confounded with generic self-conditioning.
- **Primary quantity:** `timeline_first_effect__before_neutral`, and the
  difference-in-differences `timeline_minus_paraphrase__before_neutral`.
- **Status:** run jointly with E01 (same invocation).

## E03 — Descriptive: ghost nodes in generated timelines

- **Status:** descriptive only, never load-bearing for a claim.
- Counts how often a generated timeline lists the unresolved subordinate event as an
  ordinary realized node. Illustrative material; automatic detection is approximate and
  is reported as such.

## Not authorized yet

Human validation of `before_neutral` gold (required before any paper-level claim),
incremental-discourse trajectory measurement, hidden-state patching of the connective,
natural-corpus replication.
