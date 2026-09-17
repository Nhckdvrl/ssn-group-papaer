# L36 Sequence-Landscape Re-audit

**Date:** 2026-09-17  
**Decision:** keep L36 active, but retire the generation-boundary paper identity as the primary Main story.  
**New scientific object:** the **sequence-level probability landscape** and how its mode-seeking behavior changes from classical sequence models to modern post-trained LMs.

## 1. Why the previous framing was too narrow

Beam search approximates

\[
\hat y = \arg\max_y \log p_\theta(y\mid x)=\arg\max_y\sum_t\log p_\theta(y_t\mid x,y_{<t}).
\]

The earlier L36 work focused heavily on the immediate-stop candidate `y=[EOS]`. For that single candidate, first-step EOS probability/rank is a valid and sometimes exact instrument. But it is only one path in the full search tree.

Our own Olmo results already falsify the universal-EOS story: the base model can lose large amounts of BLEU under wider search while keeping zero empty outputs and near-reference length, via generic/copy-like high-probability sequences. Therefore:

> `termination collapse` is one special channel of `mode-seeking degradation`, not the general explanation of the beam-search curse.

The E02 controlled SFT also needs a narrower interpretation. With 2,998 matched translation examples and a shared neutral `<END>` token, it causally shows that a surface-conditioned boundary-token policy can be learned. It does **not** by itself show that large-scale post-training learns an abstract, task-general concept of response completeness.

## 2. Full-text ownership audit

### Murray & Chiang (2018), *Correcting Length Bias in Neural Machine Translation*
Owns the strong link between brevity/length bias and large-beam degradation, and shows sentence-level length correction nearly eliminates the classical beam problem.

### Cohen & Beck (ICML 2019), *Empirical Analysis of Beam Search Performance Degradation in Neural Sequence Models*
Owns a broader multi-token search explanation: wider beam preserves early low-probability discrepancies which are later compensated by high conditional probabilities; constraining such discrepancies removes degradation across MT, summarization, and captioning. This is especially important because it already generalizes beyond EOS/length.

### Stahlberg & Byrne (EMNLP 2019), *Cat Got Your Tongue?*
Owns the exact-search result that classical NMT often assigns the global maximum to the empty translation; beam search errors can paradoxically protect against model errors.

### Eikema & Aziz (COLING 2020 Best Paper), *Is MAP Decoding All You Need?*
Owns the mode-vs-mass distinction in NMT. Samples from the learned distribution can reproduce data statistics reasonably well while beam/MAP outputs stray from them; the mode may carry negligible probability mass and be an inadequate summary.

### Shi, Xiao & Knight (2020), *Why Neural Machine Translation Prefers Empty Outputs*
Owns the empty-output mechanism. Importantly, empty can win either because `p(EOS|x)` is too high **or** because full adequate sequences receive too little cumulative probability. This directly rules out reducing empty-mode preference to EOS alone.

### Kulikov, Eremeev & Cho (AACL 2022), *Characterizing and addressing oversmoothing...*
Owns a sequence-level premature-termination formulation across all ground-truth prefixes, an oversmoothing metric, EOS probability/rank analysis, a training regularizer, and its effect on large-beam shortening. Crucially, reducing oversmoothing does not eliminate all large-beam quality degradation.

### Stahlberg, Kulikov & Kumar (ACL 2022), *Uncertainty Determines the Adequacy of the Mode...*
Owns the link from intrinsic uncertainty to search errors, exact-search tractability, and spread of probability mass around the mode. It does **not** directly own our discarded within-MT quartile-BLEU-damage extrapolation.

### Meister et al. (ACL 2022), *On the probability-quality paradox in language generation*
Owns a generic information-theoretic account of why high-probability/mode-seeking text need not be high-quality.

### Pang et al. (TACL 2025), *Salute the Classic*
Owns the modern observation that the classical beam-search challenge is much weaker / may not apply to LLM-MT. Their beam-size analysis is shallow: one LLM-SFT-100k system in Appendix B.2, reporting BLEU increasing and COMET changing little with beam size. They do not explain the distributional mechanism or training-stage transition.

### Wu, Lei & Monz (NeurIPS 2025), *Calibrating Translation Decoding with Quality Estimation on LLMs*
Owns direct optimization of likelihood-quality correlation in LLM-MT. They show limited training can realign hypothesis likelihood with translation quality and improve MAP/beam decoding. Therefore `likelihood-quality alignment can be trained` is not ours.

### Springer et al. (ICML 2026), *Annotations Mitigate Post-Training Mode Collapse*
Owns a different post-training distributional phenomenon: SFT reduces semantic diversity and biases models toward low-entropy fine-tuning data. This is semantic diversity / coverage collapse, not whether progressively mode-seeking search becomes more or less harmful.

### Zenn & Geiping (2026), *When are likely answers right?*
Systematically studies sequence probability vs correctness across decoding methods, hyperparameters, prompt-answer pairs, and repeated responses. Therefore generic `higher sequence probability != higher correctness` is not ours. They do not study classical-NMT -> post-trained-LLM regime transition or Base -> SFT -> preference/RL training dynamics of mode-seeking degradation.

## 3. Novelty that remains

The novelty is **not** any of:

- beam-search curse exists;
- EOS / short hypotheses matter;
- sequence probability may misalign with quality;
- MAP can be inadequate;
- post-training changes entropy/diversity;
- training can explicitly calibrate likelihood to quality.

The remaining gap is a **transition question**:

> **Why does progressively mode-seeking search degrade classical sequence models, while many modern post-trained LMs remain stable, and what structural change in the full sequence-level probability landscape accounts for that transition?**

A stronger lineage formulation:

> **Within a fixed autoregressive model lineage, how do Base -> SFT -> preference/RL stages reorganize the relation among sequence mode, typical probability mass, search path, and task utility?**

This is materially different from static probability-quality correlation. The object is the **training-stage transition in mode-seeking stability**.

## 4. Main candidate claims (not yet established)

### C1 — phenotype
Classical NMT and modern post-trained LMs differ not merely in surface failure type but in how utility changes as decoding moves toward higher-probability sequences.

### C2 — pathology migration
The classical short/empty curse may disappear while a broader mode-seeking pathology persists as generic/copy/repetition/semantic failures. If so, the correct statement is not `beam curse disappeared` but `its dominant failure basin changed`.

### C3 — lineage transition
Within at least one public same-architecture lineage, post-training changes the search-utility trajectory and/or mode-mass gap substantially even under a fixed task and candidate set.

### C4 — structural explanation
The transition is accompanied by a measurable reorganization of full-sequence geometry (e.g. mode-vs-mass gap, length-conditioned score envelope, or path-discrepancy compensation), not only a change in first-step EOS.

These are hypotheses. None should be promoted to claims before E05.

## 5. Falsifiers

Kill the Main-level reframe if any of the following holds after the E05 audit:

1. base and post-trained lineages show no reproducible change in mode-seeking degradation after controlling for task quality and interface;
2. the apparent difference is specific to beam search and does not appear under an independent sequence-level mode-seeking procedure such as best-of-N by raw model likelihood;
3. post-training only changes immediate termination/length while non-empty full-sequence mode pathology remains unchanged;
4. candidate rescoring shows no systematic reordering of adequate vs pathological full sequences across training stages;
5. all modern stability is explained by decoder normalization / stopping defaults rather than model probabilities under matched raw scoring.

## 6. Role of previous L36 experiments after the reframe

Keep:
- matched RAW classic-vs-modern endpoint contrast;
- Olmo / Tulu lineage checkpoints;
- non-empty Olmo degradation as evidence that EOS is not universal;
- EOS-rank/intervention results as a **channel-specific case study**;
- E02 as a narrow causal sandbox for format-conditioned boundary-token learning;
- cross-implementation audits as measurement credibility.

Demote:
- `generation boundary` as the paper identity;
- `rank_stop <= 2b` as anything beyond an algorithmic exposure instrument;
- E02 as evidence of generalized response-completion learning.

## 7. Current verdict

```yaml
status: ACTIVE_REFRAMED_MAIN_CANDIDATE
primary_rq: MODE_SEEKING_STABILITY_TRANSITION
old_generation_boundary_identity: DEMOTED_TO_SUBMECHANISM
empty_eos_channel: RETAIN_AS_SPECIAL_CASE
novelty: PLAUSIBLE_BUT_REQUIRES_E05
main_ready: NO
next_gate: E05_SEQUENCE_LANDSCAPE_AUDIT
```
