# E05 — Sequence-Landscape Audit

**Date:** 2026-09-17  
**Status:** FROZEN BEFORE E05 EXECUTION  
**Purpose:** decide whether L36 has a Main-level sequence-distribution story after retiring the EOS / generation-boundary identity as the primary explanation.

---

## 1. Research question

> **Why does progressively mode-seeking search degrade classical sequence models, while many modern post-trained LMs appear more stable, and what structural change in the full sequence-level probability landscape accounts for that transition?**

Lineage version:

> **Within a fixed autoregressive lineage, how do Base → SFT → preference/RL stages change the relation among sequence probability, task utility, typical probability mass, and search accessibility?**

This experiment explicitly does **not** assume that EOS, length, SFT, architecture, or scale is the cause.

---

## 2. Scientific object

For input `x`, model `M`, and a decoder that becomes increasingly mode-seeking with strength `s`, let the returned sequence be `y_s`.

Primary observables:

- `S_s = log p_M(y_s | x)` — raw cumulative sequence score;
- `U_s = utility(y_s, x)` — task utility, primarily COMET/XCOMET where available, with BLEU/chrF as secondary surface metrics;
- structural failure labels — empty, short, copy/source leakage, repetition, generic/off-task, language failure.

The primary phenomenon is the **within-input search–utility trajectory** as mode seeking increases:

- classical curse-like regime: model score increases while utility decreases;
- stable regime: model score increases while utility is stable or improves.

The project is not about a generic across-example correlation between likelihood and quality.

---

## 3. Systems

### 3.1 Classical endpoint

Primary:
- `facebook/wmt19-en-de` under raw cumulative scoring.

Breadth if compute permits:
- one independent Marian/OPUS-style NMT family;
- existing WMT19 direction panel can be reused as secondary breadth.

### 3.2 Same-lineage modern systems

Primary lineage:
- Olmo-3 Base;
- Olmo-3 SFT;
- Olmo-3 DPO;
- Olmo-3 RLVR.

Independent lineage:
- Tülu-3 Base;
- Tülu-3 SFT;
- Tülu-3 DPO / RLVR where compatible checkpoints exist.

Modern endpoint:
- Gemma-3 instruct model already used in the matched-RAW experiment.

### 3.3 Interface policy

Two analyses must be kept separate:

1. **native/deployed interface phenotype** — each post-trained model evaluated under its intended interaction format; answers the ecological `classic vs modern` question;
2. **within-lineage fixed serialization** — only where every stage retains adequate translation competence under a shared serialization. If a base checkpoint cannot operate under a chat template, that comparison is not used to claim a training-stage causal effect.

No claim may silently mix these two analyses.

---

## 4. Fixed substrate

Primary substrate:
- the same frozen En→De test subset already used by L36, with the exact source/reference ids preserved.

Suggested execution sizes:
- `n=400` for inexpensive trajectory probes;
- `n=100–200` for heavy sampling / constrained-search analyses;
- a frozen `n=50` qualitative audit set for manual pathology inspection.

The substrate must not be changed after seeing E05 results except for documented engineering failures.

---

## 5. E05-A — Search–utility trajectory

### 5.1 Beam arm

Raw cumulative sequence score; no length normalization in the primary analysis.

Beam widths:

`b ∈ {1, 4, 16, 64, 128}`

and `512` on a smaller frozen subset where computationally feasible.

For every `x, model, b` save:

- generated sequence;
- raw cumulative log probability;
- token count / length ratio;
- BLEU, chrF;
- COMET/XCOMET or another established semantic MT metric;
- empty flag;
- source-copy ratio;
- repetition score;
- target-language ID / off-language flag;
- exact token-level conditional log probabilities along the returned path.

### 5.2 Independent mode-seeking arm: likelihood-ranked Best-of-N

Beam-specific artifacts are a major alternative explanation. Therefore run an independent procedure:

1. draw `N` stochastic samples from the model under one frozen sampling policy;
2. rescore every sampled full sequence under the same model using raw cumulative sequence probability;
3. return the highest-likelihood sample.

`N ∈ {1, 4, 16, 64, 128}`.

Sampling policy is fixed before results (e.g. ancestral where numerically feasible, otherwise one fixed temperature/top-p setting used for all N within a system). Do not tune sampling separately for a desired result.

This arm asks whether moving toward high-probability sequences is harmful **independently of beam implementation**.

### 5.3 Primary readout

For each model, summarize paired within-input changes as mode seeking increases:

- `ΔS = S_high - S_low`;
- `ΔU = U_high - U_low`.

The main descriptive object is the joint distribution of `(ΔS, ΔU)`, not only an aggregate BLEU curve.

A model is `mode-seeking fragile` if stronger mode seeking reliably raises model score while lowering semantic utility for a substantial fraction of inputs. A model is `mode-seeking stable` if score rises without a corresponding utility loss.

No arbitrary universal scalar threshold is preregistered as a scientific law; confidence intervals and paired effect sizes are reported.

---

## 6. E05-B — Mode–Mass Gap

This extends the static NMT mode-vs-distribution question to modern training stages.

For each input/model, collect a frozen sample set `Y_sample` (target `K=64` or `128`).

Define a descriptive gap:

`MMG(x) = median_{y∈Y_sample} U(y) - U(y_mode_like)`

where `y_mode_like` is the most mode-seeking sequence available from the beam/Best-of-N audit. Also report mean and upper-quantile sample utility; the median is primary because a few malformed samples should not dominate.

Additional typicality diagnostics:

- percentile of `y_mode_like` in the sample distribution by length;
- percentile by token-average surprisal;
- percentile by semantic utility;
- source-copy / repetition percentile.

Interpretation:

- large positive MMG: typical sampled outputs are better than the extreme high-probability output;
- near-zero or negative MMG: mode-like outputs are no worse than typical probability mass.

This is a descriptive extension of mode-vs-mass work, not a claim that the metric itself is novel.

---

## 7. E05-C — Common-candidate cross-stage rescoring

Search produces different candidates at different stages; candidate-set changes can masquerade as probability-landscape changes. Therefore construct a shared candidate pool per input:

`C(x) = union{reference, greedy outputs, all beam outputs, all Best-of-N winners, a frozen subset of samples, known pathological outputs}`

from all stages in a lineage.

Then rescore **the identical strings** under every compatible checkpoint.

For every candidate `y ∈ C(x)` and checkpoint `M_t`, save:

- raw sequence log probability;
- normalized log probability as secondary diagnostic only;
- semantic utility;
- pathology labels.

Primary pairwise question:

> Across stages, does the probability margin between adequate and pathological full sequences systematically change?

For matched adequate/pathological pairs within each input:

`margin_t = log p_t(y_adequate|x) - log p_t(y_pathological|x)`.

A post-training `mode repair` story requires a reproducible positive shift in these margins, not merely lower EOS probability.

This analysis is especially important because it isolates **probability reordering of full sequences** from changes in the search algorithm.

---

## 8. E05-D — Search-path geometry

For final sequences from representative successful and failed cells, record the complete path of conditional token scores.

Diagnostics, deliberately borrowing existing discrepancy literature rather than claiming a new metric:

- rank of each chosen token among next-token alternatives;
- local log-probability gap to the best next token;
- first large discrepancy position;
- cumulative score deficit after the discrepancy;
- subsequent compensation by unusually high conditional probabilities;
- EOS/termination event position if applicable.

Compare at least three pathology types:

1. classical empty/short termination;
2. non-empty generic/copy/repetition failure in base LMs;
3. stable high-quality post-trained outputs.

Question:

> Does post-training alter the multi-token path structure by which bad high-probability basins become reachable, or does it only move the termination channel?

Because discrepancy-based explanations already exist, novelty can only lie in the **training-stage transition / modern-LLM comparison**, not the existence of discrepancy compensation itself.

---

## 9. E05-E — Length-conditioned score envelope (secondary mechanistic visualization)

For a frozen small subset, approximate

`F_x(L) = max_{|y|=L} log p(y|x)`

using constrained beam search or the union candidate pool binned by length.

This is not required to pass E05, but can reveal whether the high-score basin moves from:

- empty/ultrashort lengths in classical NMT;
- normal-length but generic/copy sequences in base LMs;
- adequate-length, high-utility sequences after post-training.

Treat this as a visualization/diagnostic unless the approximation is demonstrably reliable.

---

## 10. Pathology taxonomy

Every low-utility high-probability output in the manual audit set is assigned one or more labels:

- `EMPTY`;
- `SHORT_INCOMPLETE`;
- `SOURCE_COPY`;
- `GENERIC_OFF_TARGET`;
- `REPETITION`;
- `WRONG_LANGUAGE`;
- `SEMANTIC_MISTRANSLATION`;
- `OTHER`.

The central question is whether the **dominant failure basin changes across model regimes**. Do not collapse all quality degradation into the EOS category.

---

## 11. Predictions

These are hypotheses, not committed findings.

### H1 — phenotype transition
Classical NMT will show strong negative search–utility trajectories under raw mode-seeking. At least some post-trained in-format LMs will show substantially flatter or positive trajectories.

### H2 — pathology migration
Base LMs may remain mode-seeking fragile but fail through non-empty generic/copy/repetition basins rather than the classical short/empty basin.

### H3 — mode–mass transition
At least one same-architecture lineage will show a materially smaller Mode–Mass Gap after post-training than at base stage.

### H4 — full-sequence probability reordering
Common-candidate rescoring will show adequate-vs-pathological probability margins shifting toward adequate outputs across at least one post-training transition.

### H5 — termination is only one special case
Changes in first-step EOS/stop geometry will explain the termination channel but will not account for all changes in search–utility trajectory.

---

## 12. Falsifiers / stopping rules

The Main-level sequence-landscape story is **killed or sharply downgraded** if:

1. no reproducible change in search–utility trajectory appears across at least two modern lineages;
2. beam degradation differences vanish under likelihood-ranked Best-of-N, indicating a beam-implementation phenomenon rather than a distributional one;
3. common-candidate rescoring shows no systematic full-sequence adequate-vs-pathological probability reordering across post-training stages;
4. modern post-trained models retain a Mode–Mass Gap comparable to classical/base systems despite superficially different failure forms;
5. all apparent stability is explained by length normalization, stopping conventions, or incompatible prompting rather than raw model probabilities;
6. only termination/length changes while non-empty mode pathology is unchanged, leaving no broader sequence-level transition.

If these falsifiers trigger, keep the existing termination-channel work as a narrower result and do not force the Main story.

---

## 13. What E05 deliberately does not claim

- It does not claim beam search itself is the scientific object.
- It does not claim higher model likelihood should universally imply higher correctness.
- It does not claim post-training always improves calibration.
- It does not claim SFT is universally the decisive stage.
- It does not claim EOS explains all mode-seeking degradation.
- It does not claim a single scalar captures the full probability landscape.
- It does not infer architecture vs training causality from cross-era endpoint comparisons.

---

## 14. Promotion criterion

Promote L36 back to a Main-paper identity only if the following conjunction is supported:

1. a reproducible classic/base/post-trained difference in **mode-seeking search utility** exists under matched raw scoring;
2. it appears under an independent likelihood-ranked candidate procedure, not beam alone;
3. at least one same-architecture lineage exhibits a clear training-stage transition;
4. common-candidate rescoring demonstrates full-sequence probability reordering, not merely a local EOS change;
5. the result is not reducible to already-known static likelihood-quality correlation, semantic diversity collapse, or classical length bias.

If this conjunction fails, do not rescue the story by returning to the old generation-boundary identity.
