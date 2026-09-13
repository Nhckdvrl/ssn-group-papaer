# L33 Selection — Where Does Agreement Go Wrong?

**Date:** 2026-09-13  
**Target:** ACL / EMNLP / NAACL Main  
**Verdict:** **PILOT-AUTHORIZED — E01 ONLY**

This authorizes one bounded mechanism-identification experiment. It does **not** authorize a full paper program, model zoo, multilingual sweep, new benchmark, or new syntax-training method.

---

## 1. RQ + mother phenomenon + why important

### Plain-language RQ

> **When a distractor noun pulls a language model toward the wrong subject–verb agreement, is the controller-number state already corrupted before verb prediction, or does the correct controller information survive and lose only when the model reads it out?**

Short form:

> **Does agreement attraction come from state distortion or access competition?**

### Mother phenomenon

Agreement attraction is a classic, stable interference effect. In sentences such as:

> `The key to the cabinets unsurprisingly was/were rusty.`

a plural distractor (`cabinets`) can pull processing or prediction toward the ungrammatical plural verb even though the grammatical controller (`key`) is singular.

The phenotype is not speculative. It has a large human psycholinguistic literature and has repeatedly appeared in autoregressive language models. A 2026 study of 11 autoregressive Transformers reports robust human-like attraction in prepositional-modifier configurations, including the exact `google/gemma-3-4b-pt` family used by the proposed E01.

### Scientific pressure

The old theoretical dispute is not simply whether attraction exists, but **where the error enters the computation**:

- **representation / state distortion:** the distractor corrupts the number state that will later control agreement;
- **retrieval / access interference:** the grammatical controller remains represented, but the wrong information wins during the agreement readout.

Human evidence has not closed this distinction; recent work instead favors hybrid accounts or finds renewed evidence for distortion. Transformer computation gives a new opportunity to identify the two channels directly.

This matters beyond one syntax phenomenon because it asks a general model-computation question:

> **When a model makes a structured dependency error under interference, did it build the wrong internal state, or did it build the right state and access the wrong source at decision time?**

---

## 2. Candidate accounts + decisive operation

### Account A — State-distortion / construction failure

The plural distractor changes the contextual controller state **before** the final agreement computation. By the time the model predicts the verb, the state available to the agreement circuit is already biased toward plural.

Prediction: removing distractor-number influence already accumulated in the pre-verb contextual state should remove most attraction, even if the distractor remains available for later attention.

### Account B — Late-access / retrieval competition

The grammatical controller information remains available, but during the final agreement computation the model directly re-reads / weights the distractor and the wrong source wins.

Prediction: attraction should survive cleaning the earlier contextual state but disappear when fresh late access from the distractor to the pre-verb position is blocked.

### Account C — Hybrid

Both channels make material separable contributions or interact. This is pre-specified and scientifically meaningful because modern psycholinguistic model comparisons already motivate hybrid accounts.

### Decisive operation

Use a minimal singular-vs-plural-attractor pair from Wagers et al. (2009) Experiment 4 with a **neutral adverb between attractor and critical verb**:

`The key to the cabinet(s) unsurprisingly was/were ...`

At the neutral-adverb / pre-verb prediction position, for every Transformer layer boundary `l` compare:

1. **FULL** — ordinary plural-attractor run.
2. **STATE-CLEAN(l)** — replace the pre-verb residual state before layer `l` with its singular-attractor counterpart while keeping the plural attractor's own cached K/V available in all later layers.
3. **ACCESS-CLEAN(l)** — retain the plural-attractor residual state at `l`, but from `l` onward replace only the attractor→pre-verb attention-edge contribution with its singular-attractor counterpart.
4. **BOTH-CLEAN(l)** — combine the two.

The important identification fact is the causal mask: positions before the attractor are identical across the pair, the attractor cannot rewrite earlier subject-token states, and with one neutral position before the verb its influence on the final pre-verb state must either already have entered that contextual state by the chosen layer boundary or enter through later causal access from the attractor.

The operation therefore does **not** patch in the correct verb or an externally decoded grammatical label.

---

## 3. Anti-resurrection + closest owners + strongest reviewer compression

### Repo anti-resurrection

No existing killed parent in the repository was found for `agreement attraction + representation distortion vs retrieval/access competition`. It is not a generic syntax competence test and not a probe-only representation project.

### Closest owners

1. **Wagers, Lau & Phillips (2009)** — classic agreement-attraction evidence and retrieval-based theory; the published Experiment-4 materials provide the buffered attractor→adverb→verb structure used here.
2. **Ryu & Lewis (2021, CMCL)** — reproduces attraction with GPT-2 surprisal and uses attention entropy as a proxy for retrieval interference. It does not causally separate state corruption from access.
3. **Bazhukov et al. (2024, CoNLL)** — agreement-attraction probing in Russian; not a path-specific causal decomposition.
4. **Ferrando & Costa-jussà (2024, Findings EMNLP)** — identifies a causal subject–verb agreement circuit / subject-number signal in Gemma using activation patching. It studies successful agreement machinery, not the causal origin of attraction errors.
5. **Kryvosheieva et al. (ACL 2026)** — shows multiple agreement phenomena recruit overlapping causally relevant units across models/languages. It does not distinguish error-stage accounts for attraction.
6. **Gidi et al. (2026)** — traces shared agreement circuits across languages/model families but explicitly filters to examples where the model successfully produces the relevant inflection, leaving error-generation mechanisms unresolved.
7. **Recent human model-comparison / feature-distortion work** — does not settle retrieval vs representation distortion; hybrid accounts remain competitive and 2026 evidence re-opens a substantive role for distortion.

### Strongest reviewer compression

> `Classic psycholinguistics already debates distortion vs retrieval + Ryu & Lewis show Transformer attention looks retrieval-like + recent SVA circuit papers locate subject-number machinery = your paper.`

### Why that compression does not entail the strongest result

- attention entropy is a retrieval **proxy**, not a causal decomposition of the attractor effect;
- correct-SVA circuitry does not reveal where an error enters that circuitry;
- recent human evidence makes a pure retrieval interpretation non-obvious;
- recent LLM circuit work commonly removes error cases from the mechanism analysis;
- none of these prior results predicts whether the attractor's causal effect is state-mediated, late-access-mediated, or hybrid in the same checkpoint and same items.

**Ownership verdict:** `PLAUSIBLE INDEPENDENT CONTRIBUTION`.

---

## 4. Identification

### Observable

At the pre-verb position:

`m(x) = log2 P(V_sg | x) - log2 P(V_pl | x)`.

For a singular controller:

`A = m(singular-attractor) - m(plural-attractor)`.

Positive `A` is the item-level attraction shift toward the erroneous plural verb.

### Why the operation identifies the intended channels

The singular/plural-attractor pair is a natural intervention on the distractor's number feature while controller, structure, pre-attractor prefix and target alternatives are fixed.

Because a causal decoder cannot retroactively alter states at positions before the attractor, the attractor-number effect can reach the final pre-verb prediction in two ways relative to any chosen layer boundary:

- it has already been integrated into the current pre-verb contextual state;
- or it enters through later access from the attractor token.

`STATE-CLEAN` and `ACCESS-CLEAN` selectively remove these channels; `BOTH-CLEAN` tests whether the decomposition captures the total measured attractor effect.

### Selectivity control

Use Wagers Experiment 1 no-attractor / matching-number SVA items as a disjoint clean-agreement instrument set. Any operation that removes attraction only by generally destroying agreement computation fails selectivity.

### Caveat locked before results

`State distortion` is operationally a distortion of the **derived contextual controller state after the attractor**, not literal retroactive corruption of the earlier subject token's cached representation. L33 makes no claim that Transformer memory is architecturally identical to human memory.

---

## 5. E01 first-stage / support gates

### Model

`google/gemma-3-4b-pt` only.

This is pre-specified because the 2026 comprehensive attraction study already reports the relevant PP attraction phenotype for this base-model family. E01 must not search model families for a convenient effect.

### Data

Published Wagers et al. (2009) materials only:

- Experiment 1 = clean-SVA instrument set;
- Experiment 4 = attraction set with neutral pre-verb adverb.

Filter only for tokenization/target-form validity. If fewer than **16 Experiment-4 lexical item sets** survive, mark `HOLD — SUPPORT`; do not write a large bespoke replacement benchmark.

### Mother / leverage gate

Before any mechanism interpretation:

1. clean/matching-number SVA prefers the grammatical verb on **≥80%** of retained items;
2. Experiment-4 attraction has `mean A >= 0.5 bits`;
3. paired item-bootstrap 95% CI for `A` excludes 0 in the predicted direction.

If any gate fails: **STOP E01.** No prompt search, noun search, model shopping, or mechanism narrative.

### Instrument-completeness gate

For some contiguous layer region, `BOTH-CLEAN` must recover at least **70%** of the singular-vs-plural-attractor logit-margin difference while retaining clean-SVA behavior.

If this fails: `HOLD — INSTRUMENT INCOMPLETE`. Do not post-hoc invent a third mechanism.

---

## 6. Pre-result outcome interpretations / kill conditions

### State-dominant

`STATE-CLEAN` removes most attraction and `ACCESS-CLEAN` adds little.

Inference: the distractor has already changed the contextual controller state before final agreement readout.

### Access-dominant

Cleaning the earlier state has limited effect, while blocking fresh late distractor access removes attraction.

Inference: controller information survives sufficiently, but the wrong source wins during readout/access.

### Hybrid

Both channels make material, separable contributions or a stable interaction is needed.

Inference: the Transformer error has the same broad computational decomposition that hybrid psycholinguistic accounts posit, now directly identified in the model computation.

### Failure / ambiguous

If the mother effect is weak, interventions destroy clean agreement, `BOTH-CLEAN` fails completeness, or uncertainty is too broad to distinguish accounts: **HOLD / KILL**. Do not pivot to generic syntax-unit localization, another attraction construction, or another model family without fresh selection.

Report the entire layerwise recovery curve with item-clustered uncertainty; no post-hoc headline layer.

---

## 7. Resolution + compute

E01 is inference-only on one ~4B base model and a small published psycholinguistic item set. The computational burden is low; the binding risk is **statistical support and intervention selectivity**, not GPU cost.

The mother gate deliberately requires a ≥0.5-bit paired attraction effect and a confidence interval excluding zero before mechanism work. Layerwise interventions are paired within the same item/run family and therefore substantially better resolved than a model-family comparison.

If support is insufficient, do not compensate with massive synthetic stimulus generation. That would change the selected paper identity from mechanism identification to benchmark construction.

---

## 8. Main-level growth path — not authorized by E01

A full Main paper is plausible only if E01 produces a clean, reproducible causal decomposition.

Natural same-identity continuations:

1. **Feature-updating prediction.** Use the published paradigm where an earlier overt agreement cue can update the subject representation. A state-distortion account predicts a selective reduction/change of the early/state channel; an access account predicts a different pattern.
2. **Construction boundary.** The 2026 comprehensive Transformer study finds PP attraction relatively human-like but object-extracted RC attraction divergent. Test whether the behavioral boundary is explained by a change in causal channel.
3. **Optional cross-linguistic consequence.** Recent syncretism work finds unexplained language variation using surprisal/attention proxies. Only after C1/C2, test whether the state/access decomposition predicts when morphological ambiguity amplifies attraction.

These all deepen the same question: **where interference enters agreement computation and when that channel changes.**

Do not authorize model-zoo breadth merely to inflate scope.

---

## 9. Final gate

Question worth knowing before result? **YES.**  
Mother phenomenon established? **YES, conditional on exact-model E01 replication.**  
Pure competence test? **NO.**  
Direct owner already separates the two causal channels? **NO found.**  
A+B+C prior-work compression determines answer? **NO.**  
Decisive operation selective in principle? **YES, with clean-SVA + completeness gates.**  
First-stage leverage test? **YES.**  
Resolvable at current budget? **YES, conditional on published-item support.**  
Can successful result grow without changing identity? **YES.**

# Verdict

## **PILOT-AUTHORIZED — E01 ONLY**

Authorized scope is exactly:

> validate the published PP-attraction mother on `google/gemma-3-4b-pt`, validate clean SVA, then decompose the distractor-number effect into pre-readout **state-mediated** versus later **access-mediated** channels using the predeclared buffered Wagers items and layerwise path interventions.

Nothing beyond that is authorized.