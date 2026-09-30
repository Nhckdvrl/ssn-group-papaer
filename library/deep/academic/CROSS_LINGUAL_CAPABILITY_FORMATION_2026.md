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


---

## 17. High-information pressure: translation as proxy versus translation as causal model organism

This is currently the strongest workbench-level pressure produced by the literature map. It is **not yet a final RQ**.

### 17.1 Two roles of translation are often conflated

Translation appears in the multilingual literature in at least two scientifically different roles.

**Role A — interface / measurement proxy**

*Translation as a Scalable Proxy for Multilingual Evaluation* evaluates 14 models (1B–72B) across nine multilingual benchmarks and finds translation quality is often strongly correlated with downstream multilingual performance. The intended use is a cheap first-pass screen before task-specific evaluation.

This is an **observational relationship across model × language × task conditions**.

**Role B — model organism for cross-lingual transfer formation**

Several mechanistic/developmental papers use word-level or sentence translation as a tractable readout of how cross-lingual generalization itself forms. Examples include *Copy First, Translate Later* and *Semantic Pivots Enable Cross-Lingual Transfer*.

This is a much stronger scientific use: translation is treated as a window onto the formation of broader cross-lingual computation.

These roles should not be silently treated as equivalent.

### 17.2 Controlled evidence creates a tension

MONOWEB provides an unusually clean causal intervention:

> remove a very small but semantically special portion of mixed-language pretraining data.

The result is highly asymmetric:

- translation deteriorates strongly;
- cross-lingual QA changes much less;
- general understanding/reasoning is nearly stable;
- reintroducing parallel data restores most translation;
- lexical alignment is affected much more than sentence-level alignment.

This means that a factor can be **causally load-bearing for translation** without being equally load-bearing for other cross-lingual capabilities.

At the same time, the translation-proxy paper finds translation is often an excellent **observational predictor** of broad multilingual performance.

The resulting pressure is:

> **How can translation be a strong observational proxy for multilingual performance while controlled training interventions selectively alter translation without equivalent changes in other capabilities?**

This is not a contradiction. A variable can be highly predictive while not being the common causal bottleneck.

The interesting scientific object is the causal structure behind that predictive relationship.

### 17.3 A three-stage interpretation is plausible but already partly owned

Current reasoning work supports a decomposition such as:

> target-language input interface  
> → shared / dominant-language semantic-reasoning computation  
> → target-language output interface.

*Why Do Multilingual Reasoning Gaps Emerge?* shows that correcting the input-understanding stage with selective translation removes a large portion of the default multilingual reasoning gap.

*Beyond Input Understanding* then shows that if reasoning execution itself is forced into a weaker language, performance can still degrade even when the input is English.

XBridge, MRRE, LinguaMap and shared-circuit work independently make similar interface/core distinctions operational.

Therefore a paper cannot simply claim:

> “multilingual models have a shared reasoning core plus language-specific interfaces.”

That abstraction is already heavily occupied.

The remaining pressure is more precise:

> **Which multilingual capabilities are bottlenecked by the interfaces, which depend on the shared computation itself, and which require capability-specific cross-language coupling during training?**

### 17.4 Translation can be a marker without being the mechanism

A coherent hypothesis class — to test, not assume — is:

- language resource, tokenizer quality, lexical grounding and interface robustness improve translation;
- those same factors also make it easier to enter/exit shared semantic computation;
- therefore translation correlates strongly with many multilingual tasks;
- but explicit token-level bilingual correspondence is additionally and uniquely important for translation itself.

Under this picture:

> translation is an excellent **marker of interface quality** but an imperfect **causal model of the internal capability**.

This would reconcile the observational proxy paper with MONOWEB without declaring either wrong.

Other explanations must compete:
- general data quality/resource quantity creates both outcomes;
- translation metrics encode language-resource artifacts;
- benchmark construction/translation quality induces part of the correlation;
- reasoning tasks differ in contamination/prior exposure;
- model family/post-training changes the relationship.

### 17.5 Do not confuse two translation-validity questions

**Benchmark translation validity**

ACL 2026 *Quantifying the Impact of Translation Errors on Multilingual LLM Evaluation* studies whether errors introduced when translating a benchmark corrupt evaluation.

Object:
> quality of the *benchmark translation*.

**Translation-skill proxy validity**

*Translation as a Scalable Proxy* studies whether a model's own MT performance predicts its performance on other multilingual tasks.

Object:
> quality of the *model's translation capability*.

They are related through the language interface, but they are not the same scientific question.

A future workbench must keep them separate.

### 17.6 Why this pressure has top-conference ceiling

If translation is only a correlational marker, this changes how several kinds of multilingual work should be interpreted:

- translation as a scalable evaluation proxy;
- translation/WLT as a model organism for cross-lingual transfer;
- methods that improve multilinguality by increasing translation/alignment;
- attribution of reasoning gaps to input-language mapping;
- training-data design based on parallel/code-switched bridges.

The best-case outcome is not “one proxy score is less accurate”.

It is a more precise causal taxonomy of:

> **interface quality, shared computation and capability-specific bilingual coupling.**

That could explain why strong observational correlations coexist with intervention-level dissociations.

### 17.7 Practical reconnaissance surface

The expensive interventions already exist.

**Observational side**
- public scores/raw predictions from the translation-proxy project;
- audit correlations by task, model, language-resource level and sample count.

**Controlled causal side**
- FINEWEB vs MONOWEB vs +parallel vs +code-switching released 1.35B models;
- compare translation, NLU/reasoning and representation changes inside the same training recipe.

**Cheap intervention side**
- False Friends token-anchor manipulations;
- Macaroni code-switch curricula;
- Bilingual BabyLM exposure-regime controls.

**Training-dynamics side**
- Copy First dense translation checkpoints;
- XLM-R/BLOOM/OLMo trajectories for other cross-lingual objects.

**Internal-mechanism side**
- DALI / shared-concept-space patching;
- language-specific-representation ablation in reasoning;
- routing/shared-circuit parents.

This allows a workbench to combine observational, causal-training, trajectory and mechanistic evidence without foundation-model pretraining.

### 17.8 Current ownership status

As of 2026-09-30, the nearest strong papers separately own:

- translation as a scalable observational proxy;
- bilingual-data causal effects on translation;
- translated-benchmark error effects;
- translation formation dynamics;
- NLU alignment causality;
- multilingual reasoning stage decomposition.

In the current literature audit we have **not yet identified a strong paper that directly tests whether translation's observational proxy relationship corresponds to a shared causal bottleneck under controlled multilingual pretraining interventions**.

This is a provisional ownership judgment, not proof of novelty. Continue searching before candidate promotion.

### 17.9 Kill conditions for this lead

Demote this lead if:

1. a direct prior already compares translation-proxy validity under controlled pretraining interventions;
2. MONOWEB-style interventions leave the translation→downstream relationship intact once resource/metric confounds are modeled;
3. the apparent dissociation is explained entirely by benchmark translation artifacts;
4. the only surviving result is “correlation is not causation” with no capability-specific causal structure;
5. the story requires an enormous new multilingual pretraining run rather than exploiting existing interventions;
6. the explanation collapses to one model family/language family and cannot be checked elsewhere.

### 17.10 Current judgment

This lead is stronger than a generic “study multilingual alignment” topic because it begins from a concrete tension between two successful scientific practices:

> **translation as a scalable proxy / model organism**  
> versus  
> **controlled evidence that translation has capability-specific causal dependencies.**

The workbench-worthy object is not translation itself.

It is:

> **when a measurable cross-lingual capability is a marker of shared multilingual competence versus a capability-specific mechanism.**

Translation is currently the cleanest entry point because the field already supplies both strong proxy evidence and strong causal interventions.


### Adjacent proxy-validity boundary: translated benchmark vs native benchmark

*Gold vs. Translation* (ACL ARR March 2026 submission) asks a different but nearby proxy-validity question: whether machine-translated English-origin benchmarks measure the same construct as natively authored benchmarks. After controlling for model size and language proficiency, proxy validity is strong for some curriculum-overlap tasks but weakens for locality/culture-specific knowledge.

This is useful ownership pressure but does **not** directly test the central lead here:

> whether a model's **intrinsic translation capability** is a causal/shared bottleneck for its other multilingual capabilities.

Keep three objects separate:

1. quality of translated benchmark items;
2. translated-benchmark score as a proxy for native-benchmark score;
3. model MT ability as a proxy/model organism for broader multilingual competence.


---

## 18. Stronger pressure after cross-paper reconciliation: the role of parallel data changes with acquisition regime

The translation-proxy lead led to a deeper and currently stronger pressure.

### 18.1 The apparent contradiction

**Just Go Parallel (ACL 2025)** reports that adding parallel data improves not only translation but also non-English commonsense reasoning.

**MONOWEB (ACL 2026)** reports that removing mixed-language documents — and then selectively restoring parallel data — has an enormous effect on translation but almost no effect on cross-lingual QA/general reasoning.

Both are controlled decoder-LM pretraining studies. Their conclusions about the *breadth* of parallel-data benefit therefore cannot simply be collapsed into “parallel data helps multilinguality.”

### 18.2 A consequential difference in acquisition regime

The training distributions are qualitatively different.

**JGP**
- 1.1B decoder LM, trained from scratch;
- base 167B-token mix is overwhelmingly English;
- Indonesian and Chinese occupy only tiny fractions of the original monolingual data;
- EN↔ID/ZH parallel data therefore supplies both target-language exposure and explicit cross-language coupling;
- placement matters: early parallel gains can be forgotten by later non-parallel training.

**MONOWEB**
- 1.35B decoder LM, trained from scratch;
- deliberately balanced EN/DE/ES/FR monolingual exposure (~60B tokens per language in corpus construction);
- every language receives abundant standalone exposure;
- removing the small bilingual slice destroys MT much more than QA/reasoning;
- parallel data primarily restores MT/lexical alignment.

This suggests a hypothesis class:

> **parallel data may play different functional roles depending on whether the model is still acquiring the target language or already has sufficient monolingual competence in it.**

Possible roles:
1. **language-acquisition scaffold** — supplies target-language semantic/linguistic competence when exposure is scarce;
2. **cross-language semantic bridge** — couples representations/computation between already learned languages;
3. **lexical/interface alignment** — sharpens fine-grained mappings needed for translation/output conversion.

These roles need not coexist with the same strength.

### 18.3 Third regime: post-hoc language acquisition

**OpenSeal (2026 preprint)** begins from an English-centric OLMo-2 and continually pretrains it for Southeast Asian languages.

Parallel-only CPT is reported as especially effective, with benefits extending beyond translation into tasks such as XNLI/XCOPA/PAWS-X.

This resembles JGP more than MONOWEB in one crucial respect:

> the target languages are being **added / strengthened after an English-centric capability core already exists**.

That creates three useful regimes:

| Regime | Representative | Target-language state before parallel intervention | Reported role of parallel data |
|---|---|---|---|
| English-heavy joint pretraining | JGP | severely underexposed | MT + broad non-English reasoning |
| post-hoc language adaptation | OpenSeal | weak in English-centric base | MT + broader multilingual tasks |
| balanced joint multilingual pretraining | MONOWEB | abundant monolingual exposure from the start | large MT effect; little QA/reasoning effect |

This table is **not causal proof of a regime transition** because many other factors differ. It is a pressure map.

### 18.4 Why “resource regime matters” is not enough

Older work already owns the generic statement.

- Reid & Artetxe (Findings ACL 2023) ask whether parallel-data gains arise from the data or from modeling parallel interactions.
- Ansell et al. (EMNLP 2023) explicitly unify transfer strategies across varying task-specific, monolingual and parallel resource scarcity.
- Zheng et al. (EMNLP 2024) compare cross-lingual CPT with from-scratch acquisition across model/data scales.

Therefore a workbench cannot claim:

> “parallel data is more useful for low-resource languages”

or:

> “CPT and joint training behave differently.”

The scientifically sharper object would need to identify a **change in the functional role of bilingual coupling**, with evidence beyond performance curves.

### 18.5 Strong competing explanation: semantic content, not alignment

**TransWebEdu (EMNLP 2025)** is important because it translates a high-quality English corpus into nine languages and trains a 1.3B multilingual model from scratch.

The translated documents are useful even when used as target-language monolingual documents, so broad multilingual gains can arise from:

> **matched high-quality semantic content / target-language exposure**

without requiring explicit adjacent bilingual pairs.

Therefore JGP/OpenSeal broad gains cannot automatically be attributed to alignment.

A future workbench must distinguish at least:

- target-language token quantity;
- content quality/diversity;
- same-semantic-content across languages;
- explicit pair adjacency/alignment;
- training timing;
- pre-existing source-language capability.

### 18.6 Another success case: multi-way parallel CPT

**From Unaligned to Aligned (EMNLP 2025)** reports that multi-way parallel TED data improves six multilingual benchmarks relative to unaligned multilingual data during CPT/instruction tuning.

This strengthens the evidence that explicit alignment can be useful beyond MT in adaptation regimes, but does not isolate whether the decisive variable is:
- parallel structure;
- cleaner/more homogeneous content;
- target-language resource support;
- multi-way consistency;
- training stage.

### 18.7 Current high-information distinction

The strongest current formulation is no longer:

> “Is translation a good proxy?”

It is:

> **When does bilingual coupling function as a scaffold for acquiring/using a language broadly, and when does its marginal role contract to fine-grained cross-language interface alignment such as translation?**

Translation-proxy validity becomes one observable consequence of this deeper distinction.

This has a potential changed-premise consequence:

> the field often treats “parallel data” as one ingredient with one effect, but its causal role may depend on the developmental state of the target language inside the model.

### 18.8 What evidence would make this more than a literature reconciliation?

A workbench must identify a **within-controlled-family transition**, not merely compare papers.

The cleanest desired experiment is approximately factorial:

> target-language monolingual exposure × fixed parallel-data dose/format × training stage

while measuring:
- MT;
- NLU / commonsense / reasoning;
- lexical alignment;
- sentence/concept alignment;
- language-ID / output control;
- optionally internal routing/shared computation.

Critical prediction is **not preregistered**. Possible outcomes include:
- parallel benefits all capabilities at every exposure level → regime hypothesis weakened;
- broad benefit shrinks with monolingual exposure while MT benefit persists → role-transition evidence;
- only data quality matters → alignment story dies;
- timing dominates exposure → developmental-window story;
- language family/tokenizer determines transition → different object emerges.

### 18.9 Academic-scale feasibility

Do not reproduce 100B-token runs first.

**Frozen-model reconnaissance**
1. JGP released checkpoints across data placement/training stages.
2. MONOWEB/FINEWEB intervention models.
3. OpenSeal models/data if release is complete.
4. TransWebEdu models/corpus.
5. EMNLP multi-way-parallel code/artifacts.

First build a harmonized intervention-response table on overlapping tasks/languages where possible.

**Small controlled factorial**
Only if frozen families support the regime pressure:
- 0.3B–1.5B decoder LM;
- 2–3 language pairs;
- matched semantic source corpus;
- target monolingual exposure levels;
- fixed parallel dose;
- adjacent vs separated / translated-monolingual controls;
- several checkpoints through training.

The scientific goal is to reproduce the **role transition**, not leaderboard performance.

### 18.10 Orthogonal interface control: tokenizer

ICML 2026 TokSuite releases fourteen 1B models with identical architecture, data, budget and initialization, changing only the tokenizer.

This is potentially valuable as a negative/control axis:

> if MT proxy quality changes strongly with tokenizer/interface properties while semantic/reasoning performance changes differently, then part of MT’s predictive power may be interface-mediated rather than a shared competence mechanism.

Do not expand into generic tokenizer research unless this distinction becomes load-bearing.

### 18.11 Current ownership judgment

The literature clearly owns:
- resource scarcity matters;
- parallel data helps low-resource transfer;
- CPT differs from scratch training;
- multi-way aligned data can beat unaligned data;
- machine-translated high-quality monolingual data can improve multilingual understanding;
- parallel data is crucial for MT in balanced multilingual pretraining.

The current audit has **not yet found a modern decoder-LLM study that cleanly factorializes target-language monolingual acquisition state/exposure against a fixed bilingual-coupling intervention and tracks when parallel data changes from broad capability scaffold to translation/interface-specific signal.**

This is provisional. Keep searching.

### 18.12 Kill conditions

Kill or substantially reframe this lead if:

1. direct prior already performs the exposure × parallel-data factorial and reaches the same functional-role question;
2. JGP/MONOWEB differences vanish under matched downstream tasks or stronger baselines;
3. TransWebEdu-style matched content fully explains broad parallel gains;
4. only “low-resource gets bigger gains” survives;
5. no internal/behavioral measurement can distinguish scaffold vs interface roles;
6. a controlled small model exhibits a pattern that does not transfer at all to released modern LLM families.



---

## 19. Direct-prior compression: parallel/translation is no longer the preferred lead

The late audit found several unusually close 2026 works:

- *From Translation to Multilinguality* separates concatenated parallel pairs from split monolingual sides and finds pair interaction primarily benefits translation rather than broad multilingual competence across several regimes;
- MuBench includes fixed-budget controlled bilingual pretraining varying language ratios and parallel-data proportions;
- ParaRater explicitly separates pseudo-parallel examples from examples whose positive utility depends on paired bilingual interaction;
- Token Alignment Heads identifies translation-specific circuits, their training trajectory, and training examples causally important to those circuits.

Together these works heavily occupy:

> parallel-data content vs pairing  
> → translation-specific behavior  
> → specialized translation mechanism/data.

This subline remains scientifically valuable, but a small follow-up such as testing more pair formats or counting specialized heads under another condition has weak ceiling and faces concentrated company-scale competition.

**Decision:** demote it as the primary C lead. Keep it as background evidence and a possible control axis.

The earlier simple hypothesis that abundant monolingual exposure causes the broad benefit of parallel data to disappear is also **withdrawn**: MuBench reports broad non-translation gains from parallel data even under a balanced high-exposure EN:ZH regime. Do not revive that claim without a new premise.

---

## 20. Current stronger lead: what does “reasoning language” actually control?

The multilingual reasoning literature now contains a productive tension.

### 20.1 Surface reasoning language is clearly consequential

EMNLP 2025 / ICLR 2026 work shows that forcing an LRM to produce reasoning traces in a target language can substantially change accuracy, especially in low-resource languages.

This is already owned and is **not** by itself a new problem.

### 20.2 But “reasoning language” is measured at multiple incompatible levels

Current papers use several proxies:

1. **visible trace language** — language ID / script of generated CoT;
2. **decodable hidden language** — Logit-Lens token/script probabilities;
3. **latent answer dynamics** — when the correct answer becomes salient in hidden states;
4. **cross-language hidden-state similarity** — cosine/CCA-style alignment with English;
5. **mathematical trace structure** — language-independent anchors/dependencies extracted from visible traces;
6. **causal language routing** — activation patching that switches the language of generated reasoning.

These quantities should not be treated as interchangeable.

For example, Language Mixing's “internal language” is a Logit-Lens projection into vocabulary/script space, while Multilingual Latent Reasoners uses answer-rank dynamics and hidden-state similarity. Both are informative, but neither directly establishes that hidden computation literally operates in a natural language.

### 20.3 Input-understanding vs reasoning-execution is not a simple contradiction

Findings ACL 2026 *Why Do Multilingual Reasoning Gaps Emerge?* finds that, under models' natural reasoning behavior, much of the gap can be removed by translating only examples where input understanding fails.

EMNLP 2026 *Beyond Input Understanding* holds the input in English and forces the visible reasoning trace into another language; accuracy can still collapse.

These can both be true:

> target-language input  
> → access / mapping into dominant reasoning computation  
> → reasoning execution / trace generation  
> → final output.

A model may normally avoid weak target-language reasoning execution by pivoting to an English-dominant route. Forcing the visible trace language changes a different part of the system than translating the input.

### 20.4 Post-training creates a sharper tension

There is no universal “target-language reasoning is bad” law.

- EMNLP 2025 finds prompt control / small SFT improves language matching but preserves an accuracy cost.
- ICLR 2026 *Beyond English-Centric Training* finds RL cross-lingual generalization is much stronger than SFT, while explicit language-consistency prompts/rewards can reduce accuracy and correlate with larger representational shifts.
- ReasonXL reports SFT+RLVR can move reasoning fully into target European languages with little/no performance sacrifice and identifies an early-layer language-routing bottleneck.
- EMNLP 2026 AdaMame reports an adaptive SFT+RL recipe that improves language fidelity without the same fixed-reward trade-off.
- Apple 2026 GRPO Beyond English finds native-language RL can be competitive but effects and regressions are strongly model/language dependent.

The resulting scientific pressure is not:

> “Can we train models to reason in non-English?”

That is already a method race.

It is:

> **What internal computation must be preserved when post-training changes the language of visible reasoning, and why do some language-control objectives preserve cross-lingual reasoning while others damage it?**

### 20.5 Competing explanations

A workbench should make these explanations compete rather than assume an “English reasoning core”:

**E1 — routing-only.**  
Language control changes an early routing variable while leaving central reasoning computation mostly invariant. ReasonXL points in this direction.

**E2 — computation rewrite.**  
Forcing/adapting another reasoning language changes the actual reasoning trajectory/strategy and can damage mathematical dependency structure. DATG and trace-quality work support this possibility.

**E3 — output/token burden.**  
The hidden reasoning remains broadly shared, while non-English token generation makes explicit trace production longer/noisier/more error-prone.

**E4 — pretrained-structure preservation.**  
Successful RL works because it minimally perturbs a shared pretrained reasoning structure; SFT/fixed language rewards overwrite it. ICLR 2026 proposes this interpretation, but its mechanistic evidence is preliminary (final-layer PCA/shift statistics).

**E5 — language-specific good reasoning.**  
There is no single universal English-like structure to preserve; useful reasoning features differ by language. COLM 2026 pressures English-centric objectives in this direction.

These explanations imply different intervention outcomes.

### 20.6 Potentially revealing academic-scale interventions

No final RQ is registered, but high-information experiments could include:

- matched base/SFT/RL checkpoints from public multilingual reasoning projects;
- activation patching from baseline ↔ language-adapted models at the identified routing bottleneck and deeper reasoning layers;
- force visible trace language while independently patching/restoring latent states from the high-accuracy route;
- erase/change trace-language directions without changing answer-relevant states, and vice versa;
- compare answer-salience trajectory, DATG structure, causal importance of reasoning tokens, and visible language in the same samples;
- test whether accuracy can be rescued while trace language remains target-language, or trace language switched while answer dynamics remain unchanged.

The key is **orthogonalization**:

> manipulate trace language and answer-relevant computation separately.

If they cannot be independently manipulated, the decomposition may be wrong.

### 20.7 Why this could have ceiling

A positive result could change interpretation of a large current method family.

If visible reasoning language is mostly a routing/interface variable, then:
- language-fidelity rewards may optimize the wrong object;
- English-vs-native CoT comparisons can confound computation with realization;
- some “multilingual reasoning” improvements may be trace-language control rather than reasoning improvement.

If changing reasoning language genuinely rewrites computation, then:
- latent-English/shared-core narratives are too strong;
- post-training must learn language-specific reasoning structures rather than only reroute a shared core.

Either direction would matter beyond one language or one benchmark.

### 20.8 Main risks / kill conditions

Kill or demote if:
- ReasonXL or another direct prior already independently manipulates language routing and reasoning computation enough to establish this distinction;
- visible trace language and internal answer dynamics cannot be manipulated independently in strong open models;
- every effect reduces to tokenization/sequence-length differences;
- the only surviving conclusion is “English works better”;
- useful evidence requires proprietary hidden CoT or company-scale RL training;
- the phenomenon disappears on current open reasoning models after strong prompts/training.



---

## 18. Lead demotion and new pressure: when does explicit bilingual alignment transfer beyond translation?

### 18.1 The previous proxy/interventional-validity lead is demoted

The earlier lead asked whether translation's cross-sectional value as a multilingual proxy survives controlled pretraining interventions.

A direct ICLR 2026 prior now owns most of the clean version of that question:

**From Translation to Multilinguality: Revisit the Role of Parallel Data in Multilingual LLM Pretraining**

It compares:

- concatenated parallel pairs, where both translations co-occur inside one context;
- the same sides split into independent samples, removing direct context-local cross-lingual supervision.

The paper covers:

- 18 languages;
- English + one non-English language;
- English + many non-English languages;
- multiple parallel-data ratios;
- English-only Stage 1 → multilingual Stage 2;
- 1.5B and 8B models;
- 100B / 300B-token training regimes.

Its central result is that explicit parallel-format alignment produces large translation gains but only limited gains on broader monolingual/cross-lingual tasks.

Therefore **do not open a workbench whose claim is simply “translation/parallel alignment is not a causal proxy for broader multilingual competence.”** That statement is now directly owned.

### 18.2 The direct prior creates a more interesting literature conflict

Several strong neighboring works report a different broader effect.

#### ACL 2025 — Just Go Parallel

From-scratch 1.1B model trained for 167B tokens.

Non-parallel base data are extremely English-heavy:

- English: 82.35%;
- Indonesian: 0.19%;
- Chinese: 0.12%.

Important controls:

- MULTILINGUAL adds target-language sides without their English counterparts;
- PARALLEL NON-ADJACENT contains the same parallel content but shuffles English counterparts away;
- PARALLEL DISTRIBUTED / LAST co-locate aligned translation pairs.

Adjacent/distributed parallel data strongly improves MT and also improves Indonesian/common-sense performance relative to several matched controls.

This is not a pure “more target-language tokens” result.

#### EMNLP 2025 — TransWebEdu

A single high-quality English corpus is translated into nine languages.

Crucially, the pretraining sequence uses random multilingual documents rather than adjacent parallel pairs. Thus:

> same / highly matched semantic content exists across languages at corpus level, but local token-level alignment is not directly presented in the context.

The resulting 1.3B model is strong on non-English understanding and reasoning.

This separates **high-quality target-language exposure / corpus-level semantic correspondence** from **local adjacency**.

#### 2026 — OpenSeal

Starts from an English-centric OLMo-2 model and adapts it to Southeast Asian languages.

Under a fixed CPT budget, parallel-only training outperforms monolingual-only alternatives on translation and XNLI. This is a different acquisition regime from balanced multilingual pretraining from scratch:

> a strong English competence already exists; the scientific problem is how to attach new language interfaces/capabilities to that existing computation.

#### EMNLP 2025 — multi-way parallel TED2025

Reports broader multilingual gains from aligned multi-way parallel data over unaligned multilingual alternatives across several tasks.

### 18.3 Current reconciliatory hypothesis class — do not assume it

A promising explanation is that the causal role of parallel data depends on **what the target language already knows before the alignment signal arrives**.

Possible regimes:

#### Regime A — target language itself is under-acquired

Examples:
- JGP's Chinese/Indonesian under extreme English dominance;
- English-centric base → new-language CPT (OpenSeal).

Parallel data may simultaneously supply:

1. target-language lexical/syntactic/semantic exposure;
2. high-quality matched semantic content;
3. explicit cross-language alignment;
4. a path into an already strong English computation.

Broader reasoning gains are therefore plausible.

#### Regime B — target languages already have abundant monolingual competence

Examples:
- MONOWEB's balanced EN/DE/ES/FR setup;
- ICLR 2026's richer multilingual mixes.

Once each language already has strong monolingual competence and shared computation, the *incremental* benefit of putting translation counterparts in the same context may collapse mainly to translation/interface mapping.

This would reconcile apparently conflicting papers without declaring any one wrong.

### 18.4 But “resource level matters” alone is not novel

Older cross-lingual transfer work already treats:

- monolingual-resource scarcity;
- parallel-data scarcity;
- task-label scarcity;
- pretrained-language support

as interacting dimensions.

Therefore the contribution cannot be:

> “parallel data helps low-resource languages more.”

That is too old and too broad.

The sharper modern-LLM question is potentially:

> **What prerequisite multilingual competence makes explicit alignment cease to transfer beyond translation?**

or equivalently:

> **Does parallel data change its functional role as a language moves from acquisition to alignment?**

This wording is still exploratory.

### 18.5 Competing explanations that must be separated

The JGP/OpenSeal/TransWebEdu versus MONOWEB/ICLR contrast can arise from multiple causes.

1. **Monolingual exposure / competence level**
   - low target-language competence makes any high-quality bilingual data broadly useful.

2. **Training regime**
   - from-scratch joint acquisition vs continual adaptation to an English core.

3. **Data quality/content**
   - translated high-quality English content may improve reasoning because the content itself is better, not because it is bilingual.

4. **Local alignment**
   - co-occurrence inside one context may create a distinct supervision signal.

5. **Curriculum timing**
   - parallel-last can behave differently from parallel-first/distributed.

6. **Task construction**
   - XNLI/XCOPA/XStoryCloze and other translated benchmarks may reward interface quality differently from native-authored reasoning.

7. **Language family/script/tokenization**
   - JGP uses Chinese/Indonesian; MONOWEB uses Western European languages.

8. **Model state/capacity**
   - English-centric pretrained model vs random initialization; 1B vs 8B.

A strong workbench should manipulate or reuse artifacts to make these explanations compete, rather than averaging papers.

### 18.6 The attractive factorial object

The cleanest conceptual factorial is:

**Axis 1 — target-language competence before explicit alignment**
- weak / newly introduced;
- intermediate;
- already strong.

**Axis 2 — cross-language semantic relationship**
- unrelated monolingual content;
- matched semantic content but not locally adjacent;
- explicit adjacent parallel pairs.

Then evaluate separately:

- target-language LM/understanding;
- translation;
- NLU transfer;
- reasoning;
- possibly factual access.

The scientific quantity is not raw benchmark score.

It is:

> **the marginal causal effect of explicit alignment conditional on prior target-language competence and content matching.**

This is much sharper than “parallel data helps multilinguality”.

### 18.7 Feasibility without giant pretraining

We should first exploit existing trained families:

- JGP public variants/checkpoints;
- MONOWEB released intervention models;
- OpenSeal 1B/7B variants if fully released;
- TransWebLLM/TransWebEdu;
- ICLR-2026 artifacts if public.

A first analysis can ask whether the observed cross-paper pattern already follows a consistent competence-regime gradient.

Only if a missing cell is genuinely decisive should we train a small 100M–1B controlled family.

Potential cheap controlled substrate:
- BabyLM / Bilingual BabyLM;
- False Friends infrastructure.

Do not reproduce 100B–300B token runs.

### 18.8 Hard ownership warning

The ICLR 2026 direct prior is close enough that any workbench must be able to answer:

> **Why isn't this paper simply “From Translation to Multilinguality, but with resource level as another axis”?**

A valid distinction would require showing that:

- prior competence qualitatively changes the *role* of explicit alignment;
- this reconciles currently conflicting strong results;
- the interaction predicts behavior in held-out training regimes/models;
- representation/trajectory evidence explains the transition;
- and ideally yields a simple practical consequence.

If the project only adds low/medium/high resource bins to the ICLR study, kill it.

### 18.9 Current status

The original “translation proxy causal validity” lead is **DEMOTED by direct prior ownership**.

The surviving high-information pressure is:

> **parallel bilingual data appears to have different downstream roles across acquisition regimes: sometimes it improves broader understanding/reasoning, while in already multilingual models its unique explicit-alignment benefit can collapse toward translation. What changes in the model/data regime to cause this role transition?**

This is strong enough for continued search, but not yet authorized as a workbench.


---

## 18. Stronger pressure: from transfer-dominated to self-sufficient language computation

The proxy-validity lead in §17 remains useful, but a deeper object emerged after auditing resource-allocation, low-resource transfer, controlled parallel-data, and mechanistic papers.

### 18.1 The natural question

A multilingual model may perform well in a target language for at least two qualitatively different reasons:

1. it **borrows** knowledge/computation learned primarily from a high-resource language through shared parameters or a dominant-language pivot;
2. it has seen enough target-language data to develop a more **self-sufficient target-language computation**.

The scientific question is not whether transfer exists.

It is:

> **As target-language exposure increases, when and how does computation shift from transfer-dependent to more self-sufficient?**

“Borrowed” and “self-sufficient” are working descriptions, not claims about discrete modules or literal internal translation.

### 18.2 Behavioral parents already imply a regime transition

**EMNLP 2024 Outstanding — When Is Multilinguality a Curse?**

Across >10k small multilingual/monolingual models and 250+ languages, added multilingual data helps low-resource targets but stops helping / can hurt as target-language data becomes abundant.

This establishes resource-dependent cross-language utility, albeit mainly through language-modeling behavior and small models.

**NeurIPS 2025 — CLIMB / Exploring Polyglot Harmony**

Large controlled allocation experiments explicitly model cross-lingual interactions. Their empirical picture is that cross-language transfer is strongest when a target language is scarce and weakens as target-language proportion or total-data scale grows.

This gives a modern decoder-pretraining behavioral parent for a transfer-dominated → increasingly self-dominated regime.

**Apple 2026 mixture-scaling work**

Maps the target-exposure/repetition trade-off across >2,000 runs, showing that scarce target corpora can be repeated much more in mixtures than in single-source training. This strengthens the importance of the acquisition-regime axis but does not tell us what internal computation changes.

### 18.3 Bridge/intervention parents imply the role of cross-language coupling also changes

**LINK (2026)**

When target-language data is deliberately scarce, lexical substitutions in high-resource English text — a very cheap bilingual bridge — improve target scientific reasoning, commonsense and world knowledge.

This is strong evidence that in a data-constrained regime, explicit cross-language coupling can affect **general capability**, not only translation.

**ICLR 2026 From Translation to Multilinguality**

In much richer multilingual regimes, content-matched Standard-vs-Split controls find that explicit adjacent parallel alignment yields very large translation gains but essentially no gain on broad monolingual/cross-lingual evaluation.

The paper sweeps parallel-data percentage, two-stage English→multilingual training and 1.5B→8B scale, but keeps a substantial target-language/multilingual exposure regime and explicitly does not establish what happens when the target language itself becomes severely data constrained.

Taken together, the literature suggests — but does not yet prove — a regime-dependent causal role:

> **cross-language coupling may support broad capability acquisition when the target language cannot learn enough from its own data, yet become increasingly translation/interface-specific once target-language competence is self-supported.**

This must be tested rather than assumed.

### 18.4 Why “parallel data helps low-resource languages” is too weak

That statement is already densely owned.

A worthwhile workbench must distinguish:

- **target-language exposure / quality**;
- **high-resource semantic content**;
- **explicit bilingual correspondence**;
- **shared tokenizer / lexical anchors**;
- **total compute and repetition**;
- **cross-language internal dependence**.

For example:

- TransWebEdu shows translated high-quality target-language content alone can build strong target understanding/reasoning;
- Seto et al. show high-quality auxiliary English helps when target data are scarce;
- data-quality work shows corpus quality itself is a major driver;
- ICLR 2026 shows explicit pair adjacency adds translation even when content is held fixed.

Therefore any regime claim must use matched content/compute controls.

### 18.5 Internal evidence exists, but is not yet connected cleanly to resource regime

**Latent-language comparison**

Llama-2, Swallow and LLM-jp differ strongly in training language composition and in their inferred internal latent language. This supports plausibility but is cross-model/confounded evidence.

**Double Trouble (EMNLP 2026 Main)**

Matched 310M English-only vs bilingual decoders show bilingual exposure leaves systematic middle-layer differences in English contextual representations despite embedding-level alignment.

This proves bilingual training can alter the shared-language computation itself.

**DALI / shared circuits / LinguaMap / routing**

Current causal work localizes middle-layer cross-lingual shared representations/experts and shows that English/shared-space access can repair some non-English failures.

**Token Alignment Heads**

Translation itself has sparse causal heads with a distinct training trajectory, reinforcing that a translation-specific mechanism need not be the same object as broader shared semantic/reasoning computation.

What is still not cleanly established is whether **dependence on shared/dominant-language computation changes as target-language exposure moves through the behavioral transfer→self regime.**

### 18.6 New artifact: Beetle makes the earliest mechanism audit unusually cheap

EMNLP 2026 Beetle releases:

- 285 bilingual + 45 monolingual open models;
- multiple L1s with English L2;
- controlled exposure curricula (balanced/simultaneous/sequential/classroom/late);
- 100M, 2B and up to 24B-token regimes;
- ~30 checkpoints per model.

Its paper targets computational psycholinguistics, not LLM multilingual reasoning.

For us this is useful as a **training-dynamics instrument**:

- test how representation sharing / latent-language dependence changes before, during and after L2 exposure;
- compare curricula with different cumulative target exposure;
- locate candidate transition signatures without first training a model grid.

Do not generalize Beetle-only results to modern LLMs; use them to identify robust diagnostics before external validation.

### 18.7 Candidate measurements of “dependence” (diagnostics, not paper constructs yet)

A workbench should not define self-sufficiency by raw task accuracy.

Possible independent diagnostics:

1. **cross-language causal patch dependence**  
   Does replacing target-language middle-layer state with semantically matched high-resource-language state still rescue errors? Does rescue shrink as target exposure grows?

2. **language-specific direction dependence**  
   Does removing high-resource-language-specific state help/hurt differently across acquisition regimes?

3. **latent-language readout**  
   Does intermediate decoding move from high-resource pivot to target language? Useful but insufficient alone.

4. **shared circuit / routing dependence**  
   Does target performance rely increasingly less on experts/heads identified from the high-resource language?

5. **bridge intervention marginal value**  
   At fixed target content and compute, does adding explicit parallel/lexical bridge affect general target capability only in low-exposure regimes while retaining translation effects later?

6. **counterfactual high-resource ablation**  
   If a shared computation is identified, does disabling the high-resource-associated path selectively hurt low-exposure target models more?

A strong result should survive more than one diagnostic.

### 18.8 Competing explanations to attack before mechanism claims

- **data quality:** high-resource English may simply contain better knowledge;
- **semantic-content coverage:** target corpus may lack task-relevant facts/skills;
- **tokenization:** poor segmentation can mimic low-resource dependence;
- **capacity competition:** multilingual curse rather than “borrowing”;
- **training order / forgetting:** sequential curricula can create apparent pivot dependence;
- **metric language bias:** tasks may reward English-compatible representations;
- **representation readout artifact:** latent-language/probe output need not be causally used.

### 18.9 Top-conference ceiling

Local substrate:

> controlled changes in target-language exposure / acquisition schedule.

Broader object:

> **how cross-lingual transfer changes from an external support mechanism to a less necessary dependency as a target language becomes sufficiently learned.**

Possible field-level consequence:

- explains why bilingual bridges help broad reasoning under some low-resource settings yet look translation-specific in richer settings;
- clarifies when English/shared-space alignment is a genuine capability bottleneck versus an optional shortcut;
- separates translation-specific circuits from general knowledge/reasoning transfer;
- could produce a resource-aware principle for when alignment interventions are useful.

This is materially broader than “find the best language ratio”.

### 18.10 Current ownership boundary

Already owned:

- low-resource languages benefit more from multilingual data;
- optimal language allocation depends on resource level;
- explicit parallel adjacency strongly improves translation;
- lexical bridges help knowledge transfer under target-data scarcity;
- middle layers often show shared cross-language representations;
- bilingual pretraining changes hidden-state geometry;
- latent/internal language differs across existing models.

Not yet identified in this audit:

> a controlled modern decoder study that **tracks causal dependence on high-resource/shared computation across a target-language exposure gradient**, and connects that dependence to the transition from broad transfer benefits to translation-specific alignment benefits.

This remains a provisional novelty statement. Continue adversarial prior search.

### 18.11 Kill conditions

Kill/demote this lead if:

1. a direct prior already measures the same internal-dependence transition under matched resource ratios;
2. representation/patching dependence does not systematically change with resource/exposure despite behavioral transfer gradients;
3. all effects reduce to tokenizer/data-quality/content-coverage differences;
4. only tiny Beetle/BabyLM models exhibit the mechanism and it disappears in public 1B–8B evidence;
5. confirming the mechanism requires foundation-model-scale pretraining rather than existing artifacts + modest controlled runs;
6. the final contribution collapses to another data-allocation scaling law.

### 18.12 Earliest non-training reconnaissance

Before authorizing our own pretraining:

1. **Beetle trajectory audit**  
   pick 2–3 language pairs/curricula with large exposure contrast; compute middle-layer language identity/alignment and simple causal cross-language patching over checkpoints.

2. **existing-model sanity contrast**  
   Llama-2 vs Swallow vs balanced LLM-jp only as an external qualitative check, not causal evidence.

3. **Double Trouble reproduction/readout extension**  
   if released checkpoints/code are available, test whether bilingual-induced deep-state differences correlate with target-resource/exposure schedule in any released family.

4. **behavior linkage**  
   on Beetle models, add small multilingual semantic/NLU transfer tasks beyond the original reading-time/grammar evaluation; ask whether internal-dependence changes predict transfer gains.

Only if a clear gradient exists should we train a matched ratio × bridge factorial model family.
