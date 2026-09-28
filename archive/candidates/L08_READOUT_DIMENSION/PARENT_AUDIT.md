# L08 — Audit of the Parent Result

**Parent:** Takeshita, Ponzetto et al., *Randomly Removing 50% of Dimensions in Text
Embeddings has Minimal Impact on Retrieval and Classification Tasks*, EMNLP 2025 Main
(People's Choice). https://aclanthology.org/2025.emnlp-main.1410/

**Audited:** 2026-09-10, from the published PDF (`aclanthology.org/2025.emnlp-main.1410.pdf`).

This file records **what the parent actually establishes**, because L08's research
question is defined relative to it. We do not re-gamble the phenomenon; we do need
to know precisely which parts of it are load-bearing.

---

## 1. The intervention, verbatim

> "we consider two LLMs, Llama 3.1 8B and Qwen 2.5 7B, and evaluate on various six
> tasks after removing half of the last hidden representations **before they are
> projected to the vocabulary space** [...] We test removing the first and last half
> of the representations, and **reduce the unembedding matrix correspondingly**. We
> use Language Model Evaluation Harness for our evaluation."

So: keep coordinate set `S`, and `logits' = W_U[:, S] h[S]`. Transformer weights and
every layer's computation are untouched; only the hidden→vocabulary readout changes.
Masks are structured (first half / last half), not random, for the LLM experiments.
`src/readout.py` implements exactly this and `scripts/validate_intervention.py`
verifies the algebraic identity.

## 2. Reported LLM numbers (Table 3, main text)

| Model | Task | Full | First | Last |
|---|---|---|---|---|
| Llama 3.1 8B | MMLU (acc) | 0.681 | 0.580 (0.852) | 0.586 (0.861) |
| Llama 3.1 8B | SQuAD-v2 (best exact) | 51.87 | 50.07 (0.965) | 50.07 (0.965) |
| Llama 3.1 8B | GSM8K (EM strict) | 0.764 | 0.009 (0.012) | 0.014 (0.018) |
| Qwen 2.5 7B | MMLU (acc) | 0.718 | 0.709 (0.988) | 0.709 (0.987) |
| Qwen 2.5 7B | SQuAD-v2 (best exact) | 50.12 | 50.07 (0.999) | 50.07 (0.999) |
| Qwen 2.5 7B | GSM8K (EM strict) | 0.766 | 0.045 (0.059) | 0.011 (0.014) |

## 3. Finding A — the SQuAD-v2 "survival" is a metric floor, not preserved capability

`best_exact` is the SQuAD-2.0 official metric that **sweeps a no-answer threshold and
reports the best achievable exact match**. It therefore cannot fall below the score
of the constant "everything is unanswerable" predictor, i.e. the unanswerable
fraction of the split.

SQuAD-2.0 dev contains 11,873 questions, 5,945 unanswerable:

```
5945 / 11873 = 0.5007159... = 50.07 %
```

**All four truncated conditions report exactly 50.07** — two different models, two
different masks, one number, equal to the floor to 4 significant figures. Qwen's
*full-model* score (50.12) is itself only 0.05 above that floor.

The parsimonious reading is that under truncation both models answer essentially
**zero** answerable SQuAD questions correctly, and `best_exact` reports the
all-unanswerable baseline. If so, SQuAD-v2 did not survive; the metric hid a total
collapse.

This is a reading of a published table, not yet a measurement. **E01 tests it
directly** by reporting `HasAns_exact` (exact match restricted to answerable
questions), which has no such floor, alongside the `best_exact` floor for
comparability.

## 4. Finding B — three of the six task results are not independently readable

Appendix Table 4 reports COPA, DROP and HellaSwag. As printed:

- the **COPA F1 and DROP F1 columns are numerically identical in every one of the
  six rows** (Llama 0.194 / 0.094 / 0.038; Qwen 0.003 / 0.001 / 0.001);
- the **HellaSwag Acc column is numerically identical to the MMLU Acc column of
  Table 3** (0.681/0.580/0.586 and 0.718/0.709/0.709);
- COPA is a binary-choice task, so an F1 of 0.194 (Llama) or 0.003 (Qwen) at *full*
  readout is far below chance.

We treat COPA, DROP and HellaSwag as **not usable evidence** and build no claim on
them. This is a presentation problem in the parent, not a scientific attack, and the
paper's own conclusion about text encoders is unaffected.

## 5. What the parent therefore actually establishes for LLMs

After Findings A and B, the knowledge-vs-reasoning contrast rests on:

- **one surviving task**: MMLU — scored by *ranking four given candidate
  continuations* by log-likelihood, one scored decision per item;
- **one collapsing task**: GSM8K — scored by *free greedy generation*, ~100 sequential
  unconstrained arg-max decisions over a ~150k vocabulary, exact-match on the last one.

These two tasks differ simultaneously in **three** ways:

| | MMLU | GSM8K |
|---|---|---|
| **Protocol** | rank K = 4 given candidates | arg max over V ≈ 150k |
| **Depth** | 1 scored decision | ~10^2 sequential decisions |
| **Content** | factual recall | multi-step computation |

The parent reads the contrast on the **content** axis ("task-dependent", GSM8K as
the reasoning case) and explicitly defers the LLM case:

> "the high relative performance is not observed in all datasets, e.g., on GSM8K, the
> original performance is heavily lost with all models and reducing methods, **leaving
> a dedicated study on LLMs for our future studies**."

## 6. Consequence for L08

The anomaly L08 must explain is real and is an award-paper result. But the
*capability* reading of it is a hypothesis, not an observation: it is one of three
fully confounded factors, supported by an n = 1 vs n = 1 comparison in which one of
the two remaining "survivor" data points (SQuAD-v2) is metric-floored.

L08's job is therefore **not** "why is reasoning more dimension-hungry" — that
presupposes the answer. It is:

> **On which axis does the final-readout bottleneck actually live — the capability
> being exercised, or the decision protocol through which it is read out — and what
> law governs it?**

See `README.md` for the mainline this implies.
