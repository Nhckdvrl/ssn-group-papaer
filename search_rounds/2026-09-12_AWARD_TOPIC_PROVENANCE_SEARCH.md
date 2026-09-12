# 2026-09-12 — Award-Topic Provenance Search

**Target:** ACL / EMNLP / NAACL Main  
**Search correction:** avoid using fashionable areas as the default search space. Study not only what strong/award papers contain, but **where their research questions came from**; transfer those origin mechanisms into quieter domains.  
**Current exclusions/prior:** no new speech/audio; avoid pure linguistic competence tests; strongly deprioritize generic Agent / long-term memory / RAG / RL / judge and framework/harness-dependent questions.

## 1. What strong papers were born from

The useful lesson is not “copy the topic of a Best Paper.” Strong papers repeatedly arise from older scientific pressure that predates the current fashion cycle.

### A. Classical problem or law + a new measurement that makes it answerable

**Example:** Nagata & Tanaka-Ishii, ACL 2025, *A New Formulation of Zipf's Meaning-Frequency Law through Contextual Diversity*.  
https://aclanthology.org/2025.acl-long.744/

The starting point is an old empirical law. The bottleneck is that “number of meanings” is hard to define/measure broadly. Contextualized LM vectors provide a new operationalization through contextual diversity, allowing the old law to be tested in regimes that were previously difficult.

**Transferable generator:** find an old scientific relation whose important variable was historically hard to observe; ask whether modern representations/data/interventions finally make the quantity identifiable.

### B. Classical theoretical debate + a genuinely new model regime

**Example:** Kasa et al., EMNLP 2025 Outstanding, *Generative or Discriminative? Revisiting Text Classification in the Era of Transformers*.  
https://aclanthology.org/2025.emnlp-main.486/

The question comes from Efron's 1975 generative-vs-discriminative tradeoff. Transformers change the regime enough that the classical answer need not transfer mechanically.

**Transferable generator:** revisit an old debate only when the new regime changes a load-bearing assumption, not merely because “LLMs did not exist then.”

### C. Important causal estimand + an identification bottleneck + imported mature design

**Example:** Lesci et al., ACL 2024 Best, *Causal Estimation of Memorisation Profiles*.  
https://aclanthology.org/2024.acl-long.834/

Memorisation already had a causal definition, but its counterfactual was expensive/inaccessible. The paper imports difference-in-differences from econometrics to make the estimand practically measurable.

**Transferable generator:** search for quantities that everyone says are causal but are evaluated by weak proxies because the counterfactual is hard; import a mature identification design only if it changes what can be learned.

### D. Strong public/theoretical claim + surprisingly weak direct evidence

**Example:** Kallini et al., ACL 2024 Best, *Mission: Impossible Language Models*.  
https://aclanthology.org/2024.acl-long.787/

A prominent claim existed that LLMs can learn possible and impossible languages equally well, but direct experimental support was thin. The paper builds a decisive controlled comparison instead of inventing a new fashionable task.

**Transferable generator:** find important claims that are repeatedly cited or assumed but whose decisive experiment was never actually run.

### E. Stable practical anomaly + no satisfactory explanation

**Example:** Li & Cotterell, ACL 2026 Best, *Characterizing the Expressivity of Local Attention in Transformers*.  
https://aclanthology.org/2026.acl-long.1739/

Local attention is normally framed as an efficiency restriction, yet it can improve model quality. The paper starts from that counterintuitive engineering observation and gives a formal expressivity account, then corroborates it empirically.

**Transferable generator:** look for robust “a restriction/removal/simplification helps” facts whose obvious explanations fail and where a stronger theory can make new predictions.

### F. Cheap destructive intervention → hard anomaly → explanation

**Example:** Takeshita et al., EMNLP 2025 People's Choice, *Randomly Removing 50% of Dimensions in Text Embeddings has Minimal Impact...*.  
https://aclanthology.org/2025.emnlp-main.1410/

The entry experiment is extremely cheap: remove dimensions. The surprising robustness survives broad testing, obvious explanations such as ineffective space/redundancy/outliers do not fully account for it, and the paper follows the anomaly into degrading dimensions.

**Transferable generator:** cheap intervention first, but only continue when the effect is large, reproducible, survives obvious controls, and exposes a deeper scientific object.

### G. Mature theory outside NLP + modern behavior with a consequential mismatch

**Examples:**
- Sivaprasad et al., ACL 2025, *A Theory of Response Sampling in LLMs: Part Descriptive and Part Prescriptive*: https://aclanthology.org/2025.acl-long.1454/
- Shen et al., EMNLP 2025 Outstanding, *Mind the Value-Action Gap*: https://aclanthology.org/2025.emnlp-main.154/

The origin is not “LLM behavior is weird.” The papers borrow an established distinction from human decision/social science—descriptive vs prescriptive normality, or stated values vs action—and show why the distinction matters for modern model behavior.

**Transferable generator:** import a mature distinction only when it changes a consequential modern inference or action; avoid turning this into a pure psychology/linguistics competence test.

### H. Convenient field assumption / proxy → consequential construct correction

**Examples:**
- Wang et al., ACL 2025, *Fairness through Difference Awareness*: https://aclanthology.org/2025.acl-long.341/
- Zhou et al., NAACL 2025, *REL-A.I.*: https://aclanthology.org/2025.naacl-long.556/

One attacks a mathematically convenient difference-unaware fairness assumption; the other argues that model calibration/language quality are not enough when the real target is human reliance.

**Transferable generator:** identify a quantity the field measures because it is easy, then ask whether the scientifically consequential target is different enough to change conclusions.

### I. Real professional workflow → natural question and natural data

**Example:** Spangher et al., EMNLP 2024, *Do LLMs Plan Like Human Writers?*  
https://aclanthology.org/2024.emnlp-main.1216/

The paper starts from an actual journalist workflow—choosing angles and contextualizing press releases—and assembles 250k press releases / 650k articles. The scientific target is defined by real work rather than by an invented benchmark.

**Transferable generator:** look at mature human workflows with recorded intermediate/final products; the process itself may provide both the question and natural gold.

### J. Mature cognitive theory + a simple neural operationalization → unexpected representation consequence

**Example:** Xu, Dillon & Futrell, ACL 2026 Best, *Memory efficiency and resource-rational encoding in sentence processing*.  
https://aclanthology.org/2026.acl-long.1550/

The source is resource-rational working-memory theory, not the current Agent-memory trend. A simple representational-noise intervention operationalizes limited precision; beyond better human RT prediction, the model develops more categorical/compressed encoding.

**Transferable generator:** look for a mature theory that gives a precise intervention and a non-obvious representation-level prediction.

## 2. Immediate search consequence

A useful strong-paper calibration now asks **“what generated this paper?”** before asking “what can we extend?” Search should transfer the *origin mechanism*—measurement bottleneck, weakly evidenced claim, hidden assumption, robust anomaly, identification problem, natural workflow—to a different and quieter object.

Fashion itself is a weak origin. If a question exists mainly because Agent/RAG/RL/memory/judge is popular, or if its identity changes with a harness, it receives a strong negative prior.

## 3. Current quiet-domain probes — compact decisions

### Generic scientific-summary qualifier loss / overclaim — KILL
**Question:** Do LLM summaries erase scope/causal/uncertainty qualifiers from scientific results?  
**Why not:** recent work already directly studies broad generalization bias and ACL 2026 *Narrative License and Model Sycophancy in LLM Summaries of Scientific Work* covers causal/confidence overreach. Another qualifier taxonomy is a crowded cell, not a new parent.

### Published evidence ≠ complete evidence base — HOLD ONLY
**Question:** Can evidence-synthesis systems reach the same conclusion when unpublished/registry evidence is added to the published literature?  
**Why not promoted:** publication bias is a major classical problem and registries provide natural data, but the strong version currently compresses to “input evidence set matters”; LLM publication-bias detection and registry-linking work already exist. Need a new identified model-specific scientific quantity, not another systematic-review pipeline.

### Composite endpoint ≠ each component — HOLD SEARCH SEED
**Question:** If a trial shows a benefit on `death OR hospitalization`, does an LLM preserve that aggregate claim rather than silently conclude benefit on death and hospitalization separately?  
**Why interesting:** composite-endpoint interpretation is a classical, consequential evidence problem with natural trial records; aggregate significance does not license component-wise significance.  
**Why not promoted:** no direct modern owner found in this pass, but the remaining paper identity may reviewer-compress to generic scientific-summary overgeneralization plus one clinical endpoint type. It also risks being publishable only if a sizeable error effect appears. Need a broader non-artificial scientific quantity or two-sided outcome story before promotion.

### Surrogate endpoint ≠ target patient outcome — HOLD SEARCH SEED
**Question:** When a study improves a biomarker/surrogate, when does an LLM carry that evidence over to the patient-important endpoint the surrogate is intended to stand in for?  
**Why interesting:** the old scientific distinction is real and consequential, and surrogate validity can vary by setting/subgroup.  
**Why not promoted:** current direct search found LLM-assisted surrogate-analysis tooling but not the exact evidence-transfer question; however, clean independent gold for “this surrogate licenses this target-outcome claim in this setting” is difficult, and a simple test risks becoming medical/statistical competence. Needs an externally validated surrogate-status substrate and a Main-scale consequence.

### Noninferiority ≠ equivalence ≠ superiority — HOLD LOW PRIORITY
**Question:** Do LLMs preserve the hypothesis-test semantics of a clinical claim instead of flattening “noninferior” into “equivalent/as good/better”?  
**Why not promoted:** ClinicalTrials.gov-derived work already provides structured test-type gold, making the data attractive, but that also makes the current formulation look like a narrow statistical-competence test. Need a consequential downstream inference that changes when the distinction is preserved.

### Generic subgroup / significance-vs-no-significance interpretation — KILL CURRENT SEARCH FORM
**Question:** Can models avoid concluding subgroup differences merely because one subgroup is significant and another is not?  
**Why not:** this is a classical statistical fallacy with extensive methodological/spin literature; without a novel modern operation it is another competence check.

### Surface-form probability / token wording as belief — KILL
**Question:** Can semantic belief be separated from probability assigned to one verbalization/tokenization?  
**Why not:** semantic-probability, paraphrase calibration, semantic-entropy and related work already occupy the parent.

## 4. Portfolio decision from this pass

**No new candidate is promoted.** This is intentional. The three clinical-evidence ideas above remain search seeds only; none has yet passed reviewer compression + outcome robustness + natural-gold requirements.

L24 is separately **deprioritized to HOLD** because the current formulation lands in the saturated Agent/long-term-memory area, depends on a memory/entity-resolution harness, and has awkward paper-scale natural gold.

## 5. Search takeaway

Do not ask only:

> “What did the Best Paper do, and what did it leave open?”

Also ask:

> **“What older scientific pressure caused this paper to exist, and where else does the same origin mechanism exist in a quieter field?”**

The next search round should start from those provenance patterns, especially **measurement bottlenecks, weakly evidenced important claims, field assumptions, real workflows, and robust cheap anomalies**, rather than from fashionable system labels.
