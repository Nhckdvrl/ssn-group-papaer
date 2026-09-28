# L14 — Live Related Work and Novelty Audit

**Audit date:** 2026-09-11  
**Target:** ACL / EMNLP / NAACL Main  
**Status:** PASS FOR ONE BOUNDED PILOT; not paper-mainline-approved.

## 1. Current paper identity

The candidate is **not** "can LLMs understand metalinguistic negation?" as a textbook competence benchmark.

The prospective paper identity is:

> **Modern negation robustness treats sensitivity to a negative cue as monotonically desirable. But correct interpretation first requires selecting what the cue negates. Does an LLM distinguish proposition-level negation from metalinguistic rejection, and can interventions that improve ordinary negation sensitivity create systematic over-negation when the target is linguistic rather than world-state content?**

The load-bearing quantity is therefore **negation-target selectivity**, not raw MN accuracy.

---

## 2. Classical owners — assets, not novelty

Metalinguistic negation (MN) versus descriptive negation (DN) is a mature linguistic object. We do not claim to discover it.

Relevant lines include Horn, Carston/Noh, Noh et al. (2013), Blochowiak & Grisot (2018), and the Oxford Handbook treatment of metalinguistic negation.

Two classical processing accounts are useful because they give a prospective explanation before seeing LLM results:

1. **descriptive-first / repair:** `not X` is initially treated as world-state negation and reanalysed only when the correction makes that interpretation untenable;
2. **context-sensitive target selection:** discourse can license the metalinguistic target from the start.

Noh et al. (2013) use eye tracking to distinguish these possibilities. Blochowiak & Grisot (2018) provide controlled DN/MN experiments and public experimental data, including context manipulations.

Primary sources:
- https://doi.org/10.1016/j.pragma.2013.07.005
- https://doi.org/10.5334/gjgl.440
- https://www.swissubase.ch/en/catalogue/studies/13418/20191/overview
- https://doi.org/10.1093/oxfordhb/9780198830528.013.20

---

## 3. Modern owners and collision boundaries

### A. Ordinary negation blindness — owns polarity-insensitivity, not target selection

Kim et al., EMNLP 2025 Main, **Semantic Inversion, Identical Replies: Revisiting Negation Blindness in Large Language Models**:
- studies cases where negation changes a query's semantics but the model responds as if it did not;
- treats correct response to negation as semantic inversion;
- proposes a verification framework and mitigation analyses.

Source: https://aclanthology.org/2025.emnlp-main.1088/

It does **not** ask whether semantic inversion is sometimes the wrong operation because `not` targets a linguistic/metarepresentational object rather than the world proposition.

### B. Negation-improvement prompting — creates the decisive modern intervention

Barreto & Jana, Findings EMNLP 2025, **This is not a Disimprovement**:
- introduces warning/persona prompts for negation reasoning;
- reports overall improvements and large gains on distractor-negation cases;
- introduces a negative-token attention score and links greater negation attention with better performance within model families.

Source: https://aclanthology.org/2025.findings-emnlp.761/

This is not a collision. It gives L14 a pre-existing intervention whose monotonicity can be tested:

> **Does making a model attend more strongly to negation improve DN while increasing false polarity reversal on MN?**

L14 must use an existing negation-sensitivity intervention rather than inventing a prompt after seeing the result.

### C. Negation scope/systematicity — owns intra-propositional scope, not semantic-level target

Yanaka & Yamamoto (NALOMA 2026), **Revisiting the Systematicity in Negation in the Era of In-Context Learning** studies negation expressions, scope recognition and function vectors.

Source: https://arxiv.org/abs/2606.16867

Ordinary scope asks which constituent within a proposition falls under negation. L14 asks whether the negated object is the world proposition or an echoed/linguistic representation. Do not blur these quantities.

Petcu et al., Findings EMNLP 2025, **A Comprehensive Taxonomy of Negation for NLP and Neural Retrievers**, establishes that modern negation work already has broad linguistic/logical taxonomies; therefore L14 cannot sell "existing NLP ignores types of negation" as novelty.

Source: https://aclanthology.org/2025.findings-emnlp.839/

### D. Implicature recognition/cancellation — dangerous neighbor; scalar route is fenced off

Spinoso-Di Piano et al. (2026), **Evaluating Communicative Belief Updates in Large Language Models via Implicature Recognition and Cancellation**:
- evaluates recognition of implicatures and belief updating when those implicatures are cancelled;
- includes scalar and more natural implicature cancellation;
- finds an LLM–human gap, especially in natural cases.

Source: https://arxiv.org/abs/2607.25094

This directly occupies a paper framed as:

> weak utterance creates an implicature → later material cancels it → can the model update?

Therefore `some → all` and related scalar examples **cannot be load-bearing for L14**. They may appear only as a minor diagnostic subtype. The primary data must include lexical-strength and clearly form/wording-targeted MN cases whose scientific quantity is the target of negation itself, not cancellation of an implicature.

### E. Artificial Epanorthosis — new LLM-specific parent/anomaly, not a comprehension owner

Boggia (2026), **Artificial Epanorthosis: Why large language models overuse a classical rhetorical figure, and how to mitigate it**, reports systematic LLM overuse/miscalibration of corrective `Not X. Y`-style epanorthosis and demonstrates generation-side mitigation.

Source: https://arxiv.org/abs/2607.21498

This materially strengthens L14's motivation:

> LLMs disproportionately **produce** a corrective construction whose interpretation can require metalinguistic rejection rather than world-state negation.

But the paper studies production rate, genre calibration and mitigation; its stated contribution is not semantic comprehension/target selection. L14 must not claim the generic production–comprehension gap as novelty. The useful consequence is narrower: a construction that is especially characteristic of LLM output becomes a stress test for whether current negation reasoning evaluates the right computation.

---

## 4. Direct search result

Queries run on 2026-09-11 included:

- `"metalinguistic negation" large language model / LLM / GPT / transformer`
- `"descriptive negation" metalinguistic negation LLM`
- `"corrective negation" LLM / GPT / transformer`
- `"not X but Y" negation language models pragmatics`
- `"metalinguistic negation" benchmark / NLP / NLI`
- `"negation target" LLM semantics`
- ACL/EMNLP/NAACL-oriented variants.

No modern paper was found that directly owns:

1. DN versus MN as an LLM **world-state target-selection** contrast;
2. a two-sided error profile separating ordinary negation blindness from metalinguistic over-negation;
3. the causal/behavioral test of whether an existing ordinary-negation intervention trades one error against the other.

This is a bounded search result, not proof of global priority. Re-run before any full-study promotion.

---

## 5. Strongest A + B + C reviewer compression

> **Kim et al. 2025 negation blindness + Barreto & Jana 2025 negation-attention prompting + classical metalinguistic-negation stimuli = L14.**

Add pressure from:
- Yanaka & Yamamoto 2026 for scope/systematicity;
- Spinoso-Di Piano et al. 2026 for pragmatic cancellation;
- Boggia 2026 for LLM `Not X. Y` production.

This compression **wins** if L14 only reports a new MN benchmark or says models sometimes misunderstand `not X, but Y`.

### Strongest surviving independent contribution

The combination above does not currently establish:

> **whether improving target-agnostic negation sensitivity is actually a monotonic improvement in negation understanding once the negator can target a representation rather than a proposition.**

A stable DN-improvement / MN-over-negation trade-off would change the interpretation of an existing negation-robustness intervention and expose **target selection** as the missing operation.

A context manipulation can then distinguish whether the trade-off reflects a polarity-first default or context-sensitive target selection. That development is prospective and audited now, not invented after the pilot.

---

## 6. Successful-result test

### Main-worthy route

A bounded pilot establishes all of the following directionally:

1. DN and MN cannot be explained by lexical knowledge/control performance alone;
2. at least two model families show a meaningful two-sided target-selection profile;
3. an **existing** ordinary-negation intervention improves DN but systematically harms MN, or otherwise reveals a stable target-selectivity failure;
4. the effect is not confined to scalar-implicature examples.

Then C2 can test the predeclared descriptive-first versus context-sensitive account.

### Insufficient even if statistically clean

- "models are 78% accurate on MN";
- "warning prompts improve MN too";
- one adjective scale gives a cute reversal;
- only `some → all` drives the result;
- only model size differences exist;
- probe/attention maps without a discriminating behavioral operation.

These do not justify a paper program.

---

## 7. Verdict

# **NOVELTY / DEVELOPMENT-PATH AUDIT: PASS FOR ONE BOUNDED KILL-ORIENTED PILOT**

The audit does not approve the paper mainline. It authorizes only the experiment defined in `PILOT_CARD.md`.

Any material mutation away from **negation-target selectivity and its consequence for ordinary negation robustness** requires return to selection and a fresh ownership audit before expansion.
