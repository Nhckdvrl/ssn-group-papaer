# 2026-09-14 — Structural Priming Mechanism Selection

**Target:** ACL / EMNLP / NAACL Main  
**Status:** **SERIOUS CANDIDATE — E01 PILOT-AUTHORIZED — HIGH NATURAL-OWNER RISK — NO L NUMBER YET**  
**Search provenance:** standing-problem / mature-debate / real-friction search, not paper-gap generation.  
**Candidate type:** old scientific dispute + disputed diagnostic + foundation-model-specific process measurement.

---

# 0. One-sentence question

> **Does prime-specific prediction error actually drive subsequent structural priming in frozen language models, or can the inverse-frequency effect (IFE) arise even when trial-level prime→target dynamics do not exhibit the signature required by an error-driven adaptation account?**

A slightly broader scientific wording is:

> **When does structural priming provide evidence for error-driven adaptation rather than activation / associative / Bayesian dynamics?**

The first wording is the operational parent. The second is the mature scientific dispute.

---

# 1. Why this is a real old scientific problem

Structural priming has been used for decades to study how recently processed syntax changes subsequent syntactic processing/production. Its mechanism is unresolved.

Major account families include:

1. **Residual activation** — recently accessed structural / lexical-syntactic representations remain activated and facilitate reuse.
2. **Error-driven implicit learning** — unexpected structural input generates prediction error, which updates structural expectations / weights; this predicts persistence, cumulativity, and inverse-frequency effects.
3. **Associative / memory-based hybrid accounts** — e.g. Reitter, Keller & Moore (2011) use ACT-R base-level learning plus spreading activation and reproduce inverse frequency, long-term priming, cumulativity, and lexical boost.
4. **Hierarchical Bayesian adaptation** — Xu & Futrell (2024) reproduce lexical boost, inverse frequency, and asymmetrical decay through hierarchical Bayesian updating.

Therefore **IFE is not logically unique to one mechanism family**.

The question is old. That is a strength: the rival accounts are scientifically motivated and the answer matters independently of LLMs.

Key ancestry:

- Reitter, Keller & Moore (2011), _A Computational Cognitive Model of Syntactic Priming_.
- Jaeger & Snider (2013), _Alignment as a consequence of expectation adaptation_.
- Xu & Futrell (2024), _A hierarchical Bayesian model for syntactic priming_.
- Tooley & Brehm (2025), _Putting the prime in priming_.

---

# 2. The current scientific friction

## 2.1 Aggregate surprise evidence points toward error-driven learning

Jaeger & Snider (2013) showed that priming strength depends on the prime's prediction error given long-run and recent structural experience. This supplied influential evidence for expectation adaptation.

NAACL 2025 then imports the IFE into LLM ICL as a **mechanism diagnostic**:

> Zhou, Frank & McCoy, _Is In-Context Learning a Type of Error-Driven Learning? Evidence from the Inverse Frequency Effect in Structural Priming_.

They observe stronger priming for less probable structures and conclude that, in the studied setting, ICL is a type of error-driven learning and that an error signal is implicitly computed during the forward pass.

This is a strong mechanistic inference, not merely a behavioral observation.

## 2.2 But IFE is not mechanism-identifying

Reitter et al. (2011) reproduce the IFE in an ACT-R account using memory/activation mechanisms alongside base-level learning. The 2024 hierarchical Bayesian model reproduces the IFE together with properties often assigned to a different mechanism family.

The 2024 systematic review _Prime Surprisal as a Tool for Assessing Error-Based Learning Theories_ finds the empirical prime-surprisal literature mixed / methodologically heterogeneous and explicitly treats the diagnostic strength of prime surprisal as unsettled.

Thus:

> `IFE observed` does **not** by itself entail `error-driven mechanism identified`.

## 2.3 Trial-level process evidence points in the opposite direction

Tooley & Brehm (2025) derive a stronger mechanism-level prediction by linking processing of an individual prime to processing of its subsequent target.

For a strong error-driven account:

> harder / more errorful prime  
> → larger corrective update  
> → **greater target facilitation**.

Therefore prime difficulty and target difficulty should exhibit a **negative** relation in the critical regions.

Residual-activation / associative accounts do not predict this negative relation and can instead yield a **positive** relation: successfully/easily processed prime representations remain more available and facilitate the target.

The human eye-tracking data show primarily **positive** prime→target processing relations, inconsistent with the simple strong error-driven prediction.

Therefore the field currently contains a genuine tension:

> **aggregate IFE / surprise signatures have been used as evidence for error-driven learning, while trial-level cause→consequence evidence can point the other way.**

This is the mother pressure.

---

# 3. Why foundation models change the inference rather than merely instantiate the debate

Human experiments do not directly expose the language processor's own probability distribution over the prime before the critical structure arrives. Researchers often rely on:

- corpus frequency;
- verb bias norms;
- reading time as a processing-error proxy;
- condition-level structural frequency.

A frozen autoregressive LM supplies, in the **same processing system**:

1. exact token-wise probability / surprisal before and through the prime;
2. an exact trial-level target distribution after the prime;
3. arbitrarily many controlled matched prime–target trials;
4. controlled recent context, permitting the system's prior structural expectation to be manipulated and directly re-measured;
5. no parameter update during the priming episode, while still allowing context-dependent adaptation.

The last point does **not** prove the absence of learning: ICL can be functional learning in the forward pass. Its value is experimental — the entire pre-prime expectation and post-prime consequence can be observed in one fixed network.

The new leverage is therefore:

> **replace population-level proxies for prediction error with the learner's own trial-specific predictive distribution, then test whether that error quantitatively causes the subsequent adaptation attributed to it.**

This is more than “run an old priming experiment on an LLM.”

---

# 4. Exact estimands

## 4.1 Aggregate IFE (existing diagnostic)

For structure `s`, define target priming shift after a structurally congruent versus incongruent prime, using controlled prime-target pairs as in Prime-LM / Zhou et al.

The existing result is roughly:

> lower baseline probability structure → larger average priming shift.

This is **not** the new estimand. It is the diagnostic under audit.

## 4.2 Prime-specific structural prediction error

For each prime item, estimate the model's probability assigned to the observed structural continuation immediately before / at the structure-disambiguating region.

Call a theory-defined quantity:

`E_prime = prediction error / structural surprisal of the actually observed prime structure`.

The exact implementation must avoid sentence-total surprisal being dominated by lexical difficulty. Preferred variants isolate the structural decision using matched alternants / critical regions.

## 4.3 Prime→target adaptation

For the following target, measure how much the model's structural preference shifts toward the observed prime structure relative to a matched structural control.

Call:

`A_target = incremental target structural shift attributable to the prime`.

The core question is not whether `A_target > 0` — priming already exists.

It is the **within-system mapping**:

> `E_prime → A_target`.

---

# 5. Rival predictions

## H-ERR — prediction-error-driven adaptation

Holding relevant lexical/semantic factors fixed:

> higher error / surprise on the observed prime  
> → larger corrective change toward that structure  
> → stronger subsequent target facilitation.

At the processing-cost level, this corresponds to the Tooley/Brehm **negative prime-difficulty → target-difficulty** prediction.

A successful result must be item-/trial-level and not merely recover the aggregate IFE.

## H-ACT / H-ASSOC — activation / associative persistence

The priming consequence depends primarily on successful recent access / activation / memory association of the structure. Aggregate inverse frequency can arise from baseline activation or retrieval dynamics without an explicit prediction-error update.

This family does **not** require a monotonic `more prime error → larger later update` relation and can support a positive prime-processing → target-processing relation.

## H-BAYES — uncertainty-aware belief updating

A Bayesian learner can also be surprise-sensitive. Therefore a positive `E_prime → A_target` result **does not establish implicit gradient descent**.

This is important for claim discipline.

The strongest permissible conclusion after E01 is about whether **trial-specific prediction error is an actual adaptation quantity**, not whether the transformer literally runs gradient descent.

A later discriminating test could separate equal-mean priors with different evidence strength / uncertainty, because Bayesian update magnitude depends on uncertainty as well as prediction mismatch. This is **not part of E01** and should not be added unless E01 warrants it.

---

# 6. E01 — minimal pilot

**Goal:** ask whether the existing aggregate IFE and the stronger trial-level error-driven signature agree **inside the same frozen LM**.

### Data / object

Reuse high-control structural priming stimuli rather than build a benchmark. Prime-LM is attractive because it already provides large lexically disjoint / semantically controlled dative and transitive prime-target families. The Zhou et al. dative setup can also be reproduced for direct comparability.

### Models

Start with a small set of open autoregressive LMs spanning size, not dozens of model families. The scientific object is the within-model process relation, not a leaderboard.

### Measurements

For every trial:

1. measure baseline structural preference;
2. measure prime structural surprisal/error at the critical structural decision;
3. measure target structural preference after the prime;
4. compute target shift relative to a matched incongruent/control prime;
5. estimate the within-model relation between prime-specific error and subsequent target adaptation while controlling known lexical/semantic factors.

### Required sanity check

First reproduce ordinary structural priming and the aggregate IFE in the same setup. If those fail, the instrument is not comparable to the literature.

### Decisive pattern

The most scientifically valuable dissociation would be:

> robust aggregate IFE  
> **but**  
> no trial-level error→adaptation relation, or a relation with the activation-compatible sign.

That result would show directly that the IFE can coexist with process dynamics that do not support the mechanism it is commonly used to infer.

The opposite result is also useful:

> aggregate IFE + robust item-level prediction-error→adaptation relation across controlled structures/models.

That would materially strengthen the error-driven interpretation beyond current aggregate evidence.

---

# 7. Why this is not phenomenon gambling

The mother phenomenon is already stable enough:

- structural priming in humans: classic;
- structural priming in frozen Transformers: established (Sinclair et al., TACL 2022 and successors);
- IFE in LLM structural priming: NAACL 2025 and other priming work;
- rival mechanistic accounts: decades old;
- trial-level human result: published 2025.

The unknown is the **relation among already-established signatures**.

### Positive headline

> **Prediction error is a real trial-level driver of structural adaptation in frozen language models; aggregate IFE reflects the same process rather than a non-identifying frequency correlation.**

### Negative/dissociation headline

> **The inverse-frequency effect does not identify error-driven in-context learning: LMs exhibit the classic IFE even when prime-specific error fails to produce the predicted downstream adaptation.**

Both alter what evidence should be accepted for ICL mechanism claims.

---

# 8. Main-level scientific consequence

Best-case consequence is larger than structural priming itself.

The 2025 NAACL paper uses a **cognitive behavioral signature** to infer the algorithmic nature of ICL. This is an increasingly attractive research strategy: find a human diagnostic associated with mechanism M, observe it in LMs, infer mechanism M.

This project asks whether that inferential chain is valid in a case where:

- the signature is established;
- multiple cognitive algorithms can reproduce it;
- a stronger trial-level prediction exists;
- the LM exposes its own predictive distribution.

If the diagnostic fails, the paper changes the evidence standard for claims of the form:

> `human behavioral signature S is associated with mechanism M`  
> `LLM exhibits S`  
> therefore `LLM implements M`.

If it succeeds under the stronger test, it upgrades the evidence from an aggregate behavioral analogy to a process-level relation.

That is an ACL/EMNLP/NAACL Main-sized inferential step **if demonstrated cleanly across more than one structural alternation / model scale without turning into a benchmark survey**.

---

# 9. Exact-owner search and natural-owner risk

## Direct current owner

Zhou, Frank & McCoy (NAACL 2025) directly own:

> IFE in LLM structural priming → evidence for error-driven ICL.

Their follow-up line is active:

- 2025 workshop / 2026 preprint: causal interventions on continuous verb-bias features / function vectors affecting structural priming;
- Zhenghao Zhou gave a May 2026 invited talk titled **“Adaptation-to-Context in Humans and Large Language Models: Infering the underlying mechanisms of In-Context Learning with Structural Priming.”**

As of the 2026-09-14 public search, the author's publication list does **not** show a paper implementing the Tooley/Brehm trial-level prime→target diagnostic or directly testing whether aggregate IFE and item-level prediction-error dynamics dissociate in LMs.

### Risk assessment

**HIGH NATURAL-OWNER / SCOOP RISK.**

This is not a novelty collision today, but it is an obvious next scientific step for a group already working continuously on exactly this program.

Therefore:

- do not spend weeks on infrastructure before E01;
- keep owner search live;
- if a public paper/preprint appears with the same `prime error → target adaptation` estimand, kill immediately rather than shrink to a lexical/structural cell.

---

# 10. Anti-resurrection check

Repository searches for:

- `structural priming`;
- `error-driven`;
- `implicit learning`

did not locate an earlier candidate/kill owning this parent.

A nearby independently generated idea — garden-path adaptation as `prior shift vs revision/recovery` — was rejected during the same search because **K229** already closes the parent:

> `Prediction vs structural reanalysis in sentence processing, using LMs as new identifying instruments`.

Do not salvage that line through repeated exposure/adaptation.

K232/K233 also establish a general warning: simply instantiating a mature cognitive theory on LMs is not enough. The present priming candidate survives only because the proposed estimand is a **stronger process-level test of an inference currently being made in NLP**, not because the human debate is old/unresolved.

---

# 11. Reviewer-compression tests

### “This is just a follow-up to Zhou et al. 2025.”

**Response required for survival:** Zhou et al. establish an aggregate signature and infer a mechanism. This project tests whether the signature has the mechanism-identifying property required by that inference, using a trial-level prediction that the original paper does not test and that recent human evidence contradicts.

If the project only reports another priming factor or another IFE, this defense fails.

### “This is just Tooley & Brehm 2025 on LMs.”

**Response required for survival:** human reading time is an indirect processing proxy. The LM makes its own structural predictive distribution observable on every trial, letting us test the theoretical error quantity itself and compare it with the aggregate IFE in the same system.

If the project merely correlates total prime surprisal with total target surprisal, this defense fails.

### “Bayesian updating is also error-sensitive, so this cannot prove gradient descent.”

Correct. The paper must **not** claim that E01 uniquely identifies gradient descent. The first scientific issue is whether prediction error is a genuine adaptation driver and whether IFE is a valid diagnostic. Gradient-vs-Bayesian discrimination is a possible later layer only if separately identified.

---

# 12. Kill conditions

Kill before promotion if any of the following occurs:

1. current owner releases a direct `prime-specific error → target adaptation` paper;
2. exact structural prediction error cannot be isolated from lexical sentence difficulty well enough to support the theory;
3. target adaptation cannot be separated from trivial continuation/context probability effects;
4. the only story becomes “LMs differ from humans”;
5. positive result can only support vague “some form of learning” while negative result has no consequence;
6. E01 requires arbitrary hidden-state patching to create the effect rather than testing the theory-defined quantity.

---

# 13. Current decision

**SERIOUS CANDIDATE.**  
**E01 PILOT-AUTHORIZED.**  
**NO L NUMBER YET.**  
**OWNER RISK: HIGH.**

This is currently the strongest new question produced by the post-correction search method.

The next action is a cheap E01 instrument audit / sign test, not a full mechanistic paper build. In parallel, research-question search should continue so that this natural-owner line is not our only option.