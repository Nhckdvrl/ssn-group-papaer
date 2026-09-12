# 2026-09-12 — Bottleneck Migration / Contradiction / Workflow / Destructive-Control Search

**Target:** ACL / EMNLP / NAACL Main  
**Starting HEAD:** `0b776fc55847144323df6533981eddcecf2a9d77`  
**Outcome:** **0 new survivors. No compute authorized.**

This round follows the current `main` rules, not earlier prompts. Before searching, the current state/rules were checked in `CURRENT_SEARCH.md`, `RESEARCH_TOPIC_SEARCH.md`, `RESEARCH_TOPIC_SELECTION.md`, `RESEARCH_EXECUTION.md`, `TOPIC_SEARCH_PLAYBOOK.md`, `failed/KILLED_LEDGER.md`, recent `search_rounds/`, and current `candidates/` / `good/` packages.

The round deliberately prioritized:

1. old bottleneck assumption -> modern bottleneck migration;
2. repeated side anomaly across independent papers;
3. same-quantity contradiction between strong papers;
4. real workflow -> natural outcome/counterfactual;
5. destructive evaluator/probe validation.

Hard gates used throughout:

- anti-resurrection before promotion;
- SAME-QUANTITY CHECK before claiming a reversal/contradiction;
- DIRECT GOLD before treating a label/outcome as the target quantity;
- successful-result test before pilot;
- strong/near-null/heterogeneous outcome story before pilot;
- no compute merely because a pilot is cheap.

---

# A. New topic-provenance patterns learned this round

Only patterns that add something beyond the already-recorded award-provenance notes are included here.

## A1. Matched nuisance-axis isolation

### Paper

Levy, Jacoby & Goldberg, ACL 2024 Outstanding, **Same Task, More Tokens: the Impact of Input Length on the Reasoning Performance of Large Language Models**  
https://aclanthology.org/2024.acl-long.818/

### Scientific ancestry

Long-context work often confounds longer inputs with harder tasks, more evidence, different examples, or different information locations.

### Immediate pressure

Models advertise very large technical context windows, but that does not identify whether *length itself* degrades reasoning.

### Origin trigger

A nuisance variable that was routinely entangled with task difficulty.

### First decisive operation

Create multiple versions of the **same sample**, hold the required reasoning and answer fixed, and vary only padding length/type/location.

### Why both outcomes matter

- degradation -> context length itself is a causal limitation well below the technical maximum;
- invariance -> many prior long-context failures must come from task/evidence confounds rather than length per se.

### Transferable generator

> When a community explanation depends on a variable that normally co-varies with difficulty, search for a natural or exact matched design that changes only that variable while preserving the answer-bearing object.

This is stronger than generic `X != Y`: the research question comes from a **specific confounded causal attribution**.

---

## A2. Response-process validity before trait inference

### Paper

Röttger et al., ACL 2024 Outstanding, **Political Compass or Spinning Arrow? Towards More Meaningful Evaluations for Values and Opinions in Large Language Models**  
https://aclanthology.org/2024.acl-long.816/

### Scientific ancestry

Human questionnaires were imported into LLM evaluation and their multiple-choice outputs were interpreted as model values/opinions.

### Immediate pressure

The downstream claim is about a latent trait, but the observed answer may depend on how the model is forced through an artificial response format.

### Origin trigger

A mature measurement instrument being reused under a new response process.

### First decisive operation

Ask semantically equivalent questions under forced-choice, differently forced, paraphrased, and open-ended response conditions.

### Why both outcomes matter

- invariance -> the imported instrument gains evidence that it measures a stable model property;
- sensitivity -> published trait claims become under-identified because the measurement procedure itself changes the response.

### Transferable generator

> Before trusting a human/legacy instrument on LLMs, test whether its conclusion survives changes in the response process that should not change the underlying construct.

This should only generate a topic when the downstream construct claim is consequential and the response-process intervention is clearly construct-preserving.

---

## A3. Operational folklore -> explicit estimand + statistical guarantee

### Paper

Klie et al., ACL 2024 Outstanding, **On Efficient and Statistical Quality Estimation for Data Annotation**  
https://aclanthology.org/2024.acl-long.837/

### Scientific ancestry

Annotation projects routinely inspect a subset of labels to estimate quality.

### Immediate pressure

Subset sizes were often chosen without statistical power/precision justification, so a common production practice lacked a defensible inferential target.

### Origin trigger

A ubiquitous workflow step governed by convention rather than an explicit estimand.

### First decisive operation

Write the desired error-rate/acceptance guarantee mathematically, then derive the sample size needed for that guarantee.

### Why both outcomes matter

- current samples too small -> quality claims are unreliable;
- current samples larger than needed -> the same guarantee can be obtained more cheaply.

### Transferable generator

> Search ordinary NLP workflows for decisions made by rule of thumb; ask what quantity the decision is supposed to estimate and whether the current procedure has any guarantee for it.

This is useful because it can yield a paper without betting on a large model effect.

---

## A4. Conflicting evidence as an identification design for hidden source weighting

### Paper

Li et al., EMNLP 2024 Outstanding, **Formality is Favored: Unraveling the Learning Preferences of Large Language Models on Data with Conflicting Knowledge**  
https://aclanthology.org/2024.emnlp-main.304/

### Scientific ancestry

Pretraining corpora contain conflicting statements, but when sources agree it is hard to identify what source properties the model trusts.

### Immediate pressure

A model can learn the same final fact for many reasons; agreement hides weighting preferences.

### Origin trigger

Natural conflict suggests an intervention that makes otherwise latent source preference identifiable.

### First decisive operation

Present conflicting knowledge while manipulating incidental source features such as formality/spelling/majority consistency.

### Why both outcomes matter

- source-feature preference -> reveals a hidden data-weighting bias with training consequences;
- no preference -> rules out a commonly suspected shortcut and constrains explanations of conflict resolution.

### Transferable generator

> If a latent preference cannot be seen when evidence agrees, create or locate cases where equally targeted evidence conflicts, then vary one source property at a time.

The key is that the manipulated evidence supports the **same proposition**; otherwise SAME-QUANTITY fails.

---

## A5. New construct only after independent natural validation

### Paper

Wu et al., EMNLP 2024 Outstanding, **Which questions should I answer? Salience Prediction of Inquisitive Questions**  
https://aclanthology.org/2024.emnlp-main.1114/

### Scientific ancestry

Many questions can be evoked from a text, but linguistic theory did not directly specify which are worth answering first.

### Immediate pressure

Question generation creates a huge candidate space; a proposed notion of “salience” would be weak if it existed only as a new annotation label.

### Origin trigger

A practical selection problem plus a hypothesized discourse quantity.

### First decisive operation

Human salience annotation, followed by independent checks that salient questions are more likely to be answered later in the same article and that answering them improves preferred summaries.

### Why both outcomes matter

The important provenance lesson is not the exact construct, but the **triangulation requirement**: a new latent label becomes scientifically stronger when it predicts naturally occurring downstream behavior that was not used to define the label.

### Transferable generator

> If a topic requires introducing a new quantity, demand an independent natural outcome that the quantity predicts before allowing the quantity to become the paper’s scientific object.

This is a useful antidote to abstract-distinction generation.

---

# B. Investigated hooks

## B1. AMR parsing bottleneck migration: semantic concept/alignment -> structured-output realization

**Hook:** Has the AMR bottleneck moved from identifying/aliging concepts to correctly realizing a formal graph under decoder LLMs?

**Origin:** EMNLP 2017 explicitly called concept identification and alignment AMR parsing bottlenecks; modern LLMs make structured-output/graph errors.  
Older: https://aclanthology.org/D17-1129/  
Modern: https://aclanthology.org/2026.lrec-1.915/

**Why interesting:** same AMR gold graph allows unusually clean decomposition of error types, so SAME-QUANTITY is much better than in many migration ideas.

**Strongest owner:** *Context Is (Almost) Everything: Llama-3 on Structured Output and AMR Parsing* (LREC 2026) already performs fine-grained analysis over semantic phenomena, graph properties and complexity, and explicitly reports frequent structured-output errors.

**Fatal issue:** the modern error regime is already a direct paper object. A new “bottleneck migration” paper would mostly repackage its analysis across more models. Near-null leaves only an updated AMR error breakdown.

**Verdict:** `NO`.

---

## B2. Text-to-SQL schema linking: old crux -> modern foundation-model bottleneck migration

**Hook:** Is schema linking still the component that controls end-to-end Text-to-SQL performance under modern LLMs?

**Origin:** 2020 work framed schema linking as the crux of Text-to-SQL; modern LLMs radically change semantic parsing capability.

**Why interesting:** a genuine migration would redirect method effort away from a historically dominant component.

**Strongest owner:** 2025 Text-to-SQL work such as LinkAlign still explicitly treats schema linking as a critical bottleneck, including realistic large/multi-database settings.

**Fatal issue:** same-quantity successor evidence does not create reversal pressure; it explicitly **continues the old bottleneck claim**. Another model sweep is an update, not a new scientific parent.

**Verdict:** `NO`.

---

## B3. FrameNet frame identification: old OOD bottleneck -> modern LLM regime

**Hook:** Does frame identification remain the dominant OOD bottleneck when frame semantics are handled by instruction/foundation models?

**Origin:** Hartmann et al., EACL 2017 identified frame identification as the major OOD FrameNet SRL bottleneck.  
https://aclanthology.org/E17-1045/

**Why interesting:** the old claim directly guided where SRL methods spent effort.

**Strongest owner:** 2025–2026 work directly studies frame identification / frame-semantic knowledge in LLMs, including *Do LLMs Encode Frame Semantics? Evidence from Frame Identification* and ACL 2026 frame-semantic injection.

**Fatal issue:** current literature already makes modern frame identification a central object. The remaining “which stage now dominates?” question is local error analysis, not an open parent.

**Verdict:** `NO`.

---

## B4. Entity linking: candidate generation -> disambiguation / generation under LLMs

**Hook:** Did modern generative/retrieval LMs eliminate the historical candidate-generation bottleneck and move the limiting factor elsewhere?

**Origin:** classical EL pipelines divide candidate generation and disambiguation; foundation models change both retrieval and semantic matching.

**Why interesting:** an actual stage migration would affect both architecture and benchmark interpretation.

**Strongest owner:** NAACL 2024 GenDecider, EMNLP 2025 AELC/RAED and EACL 2026 unified retriever-reranker work already directly rework candidate generation/retrieval/disambiguation in the modern regime.

**Fatal issue:** the migration itself is already the active methodological axis. No unowned scientific relation remains at Main scale.

**Verdict:** `NO`.

---

## B5. Quotation attribution: unresolved coreference as old bottleneck -> modern long-context attribution

**Hook:** Has modern long-context modeling removed coreference as the limiting factor for quotation attribution?

**Origin:** quotation-attribution datasets/pipelines repeatedly report long-range anaphora/coreference errors; newer systems reach high attribution accuracy.

**Why interesting:** this initially looks like a clean old-bottleneck-to-modern-model question.

**Strongest owner:** 2026 quotation-attribution work already uses long-range anaphora/coreference signal directly and reports very strong modern performance.

**Fatal issue:** anti-resurrection. This is the same scientific parent as the already-rejected **coreference bottleneck migration** route. A new task wrapper does not create qualitatively new leverage. It also risks another construct bridge between coreference annotations and attribution errors.

**Verdict:** `NO — no new ID; resurrection of prior coreference-bottleneck route`.

---

## B6. Dialogue summarization: omission bottleneck -> hallucination/unsupported inference bottleneck

**Hook:** Have modern LLM summarizers moved from omitting salient content to adding unsupported content?

**Origin:** ACL 2023 and related dialogue-summarization work analyzed omission; modern LLM work emphasizes factuality/hallucination.

**Why interesting:** if the dominant error direction reversed, evaluation and mitigation priorities should change.

**Strongest owner:** 2024–2025 dialogue-summary evaluation frameworks already evaluate omissions and factual/unsupported errors together.

**Fatal issue:** **K175-style construct mismatch.** “Omission” gold and “unsupported inference/hallucination” gold are not the same estimand. Without the same outputs annotated for both quantities, apparent migration is not identifiable. Once such paired annotation is introduced, current factuality/coverage work already closely owns the object.

**Verdict:** `NO`.

---

## B7. Implicit discourse relation classification: data scarcity -> modern reasoning bottleneck

**Hook:** If annotation scarcity was historically the main limitation, what now controls implicit discourse relation performance under LLMs?

**Origin:** 2019-era work explicitly describes training-data shortage as a principal bottleneck.

**Why interesting:** implicit relations are a case where pretraining could plausibly erase the old resource bottleneck.

**Strongest owner:** ACL/EMNLP 2025 and EACL 2026 work already probes LLM discourse labels, circuits, label semantics, and modern relation performance.

**Fatal issue:** direct modern ownership plus unstable cross-framework label semantics. A migration claim would require comparing quantities whose ontology/annotation schemes do not cleanly align.

**Verdict:** `NO`.

---

## B8. Argument mining: knowledge/resource bottleneck -> dataset/ontology generalization bottleneck

**Hook:** Did LLM world knowledge remove the old external-knowledge/resource bottleneck, leaving dataset-specific argument ontology as the new limiter?

**Origin:** older argument-mining work explicitly discusses knowledge/language-resource bottlenecks.

**Why interesting:** ACL 2025 work reports that models can learn datasets rather than arguments, suggesting a modern failure mode qualitatively different from missing external knowledge.

**Strongest owner:** recent broad LLM argumentation and cross-dataset argument-mining papers already centralize generalization and dataset-specificity.

**Fatal issue:** “argument” labels across datasets are not a stable shared estimand; the apparent migration relies on cross-dataset construct equivalence. It also requires substantial data archaeology before the scientific quantity is identified.

**Verdict:** `NO`.

---

## B9. DocRE: long-range structural aggregation -> multi-label / positive-negative decision bottleneck

**Hook:** Has the DocRE bottleneck migrated from aggregating non-local evidence to deciding which relations actually hold for an entity pair?

**Origin:** ACL 2020 DocRE methods foregrounded non-local information aggregation and document structure as core challenges.

**Why interesting:** this is one of the cleaner examples where the modern LLM error profile visibly differs from older SLMs.

**Strongest owner:** NAACL 2025 Main, **Rethinking the Role of LLMs for Document-level Relation Extraction**, already makes the modern regime shift central: LLMs struggle with multi-label prediction, while SLMs and LLMs show different `NA`/positive-relation tendencies.  
https://aclanthology.org/2025.naacl-long.319/

**Fatal issue:** the strongest “migration” observation is already the central empirical claim of a Main paper and motivates its hybrid refiner. ACL 2026 further studies threshold/imbalance bias. Rebranding this literature as bottleneck migration is insufficient significance.

**Verdict:** `NO`.

---

## B10. OpenIE / generative IE: ordering and autoregressive error accumulation

**Hook:** Did modern decoder LLMs eliminate the old ordering/error-accumulation penalty in set-valued information extraction?

**Origin:** MacroIE (EMNLP 2021), OK-IE (Findings EMNLP 2023), set-learning IE (EMNLP 2023), and permutation-aware decoding work all identify harmful ordering / autoregressive accumulation.

**Why interesting:** foundation models are much stronger generators, so an old architecture-level limitation could in principle disappear.

**Strongest owner:** the 2023–2024 generative IE line already directly studies unordered targets, order bias, and permutation/error accumulation; modern OpenIE surveys still treat it as an active issue.

**Fatal issue:** direct parent is mature and continuous through the LLM transition. No independent modern pressure suggests an unowned reversal.

**Verdict:** `NO`.

---

## B11. Semantic parsing: paired-program annotation scarcity -> modern LLM regime

**Hook:** Is expensive utterance-program annotation still the factor that controls semantic parsing after code-capable LLMs and few/zero-shot prompting?

**Origin:** NAACL 2021 and related work explicitly describe paired program annotation as a major bottleneck.

**Why interesting:** if the bottleneck disappeared, the field’s data-collection assumptions would change substantially.

**Strongest owner:** NAACL 2022 onward code-LM/few-shot/zero-shot semantic parsing, and ACL 2025 SPOT-style work, directly target reducing task-specific annotation and still describe data/transfer as central.

**Fatal issue:** successor papers already ask the modern version of the question. Any residual “how much annotation is still needed?” study is a sample-efficiency cell, not a new Main-level parent.

**Verdict:** `NO`.

---

## B12. Text simplification: parallel-data scarcity -> meaning/readability tradeoff

**Hook:** Once LLMs remove much of the parallel-data bottleneck, does the true limiting factor become preserving meaning while increasing readability?

**Origin:** older lexical/text simplification work frequently foregrounded parallel-data scarcity.

**Why interesting:** this looks like a real migration from resource acquisition to output-quality control.

**Strongest owner:** TACL 2024 directly evaluates meaning preservation through reading comprehension; NAACL 2025 evaluates document-level metrics and error sensitivity; 2025–2026 simplification work explicitly frames the simplicity/meaning tradeoff.

**Fatal issue:** modern literature already owns the new bottleneck and its evaluation. Human readability/meaning judgments are also not a single exact gold quantity that allows a clean historical error-budget comparison.

**Verdict:** `NO`.

---

## B13. Event extraction: argument identification -> position/boundary/cross-event confusion

**Hook:** Has event extraction shifted from argument extraction as the main bottleneck to exact boundary/position/cross-event decision errors under LLMs?

**Origin:** 2022–2023 work explicitly labels event argument extraction as a bottleneck for end-to-end event extraction.

**Why interesting:** same event datasets could in principle support stage-wise error accounting.

**Strongest owner:** 2024–2025 LLM event-argument work already explicitly reports positional bias, exact argument-boundary errors, feature forgetting and cross-event argument confusion.

**Fatal issue:** current successor literature already enumerates and attacks the new error sources. Remaining contribution is an error-budget synthesis.

**Verdict:** `NO`.

---

## B14. Visually rich document IE: task-specific annotation cost -> prompt/template diversity

**Hook:** Did foundation models remove the old “thousands of labeled documents per new type” bottleneck and replace it with adaptation to document/template diversity?

**Origin:** EMNLP 2023 Main selective-labeling work explicitly calls labeling new document types a key bottleneck.

**Why interesting:** this is a real production cost that guided document-IE method design.

**Strongest owner:** 2024 LayoutLLM/few-shot VRDU/K2Q-style papers directly reduce task-specific labeling and identify prompt/template data limitations.

**Fatal issue:** the modern bottleneck is already the organizing axis of successor methods; the only remaining novelty is an historical learning-curve comparison.

**Verdict:** `NO`.

---

## B15. Fact verification: evidence retrieval as old/new bottleneck

**Hook:** Has LLM reasoning reduced evidence retrieval from the primary fact-checking bottleneck, or does retrieval still dominate?

**Origin:** fact-verification pipelines have long treated evidence retrieval as a central bottleneck.

**Why interesting:** reasoning/web-search LLMs could plausibly move the limiting stage from retrieval to verification.

**Strongest owner:** 2024 CFR still explicitly calls retrieval a bottleneck; ACL 2026 political fact-checking finds reasoning gives little gain while curated context gives a very large gain; 2026 large-table fact verification again identifies retrieval as the primary bottleneck.  
https://aclanthology.org/2024.fever-1.28/  
https://aclanthology.org/2026.findings-acl.1467/

**Fatal issue:** same-quantity modern evidence mostly says the bottleneck **persists**. There is no credible migration pressure, and the area is heavily occupied by RAG/retrieval work.

**Verdict:** `NO`.

---

## B16. P3 contradiction: global temporal consistency helps vs consistency does not imply accuracy

**Hook:** When does making temporal-relation predictions globally consistent actually improve relation accuracy?

**Origin:** structured TRE historically uses global constraints; BioNLP 2024 shows that predictions can be made temporally consistent yet remain inaccurate; EMNLP 2025 Main reports gains from complete temporal-graph generation plus constraint optimization.

**Why interesting:** this is a genuine same-object tension: both accuracy and temporal consistency are evaluated on temporal-relation graphs, rather than on unrelated metrics.

**Strongest owner:** INLG 2025, **Can LLMs Help Encoder Models Maintain Both High Accuracy and Consistency in Temporal Relation Classification?**, already centers exactly the accuracy-consistency tradeoff and finds LLM/global consistency can improve consistency at a cost to accuracy and does not beat a simple confidence-based cycle resolver. BioNLP 2024 also explicitly asks whether resolving inconsistencies improves accuracy.  
https://aclanthology.org/2025.inlg-main.41/  
https://aclanthology.org/2024.bionlp-1.6/  
https://aclanthology.org/2025.emnlp-main.1601/

**Fatal issue:** the apparent contradiction is already a direct research question. A narrower hidden condition such as graph density, cycle topology, or confidence margin would be a local mechanism cell unless it produced a new structural theory. That route would also be at high risk of K181-style narrowing.

**Verdict:** `NO`.

---

## B17. P3/P2 contradiction: LLM relation-existence decisions are conservative vs liberal

**Hook:** Why do some LLM relation-extraction studies find systematic `NO_RELATION` conservatism while DocRE work reports LLMs tending to predict relations for nearly all entity pairs?

**Origin:** ACL 2025 Findings **Conservative Bias in Large Language Models: Measuring Relation Predictions** reports `NO_RELATION` conservative bias; NAACL 2025 Main DocRE reports the opposite polarity relative to SLMs.

**Why interesting:** if both measured the same binary “does any relation hold?” decision, a hidden condition could unify a striking cross-paper contradiction.

**Strongest owner:** *Conservative Bias* already studies the behavior across multiple prompts, datasets and relation types; the DocRE paper centralizes its positive-relation bias observation.

**SAME-QUANTITY CHECK:** **fails at the intervention/interface level.** The conservative-bias work deliberately includes cases where the available relation choices do not contain an exact appropriate relation, making `NO_RELATION` a least-wrong option. DocRE is multi-label document-level prediction over a fixed ontology/entity-pair candidate regime. Unit, choice-set completeness and decision protocol differ.

**Immediate boring explanation:** constrained single-label choice with missing/ill-fitting labels vs multi-label candidate extraction under heavy class imbalance.

**Late-death issue:** to become Main, the topic would need a robust crossover/reversal after standardizing these interfaces. If the polarity disappears after standardization, the paper collapses to “different prompts/tasks induce different class priors.” That is K180-style outcome fragility.

**Verdict:** `NO`.

---

## B18. P2 repeated anomaly: LLMs underperform specialized encoders on closed structured relation tasks

**Hook:** Across SRL, TRE, DocRE and some zero-shot RE settings, why can strong generative LLMs lag much smaller task-specific encoders on closed structured prediction?

**Origin:** repeated side observations across several 2024–2026 papers.

**Why interesting:** the pattern is broad and visually striking.

**Strongest owner:** modern generation-vs-discrimination / structured-generation literature already studies the mismatch; this repository has also explicitly rejected **“generation destroys an already-good decision structure”** in a prior search round.

**Fatal issue:** anti-resurrection. The shared anomaly does not create a new scientific object; it collapses into the established generation–discrimination/readout parent. Narrowing to a specific relation task would not be qualitatively new leverage.

**Verdict:** `NO — duplicate of an already rejected parent`.

---

## B19. P4 real workflow: code-review comment -> developer acceptance / later code revision

**Hook:** Do automatic code-review-comment scores identify comments that developers actually act on in real review workflows?

**Origin:** real review systems naturally log suggested comments, reviewer acceptance, `fixed/wontFix`, and subsequent patch revisions.

**Why interesting:** this initially appears to provide exactly the kind of natural downstream outcome that benchmark-only evaluation lacks.

**Strongest owners:**

- NAACL 2025 Main CRScore builds a reference-free code-review-comment quality metric and human quality corpus: https://aclanthology.org/2025.naacl-long.457/
- FASE 2025 DeepCRCEval directly attacks text-similarity evaluation and evaluates task-relevant comment quality;
- RevMate live deployment reports acceptance and later revision behavior in Mozilla/Ubisoft;
- EASE 2026 industrial work directly evaluates automated judges against `fixed/wontFix` labels and analyzes their limitations.

**DIRECT GOLD audit:** developer action is direct gold **only for action/adoption under that workflow**. It is **not direct gold for objective comment quality**, because acceptance/fixing is affected by priorities, timing, organizational constraints and reviewer context; the 2026 industrial study explicitly makes this point.

**Fatal issue:** if the estimand is quality, K175-style construct mismatch; if the estimand is developer actionability, the direct modern parent already exists. Natural workflow therefore does not rescue novelty.

**Verdict:** `NO`.

---

## B20. P4 real workflow: Wikipedia edit -> survival/revert as natural quality outcome

**Hook:** Can modern LLM edit-quality/evaluator scores predict whether a Wikipedia edit survives community review?

**Origin:** Wikipedia has complete revision histories, reverts, patrolling outcomes and production edit-quality systems.

**Why interesting:** massive natural process data, exact timestamps, and no LLM-generated gold are available.

**Strongest owner:** ORES/Revert Risk has long treated eventual revert as an operational prediction target; Wikimedia explicitly distinguishes `reverted`, `damaging` and `goodfaith` because revert is not the same scientific quantity as damage/quality. ACL 2019 StRE also predicts edit quality from edit text.

**DIRECT GOLD audit:** revert is direct gold for **survival/revert**, not for true edit quality. Wikimedia documentation explicitly notes that edits may be reverted for reasons other than damage and therefore maintains separate manually labeled damaging/good-faith constructs.

**Fatal issue:** if the target is revert, the problem is old and operationally deployed; if the target is quality, the natural outcome is a proxy and fails direct-gold identity. Adding a modern LLM is model replacement, not novelty.

**Verdict:** `NO`.

---

## B21. P5 destructive evaluator check: text-simplification meaning-preservation metrics

**Hook:** If we selectively corrupt facts/meaning while preserving fluency and much lexical content, do simplification metrics actually respond to the lost meaning?

**Origin:** simplification evaluation depends on automatic meaning-preservation/readability metrics.

**Why interesting:** destructive controls are stronger than simple metric-human correlation when a metric is supposed to track semantic preservation.

**Strongest owner:** MeaningBERT/meta-evaluation already uses sanity checks; TACL 2024 evaluates meaning preservation via downstream reading comprehension; NAACL 2025 explicitly evaluates metric sensitivity/robustness to simplification errors.  
https://aclanthology.org/2024.tacl-1.24/  
https://aclanthology.org/2025.naacl-long.327/

**Fatal issue:** the evaluator-validity parent is directly occupied, including sensitivity tests and human downstream consequences. A new corruption taxonomy would be component overlap without a new consequence.

**Verdict:** `NO`.

---

## B22. P5 destructive evaluator check: temporal consistency as a diagnostic

**Hook:** If a temporal graph is repaired to remove cycles without changing the underlying mistaken event ordering, does a consistency metric falsely indicate improvement?

**Origin:** consistency is frequently treated as a desirable diagnostic for temporal extraction.

**Why interesting:** this is a clean destructive/projection test because one can improve the diagnostic while holding or worsening truth accuracy.

**Strongest owner:** BioNLP 2024 already performs essentially this decisive operation and shows that predictions can become consistent while remaining inaccurate; INLG 2025 directly analyzes the accuracy-consistency tradeoff.

**Fatal issue:** decisive destructive evidence already exists. No new paper identity remains.

**Verdict:** `NO`.

---

# C. Survivors

## **0 survivor**

No hook in this round satisfies all of:

- independently valuable question before results;
- same-quantity historical/modern comparison or contradiction;
- DIRECT GOLD for the load-bearing estimand;
- no direct modern owner;
- successful-result inference that reaches beyond error analysis / “another bias”;
- meaningful near-null paper;
- independently interpretable heterogeneous outcome;
- Main-level natural growth path without post-hoc story mutation.

**No new candidate directory was created and no compute is authorized.**

---

# Round-level lessons

1. **The hardest part of P1 is not finding old bottlenecks; it is finding a modern pressure that is both SAME-QUANTITY and not already owned.** In many mature NLP tasks, 2024–2026 successor papers have already explicitly named the new bottleneck.
2. **A visible change in error vocabulary is not bottleneck migration.** `long-range structure -> multi-label`, `data scarcity -> quality tradeoff`, or `omission -> hallucination` only works if both eras expose a common end-to-end estimand and the stage contributions are identifiable.
3. **Contradictions often disappear at the interface layer.** Before theorizing a hidden model property, compare unit of prediction, candidate-set completeness, label cardinality, gold ontology, and decision protocol.
4. **Natural workflow outcomes must be named literally.** `reverted`, `fixed`, `accepted`, and `clicked` can be excellent direct gold for those actions while being poor gold for `quality`, `correctness`, or `preference`.
5. **Destructive-control ideas are especially prone to direct collision.** Before designing the corruption, search whether the target evaluator’s own literature already performs sensitivity/sanity tests that implement the same causal operation.
6. **Award-paper provenance suggests a stronger next search tactic than another broad task sweep:** locate a consequential NLP inference that currently depends on a confounded variable, imported instrument, or rule-of-thumb workflow, then look for an exact matched/natural identification design. This has better outcome robustness than searching for a large reversal.
