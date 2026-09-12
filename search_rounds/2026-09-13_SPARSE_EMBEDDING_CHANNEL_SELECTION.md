# L32 Selection — Where Do Ultra-Sparse Tuned Token Embeddings Act?

**Date:** 2026-09-13  
**Target:** ACL / EMNLP / NAACL Main  
**Verdict:** **PILOT-AUTHORIZED — E01 ONLY**

This record authorizes one bounded causal-localization experiment. It does **not** authorize a full paper program, broad multilingual sweep, representation study, or new PEFT method.

---

## 1. RQ, mother phenomenon, importance

### Plain-language RQ

> **When only a handful of frequent token embeddings learn a translation task, where does their causal effect actually enter a decoder-only LM: through the task/source prefill, through generated-target feedback, or through both?**

Short title / mnemonic:

> **Where Do 18 Embeddings Work?**

### Mother phenomenon

Yuan et al., NAACL 2025, *KS-Lottery: Finding Certified Lottery Tickets for Multilingual Transfer in Large Language Models*:

https://aclanthology.org/2025.naacl-long.458/

The paper establishes a large, non-fragile mother effect:

- LLaMA-7B without tuning averages ~4.6 spBLEU over the reported en→{ro, es, de, ca} set;
- full tuning is ~27.3 and embedding tuning ~29.0;
- Partial Tuning using the tiny selected token-embedding set reaches ~27.9 average;
- en→ca with the strict set uses only **18 token embeddings** and reaches 37.7 spBLEU versus 5.7 for the base model;
- the selected rows include high-frequency / function-like tokens such as newline, `a`, `the`, `in`, `to`, `of`, `and`, punctuation, digits, etc.;
- the authors explicitly find winning tickets are high-frequency tokens and show Frequency Tuning nearly matches full embedding tuning (28.8 avg vs 27.9 for embedding tuning in their five-language table);
- standard Prefix Tuning is substantially weaker (17.4 avg vs 27.9 Partial Tuning in the four-language comparison).

This is not a paper that depends on first discovering a tiny effect. The unresolved object is the **causal route by which the already-large sparse-embedding effect enters autoregressive computation**.

### Why important

The published result is often read as evidence that multilingual/task adaptation has an extremely low-dimensional locus in the embedding layer. But an input embedding row in a decoder-only LM is reused in multiple computational roles:

1. instruction/template tokens during prefill;
2. source-sentence tokens during prefill;
3. generated target tokens when they are fed back as autoregressive history.

Those interpretations imply very different science:

- **source interface / lexical-context adaptation**;
- **task-prompt adaptation**;
- **recurrent target-side control injection**;
- or a **joint source↔target interaction**.

Knowing that 18 rows suffice does not tell us which of these is load-bearing.

---

## 2. Scientific accounts and decisive operation

### Accounts

**A — Source-interface account.**  
The tuned rows mainly change how the frozen transformer interprets the instruction/source context. Their useful effect should already be present before target generation begins.

**B — Autoregressive-feedback account.**  
The rows are powerful because high-frequency winner tokens repeatedly re-enter the network in the generated target prefix, acting like recurrently injected control vectors. Their effect should appear mainly after target generation begins and should grow after winner-token occurrences in the target history.

**C — Task-prefix account.**  
A substantial share of the effect is carried by occurrences in the fixed translation instruction/template rather than the source content or target history.

**D — Joint-access account.**  
Neither phase alone is sufficient; the sparse update works because the same adapted rows are reused across phases and their effects interact.

### Decisive operation

Train **one** sparse-embedding-adapted model, then at inference selectively expose the *same learned embedding deltas* at different token positions. No retraining differences are used to define the main causal comparison.

For every selected token row `e_i`, retain both:

- base row `e_i^0`;
- tuned row `e_i^*`.

At each input position choose `e_i^0` or `e_i^*` according to segment role.

Primary arms:

- **BASE** — base rows everywhere;
- **ALL** — tuned winner rows wherever they occur (ordinary Partial Tuning behavior);
- **INSTRUCTION** — tuned rows only in the fixed instruction/template span;
- **SOURCE** — tuned rows only inside the source sentence;
- **PREFILL** — tuned rows in instruction + source, base rows for generated-target feedback;
- **TARGET** — base rows in the full prefill, tuned winner rows only when generated/reference target tokens are subsequently fed back as input.

Because generation uses KV cache, this intervention is cleanly implementable: prefill embeddings are fixed at the initial pass, while each newly generated target token can independently use the base or tuned row on the next step.

---

## 3. Anti-resurrection + closest owners + reviewer compression

### Anti-resurrection

No killed repo parent was found that owns this exact scientific object. It is not K168/tokenizer bottleneck, not generic multilingual competence, not generic PEFT, and not a representation/readout probe story. The causal object is **the phase/segment through which an already-established sparse parameter update affects decoder-only computation**.

### Closest owners

1. **Yuan et al. 2024, Findings ACL — How Vocabulary Sharing Facilitates Multilingualism in LLaMA?**  
   https://aclanthology.org/2024.findings-acl.721/  
   Establishes that embedding tuning and very early layers can activate multilingual capability; attributes cross-lingual behavior partly to vocabulary sharing. It does not isolate source, instruction, and target-history access to tuned rows.

2. **Yuan et al. 2025, NAACL — KS-Lottery.**  
   https://aclanthology.org/2025.naacl-long.458/  
   Owns the sparse winning-ticket phenotype, selection/certification, frequency observation, and PEFT result. It does not identify *where in the autoregressive sequence* the tuned rows causally matter.

3. **Li & Liang 2021 — Prefix-Tuning.**  
   Establishes that a small number of learned prefix vectors can condition a frozen LM. This makes a static-prompt explanation plausible, but does not imply the role of naturally recurring tuned token embeddings. Moreover KS-Lottery's own comparison shows standard Prefix Tuning is materially weaker than sparse token-embedding tuning in this setting.

4. **Qu et al. 2025, MRL — Improving Language Transfer Capability of Decoder-only Architecture in Multilingual NMT.**  
   https://aclanthology.org/2025.mrl-main.13/  
   Shows that source/target interaction and source-token encoding are important in decoder-only multilingual translation. It does not study sparse embedding adaptation or its causal access channel.

5. **LLaMA architecture.**  
   Hugging Face `LlamaConfig` uses `tie_word_embeddings=False` by default. Thus changing the selected input rows does not directly change the LM-head logits; the causal effect must occur when those token IDs are read as inputs.  
   https://huggingface.co/docs/transformers/en/model_doc/llama

### Strongest reviewer compression

> `Embedding tuning activates multilinguality + KS-Lottery says 18 frequent rows suffice + prefix vectors can steer generation + decoder-only MT mixes source and target context = your paper.`

### Why that compression does **not** imply the strongest result

Those components do not determine whether the sparse gain is carried by:

- instruction occurrences,
- source occurrences,
- autoregressively re-entered target occurrences,
- or cross-phase reuse.

They make each account plausible. They do not choose among them. In particular, Prefix Tuning being much weaker than Partial Tuning prevents the simple inference that the 18 rows are merely a tiny soft prompt, while the 2024 vocabulary-sharing paper does not establish that source-side occurrences are the causal locus.

**Ownership verdict:** `PLAUSIBLE INDEPENDENT CONTRIBUTION`.

---

## 4. Identification

### Behavioral observable

Two complementary observables on Flores-101 en→ca:

1. **free-running translation quality:** spBLEU with the parent-style decoding setup;
2. **fixed-trajectory next-token behavior:** teacher-forced reference-token log probability / NLL and next-token accuracy, using the gold target prefix.

The teacher-forced observable is important because it localizes target-feedback effects without letting different generated sequences create different future inputs.

### Primary estimands

For metric `M`, define sparse-adaptation gain:

`Δ_ALL = M(ALL) - M(BASE)`.

For channel `c`:

`Δ_c = M(c) - M(BASE)`

and recovery fraction:

`R_c = Δ_c / Δ_ALL`.

Main comparisons:

- `R_PREFILL` vs `R_TARGET`;
- decomposition of `R_PREFILL` into `R_INSTRUCTION` and `R_SOURCE`;
- `M(ALL)` relative to `M(PREFILL)` and `M(TARGET)` to detect joint dependence.

For teacher-forced evaluation, additionally estimate target-position effects as a function of whether/how many winner-token occurrences have appeared previously in the target prefix. This timing analysis is diagnostic, not a separate paper claim.

### Why the intervention identifies the intended quantity

- Same base model.
- Same learned 18-row update.
- Same examples.
- Same decoding/evaluation.
- Only **where the already-learned delta is causally accessible** changes.
- LLaMA input embeddings are untied from the output head, so the intervention is not secretly changing output classifier weights.

This is much cleaner than training separate source-only / target-only models and interpreting optimizer differences as mechanism.

### Support audit

Before interpreting TARGET vs PREFILL, count occurrences of the 18 selected token IDs separately in:

- fixed instruction/template;
- source sentences;
- reference target sentences.

The pilot proceeds only if SOURCE and TARGET each have enough independent support for estimation. Operationally, require at least **250 Flores sentences with ≥1 selected-token occurrence** in each of source and reference-target spans. Given the selected punctuation/function tokens this is expected, but it must be checked rather than assumed.

If this fails, **HOLD / redesign**; do not declare the absent channel unimportant from zero opportunity.

---

## 5. E01 first-stage validity

### Training setup

Use the parent en→ca regime as closely as possible:

- **model:** LLaMA-7B family checkpoint compatible with the published 32k token IDs; do not silently substitute a tokenizer/model with different row semantics;
- **training data:** 10k en→ca bilingual instruction examples from the public Lego-MT parallel source;
- **trainable parameters:** the published strict 18 token rows from the en→ca KS-Lottery table;
- **all transformer parameters and LM head frozen**;
- parent Partial-Tuning hyperparameter starting point: LR `1e-2`, 5 epochs;
- **3 independent training seeds** if exact parent initialization/data order is unavailable.

### Instrument / mother replication gate

Before any mechanism interpretation, ordinary **ALL** access must reproduce a large sparse-tuning effect.

Frozen gate:

> `spBLEU(ALL) - spBLEU(BASE) >= +15` on en→ca Flores devtest, and the effect must have the same sign in all 3 training seeds.

The published gap is much larger (~+32 for en→ca), so +15 is deliberately conservative while still requiring material causal leverage.

If this gate fails:

> **STOP E01. No source/target mechanism claim.**

Diagnose only compatibility/data/token-ID reproduction. Do not prompt-search or reinterpret a weak first stage.

---

## 6. Successful-result chain

### If TARGET dominates

Observation:

> Most of the sparse adaptation gain disappears when tuned rows are denied to target-prefix feedback, even though source/instruction access remains; target-only access recovers a large fraction of the gain and effects emerge after winner-token occurrences.

Inference:

> Ultra-sparse embedding adaptation is not mainly a lexical remapping of source words. Frequent adapted rows act as **recurrently re-injected control/state vectors** during autoregressive generation.

Main-level potential:

> Parameter count is not the right explanation for why these 18 rows are powerful; **reuse opportunity over the trajectory** is load-bearing.

### If SOURCE dominates

Observation:

> Source-only access recovers most of the gain, before target feedback can act.

Inference:

> A tiny set of frequent function/context token embeddings reconfigures how the frozen transformer reads the source, despite almost all source lexical embeddings remaining unchanged.

Main-level potential:

> Sparse multilingual adaptation operates through a small number of **context anchors / interface vectors**, not by broadly relearning a target vocabulary.

This is not already implied by “vocabulary sharing”: the experiment identifies the causal sequence phase, and the 18 rows are far too sparse to constitute ordinary vocabulary remapping.

### If INSTRUCTION dominates

Observation:

> Tuned rows matter primarily where they occur in the fixed task instruction/template.

Inference:

> The published “multilingual winning ticket” is substantially a task-conditioning interface rather than a language-wide parameter locus.

This would materially reinterpret the parent result. It would then require follow-up prompt/template transfer before any full-study claim.

### If joint access is necessary

Observation:

> PREFILL and TARGET alone recover little, while ALL recovers the large mother effect.

Inference:

> The same sparse update functions through **cross-phase reuse** rather than a single static location.

This is also scientifically meaningful and predicts strong dependence on occurrence pattern / trajectory reuse.

### Failure outcome

If channel effects are small, unstable across seeds, or explained entirely by opportunity/support differences after the predeclared support audit, E01 kills/holds this route. Do not invent a new representation paper.

---

## 7. Resolution / compute budget

### Effect size and statistical resolution

Published mother effect for en→ca:

- BASE: ~5.7 spBLEU;
- strict sparse Partial Tuning: ~37.7 spBLEU.

Therefore the first-stage effect is enormous relative to ordinary evaluation noise.

E01 uses paired inference on the **same Flores examples**, so channel contrasts can use paired bootstrap confidence intervals. Teacher-forced evaluation additionally provides thousands of target-token observations, clustered by sentence. A several-point spBLEU channel contribution or a substantial fraction of the parent gain should be resolvable without a model-zoo sweep.

### Compute

Training changes only 18 embedding rows but still backpropagates through a 7B frozen transformer. The bounded budget is:

- one 7B model;
- one language pair;
- 10k training examples;
- 5 epochs;
- up to 3 training seeds;
- six cheap inference-time access arms on one Flores devtest.

This is comfortably smaller than controlled pretraining / RL pilots and is feasible on a single modern 80–96GB GPU per seed. No full-model training is authorized.

### Resolution stop rule

If the ALL first stage passes but 95% paired bootstrap intervals remain broad enough that both `PREFILL-dominant` and `TARGET-dominant` interpretations remain plausible, mark **HOLD — RESOLUTION**, increase only evaluation resampling / a predeclared second natural test split if available, and do not scale models first.

---

## 8. Main-level growth path

E01 is only causal channel identification. A Main paper is plausible only if E01 creates a stable mechanism to deepen.

Natural same-identity continuations, each requiring fresh authorization:

1. **Reuse/opportunity law.** Does adaptation value track how often a tuned row is causally re-entered in the relevant phase, rather than semantic identity or parameter magnitude?
2. **Training-origin intervention.** Mask gradients to selected rows by sequence segment during training and test whether the channel identified by E01 is also where the useful update is learned.
3. **Cross-language prediction.** Does source-vs-target frequency/support predict which rows become winning tickets across language pairs?
4. **Mechanistic consequence.** Trace how one winner-row perturbation changes target-language state or translation logits over subsequent positions, conditioned on the E01-supported account.

Do **not** start with a 101-language sweep, a new KS selection algorithm, or a PEFT leaderboard. Those would dilute the scientific identity.

---

## 9. Final gate

Question worth knowing before result? **YES.**  
Stable mother? **YES, large published effect.**  
Owner already answers channel question? **NO found direct owner after exact/source-target/sparse-embedding searches.**  
A+B+C naturally entails answer? **NO. Competing components support different accounts.**  
Decisive operation selective? **YES — same learned deltas, segment-gated at inference.**  
First-stage causal leverage test? **YES — ALL vs BASE >= +15 spBLEU required.**  
Resolvable at current budget? **YES, conditional on mother replication/support audit.**  
Can strongest result grow without padding? **YES, via reuse/opportunity law and training-origin intervention.**

# Verdict

> **PILOT-AUTHORIZED — E01 ONLY**

Authorized E01:

> Reproduce the large en→ca 18-row sparse-tuning effect, then causally gate the *same tuned embedding rows* by instruction / source / target-feedback segment under both fixed-trajectory and free-running evaluation to determine where the sparse adaptation gain enters decoder-only computation.

### Hard non-authorizations

- no broad multilingual/model-zoo sweep;
- no hidden-state/probing package before E01;
- no new PEFT method;
- no claim that high frequency itself is causal before a separate controlled test;
- no source/target conclusion if segment occurrence support is inadequate;
- no mechanism story if ALL fails the +15 spBLEU first-stage gate.