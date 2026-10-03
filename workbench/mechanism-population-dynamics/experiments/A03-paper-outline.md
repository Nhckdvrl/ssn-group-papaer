# A03 — Paper outline (English; v3, 2026-10-03 22:01, restructured after the top-venue alignment in A05). [P] = pending run.

## Title
**The Seed Picks the Slot, the Data Fills It: Nature and Nurture in Language-Model Circuits**
(alternates: *Seeds Decide Where, Data Decides What*; *Born with a Body Plan: How Random Initialization Lays Out Language-Model Circuits*)

## Abstract
Where do a language model's circuits come from? We separate nature from nurture using a natural experiment hidden in public pretraining suites, where one random initialization was trained on many different corpora: DataDecide (14 sizes, 4M–1B parameters, up to 25 corpora per seed) and Pythia (standard vs. deduplicated Pile, 70M–12B [P]). The answer is a division of labour: **the seed picks the slot, the data fills it.** Which head within a layer becomes an induction, previous-token or retrieval head is inherited from the initialization, with zero contribution from the data; from 60M parameters on, the head layout alone identifies a model's seed with 98–100% accuracy, even on a corpus never paired with that seed. What models represent, how strong their circuits are, when they emerge and how they behave is set by the data: the seed has no main effect on 154 benchmark × size cells, and 1% of instruction data installs a context-trust switch keyed to the literal template "Question:". The slot is chosen in a critical period in the first 1–2.5% of training and then defended against noise as large as the weights; by the end of training the weights retain almost none of their initial values (r = 0.04), yet the anatomy remembers the seed. Inheritance follows the data's statistics — the more similar two corpora's token distributions, the more faithfully a seed's layout recurs on both — and strengthens with scale. Component-level interpretability claims are claims about a seed: data shapes what circuits do, not where they live.

## 1. Introduction (order and claims)
- Opening: MI describes models by components; every model is the product of two random draws, the seed and the data; stability work varies only the seed (Bali 2026; PolyPythias 2025; Tigges 2024), data-centric work — including mechanistic data attribution (MDA, ICML 2026 Oral) — varies only the data. Nobody has separated the two for mechanisms.
- The natural experiment (DataDecide, Pythia) → Fig 1 (which head is strongest across 25 corpora, per seed) and Fig 2 (determination map).
- Five findings (bold noun phrase + one sentence + section):
  1. **A natural nature × nurture experiment for mechanisms** (§2): hidden seed × data crossings, audited; the determination map assigns 13 mechanistic properties to universal / seed / data / neither.
  2. **The seed picks the slot** (§3): placement is inherited across corpora and the data component is zero — at 14 sizes, in 2 families [P: up to 12B], for all 9 head roles we measured, including a weight-only copying score (E59); one head is the strongest in up to 56% of 25 corpora for a given seed (chance 6%).
  3. **The data fills it** (§4): strength, timing, content, behaviour and benchmarks come from the data; no lucky seeds; the "Question:" switch.
  4. **A critical period, then an attractor** (§5): the slot is fixed in the first 1–2.5% of training; afterwards weight-sized noise returns roles to their slots; the weights forget the seed (r = 0.04), the anatomy remembers it.
  5. **Inheritance follows corpus statistics and scale** (§6): a dose–response law on corpus distance at every size, robust to shared sources; code re-draws the slot; stronger in larger models [P: E57, E46b2].
- Applications (§7): anatomical seed identification (98–100%); seed-matched designs for data attribution and model diffing; interpretability findings transfer across data within a seed, not across seeds.

## 2. A natural nature × nurture experiment
- 2.1 Suites and audits: DataDecide (SI / SD / DD pairs); Pythia std vs deduped (identical step-0 tensors at 70M / 160M / 410M / 1.4B / 2.8B / 6.9B / 12B, rounding-level at 1B); training-start audit; PolyPythias weight-seed finding (P09).
- 2.2 Measurements: head-role maps (M1 induction, M2 previous-token, M3 sink, M4 retrieval, + duplicate-token, current-token, two-back, delimiter, OV copying; E59); within-layer vs layer-profile decomposition; unbiased two-way variance components; permutation / bootstrap.
- 2.3 Symmetry view: heads in a layer are exchangeable, so which head takes a role is decided by symmetry breaking; by symmetry the data alone cannot prefer a head; the question is whether one seed breaks the symmetry the same way on different data.
- 2.4 The determination map (Fig 2).

## 3. The seed picks the slot
- 3.1 1B, 3 seeds × 25 corpora (E35): data component of placement 0; seed effect in 56–80% of heads; within-layer SI 0.27–0.34 vs SD ≈ 0; source-disjoint corpora included.
- 3.2 Breadth: all 14 sizes (E45), 5 seeds at 1B, Pythia 70M–410M (E44) [P: 1B–12B, E58]; 9 roles incl. a weight-only copying score, all seed-placed (E59: 0.16–0.36 vs ≈ 0); causal ablation maps (E42).
- 3.3 What is universal: the layer of each role; the algorithm (previous-token → induction composition in 75 / 75 models, E55; consistent with Tigges 2024).
- 3.4 Coordinates, not content (E43): residual coordinates and outlier dimensions inherited (0.20 vs 0); MLP neuron identity not (0.008); CKA / best-match content not (SD ≥ SI ≈ DD); no linear connectivity.

## 4. The data fills it
- 4.1 Strength (E35) and timing (E54: induction onset — corpus 0.81, seed 0.00; previous-token onset universal). Consistent with MDA: data modulates the emergence rate of heads.
- 4.2 Behaviour: knowledge-conflict behaviour (E36, 0 / 12 seed effects), 11 benchmarks × 14 sizes (E51): no lucky seeds; seed variance is entirely seed × data interaction.
- 4.3 A switch installed by 1% of the data (C04): factorial, cue dissection, development, OLMo 2 mid-training, three datasets, 60M–1B; template-swap continued pretraining [P: E48b].
- 4.4 Where the switch lives: distributed, not seed-placed (E50) — late, data-installed functions are hosted flexibly.

## 5. A critical period, then an attractor
- 5.1 Public suites: final seed effect reached by 3.6% of training at 1B (E37) and ≈ 2% in Pythia-70M (E40).
- 5.2 Controlled pretraining (E46, Fig 5): switching the corpus or adding noise at step 100 (1%) re-draws the slot; from step 250 (2.5%) on, noise as large as the weights returns roles to their slots (0.79–0.98, against 0.05 at initialization); finite basin at initialization (≤ 1% perturbations change nothing).
- 5.3 Not readable at birth (E39, E41): no single-head statistic of the initial weights or gradient predicts the winner → collective symmetry breaking (cf. winner-take-all pathway specialization, ICML 2026).
- 5.4 Weights forget, anatomy remembers: final-vs-initial weight correlation 0.03–0.09; no linear connectivity; yet the seed is identifiable from the anatomy (§7.1). Contrast with the forgetting-time view (Adam-family training erases functional memory of initialization): our models are AdamW-trained and their functional memory is indeed gone (§4.2), but their anatomical memory is not.

## 6. Inheritance follows corpus statistics and scale
- 6.1 Corpus-distance law (E60, Fig 6): across DataDecide recipe pairs, unigram JS distance predicts same-seed similarity at every size (1B: ρ ≈ −0.56 to −0.60; 300M–1B: up to −0.8); holds on source-disjoint pairs (ρ −0.36 to −0.82) → token statistics, not shared documents.
- 6.2 Beyond the natural range (E46, E56): c4–papers (JS 0.13) inherit (0.19), code pairs (0.40–0.43) re-draw the slot.
- 6.3 Scale: inheritance grows with log parameters (E45, ρ 0.81–0.92); the distance law sharpens with scale (|ρ| ≈ 0.4–0.5 at 90M → 0.7–0.8 at ≥ 300M); developmental view [P: E57 — at 10M inheritance is already as weak at 8% of training as at the end: small models never inherit rather than forget]; controlled scale test [P: E46b2]; init scale and learning rate do not explain it (E46c).
- 6.4 Mechanism sketch: during the critical period the gradient signal is dominated by low-order token statistics (the unigram-output stage; Fehlauer et al., EMNLP 2025); corpora with the same statistics break the symmetry the same way.

## 7. Applications and consequences
- 7.1 Anatomical seed identification (E61): leave-one-corpus-out, 98–100% from 60M up, 100% with 5 seeds at 1B, true seed ranked 1 / 10 in Pythia; complementary to SeedPrints (output fingerprints of one weight lineage): we identify independently trained siblings from their internal layout.
- 7.2 Interpretability practice: component findings transfer within a seed across data, not across seeds; report per seed; roles and algorithms are the reproducible units.
- 7.3 Data attribution and model diffing: the data shapes emergence (MDA), the seed shapes placement → attribute emergence, not location; compare seed-matched models.
- 7.4 Benchmarking: no lucky seeds; sharing seeds across recipes does not reduce comparison noise.

## Figures
1. Hook: which head is strongest across 25 corpora, 3 seeds × 3 roles (`fig_hook_1b_prevtoken.png`).
2. Determination map (`fig_determination_map.png`).
3. Coordinates vs content (`fig_crossover_e43.png`).
4. Scale: inheritance and seed-identification accuracy vs size, DataDecide + Pythia (`fig_scale_e45.png` + E61) [P: up to 12B].
5. Critical period and basin (`fig_critical_period_e46.png`) + public-suite lock-in.
6. Corpus-distance law (`fig_corpus_distance_e60.png`) + controlled corpora.
7. The data fills it: benchmarks (`fig_benchmarks_e51.png`) and the switch (`fig_flan_scale_e47.png`).

## Limitations (scope, not headline hedges)
Attention-score roles are the primary measurement (ablation maps agree but are noisier); DataDecide hyperparameters co-vary with size; controlled models are small; one instruction-data family for the switch.
