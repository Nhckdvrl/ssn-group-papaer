# L13 — Data and Gold Contract

Version: **stimuli_v1** (2026-09-11). Builder: `scripts/build_stimuli.py`.
Artifact: `data/stimuli_v1.jsonl` (regenerable, deterministic, tracked).

## 1. Unit of analysis

One **base scenario** = one agent, one target event `E`, one main-clause event `M` that
is a plausible blocker of `E` when it precedes `E`. The base is the unit for all
statistics; conditions are within-base and paired.

40 bases × 5 conditions = **200 items**.

## 2. Conditions

For base *Maya / "Maya submitted the application" / "the portal closed"*:

| condition | passage | strict gold |
|---|---|---|
| `after` | After Maya submitted the application, the portal closed. | `YES` |
| `before_neutral` | Before Maya submitted the application, the portal closed. | `NOT_DETERMINED` |
| `before_confirm` | Before Maya submitted the application, the portal closed. She managed to send it by email later that evening. | `YES` |
| `before_cancel` | Before Maya submitted the application, the portal closed. The closure was permanent and she never sent it. | `NO` |
| `nontemporal_neutral` | Maya planned to submit the application. The portal closed at midnight. | `NOT_DETERMINED` |

`after` and `before_neutral` differ **only** in the connective; this is checked
mechanically by `scripts/validate_stimuli.py`.

`nontemporal_neutral` is load-bearing, not decoration: it establishes that the model
will use the middle label at all on this material, so that a low `NOT_DETERMINED` rate
under `before_neutral` cannot be explained by label avoidance.

## 3. Probes

Both probes use the identical target proposition string `E` in every condition.

- **P1 strict commitment.** "Based only on the passage, does the passage guarantee that
  *E*?" → `YES` / `NO` / `NOT DETERMINED`. Scored by label-token log-probabilities over
  the three options; every item is scored under **all 6 option permutations** and
  averaged, removing option-position and label-letter bias.
- **P2 occurrence likelihood.** "How likely is it that *E* (eventually) happened?" on a
  1–5 scale, scored the same way over the five digits.

P1 and P2 are reported separately and never merged. Their dissociation is itself a
result: strict non-entailment and pragmatic expectation are different quantities, and
conflating them is the documented failure mode of prior semantic-paradox benchmarks.

## 4. Task-order manipulation

Identical passage and identical P1 probe under two task orders:

- `fact_first`: probe directly.
- `timeline_first`: the model is first asked to list the events of the passage in
  chronological order; its own generated timeline is appended to the context; then the
  same P1 probe is scored.

This manipulation, not the raw error rate, is the decisive evidence for Account B.

## 5. Gold definition and its limits

Gold is **strict semantic licensing by the passage**, not real-world plausibility.
- `after` → the subordinate clause is veridical; `YES` is entailed.
- `before_neutral` → `before` is non-veridical and `M` is a plausible blocker, so the
  passage licenses neither `YES` nor `NO`.
- `before_confirm` / `before_cancel` → later text asserts realization / non-realization
  explicitly.

**Declared risk.** For `before_neutral` many readers draw a pragmatic inference that `E`
happened. That is why the probe wording is "does the passage guarantee" and why P2
exists as a separate channel. We do **not** score `before_neutral` as "model wrong if it
says YES to likelihood".

## 6. Human validation (required before any claim leaves pilot status)

Before `before_neutral` gold is used in a paper-level claim, 3–5 proficient English
annotators rate every item on:
1. naturalness (1–5);
2. strict commitment (`YES` / `NO` / `NOT DETERMINED`) — the same P1 wording;
3. occurrence likelihood (1–5) — the same P2 wording.

Items whose human strict-commitment majority disagrees with gold, or whose naturalness
median < 4, are dropped and reported. Pilot results computed before validation are
labelled provisional in `EXPERIMENTS.md`.

## 7. What we do not do

- No LLM-generated gold. Passages are hand-authored; labels follow from the construction.
- No synthetic world, ontology, or template zoo. One sentence pattern, natural English.
- No claim that `before` means "did not happen".

## 8. External validity (later, not in pilot)

Natural-text replication using existing temporal + factuality annotation (UDS
factuality/time on EWT, RED, MAVEN-FACT) is planned only if the controlled pilot
establishes coupling. It is validation, not the main estimand.
