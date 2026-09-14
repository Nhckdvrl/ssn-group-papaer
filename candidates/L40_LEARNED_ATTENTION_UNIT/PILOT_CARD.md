# L40 — E01 Pilot Card

**Candidate:** L40 — The Unit of Learned Attention  
**Authorization:** `E01 ONLY`

## Locked scientific sentence

> **After distinct linguistic histories have converged on the same current cue use, does an identical new learning event still reveal a history-dependent bias, and if so is that bias attached to a formal cue class or to a particular form–grammatical-function relation?**

---

# 1. Non-negotiable separation

E01 has two stages that must not leak into one another.

### E01-A — instrument construction

May inspect only current-state/equivalence quantities.

### E01-B — challenge

May inspect future-learning estimands only after grammar, tokenizer, model, history budget, common-state duration, equivalence margins, challenge data and primary statistic are frozen.

If challenge outcomes influence any of those choices, the run is contaminated and must be repeated with fresh seeds.

---

# 2. History design

Two cue classes:

- `M`: bound morphology;
- `L`: free lexical/function cue.

Two grammatical functions:

- `T`: TENSE;
- `N`: NUMBER.

Four randomized histories:

```text
MM: T <- M ; N <- M
ML: T <- M ; N <- L
LM: T <- L ; N <- M
LL: T <- L ; N <- L
```

Both cue classes remain present in every arm. Manipulate predictiveness/contingency, not raw presence.

The critical `ML` and `LM` arms must be exactly matched on total M exposure, L exposure, predictive M events, predictive L events, T/N events, token budget, training steps, entropy and stem inventory.

---

# 3. Surface/tokenization gate

Before confirmation seeds, verify that cue classes are not confounded by:

- token count;
- BPE segmentation;
- marker length;
- frequency;
- position;
- vocabulary size;
- number of supervised target tokens.

Use a fixed character/byte or purpose-built tokenizer if ordinary subword tokenization gives one cue class an accidental advantage.

---

# 4. Common-state phase

All histories receive the same common-language experience in the same data order.

Choose common-phase duration on development seeds using **only equivalence metrics**. Never inspect future challenge outcomes while calibrating this phase.

Before challenge, `ML` and `LM` must fall within frozen equivalence margins on:

1. held-out TENSE competence;
2. held-out NUMBER competence;
3. `M`-only TENSE use;
4. `M`-only NUMBER use;
5. `L`-only TENSE use;
6. `L`-only NUMBER use;
7. cue-conflict preference for both functions;
8. common-corpus LM loss;
9. initial held-out loss on every future challenge family.

If equivalence fails, stop. No residualization rescue.

---

# 5. Future challenge

Clone each matched checkpoint into frozen branches using novel cue markers and preferably novel stems.

```text
C1: novel M -> T
C2: novel M -> N
C3: novel L -> T
C4: novel L -> N
C5: unrelated new relation control
```

Within each challenge branch, histories receive byte-identical examples in the same order with the same optimizer/update count.

---

# 6. Primary estimand

For history `H` and future relation `F`:

```text
G(H,F) = heldout_loss_before - heldout_loss_after_fixed_early_update
```

Also freeze a short early-learning AUC before saturation.

The decisive morphology crossover is:

```text
G(ML, M->T) > G(LM, M->T)
G(ML, M->N) < G(LM, M->N)
```

with the mirror pattern for free cues.

This reversal cannot be explained by total morphology exposure because `ML` and `LM` contain the same amount of predictive morphology.

---

# 7. Decision table

| observation | interpretation | decision |
|---|---|---|
| clean cue×function crossover, no broad C5 shift | form×function-specific learning state | PASS / develop |
| `MM/LL` cue-class effect across functions, weak mixed crossover, no broad C5 shift | cue-class-wide state | PASS / develop |
| no history effect after valid current-state matching | current-state sufficiency; strong latent-associability account unnecessary | scientific null; re-select paper scope |
| broad C5 + all-branch shift without theory-specific interaction | generic plasticity | KILL L40 |
| residual current cue-use differences predict challenge | identification failed | instrument failure |
| effect appears only after model/marker/common-length shopping | phenomenon gambling | kill contaminated E01 |

---

# 8. E01 hard rules

1. No model-family shopping after challenge results.
2. No changing TENSE/NUMBER after a null crossover.
3. No choosing marker forms post hoc.
4. No selecting seeds by effect direction.
5. No mechanistic interpretability before the learning-state quantity is established.
6. No rescue from generic plasticity by activation analysis.
7. Null after a valid equivalence gate is an allowed scientific answer.
8. Generated sentences are not independent training replications; uncertainty must be estimated across independent model seeds/checkpoints appropriately.

---

# 9. Minimum E01 report

Return:

1. frozen generator/tokenization contract;
2. history-balance table;
3. history-competence table;
4. common-state equivalence table and margins;
5. pre-challenge equivalence table;
6. early-learning curves for C1–C5;
7. seed-level morphology and free-cue crossover statistics with uncertainty;
8. `MM` vs `LL` global cue-class contrast;
9. unrelated-control result;
10. one preregistered decision from the table above.

Do not broaden the claim in the pilot report.