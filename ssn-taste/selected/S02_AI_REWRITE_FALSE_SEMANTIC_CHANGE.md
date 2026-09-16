# S02 — AI Rewrite ≠ Semantic Change

**Status:** SELECTED / PILOT-AUTHORIZED  
**Registered:** 2026-09-16  
**Origin in search:** C2 — AI→False Semantic Change  
**Primary venues:** ACL / EMNLP / NAACL Main  
**Research type:** exploratory measurement-validity / changed-premise study  

---

## 1. One-sentence research question

> **Can meaning-preserving LLM rewriting make lexical-semantic-change (LSC) methods report semantic change even when the underlying word meanings have not changed?**

A stronger paper-level formulation is:

> **Which lexical-semantic-change measurements remain invariant when a corpus undergoes meaning-preserving AI rewriting, and which measurements mistake AI-induced contextual redistribution for semantic change?**

The paper is **not** about detecting AI-generated text, and it is **not** about showing that LLM writing has a different style. The scientific object is the validity of semantic-change inference under a new real-world corpus regime.

---

## 2. Why this question is naturally worth asking

Diachronic lexical-semantic-change work normally observes two corpora from different periods and interprets changes in a target word's contextual distribution as evidence about changes in meaning or sense usage.

That interpretation has always required care: genre, register, topic, corpus composition, frequency, and contextual variance can move even when lexical meaning does not. This is known and must **not** be claimed as our novelty.

The changed premise is that, after widespread LLM adoption, corpus composition can change through an additional operator that did not previously exist at comparable scale:

> a human-authored passage can be systematically rewritten by an LLM while preserving its intended meaning.

This operator can alter lexical choice, collocations, local syntax, discourse packaging, and contextual distributions without requiring any underlying semantic innovation by the human population.

Therefore a new empirical question becomes possible and practically important:

> if the world changes from `human text` to `human text → LLM rewrite`, how much of the resulting signal is interpreted by standard LSC methods as lexical-semantic change?

This matters because current corpora are increasingly mixtures of human-written, AI-assisted, and AI-generated text. A 2025 ACL Main paper measured rapidly increasing AI-generated-text prevalence on Medium and Quora, while 2026 work on scientific writing found substantial post-LLM lexical, contextual, and stylistic shifts. These papers establish the **changed regime**; they do not provide the counterfactual measurement test proposed here.

---

## 3. The key scientific distinction

The paper separates two quantities that are easy to conflate:

### A. Meaning change

The lexical item acquires, loses, broadens, narrows, or changes senses/meaning relations.

### B. Meaning-preserving contextual redistribution

The meaning of the lexical item stays fixed, but the distribution of contexts in which it appears changes because an LLM rewrites surrounding language.

A distributional LSC method may respond to both A and B. The scientific question is **not whether B can change embeddings in the abstract**; that is already unsurprising. The question is whether the measurements currently used to support semantic-change conclusions are invariant enough to separate the two under the emerging post-LLM corpus regime.

---

## 4. Why this is exploratory rather than a gambling paper

There is **no required anomalous outcome**.

All three broad outcomes are informative:

1. **High robustness.** Most LSC methods remain stable under meaning-preserving AI rewriting.  
   This would provide positive evidence that common semantic-change measurements are more invariant to realistic post-LLM distribution shift than expected.

2. **Selective sensitivity.** Some method families, target-word classes, or rewriting regimes are affected while others remain stable.  
   This identifies the invariance boundary and gives concrete guidance about which scientific conclusions are reliable under which corpus conditions.

3. **Broad sensitivity.** Meaning-preserving rewriting induces substantial apparent semantic change across methods.  
   This would show that post-LLM corpora create a new validity problem for diachronic semantic inference and motivate correction or robustness procedures.

Thus the paper asks **what happens and under what conditions**, rather than betting on a dramatic false-positive phenomenon.

Semantic-preservation checks, robustness analyses, and decomposition experiments are **controls and scientific analyses**, not life-or-death gates requiring one particular outcome.

---

## 5. Nearest-prior audit

### 5.1 What prior LSC work already owns

Prior LSC work already establishes that distributional methods can confuse contextual/discourse variation with genuine semantic change.

Important prior observations include:

- global genre/discourse shifts can produce false discoveries;
- corpus imbalance and register differences can distort diachronic comparisons;
- contextualized methods can assign high change scores to words whose lexicographic meaning has not changed;
- simple context changes can create false positives even when usage remains within one sense.

**We must cite this literature explicitly.** The novelty claim must never be `context shift can fool semantic-change methods`.

### 5.2 What recent AI-writing work already owns

Recent work establishes that:

- AI-generated text has become common on major online platforms;
- AI-generated/assisted text differs from human text in lexical, topical, and stylistic distributions;
- scientific writing after widespread LLM adoption shows measurable lexical and usage-context changes;
- preference tuning itself can systematically shift lexical choice distributions.

Again, the novelty claim must never be `LLMs change writing style` or `AI text is increasingly common`.

### 5.3 The currently unowned intersection

The current candidate lives at the intersection:

> **Take text whose underlying meaning is held fixed by construction; apply a realistic LLM rewriting operator; then ask whether state-of-the-art semantic-change measurements infer change anyway.**

This creates a **known-no-semantic-change counterfactual** that observational diachronic corpora normally cannot provide.

The key addition is therefore not another source of corpus bias. It is an identifying operation for testing **measurement invariance under a newly common, exogenous rewriting process**.

### 5.4 Reviewer-compression audit

The dangerous compression is:

> “Genre/context shift was already known to cause false positives; AI rewriting is just another domain shift.”

The paper must answer this directly rather than evade it.

The defense is substantive only if the experiments establish the following:

- AI rewriting is a **real new corpus-generation process**, not an arbitrary synthetic style perturbation;
- the source/rewrite pairing provides a counterfactual control unavailable in ordinary diachronic corpora;
- the study measures which current LSC estimands are invariant to this process, rather than merely reporting that embeddings moved;
- the analysis distinguishes AI-induced redistribution from genuine sense change using positive controls and paired semantic-preservation checks.

If the work degenerates into `ChatGPT paraphrases change embedding distance`, it is not Main-level.

---

## 6. Remove-the-trigger-paper test

The question survives removal of any single recent paper.

Even without the 2025 ACL prevalence study or the 2026 scientific-writing study, widespread AI-assisted rewriting creates a natural methodological problem for diachronic corpus inference:

> the observed text distribution can change because the production process changed, even when the underlying lexical semantics did not.

Recent papers are evidence that the premise is already occurring in the real world; they are not the sole source of the research question.

This is therefore a **changed-premise question**, not a future-work follow-up to one trigger paper.

---

## 7. Main-conference scope

The parent question is:

> **When does contextual redistribution constitute evidence of semantic change, and are contemporary LSC measurements invariant to a new large-scale rewriting process that preserves intended meaning?**

The concrete paper does not need to solve semantic-change validity universally. Its controlled claim can remain narrower:

> **We causally measure the sensitivity of representative LSC methods to meaning-preserving LLM rewriting and characterize which rewriting-induced distribution changes are mistaken for lexical-semantic change.**

This is wider than a single-model or single-metric robustness test, but narrower than `AI has changed language`.

The natural Related Work neighborhood is:

1. lexical semantic change detection and measurement;
2. known corpus-composition / genre / contextual confounds in LSC;
3. AI-assisted / AI-generated writing and linguistic distribution shift;
4. only secondarily, AI-text detection or generic paraphrase robustness.

The paper should **not** be framed as an AI-text-detection benchmark.

---

## 8. Sasano-taste fit

### Easy to understand

A reviewer can understand the puzzle immediately:

> “If a model rewrites the same meaning in a different style, will our semantic-change detector claim the word changed meaning?”

### Question first, method second

The contribution exists before choosing a particular embedding model, LLM, benchmark, or metric.

### Changed real-world premise

This is close to the strongest Utami-style pattern: an external technological change alters the population/process being observed, which may change the interpretation of a familiar linguistic measurement.

### Clean identification

The same original text can be paired with its rewrite, so underlying intended meaning can be held approximately constant while the surface/context distribution changes.

### No anomaly dependence

Robustness, selective sensitivity, or broad sensitivity are all scientifically interpretable.

### Feasible

The first meaningful experiment needs no new large model training and no massive human annotation campaign.

---

## 9. Minimal pilot

### 9.1 Data

Start with a clean human-written corpus containing enough repeated target-word usages. Two reasonable starting choices are:

- scientific/technical text, because real AI-assisted-writing shifts are already documented there;
- a balanced general-domain corpus, to avoid making the first result depend on one genre.

The pilot does **not** need a new benchmark.

### 9.2 Counterfactual construction

For each sampled passage containing a target word:

- **Period H:** original human-written passage;
- **Period R:** an LLM rewrite instructed to improve fluency/style while preserving meaning and factual content.

Use paired rewriting: every R item has a known H source.

Prefer at least two rewriting regimes with a natural interpretation, for example:

- light copy-edit / fluency improvement;
- stronger professional/formal rewrite.

The point is not to maximize stylistic distance, but to sample realistic AI assistance.

### 9.3 Semantic-preservation controls

These are experimental controls, **not outcome gates**.

Use several cheap checks:

- bidirectional semantic-similarity / entailment filtering;
- preservation of entities, numbers, negation, and target-word sense where applicable;
- a small manually audited sample;
- optionally a second independent judge/model.

The goal is to bound how much genuine meaning change was accidentally introduced by rewriting.

### 9.4 LSC methods

Use representative families rather than many nearly identical systems:

1. a static/distributional baseline;
2. a contextual-embedding change measure;
3. a stronger recent usage/sense-distribution method, e.g. clustering/transport-style measurement.

The paper should ask whether the conclusion is **method-family dependent**, not chase a leaderboard.

### 9.5 Measurements

Core quantities:

- change score on H→R despite intended semantic invariance;
- rank instability among target words;
- false-positive rate under thresholds calibrated on appropriate controls;
- correlation between apparent change and rewrite-induced lexical/contextual statistics;
- method-family agreement/disagreement.

### 9.6 Positive control

Include a condition with **genuine sense-distribution change** so that a method that is perfectly invariant to rewriting but also blind to real change is not rewarded.

This can be created from existing LSC annotations or by controlled mixture of usages from distinct attested senses.

The desired measurement question is therefore two-dimensional:

> **sensitivity to real semantic change vs invariance to meaning-preserving rewrite.**

That is scientifically stronger than simply minimizing H→R distance.

---

## 10. Analysis that could make the paper substantially stronger

If the pilot shows any non-trivial method differences, decompose the rewrite operator instead of immediately adding more models.

Candidate quantities:

- lexical substitution around the target;
- collocational redistribution;
- syntactic normalization;
- register/formality shift;
- local contextual diversity;
- document/topic distribution;
- target frequency;
- contextual-embedding variance.

The goal is not to produce a giant taxonomy. It is to determine **which meaning-preserving distribution changes each LSC family treats as evidence of semantic change**.

A particularly clean result would be a robustness frontier:

> Method family X is invariant to lexical/style normalization but reacts strongly to collocational redistribution; method family Y behaves differently.

That would turn the paper from an AI-era cautionary example into a general measurement result.

---

## 11. What this paper must NOT become

Do not drift into:

- AI-generated-text detection;
- `AI is changing English` as a broad sociolinguistic claim;
- another lexical-overuse inventory;
- a benchmark containing thousands of manually curated changed words;
- a generic paraphrase-robustness paper;
- `one LSC metric drops by N% on ChatGPT text`;
- claiming that any change in context equals a false semantic change;
- treating AI-written text as intrinsically inauthentic or linguistically invalid.

The scientific object is **semantic-change inference under a changed text-production regime**.

---

## 12. Remaining open questions — not life-or-death gates

These are questions for the pilot and paper design. No particular answer is required for the topic to remain scientifically meaningful.

### How strong is the effect?

Could be negligible, selective, or broad. All are findings.

### Which rewrite regimes matter?

Light proofreading may be almost invariant while stronger rewriting may shift collocations substantially. The dose-response itself may be informative.

### Which LSC family is most robust?

Different methods may trade off sensitivity to genuine sense redistribution against invariance to stylistic/contextual redistribution.

### How much semantic-preservation validation is enough?

The pilot can establish the cheapest reliable protocol before scaling.

### How far does the result generalize beyond scientific English?

This is a scope question, not an admission criterion. One clean domain is sufficient for the first pilot; expansion should follow evidence.

The only ordinary reason to demote the topic at this stage would be discovery of a **direct prior that already performs the same known-no-semantic-change AI-rewrite intervention and answers the same parent RQ**, or evidence that no clean experimental identification is possible at reasonable cost.

---

## 13. Immediate pilot plan

### P0 — smallest useful experiment

1. Sample roughly 1k–3k passages from one existing corpus.
2. Select a few hundred sufficiently frequent target lemmas.
3. Produce one paired meaning-preserving rewrite per passage with one strong LLM.
4. Filter obvious semantic failures automatically and manually audit ~100 pairs.
5. Run 2–3 representative LSC measurements on original→rewrite.
6. Add one genuine-change positive control.
7. Plot, for every method, **real-change sensitivity vs rewrite invariance**.

This is enough to learn whether the question has a rich empirical structure. It does not require training a large model.

### P1 — only if P0 reveals structure

- add a second rewrite regime;
- decompose lexical/collocational/syntactic changes;
- add one additional domain or language if scientifically motivated;
- test whether simple balancing/correction restores invariance.

Do not start with a large benchmark or dozens of LLMs.

---

## 14. Current verdict

**SELECTED / PILOT-AUTHORIZED.**

C2 survives the Sasano-taste, Main-scope, feasibility, and first deep nearest-prior audit.

Its novelty is **not** that distribution shift can cause false semantic-change signals; prior LSC work already knows that. Its independent changed-premise contribution is the controlled study of whether **meaning-preserving AI rewriting — now a real corpus-generation process at scale — breaks the invariance required to interpret contemporary diachronic LSC measurements as semantic change**, using paired counterfactual text where the intended meaning is held fixed by construction.

Proceed to a cheap pilot before adding complexity.
