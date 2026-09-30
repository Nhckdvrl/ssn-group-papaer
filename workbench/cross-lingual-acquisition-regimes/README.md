# Cross-Lingual Acquisition Regimes — Workbench

**Lane:** sasano-taste / model-science crossover  
**Stage:** ACTIVE EXPLORATORY WORKBENCH — **not a candidate**  
**Target ceiling:** ACL / EMNLP / NAACL / ICLR / NeurIPS main-track scale.  
**Core discipline:** reconcile conflicting controlled results before inventing a method.

---

## 0. Why this workbench exists

Recent strong multilingual-pretraining papers disagree in a scientifically meaningful way about what parallel / bilingual data actually buys.

### Parent A — Just Go Parallel (ACL 2025)

Controlled training finds that adding parallel data improves both:
- translation;
- multilingual commonsense reasoning.

### Parent B — The Role of Mixed-Language Documents (ACL 2026)

Controlled from-scratch pretraining finds a sharply different pattern:
- removing bilingual/mixed-language documents causes a very large translation drop;
- cross-lingual QA and general reasoning remain largely stable;
- adding parallel data back restores most translation;
- the same intervention barely changes the other cross-lingual tasks.

### Parent C — OpenSeal (2026)

Starting from an English-centric OLMo-2 model, controlled continual-pretraining experiments find that parallel-only CPT is unusually effective not only for translation but also for multilingual NLU/reasoning-style evaluation.

### Parent D — TransWebEdu (EMNLP 2025)

Machine-translating a high-quality English pretraining corpus into target languages yields strong non-English understanding/reasoning in a 1.3B model. This warns that “parallel data helps” may mix several causal factors:
- bilingual correspondence;
- target-language exposure;
- high-quality matched semantic content.

These results are not cleanly summarized by either:

> “parallel data is necessary for multilingual reasoning”

or:

> “parallel data matters only for translation.”

The workbench exists to discover **which training regime makes each statement true**.

---

## 1. Working scientific pressure — not a registered claim

A plausible explanation suggested by the parent mismatch is:

> the function of bilingual/parallel signal changes with the target language's acquisition state.

One possible regime decomposition is:

### Acquisition-limited regime

The target language itself is weakly represented / low-exposure / newly introduced.

Parallel data may jointly provide:
- target-language lexical/syntactic exposure;
- high-quality semantic content;
- a cross-language bridge;
- an optimization scaffold into an already capable source-language model.

In this regime, reasoning/NLU may improve together with translation.

### Alignment-limited regime

The target language already has abundant monolingual exposure and adequate language modeling competence.

Parallel data may contribute mainly:
- token/phrase correspondence;
- lexical alignment;
- input/output interface calibration;
- translation-specific mapping.

In this regime, translation may move strongly while QA/reasoning barely changes.

**This explanation is not assumed true.**

The first purpose of the workbench is to test whether the JGP/OpenSeal/MONOWEB difference is actually explained by acquisition regime rather than by:
- benchmark choice;
- model architecture;
- continual-pretraining vs from-scratch training;
- data quality;
- training-token count;
- language family/script;
- source/target imbalance;
- translated-content quality;
- instruction/post-training differences.

---

## 2. Top-conference ceiling contract

Local substrate:

> parallel-data interventions in open multilingual pretraining families

Broader object:

> **when cross-language supervision acts as language acquisition, semantic transfer, alignment, or interface calibration**

Possible field-level consequence:

> multilingual “bridge” data is not one mechanism; its causal role depends on what the model already knows about the target language and on the downstream capability being measured.

The workbench remains authorized only if exploration can separate at least two of these causal roles with evidence that survives:
- multiple training families;
- multiple capabilities;
- explicit alternative-explanation controls.

The workbench must be demoted if the best surviving result is only:
- “parallel data helps low-resource languages more”;
- another data-scaling curve;
- another language-resource correlation study;
- one new multilingual benchmark;
- one model family behaving differently;
- a translation-only effect already owned by MONOWEB;
- a generic recommendation to use more parallel data.

---

## 3. Nearest-prior ownership

### Already owned — do not claim

**Just Go Parallel**
- parallel data can improve decoder-LLM translation and multilingual commonsense reasoning.

**MONOWEB**
- naturally occurring bilingual documents are not uniformly required for all multilingual capabilities;
- translation is especially sensitive to parallel/token-level bilingual alignment;
- QA/reasoning can remain strong without those documents in its balanced training setup.

**OpenSeal**
- for extending an English-centric model to Southeast Asian languages under a fixed CPT budget, parallel-only data can outperform standard multilingual CPT.

**TransWebEdu**
- translated high-quality English data can be an effective multilingual pretraining source for non-English understanding/reasoning.

**False Friends / multilingual anchor literature**
- token overlap / semantic anchors can accelerate alignment but are not a universal necessary condition.

### Potentially unowned if earned

A stronger statement may remain open if experiments establish that:

> **the downstream role of bilingual correspondence changes systematically as target-language competence/exposure changes, producing a transition from acquisition/scaffolding effects to alignment/interface effects.**

This statement must not be claimed from cross-paper comparison alone.

It requires controlled evidence.

---

## 4. Why this is not the existing Guo/Sasano multilingual-factor line

The Sasano-lab multilingual factor work asks which language-level properties such as:
- language distance;
- resource quantity;
- dataset/task factors

correlate with performance differences across languages/models.

This workbench must remain distinct.

It asks a **causal training question**:

> for the same target language/model family, what causal function does cross-language supervision play at different acquisition states?

Do not turn this into another regression over language distance/resource amount.

---

## 5. Baseline residency

Before new training, fully understand four parents.

### A. MONOWEB family

Recover exact:
- released checkpoints;
- training-data composition;
- per-language monolingual token budgets;
- bilingual-data categories;
- translation/QA/reasoning metrics;
- training curves.

Reproduce the published asymmetry with released models.

### B. Just Go Parallel

Audit:
- base recipe;
- monolingual data proportions for each target language;
- parallel-data dose;
- whether reasoning gains are concentrated in the weakest target languages;
- training-from-scratch details;
- task evaluation.

The key question is whether target-language scarcity and parallel-data benefit co-vary inside the paper.

### C. OpenSeal

Audit:
- OLMo-2 pretraining language exposure before CPT;
- multilingual vs mixed vs parallel-first/last/only settings;
- exact token budget;
- XNLI/XCOPA/PAWS-X and translation gains by language;
- which languages had the weakest pre-CPT competence.

### D. TransWebEdu

Audit:
- whether translations are paired/adjacent or simply used as target-language documents;
- data-quality controls;
- whether improvements require explicit sentence-pair alignment;
- target-language exposure and benchmark coverage.

This is necessary to separate:

> **bilingual alignment**

from

> **matched high-quality semantic content / target-language acquisition**.

---

## 6. Pressure map before deep dive

Do not immediately optimize one hypothesis.

At minimum compare these competing explanations.

### H1 — Acquisition-state interaction

Parallel data helps reasoning primarily when target-language competence is still acquisition-limited.

### H2 — Training-stage interaction

The decisive factor is not language competence but continual-pretraining vs joint from-scratch optimization.

### H3 — Data-quality / semantic-content effect

Reasoning improves because parallel datasets inject high-quality source-language semantic content into target-language training, not because paired correspondence matters.

### H4 — Capability-specific bridge granularity

Translation uniquely needs fine-grained token/phrase alignment, while reasoning needs only sentence/concept-level shared semantics.

### H5 — Evaluation artifact

Apparent reasoning differences come from translated benchmark construction, answer format, or target-language generation quality rather than reasoning computation.

### H6 — Language-family / tokenizer interaction

MONOWEB's European-language balanced setup and JGP/OpenSeal's lower-resource / more distant languages create the effect.

These explanations must compete.

---

## 7. Earliest revealing experiments

### P0 — Parent-table reconstruction

Build one auditable table across JGP / MONOWEB / OpenSeal / TransWebEdu with:

- model/base model;
- from-scratch vs CPT;
- target languages;
- target-language monolingual exposure before intervention;
- parallel-data dose;
- total token budget;
- whether pairs are explicitly adjacent;
- translation metric;
- NLU/reasoning metrics;
- per-language effects;
- released models/data/code.

This table is evidence, not literature decoration.

### P1 — Within-parent effect decomposition

Using released results/models where possible:

- measure parallel intervention effect separately for translation and reasoning/NLU;
- normalize effect by each language's pre-intervention competence/exposure;
- inspect whether reasoning gains concentrate where target-language competence is weakest.

If this pattern is absent inside JGP/OpenSeal, H1 weakens immediately.

### P2 — MONOWEB competence stress test

Do **not** retrain MONOWEB first.

Ask whether the published “reasoning is unchanged” conclusion survives when evaluation is sliced by:
- weakest language/task combinations;
- language-model competence;
- lexical vs semantic dependence;
- target-language generation burden.

If only translation changes across all meaningful slices, H1 becomes harder to sustain.

### P3 — Existing-model factorial approximation

Exploit existing intervention families to approximate two axes:

- target-language acquisition strength;
- presence/type of bilingual bridge.

Candidate families:
- MONOWEB/FINEWEB/+parallel;
- OpenSeal multilingual/parallel-only/order variants;
- False Friends anchor variants;
- Bilingual BabyLM/Macaroni exposure variants.

The goal is not to pool incomparable scores.

The goal is to look for the same qualitative interaction under independent systems.

### P4 — Minimal new controlled training only if needed

If the existing families strongly support H1 but do not isolate it, train a **small 1B-ish controlled model family**.

Factorial design:

**Axis A — monolingual target exposure before/alongside bridge**
- low;
- medium;
- high.

**Axis B — cross-language coupling**
- unpaired monolingual;
- semantically matched but unpaired/reshuffled translated content;
- explicitly paired parallel content.

Hold constant:
- target-language token count;
- source semantic content;
- tokenizer;
- optimization budget;
- model architecture.

Readouts:
- language modeling competence;
- translation;
- NLU;
- reasoning;
- representation alignment.

This factorial test is much more informative than simply increasing parallel-data percentage.

No 7B foundation-model pretraining is authorized at entry.

---

## 8. Why the translated-content control matters

A central confound is:

> parallel corpus = bilingual alignment + high-quality target-language text + matched semantic content.

TransWebEdu demonstrates that machine-translated high-quality English data alone can produce strong multilingual understanding/reasoning.

Therefore a strong causal design should eventually compare:

1. **ordinary target-language monolingual data**;
2. **translated target-language data with pairing destroyed / sentences shuffled**;
3. **explicit source-target parallel pairs**.

If (2) recovers reasoning but only (3) recovers translation:

> strong evidence for **semantic-content/acquisition vs alignment** role separation.

If only (3) improves both:

> explicit bilingual bridge remains load-bearing for reasoning too.

If neither reproduces JGP/OpenSeal gains:

> another regime variable is responsible.

This is currently one of the highest-information distinctions in the workbench.

---

## 9. Relation to translation-as-proxy line

The earlier library pressure remains useful but is now secondary.

Translation can be highly correlated with broad multilingual performance across models/languages while a controlled bridge intervention moves translation without moving reasoning.

The acquisition-regime hypothesis offers one possible reconciliation:

- low target-language competence makes translation quality a marker of broad language/interface competence;
- after target-language competence saturates, translation retains additional dependence on explicit bilingual alignment.

Thus the proxy relationship may itself be **regime-dependent**.

Do not make “correlation is not causation” the paper.

The stronger scientific question is what causal roles are being mixed by that correlation.

---

## 10. Mechanistic branch — only after behavioral/training object is stable

If the regime interaction survives, then ask how the internal computation changes.

Possible diagnostics:

- lexical vs sentence/concept alignment;
- shared semantic subspace;
- language-specific directions by layer;
- cross-lingual activation patching;
- routing/shared-neuron use;
- output-language control.

A plausible but unproven prediction is:

- acquisition-limited models use parallel data to create broader shared semantic access;
- acquisition-saturated models already have shared semantic access and use parallel data mainly to sharpen lexical/input-output mapping.

Do not probe this before the behavioral interaction is established.

---

## 11. Method permission

No method at entry.

A method becomes justified only if:

> acquisition regime  
> → identifiable bottleneck  
> → controllable data/interface choice  
> → improved sample efficiency or multilingual capability.

Possible outcomes might eventually motivate adaptive data curricula, but **do not pre-commit** to curriculum learning.

A good paper may remain analysis-only if it establishes a durable causal law.

---

## 12. Hard kill / pivot conditions

### Kill this lead if

- JGP/OpenSeal reasoning gains do not covary at all with target-language acquisition weakness;
- the cross-paper difference disappears after matching benchmark/evaluation definitions;
- TransWebEdu shows explicit pairing is irrelevant and all gains reduce to generic translated-data quality;
- MONOWEB's reasoning null is specific to weak/insensitive tasks;
- a direct prior already identifies the same acquisition-state × parallel-data interaction;
- a clean test requires company-scale multilingual pretraining.

### Pivot if

The experiments instead reveal a simpler object such as:
- explicit pairing matters only for translation, while translated semantic content explains reasoning;
- CPT and joint pretraining fundamentally use bilingual data differently;
- bridge utility depends on *when* data is introduced rather than target-language competence;
- translation proxy validity changes sharply after target-language competence passes a threshold.

A pivot must simplify the scientific object.

---

## 13. Compute contract

Early phases:
- frozen inference / published-result reconstruction;
- public 1B–7B checkpoints;
- single-node analysis.

If P4 becomes necessary:
- target roughly 0.5B–1.5B controlled models;
- limited token budget;
- one 4×A100/PRO6000 node;
- no multi-node foundation-model pretraining.

---

## 14. Current paper identity

**None.**

Current workbench object:

> **the causal role of bilingual/parallel supervision across multilingual acquisition regimes**

Current leading explanation:

> **parallel supervision may shift from acquisition/scaffolding to translation/interface alignment as target-language competence increases.**

This explanation must earn survival.

It is not the title, contribution, or expected result.

---

## 15. Primary references

- Just Go Parallel — ACL 2025  
  https://aclanthology.org/2025.acl-long.1602/
- The Role of Mixed-Language Documents for Multilingual Large Language Model Pretraining — ACL 2026  
  https://aclanthology.org/2026.acl-long.1706/
- OpenSeal — 2026  
  https://arxiv.org/abs/2602.02266
- Multilingual Language Model Pretraining using Machine-translated Data / TransWebEdu — EMNLP 2025  
  https://aclanthology.org/2025.emnlp-main.1426/
- False Friends Are Not Foes — Findings EMNLP 2025  
  https://aclanthology.org/2025.findings-emnlp.1153/
- Feeding BabyLMs Macaroni — 2026  
  https://arxiv.org/abs/2609.30535
- Deep map  
  ../../library/themes/multilingual/CROSS_LINGUAL_CAPABILITY_FORMATION_2026.md
