# A03 — Paper outline (draft, English; 2026-10-03 13:20). Items marked [P] are pending experiments; numbers are current.

## Title options
1. **Seeds Decide Where, Data Decides What: A Double Dissociation in How Language Models Form Mechanisms**
2. Born Here, Taught That: Initialization Places Mechanisms, Data Shapes What They Do
3. The Seed Picks the Head: Disentangling Initialization and Data in Language-Model Mechanisms

## Abstract (current numbers)
Mechanistic interpretability treats a model's circuits as products of its training data. We test this using factorial structure hidden in public pretraining suites, where the same random initialization was trained on many different corpora: DataDecide (3 seeds × up to 25 corpora at 14 sizes, 4M–1B; five seeds at 1B) and Pythia (standard vs. deduplicated Pile, 70M–410M). We verify the shared initialization from checkpoint hashes and from the earliest training checkpoints, and in doing so find that one widely used variant family (PolyPythias weight-seed) did not actually change its initialization. Crossing initialization with data reveals a double dissociation. *Where* a mechanism sits — which head within a layer becomes an induction, previous-token or retrieval head, and which residual-stream coordinates carry which features — is inherited from the initialization: models trained on different (even source-disjoint) corpora from one seed agree on head identity (within-layer ρ ≈ 0.3 at 1B; 0 across seeds), the data component of placement is zero, and the inheritance strengthens with scale. Yet the trained weights retain almost none of their initialization (r ≈ 0.04), same-seed models are not linearly connected, and *what* is represented — CKA, best-matched units — is no more similar for shared seeds than for unrelated ones. Conversely, *what* models do is set by data alone: across 14 sizes and 11 benchmarks the seed has no main effect (significant in 4–8% of 154 cells, the false-positive rate), and a ~1% slice of instruction data installs a context-reliance switch keyed to the literal template "Question:" (60M–1B, two training stacks, three conflict datasets) [P: a controlled continued-pretraining intervention that rewrites the template moves the trigger]. Controlled pretraining experiments [P] locate placement in an early critical period and identify what sets the strength of inheritance. The seed is therefore the unit over which component-level mechanistic claims can be compared, while behaviour-level claims generalise over seeds but not over data.

## 1. Introduction (claims in order)
- Hook (Fig 1): replacing the entire corpus does not move an induction head; 1% instruction data rewires when the model trusts its context.
- Gap: universality / stability work varies either the seed (Bali 2026; PolyPythias; Gurnee 2024) or the data (data attribution; Chen 2026), never both; so "where does a mechanism live" has never been decomposed into nature vs. nurture.
- Contributions (5): factorial substrate + audits; where ← seed (scale, families, coordinates vs content); what ← data (benchmarks, the Flan switch, causal template rewrite); how / when (critical period, what sets inheritance); consequences (seed-matched comparisons; no lucky seeds; QA-format conflict benchmarks partly measure a template switch).

## 2. Setup
- 2.1 Factorial substrate: DataDecide (14 sizes; SI / SD / DD pairs), Pythia std / deduped, PolyPythias seeds; audits (hashes; training-start check; P09).
- 2.2 Measurements: head-role maps (induction, previous-token, sink, retrieval); within-layer vs layer-profile decomposition; unbiased variance components (two-way, no replication); permutation / bootstrap.
- 2.3 Gauge view: heads in a layer are exchangeable; "which head" is a gauge choice, so any seed effect on identity is pure symmetry breaking, and any effect on gauge-invariant quantities is substantive.

## 3. Where comes from the seed
- 3.1 1B crossing (E35): data component of placement = 0; init significant in 56–80% of heads.
- 3.2 Within-layer vs layer profile (E35 / E44 post-hoc): which layer is near-universal; which head within a layer is inherited.
- 3.3 Scale (E45) [P for ≥ 90M]: inheritance present at every size, grows with scale (within-layer SI 0.02 at 4M → 0.12–0.16 at 60M → ~0.3 at 300M–1B); 20M dip (16 × 8).
- 3.4 Second family (E44): Pythia std vs deduped, 8/8 decidable cells; order does not matter (rerun ≈ order change ≫ init change).
- 3.5 Causal check (E42): ablation-defined maps also inherited but weakly (single-head effects are redundant / noisy); head-level transfer ≈ 20% (below our bar).
- 3.6 Coordinates vs content (E43; Fig 3): residual coordinates and head identity inherited; MLP neurons not [P: E52 specialised neurons]; content (CKA / best match) not inherited; no linear connectivity; weights forget the init (r ≈ 0.04).

## 4. What comes from the data
- 4.1 No main effect of the seed on behaviour (E36: 0/12 conflict conditions; E51: 154 benchmark cells) → no lucky seeds; seed noise is all seed × data interaction (practical: paired-seed recipe comparisons do not reduce noise).
- 4.2 The Flan switch (C04): factorial (E26), cue dissection (E32), development (E29), OLMo 2 mid-training (E30), PopQA (E34), NQ-Swap (E49; partial cue specificity), scale 60M–1B (E47).
- 4.3 Causal template rewrite (E48) [P].
- 4.4 Does the seed host the switch? (E50) [P].

## 5. How and when placement is fixed
- 5.1 Early lock-in (E37 1B ≈ 3.6%; E40 Pythia-70M ≈ 2%); weights at lock-in still ≈ 25% init-correlated.
- 5.2 Not readable from single heads (E39, E41) → collective symmetry breaking.
- 5.3 Controlled pretraining (E46 / E46c) [P]: data swap / perturbation at step k (critical period), init-perturbation dose (basin), what sets inheritance (init scale, learning rate).

## 6. Consequences and discussion
- Seed-matched designs for data-attribution / model-diffing studies; reporting standards ("component claims are per-seed").
- Relation to SeedPrints (init leaves an output fingerprint; we show what is and is not inherited mechanistically), to LMC / model merging (shared seed ≠ shared basin), to universality (Chughtai, Gurnee, Bali).
- Limitations: attention-score roles vs causal importance; DataDecide hyperparameters co-vary with size; small controlled models; one instruction-data family (Flan).

## Figures / tables
- Fig 1: design + hook. Fig 2: dissociation matrix (init vs data components for placement / content / strength / benchmarks / switch). Fig 3: coordinates vs content (E43, draft in `results/figs/`). Fig 4: scale + family (E45, E44). Fig 5: lock-in + controlled critical period (E37, E40, E46). Fig 6: the switch (E26, E32, E29, E30, E47, E48). Fig 7: benchmarks (E51).
- Appendix: audits (P09, training-start), all pre-registrations and voided claims, robustness (fineweb pair, metrics), E53 (parked).
