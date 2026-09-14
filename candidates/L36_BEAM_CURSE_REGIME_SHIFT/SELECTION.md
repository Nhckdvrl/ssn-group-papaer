# L36 — Why Did the Beam-Search Curse Disappear?

**Date:** 2026-09-14  
**Target:** ACL / EMNLP / NAACL Main  
**Status:** **PILOT-AUTHORIZED — E01 ONLY**

## 1. Research question

> **Why does the classic intrinsic-uncertainty → beam-search-pathology law appear to break in LLM-based machine translation?**

A sharper form is:

> **Machine translation remains intrinsically ambiguous. Why, then, does widening beam search no longer expose the severe mode inadequacy / quality collapse that classic NMT exhibits? Which model-level condition changed?**

This is not a decoder-method paper and not a request to find a better beam size. The scientific object is an old empirical law about how **task ambiguity is converted into model-distribution geometry and search pathology**, and why that law changes in the LLM regime.

---

## 2. Scientific pressure / mother phenomenon

### Old conditional law — ACL 2022

Stahlberg, Kulikov & Kumar, ACL 2022, *Uncertainty Determines the Adequacy of the Mode and the Tractability of Decoding in Sequence-to-Sequence Models*:

- define sentence-level **intrinsic uncertainty** from disagreement among independently written human references;
- show at both task and sentence level that higher intrinsic uncertainty is associated with flatter model distributions, more search errors, less tractable mode search, and worse mode adequacy;
- classic MT (high uncertainty) exhibits the beam-search curse, while lower-uncertainty GEC does not;
- MT quality peaks at a small beam and then drops dramatically as beam size grows.

Primary source: https://aclanthology.org/2022.acl-long.591/

Crucially, their MT uncertainty substrate is natural and reusable: official WMT19 English→German test sources paired with additional independently authored human references from Freitag et al. (2020). Their uncertainty score is computed only from human-reference disagreement, so it does not depend on the model being tested.

### Modern regime reversal — TACL 2025

Pang et al., TACL 2025, *Salute the Classic: Revisiting Challenges of Machine Translation in the Age of Large Language Models*:

- revisit the six classic NMT challenges with Llama2-based translation LLMs;
- state that the classic beam-search challenge may not apply to LLM translation;
- Appendix B.2 sweeps beam width on German→English and reports that larger beam improves surface BLEU while semantic COMET changes little rather than collapsing.

Primary source: https://aclanthology.org/2025.tacl-1.4/

The released LLM4MT repository also states that its implementation follows the ParroT / HuggingFace generation codebase. The public ParroT `inference.py` uses standard `GenerationConfig` beam search (`num_beams`, `max_new_tokens`, EOS/pad IDs) rather than a bespoke search algorithm. This makes a faithful scoring-semantics audit feasible.

### The obvious old explanation did not disappear — NeurIPS 2025

Wu, Lei & Monz, NeurIPS 2025, *Calibrating Translation Decoding with Quality Estimation on LLMs*:

- shows that even translation-specialized LLMs retain weak alignment between sequence likelihood and actual translation quality;
- directly improving likelihood–quality calibration improves MAP decoding substantially.

Primary source: https://papers.neurips.cc/paper_files/paper/2025/hash/e46f7f5c7e981a61cbcf6b56b7a8fe9d-Abstract-Conference.html

Therefore the disappearance of the curse cannot simply be asserted to follow from `LLM likelihood now equals translation quality`.

---

## 3. Provenance: premise collision

Established premise A:

> **High intrinsic output uncertainty causes classic neural seq2seq models to spread probability mass over many alternatives, making the mode inadequate and large-beam search pathological.**

Established premise B:

> **MT remains a one-to-many task in the LLM era, yet a strong modern TACL study reports that the classic large-beam deterioration is absent.**

Established premise C:

> **LLM translation likelihood is still imperfectly aligned with translation quality.**

Collision:

> If the external task ambiguity is still present and likelihood–quality misalignment is still present, **which intermediate model/search quantity stopped transmitting ambiguity into the beam-search curse?**

The contribution cannot be `ACL 2022 + TACL 2025`. It must identify the missing condition and revise the old law.

---

## 4. Candidate accounts

### A — Decoding-semantics artifact

The apparent regime shift is caused by a change in scoring / stopping conventions (e.g. length normalization, stopping rule, EOS treatment), not by a changed learned distribution.

Prediction:

> under a faithfully matched classical scoring semantics, high-uncertainty LLM translation again shows large-beam deterioration.

If this account fully explains the reversal, **the Main route dies**. A configuration audit is not sufficient contribution.

### B — Termination / length pathology migrated

Classic large-beam deterioration arose because better mode search exposed pathological short/empty hypotheses. LLM post-training / instruction conditioning may have changed termination and length geometry enough that wider search no longer uncovers these modes, even though likelihood–quality alignment remains imperfect.

Predictions:

- modern LLMs show far less beam-dependent shortening / premature EOS on the same uncertainty strata;
- later causal work should be able to reintroduce the pathology by controlled EOS / length-score perturbation, preferentially on high-uncertainty items.

### C — Model uncertainty no longer tracks task uncertainty in the same way

The task remains intrinsically ambiguous, but the LLM conditional distribution allocates probability mass differently: e.g. more mass is concentrated on a set of adequate paraphrases or the mode is less arbitrary.

Predictions:

- human-reference uncertainty `u` remains fixed by construction;
- the old `u → probability-mass spread / mode inadequacy` relationship weakens or changes in the LLM;
- high-`u` sentences need not show the old search-tractability signature.

### D — Global misalignment is not search-exposed misalignment

Likelihood and quality can be weakly correlated over the broad hypothesis distribution while the hypotheses newly exposed by increasing beam width are not adversarially ordered.

Prediction:

> global likelihood–quality misalignment remains, but the **beam frontier** does not systematically introduce higher-scoring / lower-quality hypotheses as width grows.

These accounts are not assumed mutually exclusive. E01 is designed only to establish whether the old uncertainty law truly breaks under controlled semantics; mechanism localization belongs after that gate.

---

## 5. Closest owners / reviewer compression

### Koehn & Knowles 2017; Yang et al. 2018

Own the classic beam-search curse and length/stopping corrections.

- https://aclanthology.org/W17-3204/
- https://aclanthology.org/D18-1342/

### Eikema & Aziz 2020 / 2022

Own mode inadequacy and the finding that mode-seeking can select idiosyncratic high-probability translations; MBR does not exhibit an equivalent beam-search curse.

- https://aclanthology.org/2020.coling-main.398/
- https://aclanthology.org/2022.emnlp-main.754/

### Stahlberg et al. 2022 — most dangerous old owner

Own the conditional law linking intrinsic uncertainty to probability-mass spread, search difficulty, mode inadequacy and large-beam deterioration in classic seq2seq models.

They do **not** test modern decoder-only translation LLMs or explain a regime where the same MT ambiguity no longer produces the pathology.

### Pang et al. 2025 — modern mother owner

Own the observation that the classic beam challenge appears absent in one LLM-MT regime.

They do **not** connect this reversal to the 2022 uncertainty law, stratify by intrinsic ambiguity, or identify what model/search quantity changed.

### Wu et al. 2025

Own persistent likelihood–quality misalignment and a calibration method for LLM-MT.

They do **not** explain why wider beam search fails to amplify that misalignment into the classic curse.

### Strongest reviewer compression

> `ACL 2022 already says uncertainty causes the curse; TACL 2025 already says LLMs do not have the curse; old length-bias papers already discuss stopping. L36 merely puts them together.`

### Surviving contribution

That compression does **not** identify why the established conditional law breaks. The paper earns Main-level novelty only if it shows, on matched intrinsic-uncertainty units, **which intermediate relation changed in the LLM regime** and turns that into a revised conditional law / causal prediction.

Current ownership verdict: **PLAUSIBLE INDEPENDENT CONTRIBUTION**.

Fresh repository search found no prior beam-search candidate or killed route; this is not a resurrection of L08/L19/L32/L35.

---

## 6. SAME-QUANTITY / construct validity

The strongest design reuses the exact old scientific quantity rather than inventing a new ambiguity proxy.

### Intrinsic uncertainty

For a source sentence with multiple independently authored references `y_1...y_n`, reuse Stahlberg et al.'s normalized average pairwise Levenshtein disagreement `u`.

This is external task ambiguity and is **model-independent**.

### Search pathology

Predeclare two levels:

1. **system-level curse:** quality as beam width increases;
2. **sentence-level conditional law:** whether the beam-width effect becomes more adverse as `u` increases.

Do not infer task uncertainty from token entropy; that would change the quantity.

### Model-side quantities for later mechanism

Keep distinct from intrinsic uncertainty:

- output-length / EOS behavior;
- sequence-score spread;
- n-best / beam-frontier score-quality ordering;
- probability-mass concentration where tractable to estimate.

The paper's conceptual payoff is precisely to ask whether `task uncertainty → model uncertainty/search pathology` is invariant across model regimes.

---

## 7. E01 — exact bounded authorization

**Purpose:** decide whether there is a real modern-regime law to explain. E01 is not a mechanism paper by itself.

### E01a — published-mother / decoding-semantics audit

Use the released TACL LLM4MT checkpoint + its public WMT23 German→English test substrate.

Run a predeclared beam sweep with all generation semantics explicit:

- beam widths: at minimum `1, 4, 8, 16, 32` (add 64 only if feasible);
- identical max-new-token budget and prompt;
- explicit EOS / pad;
- report both the repository-compatible HuggingFace length-normalized beam score and a raw cumulative-log-probability rescoring / selection view where technically valid;
- no sampling in the primary comparison;
- report output length, EOS rate, BLEU and COMET/chrF as secondary semantic checks.

**Gate:** the claimed modern non-collapse must survive explicit semantics. If a faithful scoring interpretation restores a classic severe large-beam collapse, L36 is **KILL as a Main route**. Do not pivot into a decoder-configuration paper.

### E01b — old uncertainty substrate, modern LLM

Use the ACL-2022 WMT19 English→German multi-reference substrate with the published additional human references. Freeze the exact human-reference uncertainty score before model inference.

Primary modern checkpoint: an open translation-specialized LLM supporting English→German, e.g. `Unbabel/TowerInstruct-7B-v0.2` (exact revision and prompt frozen before scoring).

Run the same explicit beam-width sweep.

Primary estimand:

> **`beam_width × intrinsic_uncertainty` interaction on translation quality**, with uncertainty either continuous or in predeclared quantiles.

Required reporting:

- corpus / quantile multi-reference BLEU and chrF;
- sentence-level quality statistic only as a supporting analysis;
- output length and EOS rate by uncertainty × beam;
- candidate sequence scores needed for the later frontier audit;
- no LLM judge as the load-bearing target.

### Mother gate

L36 proceeds only if both are true:

1. a modern open LLM shows no classic severe large-beam quality collapse under explicit semantics; and
2. the **high-intrinsic-uncertainty** stratum specifically fails to recover the strong adverse beam-width pattern predicted by the old law.

If high-`u` modern examples reproduce the classic law, **STOP / KILL**. The old law survives; TACL's aggregate result was not a scientific regime change.

### Scope

No training, model zoo, new data collection, new evaluator, new decoder, or calibration method is authorized in E01.

---

## 8. Resolution / feasibility

This is unusually favorable for a first-stage mechanistic question:

- E01 is inference-only;
- WMT19 + additional human references already provide the load-bearing uncertainty observable;
- WMT-scale test sets provide hundreds of independent items per uncertainty bin;
- the classic beam-width effect is large, so E01 does not rely on resolving a 1–2 pp second-order training interaction;
- one 7B translation LLM plus the released TACL checkpoint is sufficient for the gate.

The purpose of E01 is not to estimate a tiny null. If uncertainty-stratified curves are too noisy to distinguish a classic collapse from saturation, HOLD rather than expanding models post hoc.

---

## 9. Successful-result chain

The strongest E01 result would be:

> same human-defined high-uncertainty MT inputs that motivated the old law → modern translation LLM remains stable as beam widens under faithful decoding semantics → external task ambiguity alone is no longer sufficient to induce the beam-search curse.

That result alone authorizes mechanism work; it is not yet the final Main contribution.

A Main-level successful chain must later become:

> fixed intrinsic ambiguity → changed model-side search geometry identified → selective intervention restores/removes the curse → **revised conditional law explaining when uncertainty becomes search pathology**.

A candidate revised law might take the qualitative form:

> intrinsic ambiguity produces the beam-search curse only when it is transmitted into a diffuse / poorly terminated model distribution whose wider-search frontier increasingly exposes inadequate high-score hypotheses.

That wording is a hypothesis, not a pre-declared conclusion.

---

## 10. Outcome interpretations / kill rules

### Outcome A — old law survives

High-`u` LLM sentences deteriorate strongly with beam under matched semantics.

**Verdict:** KILL L36. TACL's aggregate result does not establish a regime shift.

### Outcome B — reversal is only scoring/stopping convention

Raw/classical semantics recover the old curse; modern defaults hide it.

**Verdict:** KILL Main route. Do not rescue as a HuggingFace configuration note.

### Outcome C — genuine broken law

High-`u` modern LLM sentences remain stable under wider beam even after semantics are controlled.

**Verdict:** E01 PASS. Then a fresh authorization may test B/C/D accounts with model-side distribution measures and a selective causal operation (e.g. controlled EOS/length perturbation).

### Outcome D — heterogeneous only by a predeclared structural variable

Potentially meaningful only if it is already motivated by the old literature (e.g. sentence-level intrinsic uncertainty / length). No post-hoc taxonomy mining.

---

## 11. Main-level growth path

If E01 passes:

- **C1 — law break:** reproduce the old uncertainty-conditioned pathology on classic NMT evidence and show that it fails in modern LLM-MT on the same intrinsic-uncertainty construct;
- **C2 — missing link:** identify which model-side relation changed (termination/length, probability-mass spread/mode adequacy, or search-frontier likelihood–quality ordering);
- **C3 — causal boundary:** selectively perturb that relation and recover / remove the curse as predicted;
- **C4 — revised law:** explain why high task ambiguity is insufficient by itself and state the hidden model/search condition that mediates the pathology.

No new MT method is required. A method is acceptable only as a consequence of the scientific result, not as the paper identity.

---

## 12. Verdict

```yaml
natural_question: PASS
provenance: OLD_LAW_X_MODERN_REGIME_PREMISE_COLLISION
mother_phenomenon: PASS_WITH_BOUNDED_REPLICATION_GATE
old_law: STRONG_ACL_MAIN
modern_reversal: TACL_SUPPORTED_BUT_NEEDS_EXPLICIT_SEMANTICS_AUDIT
anti_resurrection: PASS
same_quantity: PASS_VIA_PUBLISHED_MULTI_REFERENCE_UNCERTAINTY
central_owner: NOT_FOUND
reviewer_compression: SERIOUS_BUT_SURVIVABLE_ONLY_WITH_MECHANISM
successful_result_upper_bound: PASS
identification: PASS_FOR_E01_LAW_BREAK
resolution: PASS_FOR_E01
compute_cost: LOW_INFERENCE_ONLY
mainline: NO
verdict: PILOT_AUTHORIZED_E01_ONLY
```

**Authorized now:** only E01a/E01b above.  
**Not authorized:** mechanism training, decoder design, broad model sweep, new dataset/benchmark, quality-estimation method, RL, or paper-scale expansion.

**Promotion condition:** a modern LLM must violate the old uncertainty-conditioned large-beam pathology under explicit matched decoding semantics. Only then is there a law break worth explaining.