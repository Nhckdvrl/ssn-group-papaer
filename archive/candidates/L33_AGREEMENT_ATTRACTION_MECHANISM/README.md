# L33 — Where Does Agreement Go Wrong?

**Status:** `PILOT-AUTHORIZED — E01 ONLY`  
**Date:** 2026-09-13  
**Target:** ACL / EMNLP / NAACL Main

## RQ

> **When a distractor noun pulls a language model toward the wrong subject–verb agreement, is the controller-number state already corrupted before verb prediction, or does the correct controller information survive and lose only when the model reads it out?**

Short form:

> **Does agreement attraction come from state distortion or access competition?**

## Mother phenomenon

Agreement attraction is the classic failure in examples such as:

> `The key to the cabinets unsurprisingly was/were rusty.`

A plural distractor (`cabinets`) pulls prediction/processing toward a plural verb even though the grammatical controller (`key`) is singular.

This is not a phenomenon we need to discover from scratch. Agreement attraction has a long human psycholinguistic literature and has repeatedly appeared in neural language models. Most recently, von der Malsburg & Padó (2026), *Diverging Transformer Predictions for Human Sentence Processing*, test 11 autoregressive Transformers and find that prepositional-modifier configurations robustly reproduce human-like attraction patterns, including Gemma-3 base models.

Primary modern model source:

- https://arxiv.org/abs/2603.16574

Classic computational/theoretical distinction:

- **representation / state distortion:** the attractor corrupts the number state that will later drive agreement;
- **retrieval / access interference:** the controller representation remains intact, but the wrong item/information wins when agreement is computed.

Recent human evidence does not close this distinction. Large-scale/model-comparison work favors hybrid accounts, and 2026 experiments provide renewed evidence that representational distortion contributes alongside retrieval interference.

Relevant sources:

- Wagers, Lau & Phillips 2009: https://doi.org/10.1016/j.jml.2009.04.002
- Yadav et al. / *Number feature distortion modulates cue-based retrieval in reading*: https://doi.org/10.1016/j.jml.2022.104458
- Keshev et al. 2026: https://doi.org/10.3389/flang.2025.1708378

## What prior LLM work owns — and does not own

Prior LLM work owns important components:

- Ryu & Lewis 2021 show GPT-2 surprisal reproduces agreement-attraction effects and use attention entropy as a proxy for retrieval competition: https://aclanthology.org/2021.cmcl-1.6/
- Bazhukov et al. 2024 probe agreement attraction in Russian: https://aclanthology.org/2024.conll-1.22/
- Ferrando & Costa-jussà 2024 identify a causal SVA circuit / subject-number signal in Gemma: https://aclanthology.org/2024.findings-emnlp.590/
- Kryvosheieva et al. ACL 2026 show different agreement phenomena recruit overlapping causally relevant units: https://aclanthology.org/2026.acl-long.7/
- Gidi et al. 2026 trace agreement circuitry across languages and model families: https://arxiv.org/abs/2608.18545

The closest 2026 circuit work explicitly filters to **successful agreement behavior**. It identifies machinery for correct agreement; it does not identify why attraction errors happen.

No direct owner was found that causally separates, within the same autoregressive LM attraction effect, **pre-readout state corruption** from **late distractor access**.

## Why decoder-only Transformers make the old distinction newly identifiable

The causal mask gives a useful asymmetry.

In a pair that differs only in attractor number:

- all token states **before** the attractor are identical;
- the attractor cannot rewrite an earlier subject token's cached state;
- but it can change the contextual state built at later positions;
- and later agreement computation can also directly access the attractor again through attention.

Therefore L33 does **not** claim that the literal subject-token KV is overwritten. `State distortion` is operationally the attractor-number effect that has already entered the **derived pre-verb controller/context state** before the agreement readout; `access competition` is fresh causal influence from the distractor during the later readout.

This is a model-computation question, not a claim that Transformer memory is identical to human memory.

## Authorized E01

### Model

Use `google/gemma-3-4b-pt` only for E01.

Reason: the 2026 11-model agreement-attraction study already reports the relevant PP attraction pattern for this exact base model, so E01 is not model-shopping for a phenotype.

### Published stimuli only

Use Wagers et al. (2009) published materials, with no new hand-written primary test set.

Two disjoint roles:

1. **Experiment 1 / clean-SVA instrument set:** subject number varies, no attractor; a neutral adverb precedes the agreement-bearing verb.
2. **Experiment 4 / attraction set:** singular subject + singular/plural PP attractor + neutral adverb before the verb, e.g. `The key to the cabinet(s) unsurprisingly was/were ...`.

The neutral adverb is essential: it creates one same-token prediction position after the attractor and before the verb.

Filter only for model-tokenization validity:

- singular/plural attractor variants have aligned token counts;
- target singular/plural verb forms can be compared cleanly;
- no condition-specific truncation or prompt rewriting.

If fewer than 16 Experiment-4 lexical item sets survive, `HOLD — SUPPORT`; do not manufacture a large synthetic benchmark to rescue E01.

### Behavioral observable

At the pre-verb position define

`m(x) = log2 P(V_sg | x) - log2 P(V_pl | x)`.

For a singular controller, define attraction shift

`A = m(singular-attractor) - m(plural-attractor)`.

Positive `A` means the plural attractor causally shifts the model toward the erroneous plural verb.

### Mother / leverage gate

Before any internal mechanism interpretation:

1. clean no-attractor / matching-number SVA must prefer the grammatical verb on at least 80% of retained items;
2. Experiment-4 attraction must have `mean A >= 0.5 bits`;
3. a paired item bootstrap 95% CI for `A` must exclude 0 in the predicted direction.

If any gate fails: **STOP.** Do not search templates, nouns, prompts, or another model to manufacture attraction.

## E01 causal decomposition

The singular-attractor and plural-attractor runs differ only in attractor number. Because of causal masking, positions before that attractor are identical.

For every Transformer layer boundary `l`, run a path-specific decomposition at the neutral-adverb / pre-verb prediction position.

### 1. FULL

Ordinary plural-attractor run. This contains the full attraction effect.

### 2. STATE-CLEAN(l)

Run the plural-attractor sentence, but at the neutral-adverb position replace the residual state immediately before layer `l` with the corresponding state from the singular-attractor run.

Then continue normally with the **plural attractor's own cached K/V still available** in all later layers.

Interpretation: removes all attractor-number influence already integrated into the current pre-verb state by layer `l`, while preserving opportunities for fresh later access to the plural distractor.

### 3. ACCESS-CLEAN(l)

Keep the plural-attractor residual state at layer `l`, but from layer `l` onward replace only the attractor→pre-verb attention-edge contribution with its singular-attractor counterpart.

All already-accumulated contextual state remains plural-attractor state.

Interpretation: preserves early/state-mediated influence but prevents fresh late direct access to the plural attractor.

### 4. BOTH-CLEAN(l)

Combine the two operations.

This is an instrument-completeness control. With one neutral position between attractor and verb, any post-attractor influence on the final prediction must either already be in that position's residual state at the boundary or enter it through later causal access from the attractor. Earlier source positions are identical across the pair.

### Completeness gate

At some contiguous layer region, `BOTH-CLEAN` must recover at least **70%** of the singular-vs-plural attractor logit-margin difference without materially destroying clean-SVA performance.

If it does not, mark `HOLD / INSTRUMENT INCOMPLETE`. Do not narrate the residual as a third mechanism after seeing the result.

## Pre-result interpretations

- **State-dominant:** cleaning the pre-readout state removes most attraction while later access-cleaning adds little. The model has already built a distorted controller/context state before final agreement readout.
- **Access-dominant:** the pre-readout state can remain attraction-contaminated with little consequence, while blocking late distractor access removes the effect. Correct controller information survives but loses during readout/competition.
- **Hybrid:** both channels make material, separable contributions or a stable interaction is required. This is scientifically legitimate and connects naturally to modern psycholinguistic hybrid accounts.
- **No complete/selective decomposition:** E01 kills/holds L33. Do not pivot to generic syntax-unit localization or another attraction benchmark.

Report the entire layerwise recovery curve and item-clustered uncertainty; do not choose a layer post hoc for the headline.

## Strongest reviewer compression

> `Classic agreement-attraction theory already debates distortion vs retrieval + Ryu & Lewis say Transformer attention looks retrieval-like + recent SVA circuit papers identify subject-number machinery = L33.`

Why this does **not** entail the result:

- attention entropy is a retrieval proxy, not a causal separation of failure stages;
- correct-SVA circuitry does not tell us how an attraction error enters that circuitry;
- 2026 human work specifically reopens representational distortion, so a retrieval interpretation is not theoretically predetermined;
- recent SVA circuit work often excludes error cases by design;
- none of the components predicts whether the causal attractor effect is already embedded in the pre-readout state, enters during late access, or requires both.

Verdict: `PLAUSIBLE INDEPENDENT CONTRIBUTION`.

## Main-level growth path — NOT AUTHORIZED YET

Only if E01 yields a selective, reproducible decomposition:

1. **Feature-updating prediction.** Use the published Keshev et al. paradigm where an earlier overt agreement cue can update the subject representation. A state-distortion account predicts selective reduction of the early/state channel; an access account predicts a different pattern.
2. **Construction boundary.** The 2026 comprehensive Transformer study finds PP attraction human-like but object-extracted RC attraction divergent. Test whether this behavioral boundary corresponds to a change in the causal channel rather than merely a score difference.
3. **Optional cross-linguistic consequence.** 2026 syncretism work reports unexplained language variation using surprisal/attention proxies. Only after C1/C2, test whether the state/access decomposition predicts when syncretism amplifies attraction.

These deepen one identity: **where interference enters the agreement computation and why its behavioral signature changes across conditions.** They are not authorized by this README.

## Non-authorized

Do not yet do:

- cross-lingual sweep;
- model zoo;
- instruction-tuned comparisons;
- SAE/probe atlas;
- human-subject experiments;
- new attraction benchmark;
- new agreement training method;
- training-dynamics study;
- claims about the human brain/memory mechanism.

# Verdict

## `PILOT-AUTHORIZED — E01 ONLY`

E01 is exactly the bounded mother-validation + path-decomposition experiment above. Full-study status depends on E01.