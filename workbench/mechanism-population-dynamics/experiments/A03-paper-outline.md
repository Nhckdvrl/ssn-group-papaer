# A03 — Paper outline v5 (English; 2026-10-04; nature and nurture, three acts, nothing tightened — see A07 §8). [P] = pending run.

## Title
**The Seed Picks the Slot, the Data Fills It: Nature and Nurture in Language-Model Circuits**
(hook line for the first screen: *the weights forget the seed; the circuits remember it*)

## Abstract
Where do a language model's circuits come from — its random initialization or its training data? We answer with seed × corpus crossings hidden in public pretraining suites: DataDecide (14 sizes, 4M–1B parameters, up to 25 corpora per seed) and Pythia (standard vs. deduplicated Pile, 70M–12B). Language models turn out to have a nature and a nurture. **Nature decides where:** which head becomes an induction, previous-token, retrieval or any of six other head roles is inherited from the seed, identically across corpora, and the data contributes nothing — provably so, by the permutation symmetry of heads. The inheritance is so strong that a model's seed can be read off its circuit layout with 98–100% accuracy, although its weights retain a correlation of only 0.04 with their initial values: the weights forget the seed, the circuits remember it. **Nurture decides what:** what the model represents, how strong its circuits are, when they emerge and how it behaves come from the data; the seed has no main effect on any of 154 benchmark × size cells — there are no lucky seeds — and a 1% slice of instruction data writes a context-trust switch keyed to the literal template "Question:". Nature is written in a critical period: in controlled pretraining the slot is chosen in the first 1–2.5% of training and then defended even against noise as large as the weights. Two levers set how much of a model is nature: the temperature of SGD and the similarity of its corpora; because standard scaling recipes train larger models colder, larger models are more innate. Component-level interpretability findings therefore travel with the seed, not with the data, and data attribution explains whether a circuit forms but not where it lives.

## 1. Introduction — first screen
1. **Hook (the paradox).** Two LMs from one seed, different corpora: weights 96% decorrelated from the init, no seed effect on any benchmark — yet their circuits sit on the same heads, so reliably that the seed is identifiable from the layout (98–100%). The weights forget the seed; the circuits remember it. (Fig 1.)
2. **The question and why it matters.** Every model is the product of two random draws — seed and data. Interpretability credits circuits to data (MDA traces heads to samples); training is thought to erase the init (forgetting-time view: Adam erases functional memory); seed variation is treated as noise. Prior work varies only the seed (Bali 2026; PolyPythias; Tigges 2024) or only the data (MDA; Chan 2022). We separate nature from nurture for the first time.
3. **The answer in one paragraph.** Nature decides where (seed; provably not data), nurture decides what (data; no lucky seeds; 1% data writes a behaviour); nature is written in a critical period of symmetry breaking; SGD temperature and corpus statistics set how much is nature; larger models are more innate.
4. **Findings (bold, with sections) + applications:**
   1. **Nature decides where** (§3): 9 head roles, 14 sizes, 2 families; data contribution 0 by measurement and by theorem; seed identifiable from the layout 98–100%; one head wins in up to 56% of 25 corpora (chance 6%).
   2. **Weights forget, circuits remember** (§3): final-vs-initial weight r = 0.03–0.09, no linear connectivity, no shared representation content — yet shared anatomy and coordinates.
   3. **Nurture decides what** (§4): strength, onset time, content, benchmarks, knowledge-conflict behaviour; no lucky seeds; 1% instruction data writes a "Question:"-keyed switch.
   4. **Nature is written in a critical period** (§5): the slot is chosen in the first 1–2.5% of training and then becomes an attractor; replicated in a 30× larger controlled model; public suites lock in at 2–4%.
   5. **SGD temperature and corpus statistics set how much is nature — larger models are more innate** (§6): order-only agreement 0.43 → 0.90 as LR / batch falls; corpus-distance law at every size (up to −0.8); scaling recipes cool with size.
   - **Applications** (§7): component findings travel with the seed (10× transfer); attribute emergence, not location; seed-matched comparisons; no seed selection across recipes; the layout as a birth certificate (seed identification).

## 2. Natural experiment and ruler
- 2.1 DataDecide and Pythia crossings, audited (step-0 identity at every Pythia size 70M–12B; training-start audit; the PolyPythias weight-seed finding).
- 2.2 Lemma 1 (the data cannot choose the head): permutation-invariant init + permutation-equivariant training ⇒ different-seed agreement is exactly chance for any data; above-chance agreement across corpora is carried by the seed. Observed: −0.02 to 0.00 for 9 roles — the theorem holds, and same-seed agreement (0.16–0.36) is pure inheritance.
- 2.3 Nine head-role maps (incl. weight-only OV copying), "which layer" vs "which head", variance components, permutation / bootstrap / Mantel tests; the determination map.

## 3. Nature decides where — and the weights forget it
- 3.1 1B 3 × 25 crossing; 5 seeds at 1B; 14 sizes; Pythia 70M–12B (12B: 0.38–0.51 vs permutation 95th pct 0.04; same strongest head in the induction and previous-token layers); 9 roles (E59); ablation maps (E42).
- 3.2 Birth certificate: seed identification 98–100% from 60M (E61), already at 3–4% of training; Pythia sibling ranked 1 / 10.
- 3.3 Universal: layer of each role; the algorithm (previous-token → induction in 75 / 75, E55).
- 3.4 Weights forget, circuits remember (E43): weights r = 0.03–0.09; no linear connectivity; CKA / best-match content not inherited; residual coordinates inherited.

## 4. Nurture decides what
- 4.1 Strength (E35) and onset time (corpus 0.81, seed 0.00; E54).
- 4.2 No lucky seeds (E36, E51).
- 4.3 1% of the data writes a behaviour (C04): with/without Flan in pretraining (+1.3 to +3.5 nats context trust, QA format only); keyed to the literal "Question:" ("Q:", "Query:" don't trigger); PopQA, NQ-Swap; appears at 3.6% of pretraining; 60M–1B; OLMo 2 mid-training installs it in an independent stack; acquired in pretraining, not by continued pretraining at matched dose (E48b); hosted by distributed heads, not seed-placed (E50).

## 5. Nature is written in a critical period
- 5.1 Not readable at birth (E39, E41).
- 5.2 Branching and perturbation (E46, Fig 4): 1% re-draws, 2.5% locks; weight-sized noise returns roles to their slots; L-size replication (E46b); public suites lock in at 2–4% (E37, E40, E57).

## 6. How much is nature: SGD temperature and corpus statistics
- 6.1 SGD temperature (E62, Fig 5a): batch 16 / 64 / 512, LR 3e-3 / 1e-3 / 3e-4 — order-only agreement 0.43 / 0.57 / 0.61 / 0.82 / 0.90, inheritance 0.01 → 0.22; LR × 3 ≈ batch / 4.
- 6.2 Corpus statistics (E60, Fig 5b): corpus distance predicts inheritance at every size (up to −0.8), source-disjoint pairs too; code re-draws the slot (E56).
- 6.3 Larger models are more innate (E45, Fig 3): inheritance grows with log parameters (ρ 0.81–0.92); the cause is the recipe's cooling (DataDecide 2.1e-7 → 1.5e-9 LR per batch token; a 30× larger model at fixed temperature inherits no more, E46b); Pythia, trained cold, is innate at every size.

## 7. Applications
Component findings travel with the seed (E42: 19.5% vs 2.0%); data attribution explains emergence, not location (with MDA); seed-matched model comparisons; no seed selection across recipes (E51); the layout as a birth certificate (E61; complements SeedPrints).

## 8. Discussion
A protomap for language models (Rakic vs O'Leary); why the seed matters so precisely and so little (symmetry breaking under noise); limitations (attention-defined roles primary; DataDecide co-scales factors; controlled models small; one instruction-data family; template-swap intervention not achieved).

## Figures (7)
1. Hook: per-seed winner histograms across 25 corpora + identification accuracy.
2. Determination map (nature / nurture / universal / neither).
3. Nature across scale and families (`fig_scale_v2.png`) + weights forget, circuits remember (`fig_crossover_e43.png`).
4. Critical period and lock-in (`fig_critical_period_e46.png`, `fig_lockin.png`).
5. How much is nature: SGD temperature (`fig_temperature_e62.png`) and corpus distance (`fig_corpus_distance_e60.png`).
6. Nurture: no lucky seeds (`fig_benchmarks_e51.png`).
7. Nurture writes a behaviour: the "Question:" switch (`fig_flan_scale_e47.png`).
