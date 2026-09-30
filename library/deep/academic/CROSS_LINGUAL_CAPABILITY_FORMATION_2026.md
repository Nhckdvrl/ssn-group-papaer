# Cross-Lingual Capability Formation — Literature & Artifact Map (2026-09-30)

**Role:** reusable deep academic map for search/workbench decisions.  
**Status:** literature/territory asset only — **not a workbench, candidate, or paper claim**.  
**Primary question-forming object:** how shared multilingual computation and cross-lingual transfer **form during training**, and why different multilingual capabilities depend on different forms of cross-language coupling.

---

## 0. Why this territory is scientifically live

A single phrase such as “multilingual alignment” hides several different phenomena:

- lexical correspondence / translation;
- sentence-level semantic alignment;
- task transfer in NLU;
- language-agnostic concept representations;
- multilingual reasoning;
- factual knowledge consistency / transfer;
- output-language control.

Recent controlled work does **not** support treating these as one scalar capability.

The most important 2025–2026 pressure is the coexistence of several apparently conflicting results:

1. explicit bilingual / parallel data can be disproportionately important for translation;
2. other cross-lingual QA / reasoning capabilities can remain strong after mixed-language documents are removed;
3. shared or English-pivot middle-layer representations correlate with and can causally repair NLU transfer failures;
4. language-neutral representation alone is not sufficient for transfer in a controlled testbed;
5. language-specific representations can actively interfere with multilingual reasoning, while language-specific information remains necessary near the output;
6. factual knowledge transfer is often weak, asymmetric, frequency-dominated, and stage-dependent.

The useful object is therefore not “does alignment help?” but the **formation and use of cross-lingual computational structure**, with capability, representation level, training stage, and coupling signal kept distinct.

---

## 1. Historical parent: cross-lingual structure without explicit pairwise alignment

### Conneau et al. — Emerging Cross-lingual Structure in Pretrained Language Models (ACL 2020)

**Parent belief:** shared vocabulary and joint multilingual exposure were natural explanations for zero-shot transfer.

**Pressure / changed premise:** controlled multilingual masked-LM experiments showed transfer can emerge even with disjoint vocabularies and different domains, provided higher layers share parameters. Separately trained monolingual representations can also be aligned post hoc.

**Reusable move:** remove an apparently necessary bridge rather than merely strengthen it.

https://aclanthology.org/2020.acl-main.536/

### Artetxe et al. — On the Cross-lingual Transferability of Monolingual Representations (ACL 2020)

Freeze a monolingual Transformer and learn only a new language’s lexical embeddings. No shared vocabulary or multilingual joint training is required, yet the resulting model transfers competitively on cross-lingual classification and XQuAD.

**Boundary:** do not claim that shared vocabulary or explicit parallel exposure is a necessary condition for cross-lingual transfer.

https://aclanthology.org/2020.acl-main.421/

### Dufter & Schütze — Identifying Elements Essential for BERT’s Multilinguality (EMNLP 2020)

Uses intentionally small, fast controlled training to identify architectural / linguistic ingredients affecting multilinguality.

**Research-craft lesson:** a small controlled sandbox can be legitimate when it is used to isolate a real mechanism and then checked against larger models — but the sandbox cannot be the only evidence for a modern-LLM claim.

https://aclanthology.org/2020.emnlp-main.358/

---

## 2. Lexical anchors: not necessary, but often useful

### Hua et al. — mOthello (Findings NAACL 2024)

A controlled synthetic testbed separates:

- representation alignment;
- cross-lingual transfer.

Anchor tokens strongly improve language-neutral representation alignment, yet near-perfect representation alignment does **not** by itself produce cross-lingual transfer. A unified output space yields both.

**Important boundary:** “representations align” is neither automatically a capability claim nor sufficient evidence of transfer.

Paper: https://aclanthology.org/2024.findings-naacl.103/  
Code: https://github.com/ethahtz/multilingual_othello

### Kallini et al. — False Friends Are Not Foes (Findings EMNLP 2025)

Controlled bilingual autoregressive training across six EN-X pairs and four token-overlap conditions:

- full overlap;
- high-semantic-similarity overlap;
- low-semantic-similarity overlap;
- no overlap.

The implementation remaps token IDs while holding segmentation/frequency confounds much more tightly than ordinary tokenizer comparisons. Any overlap tends to help relative to fully disjoint vocabularies; semantically corresponding overlap helps most.

**Interpretation:** token overlap is better viewed as an **anchor / accelerator / inductive bias** than as a necessary condition.

Paper: https://aclanthology.org/2025.findings-emnlp.1153/  
Code: https://github.com/jkallini/false-friends

---

## 3. Bilingual documents: a task-dependent causal intervention

### Shao et al. — The Role of Mixed-Language Documents for Multilingual Large Language Model Pretraining (ACL 2026)

One of the most important current parents because it manipulates the **pretraining corpus itself** rather than analyzing a final model.

Setup:

- EN/FR/DE/ES web data;
- FINEWEB baseline vs MONOWEB with mixed-language documents removed;
- parallel and code-switching subsets reintroduced separately;
- 1.35B decoder-only models trained from scratch;
- corpus and trained models released.

Headline asymmetry:

- mixed-language documents are <2% of the corpus;
- removing them causes a very large translation drop;
- cross-lingual QA changes much less;
- general understanding/reasoning is nearly stable;
- parallel documents recover most translation;
- naturally occurring code-switching restores much less;
- loss of mixed-language data strongly damages lexical-level alignment while sentence-level alignment remains much more intact.

**Changed premise:** “bilingual exposure benefits multilingual capability” is too coarse. Different capabilities depend on different cross-language signals and representation granularities.

Paper: https://aclanthology.org/2026.acl-long.1706/  
Dataset: https://huggingface.co/datasets/UCLNLP/monoweb-dataset  
Model link stated in paper: https://huggingface.co/UCLNLP/monoweb

### Ji et al. — Data-Centric Continual Pre-training for 500+ Languages (Findings ACL 2026)

Continual-pretraining study with Llama 3 family and large-scale bilingual translation data across 500+ languages. Parallel data generally improves transfer, especially in lower-resource settings.

**Use:** large-scale method/data boundary. Do not compete by “more languages / larger multilingual corpus”; use as evidence that parallel-data utility remains real outside the controlled EN-Western-European setup.

https://aclanthology.org/2026.findings-acl.937/

---

## 4. Code-switching: definition and regime matter

### Rooryck et al. — Feeding BabyLMs Macaroni (arXiv 2026-09)

Small decoder-only models trained on English/Dutch/Chinese BabyBabelLM variants. Word-level → sentence-level → monolingual code-switch curricula induce stronger alignment of parallel representations, particularly across scripts, and the alignment persists into later monolingual training. Code/data/models are released.

**Why this does not simply contradict Shao et al.:**

The interventions differ substantially:

- Shao et al. isolate *naturally occurring* web code-switching inside a large-pretraining regime and find little recovery of translation;
- Macaroni constructs semantically controlled code-switching and studies a curriculum in a small-data developmental regime.

This mismatch is a **pressure**, not a contradiction to resolve by averaging results. “Code-switching” is not one treatment.

Paper: https://arxiv.org/abs/2609.30535  
Code/models/data: https://github.com/drooryck/multilingual-macaroni

---

## 5. Alignment and NLU: correlation → causal intervention

### Kargaran et al. — MEXA (ACL 2025)

Uses parallel sentences and English-pivot representation similarity to estimate multilingual task performance. Across multiple model families/tasks, middle-layer alignment is highly predictive.

Paper: https://arxiv.org/abs/2410.05873  
Code: https://github.com/cisnlp/MEXA

### Liu & Niehues — Middle-Layer Representation Alignment for Cross-Lingual Transfer in Fine-Tuned LLMs (ACL 2025)

Analyzes 1,000+ language pairs and turns middle-layer alignment into a training objective; reports gains on slot filling, MT and structured generation.

Paper: https://aclanthology.org/2025.acl-long.778/  
Code/models: https://github.com/dannigt/mid-align

### Ravisankar et al. — Can you map it to English? (EACL 2026)

Moves from language-level correlation to **instance-level causal evidence**:

- DALI compares cross-lingual representation alignment for transfer-success vs transfer-failure examples;
- failures are less English-aligned in middle layers;
- patching semantically equivalent English activations into failed non-English instances can flip predictions correctly;
- control patching tests alternative explanations.

This establishes that alignment can be causally load-bearing for some NLU decisions.

Paper: https://aclanthology.org/2026.eacl-long.225/  
Code: https://github.com/Kartik21/XLingAlignment

**Boundary:** any new work saying only “better middle-layer English alignment correlates with multilingual NLU performance” is already heavily owned.

---

## 6. Shared concept spaces: formation during pretraining

### Dumas et al. — Separating Tongue from Thought (ACL 2025)

Cross-lingual activation patching separates output language from concept identity and provides causal evidence for language-agnostic concept representations.

https://aclanthology.org/2025.acl-long.1536/

### Körner et al. — When Meanings Meet (EACL 2026)

Uses activation patching over intermediate pretraining checkpoints to study **when shared concept spaces emerge**.

Key points:

- shared concept spaces appear early and refine through training;
- alignment strength depends on language / training composition;
- output-language mapping remains a separate requirement;
- manual inspection finds that some apparent translation “improvements” are actually behavior changes such as sense selection or stopping homograph copying.

This is an important research-craft exemplar: even causal interventions need **object-validity checks** before an automatic metric is interpreted as the desired capability.

Paper: https://aclanthology.org/2026.eacl-long.145/  
Code: https://github.com/mainlp/shared-concept-spaces

---

## 7. Reasoning: shared computation can coexist with harmful language-specific signal

### Zhao et al. — When Less Language is More (NeurIPS 2025)

A particularly important counter-pressure:

- identify language-specific representation directions;
- remove them in lower/middle reasoning layers;
- multilingual reasoning improves across 10 open-weight models / 11 languages;
- retaining language information near upper/output layers remains important for language fidelity.

**Implication:** “more language-specific representation” is not monotonically useful. Reasoning and surface realization can prefer different information at different depths.

Paper: https://proceedings.neurips.cc/paper_files/paper/2025/hash/372bd0e47f2d5bceca7e300e1446849c-Abstract-Conference.html  
Code: https://github.com/MuyuenLP/Language-Reasoning-Disentangle

### LinguaMap (ICLR 2026)

Reports a three-stage structure:

- early shared semantic mapping;
- middle task reasoning;
- late language-specific generation.

Selective late-layer tuning can improve language consistency without changing the reasoning core much.

https://proceedings.iclr.cc/paper_files/paper/2026/hash/00295cede6e1600d344b5cd6d9fd4640-Abstract-Conference.html

### Beyond English-Centric Training (ICLR 2026)

Compares RL and SFT for multilingual reasoning and reports stronger cross-lingual generalization under RL, including non-English RL training regimes.

**Use:** post-training changes the *kind* of cross-lingual generalization; pretraining alignment findings should not be assumed to transfer unchanged to reasoning post-training.

https://proceedings.iclr.cc/paper_files/paper/2026/hash/9320df227557d00ce68f1b8b07ea2d49-Abstract-Conference.html

### Multilingual Routing in Mixture-of-Experts (ICLR 2026)

Finds language-specific routing in early/late layers and more cross-lingual routing alignment in middle layers. Steering middle-layer routing toward English-associated task experts modestly improves multilingual performance.

**Use:** shared computation can be visible not only in residual representations but also in **which parameters are executed**.

https://proceedings.iclr.cc/paper_files/paper/2026/hash/1b558190825286a3defcc78d02fa2189-Abstract-Conference.html

---

## 8. Factual knowledge: consistency and transfer are a different regime

### Qi et al. — Cross-Lingual Consistency of Factual Knowledge (EMNLP 2023)

Model size improves factual accuracy but not necessarily cross-lingual consistency. Editing a fact in English transfers selectively depending on language-pair consistency.

https://aclanthology.org/2023.emnlp-main.658/

### Liu et al. — Tracing Multilingual Factual Knowledge Acquisition in Pretraining (Findings EMNLP 2025)

Uses the open OLMo-7B training trajectory.

Main picture:

- recall and consistency improve during pretraining;
- fact frequency is the dominant, largely language-agnostic driver;
- genuine cross-lingual transfer is visible for some low-frequency non-English facts;
- transfer appears particularly important earlier in training rather than as a uniform late-stage process.

Paper: https://aclanthology.org/2025.findings-emnlp.113/  
Code/data: https://github.com/cisnlp/multilingual-fact-tracing

### Zhao et al. — Tracing Multilingual Knowledge Acquisition Dynamics in Domain Adaptation (EACL 2026)

Continual-training setup designed to match training/evaluation knowledge coverage. Finds cross-lingual knowledge transfer remains difficult and studies a loss-shielding mechanism.

https://aclanthology.org/2026.eacl-long.269/

### LiveCLKTBench (ACL 2026)

Attempts to isolate genuine new cross-lingual knowledge transfer from facts already seen during pretraining by using time-sensitive knowledge. Finds transfer asymmetric and dependent on language/domain.

https://aclanthology.org/2026.acl-long.694/

**Boundary:** factual transfer should not be inferred from translation/NLU alignment, and existing pretrained knowledge exposure is a major confound.

---

## 9. Training-dynamics artifacts we can actually use

### XLM-R Across Time

39 intermediate checkpoints from an XLM-R-base-style replica, from 5k to 1.5M steps.

Paper: https://aclanthology.org/2022.emnlp-main.234/  
Checkpoints: https://nlp.cs.washington.edu/xlmr-across-time/

### BLOOM checkpoints

Used by *Probing the Emergence of Cross-lingual Alignment during LLM Training* (Findings ACL 2024) to track alignment over training/model scale.

https://aclanthology.org/2024.findings-acl.724/

### OLMo-7B trajectory

The multilingual factual-tracing repository supplies scripts/data for intermediate checkpoints.

https://github.com/cisnlp/multilingual-fact-tracing

### MONOWEB intervention models

The costly from-scratch bilingual-document intervention has already been run; the ACL 2026 paper states that trained models and the corpus are released.

https://aclanthology.org/2026.acl-long.1706/

### Small controlled-pretraining sandboxes

- False Friends: GPT-2-style controlled token-overlap intervention.
- Macaroni: small multilingual decoder-only pretraining with released code/data/models.
- mOthello: synthetic but highly controlled alignment-vs-transfer testbed.

These are useful for **causal manipulation**, not sufficient alone for a modern-LLM conclusion.

---

## 10. Current pressure map

### P1 — Alignment is not one object

Lexical, sentence, concept, routing, reasoning, factual and output-language alignment are distinct.

A model can preserve sentence-level alignment while losing lexical translation ability; concept space can be shared while output mapping differs; language-neutral state can exist without transfer.

### P2 — Cross-language bridges can be accelerators rather than requirements

Shared vocabulary and parallel data are very useful in many regimes, yet strong cross-lingual structure can emerge without shared token IDs or direct aligned sentences.

The important distinction is:

> **necessary condition vs symmetry-breaking / optimization shortcut / accelerator**

Do not collapse these.

### P3 — Different capabilities appear to require different bridge granularity

Current strongest evidence suggests:

- translation: unusually dependent on explicit fine-grained correspondence;
- NLU: middle-layer semantic alignment can be causally important;
- reasoning: language-specific state may be harmful in the reasoning core and useful near output;
- factual transfer: dominated by exposure/frequency with weak, asymmetric transfer.

This is a field-level pressure, **not yet a paper claim**.

### P4 — Training stage matters

Cross-lingual structure can emerge early, degrade, move across layers, or become less important later.

Endpoint-only comparisons can hide the actual formation mechanism.

### P5 — Measurement is easy to misinterpret

- aligned representation ≠ transfer;
- probe/metric gain ≠ causal use;
- translation automatic score ≠ genuine semantic improvement;
- correct target-language answer ≠ genuine transferred knowledge rather than prior exposure.

### P6 — English is both a useful pivot and a dangerous assumption

Many modern studies explicitly use English as pivot because training is English-heavy. This is empirically useful, but a scientific claim about “universal shared semantics” should not silently become “alignment to English”.

A strong workbench needs at least some non-English↔non-English evidence or a clear justification for the English-pivot claim.

---

## 11. Workbench-worthy diagnostic questions (not final RQs)

A future workbench should choose only a few of these after reproducing parents:

1. Under matched training interventions, do lexical, sentence, concept, reasoning and factual alignment emerge at the same time or decouple?
2. Which bridge manipulations change **representation alignment** but not **functional transfer**, and vice versa?
3. When parallel/token anchors improve one capability but leave another unchanged, what computational object actually changed?
4. Are cross-language bridges necessary only for mapping *into/out of* a shared computation, while the central computation itself is language-independent?
5. Does cross-lingual transfer peak early and later get overwritten by language-specific specialization?
6. Can an intervention that improves translation alignment hurt reasoning by injecting language-specific structure into layers where language-neutral computation is beneficial?
7. Which claims survive the move from cheap controlled models to public 7B-scale training trajectories/intervention models?

These are **reconnaissance axes**. Do not pre-register a preferred sign.

---

## 12. Strongest practical entry stack under academic compute

### Tier A — no training / frozen analysis

- MONOWEB vs FINEWEB intervention models;
- DALI activation patching on Llama/Aya;
- Language-Reasoning-Disentangle on 7B-class open models;
- OLMo/BLOOM/XLM-R intermediate checkpoints;
- MEXA / shared-concept-space tooling.

This fits a single 4×A100/PRO6000 node for analysis/inference.

### Tier B — small controlled training

- False Friends codebase;
- Macaroni code/data/models;
- mOthello only as a mechanism sanity sandbox.

Use this only to perform interventions impossible on public large models.

### Tier C — light adaptation

- LoRA / small continued pretraining on 1B–8B models;
- targeted bridge manipulations after a load-bearing causal question appears.

### Do not start with

- reproducing MONOWEB-scale pretraining;
- 400-language scaling laws;
- new huge multilingual corpus construction;
- foundation-model pretraining.

---

## 13. Ownership boundaries / things not to rediscover

Do not build a paper whose central claim is merely:

- shared vocabulary is necessary for multilinguality — contradicted by old parents;
- token overlap helps — already controlled by False Friends;
- bilingual data helps translation — strongly owned by MONOWEB and multilingual CPT work;
- middle-layer English alignment predicts multilingual NLU — MEXA/DALI own it;
- shared concept spaces exist — ACL 2025 and EACL 2026 own it;
- alignment emerges during pretraining — XLM-R/BLOOM/EuroLLM trajectory work already exists;
- language-specific signal can hurt multilingual reasoning — NeurIPS 2025 owns a strong version;
- multilingual factual consistency varies across languages — old and current work owns it;
- language distance / resource amount correlates with transfer — dense prior and too close to ordinary factor analysis.

A new contribution needs a **changed problem representation or causal distinction**, not a larger sweep.

---

## 14. Research-navigation lessons from the lineage

### Rewind A: “shared vocabulary causes transfer”

Parent intuition  
→ remove shared vocabulary  
→ transfer survives  
→ shared deep computation is more fundamental.

Later successor  
→ controlled token overlap still improves transfer  
→ revised view: overlap is useful without being necessary.

**Reusable move:** replace binary necessity claims with causal-role decomposition.

### Rewind B: “alignment predicts capability”

Global correlation (MEXA)  
→ instance-level failure analysis (DALI)  
→ activation patching  
→ causal evidence for some NLU decisions.

Then mOthello / reasoning / translation evidence prevents the causal result from becoming a universal law.

**Reusable move:** association → matched failure slice → causal intervention → check task boundary.

### Rewind C: “bilingual data creates multilinguality”

Training folklore  
→ remove all mixed-language documents from pretraining  
→ translation collapses but QA/reasoning largely survive  
→ inspect data type and representation granularity.

**Reusable move:** remove a tiny but semantically special data component, then use asymmetric downstream effects to discover multiple capabilities hidden under one label.

### Rewind D: “multilingual reasoning needs better target-language reasoning”

English-alignment methods  
→ inspect internal language vs reasoning state  
→ language-specific components can be actively harmful in middle reasoning layers  
→ preserve/reinject them only where language realization needs them.

**Reusable move:** successful method family → localize what part is actually load-bearing → remove rather than add signal.

---

## 15. Risks

1. **English-centricity:** many artifacts use English as pivot; avoid claiming universal multilingual structure from English-only coupling.
2. **task taxonomy leakage:** “reasoning”, “NLU”, “translation”, and “knowledge transfer” are broad labels; experiments need precise operational tasks.
3. **pretraining vs post-training:** a final instruction/RL model may not preserve pretraining-stage relationships.
4. **metric validity:** representation similarity can be non-causal; patching can introduce off-manifold states; automatic translation evaluation can misclassify behavior.
5. **toy-to-large extrapolation:** small controlled models are intervention tools, not final external-validity evidence.
6. **language-family confounds:** script, tokenizer, data volume, typology and benchmark quality often co-vary.
7. **field density:** multilingual transfer is established and active. This is acceptable; novelty must come from a sharper causal distinction, not “one more language/model”.

---

## 16. Current territory judgment

This territory is **not empty and should not be**.

It has:

- a mature historical lineage;
- new 2025–2026 causal and training-dynamics work;
- unresolved tensions rather than a single exhausted question;
- multiple open artifacts at academic scale;
- cheap controlled-pretraining sandboxes;
- several independent evidence types;
- no need to compete on foundation-model scale.

The strongest current abstraction is:

> **cross-lingual capability formation and use: how different kinds of shared computation emerge from weak or explicit cross-language coupling, and why their functional role differs across translation, NLU, reasoning and knowledge transfer.**

This is still a **territory**, not a registered paper RQ.
