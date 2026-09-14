# L34 E01 — G0 verdict and the blocked primary estimand

**Date:** 2026-09-14
**Runs:** 11 complete (`PIT_A`×3, `PIT_B`×3, `PIT_BAL`×2, `NO_PIT`×3), shared trunk, Llama-3.2-3B base.
**Read first:** [`G1_RESULTS.md`](G1_RESULTS.md) — the instrument gate already failed.

---

## 1. G0 — the mother check also fails, and it fails *inverted*

Mean gold-answer NLL/token, held-in templates (**lower = better**), vs the no-curriculum reference:

| arm | OLD | Δ vs `NO_PIT` | NEW | Δ vs `NO_PIT` |
|---|---|---|---|---|
| `NO_PIT` | 1.2235 | — | 0.2797 | — |
| `PIT_BAL` | 2.2623 | **+1.0387** [+1.021, +1.057] | 0.7705 | **+0.4908** [+0.483, +0.499] |
| `PIT_A` | 2.5118 | **+1.2882** [+1.273, +1.304] | 1.1987 | **+0.9190** [+0.910, +0.928] |
| `PIT_B` | 2.0978 | **+0.8742** [+0.856, +0.892] | 0.7285 | **+0.4488** [+0.439, +0.459] |

Held-out templates give the same picture (all arms +0.64 to +1.19 worse than `NO_PIT`).

Forced-choice top-1 against 15 same-pool distractors (no decoding) agrees:

| arm | OLD held-in | NEW held-in | OLD held-out | NEW held-out |
|---|---|---|---|---|
| `NO_PIT` | **75.3%** | **99.8%** | **73.2%** | **99.5%** |
| `PIT_BAL` | 54.8% | 99.1% | 48.7% | 91.3% |
| `PIT_A` | 49.4% | 91.6% | 47.9% | 87.7% |
| `PIT_B` | 57.9% | 98.8% | 53.9% | 98.3% |

> **Every access-curriculum arm is worse than no curriculum at all, on both OLD and NEW facts,
> on both measures, on both template sets.**

G0 required a PIT-style *advantage* for the curriculum on NEW facts. The instrument produces a
large, consistent *disadvantage*. The parent phenomenon is not merely absent — it is reversed.

This independently confirms the `G1_RESULTS.md` §3 root cause: an access curriculum whose answers
are permanently ungrounded is net-destructive, not net-instructive.

### The preregistered G0 escalation does not apply

`E01_PREREGISTRATION.md` §6 G0 permits one escalation (3B → 7B/8B) if the parent phenomenon is
absent. That clause anticipates an effect **too small to resolve at 3B**. What was observed is a
large effect of the **wrong sign** with a mechanism identified in the G1 diagnostic. More parameters
would reproduce the same construct fault at higher cost. **Escalation is therefore not taken**, and
no 7B/8B run is launched.

## 2. The primary estimand is large, positive — and must be discarded

Recorded for reproducibility only. **This is not evidence for Account A.**

| template set | `CROSS(OLD)` | `CROSS(NEW)` | **`PROSPECTIVE`** |
|---|---|---|---|
| held-in | +0.0910 [+0.061, +0.121] | +0.5124 [+0.492, +0.533] | **+0.4215** [+0.386, +0.458] |
| held-out | +0.0255 [−0.003, +0.054] | +0.8388 [+0.817, +0.861] | **+0.8134** [+0.777, +0.849] |

On its face this clears every numeric condition in G2: positive, CI excluding 0, twenty to forty
times the 0.02 nats/token floor, mirror-consistent (`PREF(PIT_A, NEW)` = +0.230 vs
`PREF(PIT_B, NEW)` = −0.282, opposite signs), and it replicates on held-out paraphrases.

**It is still void**, for reasons fixed before any run:

1. **G1 failed.** Neither arm improved the family it was trained on (`G1_RESULTS.md` §2). There is
   no demonstrated access specialization for the NEW-vs-OLD contrast to be a specialization *of*.
2. **G0 failed inverted.** All curriculum arms are far worse than `NO_PIT`. The "preference" being
   measured is *which family was damaged less*, not which was encoded better. A crossover among
   uniformly damaged arms cannot show that anticipated access improved encoding.
3. **The OLD crossover changes sign across phases** — −0.155 post-Phase-1, +0.091 post-Phase-2
   (held-in). A stable encoding property should not invert when identical documents are added.

The most likely reading of the +0.42/+0.81 is a **answer-format-prior × recency** interaction: the
curriculum installs a family-shaped answer prior, and freshly written NEW facts are more exposed to
that prior than consolidated OLD facts. That is a fact about the instrument, not about prospective
encoding.

> This is exactly the outcome the preregistration existed to catch: the decisive-looking number came
> out big, positive, significant and paraphrase-robust, and it is worthless because the validity
> gates ahead of it failed. Reporting it would have been a false positive.

## 3. Status

- E01 is **closed**. It did not test L34's scientific question.
- L34 is **not** killed by this run, and is **not** supported by it.
- Accounts A, B and C are all untouched.
- Next step is Selection-level, not another run: see `G1_RESULTS.md` §5 for the grounding
  constraint any successor instrument must satisfy.

## 4. Artifacts

`results/e01/final_l3b_*.json` (11), `results/e01/post_p1_l3b_*.json` (8), logs in `results/logs/`.
Analysis is `src/analyze.py`; the estimands were not edited after seeing any result.
