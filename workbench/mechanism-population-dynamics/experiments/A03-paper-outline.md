# A03 — Paper outline (English; rewritten 2026-10-03 21:12 after narrative calibration, A02 §8). [P] = pending run; numbers are current.

## Title options
1. **The Seed Picks the Slot, the Data Fills It: Nature and Nurture in Language-Model Circuits**
2. Seeds Decide Where, Data Decides What: How Language Models Inherit Their Anatomy
3. Born with a Body Plan: Random Initialization Determines Where Language Models Grow Their Circuits

## Abstract
Where do a language model's circuits come from? Interpretability research implicitly credits them to the training data. We separate nature from nurture using a factorial design hidden in public pretraining suites, in which one random initialization was trained on many different corpora: DataDecide (14 sizes, 4M–1B parameters; 3 seeds × up to 25 corpora, 5 seeds at 1B) and Pythia's standard and deduplicated runs (70M–12B [P: 6.9B/12B]). The answer is a clean division of labour. **The seed picks the slot:** which head within a layer becomes an induction, previous-token or retrieval head, and which residual-stream coordinates carry outlier features, is inherited from the initialization whatever the corpus — models grown from one seed on different data choose the same strongest head up to 5× more often than chance, while the data contributes exactly zero to placement. **The data fills the slot:** what the model represents, how strong its circuits are, when they emerge and how the model behaves are set by the data, and the seed has no main effect on any of them — across 154 benchmark × size cells there are no lucky seeds, and a 1% slice of instruction data installs a behavioural switch keyed to the literal template "Question:". The algorithm itself (previous-token → induction composition) and the layer in which each role lives are universal. Placement is decided by symmetry breaking in a critical period during the first 1–4% of training, inside a finite basin around the initialization; afterwards, changing the data no longer moves it. Strikingly, the trained weights retain almost nothing of their initialization (r = 0.04): the weights forget the seed, but the roles remember it. Inheritance grows with scale, so the larger the model, the more of its anatomy is fixed at birth. Component-level mechanistic claims are therefore claims about a seed; data attribution and model diffing should be seed-matched; and the reproducible objects of interpretability are roles and algorithms, not components.

## 1. Introduction
- Hook (Fig 1): 1B models grown from one seed on different corpora (C4, DCLM, Dolma, FineWeb-Edu, …) pick the same previous-token head five times more often than chance, with zero contribution from the data; models grown on the same corpus from different seeds agree only at chance.
- Question: nature vs nurture for mechanisms. Prior stability / universality work varies only the seed (Bali 2026; PolyPythias; Gurnee 2024; MultiBERTs) or only the data (Chan 2022; data attribution), so the two have never been separated.
- Contributions:
  1. **A natural factorial for mechanisms.** Hidden init × data crossings in DataDecide and Pythia, audited by step-0 hashes and by the earliest training checkpoints (finding along the way that the PolyPythias weight-seed variants did not change their initialization).
  2. **The determination map** (Fig 2): for each mechanistic property, how much is universal, set by the seed, set by the data, or idiosyncratic (seed × data).
  3. **The seed picks the slot** — across 14 sizes and two families, the slot is inherited and the data component is zero; coordinates are inherited, contents are not; weights forget the seed while roles remember it.
  4. **The data fills the slot** — strength, timing, content and behaviour come from data; no lucky seeds; the "Question:" switch.
  5. **When and why** — a critical period and a basin of attraction in controlled pretraining; inheritance grows with scale and requires shared early-training statistics (code resets the slot).
  6. **Consequences** for interpretability, data attribution, model diffing and benchmarking practice.

## 2. A natural factorial for mechanisms
- 2.1 Suites: DataDecide (SI / SD / DD pairs); Pythia std vs deduped (shared step 0 at 70M/160M/410M/6.9B/12B [P: 1B–2.8B tensor check]); PolyPythias seeds as the different-seed reference.
- 2.2 Audits: step-0 hashes; training-start check (P09); excluded mismatched shard.
- 2.3 Measurements: head-role maps (M1 induction, M2 previous-token, M3 sink, M4 retrieval); ablation maps; within-layer vs layer-profile decomposition; unbiased two-way variance components; permutation / bootstrap inference.
- 2.4 Symmetry view: heads within a layer are exchangeable, so *which* head takes a role is decided by symmetry breaking. By symmetry the data alone cannot prefer a head; the empirical question is whether one seed breaks the symmetry the same way on different data (deterministic, seed-driven) or differently (chaotic, data-driven).

## 3. The seed picks the slot
- 3.1 1B crossing, 3 seeds × 25 corpora (E35): data component of placement = 0; seed effect significant in 56–80% of heads; within-layer SI 0.27–0.34, SD ≈ 0; source-disjoint corpora included.
- 3.2 Five seeds × 10 corpora at 1B (E45): within-layer 0.32 / 0.47 / 0.29; top-head agreement 0.30 / 0.20 / 0.14 vs chance 0.06 (M2 / M4 / M1).
- 3.3 Second family (E44, E58 [P]): Pythia std vs deduped 8/8 cells at 70M–410M, extended to 6.9B / 12B [P]; batch order barely matters (rerun ≈ order change ≫ seed change).
- 3.4 Universal parts (E35, E55): which *layer* hosts a role is near-universal; previous-token → induction K-composition present in 75/75 1B models.
- 3.5 Coordinates vs content (E43, Fig 3): residual coordinates and massive-activation dimensions inherited (0.20 / 0.17 vs 0); MLP neuron identity not (0.008); CKA / best-match content not (SD ≥ SI); no linear connectivity (barrier 7.5 vs 7.0 nats); final-vs-initial weight correlation 0.03–0.09.
- 3.6 Causal check (E42): ablation-defined maps also inherited (weaker; single-head effects are redundant).

## 4. The data fills the slot
- 4.1 Strength and timing: data sets circuit strength (4/6 metrics; seed component ≈ 0, E35); induction emergence time is set by the corpus (variance share 0.81, seed 0.00; E54); previous-token timing is universal.
- 4.2 Behaviour: no main effect of the seed on knowledge-conflict behaviour (0/12, E36) or on 11 benchmarks × 14 sizes (154 cells at the false-positive rate, E51) → no lucky seeds; all seed variance is seed × data interaction, so sharing seeds across recipes does not reduce comparison noise.
- 4.3 A switch installed by 1% of the data (C04): with/without Flan factorial (E26), cue dissection ("Question:" yes; "Q:" and "Query:" no; E32), no-context control (E31), PopQA (E34), NQ-Swap (E49), development from 3.6% of training (E29), OLMo 2 mid-training (E30), 60M–1B (E47); template-swap continued pretraining (E48 / E48b [P]).
- 4.4 Hosting: the switch is implemented by heads that are stable within a model (split-half 0.93) but not seed-placed (E50) — late, data-installed functions are hosted flexibly.

## 5. When and why the slot is fixed
- 5.1 Early lock-in in public suites: 1B reaches its final seed effect by 3.6% of training (E37); Pythia-70M by ≈ 2% (E40).
- 5.2 Not readable at birth: no single-head statistic of the initial weights or initial gradient predicts the winner (E39, E41) → collective symmetry breaking.
- 5.3 Controlled pretraining (E46): basin of attraction (perturbations ≤ 1% of the weight scale leave the layout unchanged; 10% partly; 100% re-draws it); critical period (switching the corpus at step 100 re-draws the layout, from step 250 on it is retained) [P: final D arm]; batch order matters in tiny models.
- 5.4 Scale and the boundary: inheritance grows with log parameters (ρ 0.81–0.92; thresholds 60M–150M; E45); controlled models reproduce the small-scale end (E46 A) and a larger controlled model [P: E46b]; corpora with different early statistics (code) re-draw the slot (E56 [P]); developmental trajectories by size [P: E57]; init scale and learning rate do not explain the trend (E46c).

## 6. Consequences
- Interpretability: report component-level findings per seed; expect them to transfer across data with the same seed, not across seeds; roles and algorithms are the reproducible units.
- Data attribution / model diffing: compare models grown from the same seed; otherwise seed-driven placement differences masquerade as data effects.
- Benchmarking: seed selection cannot be transferred across recipes; paired seeds do not reduce recipe-comparison noise.
- Evaluation: QA-formatted knowledge-conflict benchmarks partly measure a template-keyed switch.
- Relation to SeedPrints (init fingerprint in outputs), LMC / model merging (shared seed ≠ shared basin), universality (Chughtai, Gurnee, Tigges, Bali).

## Figures
1. Hook + design: seeds × corpora grid of previous-token maps; SI / SD / DD at every size.
2. **Determination map**: rows = layer of a role, algorithm, which head, residual coordinates, neuron identity, content (CKA), strength, emergence time, behaviour, benchmarks, Flan switch, weight values; columns = universal / seed / data / interaction.
3. Coordinates vs content (E43).
4. Scale (E45 + Pythia to 12B) and top-head agreement.
5. Critical period and basin (E46), with the public-suite lock-in curves (E37, E40) and developmental trajectories by size (E57).
6. The switch (E26, E32, E29, E30, E47, E48).
7. No lucky seeds (E51).

## Limitations (as scope, not as headline hedges)
Attention-score roles are the primary measurement (ablation maps agree but are noisier); DataDecide hyperparameters co-vary with size; controlled models are small; one instruction-data family (Flan) for the switch.
