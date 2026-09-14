# Search Kill Batch — K246–K252

Date: 2026-09-14  
Target: ACL / EMNLP / NAACL Main  
Source round: `search_rounds/2026-09-14_PRESSURE_SEARCH_K246_PLUS.md`

This batch registers the parent-level failures from the broad search after K245. These are anti-resurrection boundaries, not backup ideas.

A new model, dataset, prompt, language, benchmark, narrower mechanism, or generic causal-intervention wrapper does **not** reopen them.

---

## K246 — Probability knowledge → native stochastic generation

**Parent RQ**

> When an LLM can state the correct target probability distribution, why does its own generated sample distribution fail to match it? Is there a missing/failed computation between probability representation and stochastic action generation?

**Status:** KILL  
**Primary failure:** `NOVELTY_PARENT_COLLISION`  
**Secondary failure:** `CROWDED_PARENT / PROHIBITED_BEHAVIOR_TO_MECHANISM_SALVAGE`

**Why it looked promising**

The question has a clean dissociation: semantic knowledge of a distribution is not the same quantity as the empirical distribution of actions. Both outcomes would matter for agent simulation and for what `probabilistic reasoning` means computationally.

**Decisive owner evidence**

1. Gu et al., COLING 2025, *Do LLMs Play Dice? Exploring Probability Distribution Sampling in Large Language Models for Behavioral Simulation*  
   https://aclanthology.org/2025.coling-main.360/  
   Already separates probability understanding from probability sampling and reports that models understand probabilities but struggle with probabilistic sampling.

2. Guo et al., Findings EMNLP 2025, *The Illusion of Randomness: How LLMs Fail to Emulate Stochastic Decision-Making in Rock-Paper-Scissors Games?*  
   https://aclanthology.org/2025.findings-emnlp.458/  
   Explicitly frames a cognition–behaviour gap: models articulate the correct Nash distribution while realized choices deviate, and investigates positional bias as a source.

3. Zhao et al., ACL 2026, *Large Language Models Are Bad Dice Players: LLMs Struggle to Generate Random Numbers from Statistical Distributions*  
   https://aclanthology.org/2026.acl-long.1051/  
   Large-scale native-sampling audit across 11 models and 15 distributions; directly studies batch vs independent-request protocols.

**Reviewer compression**

> “Recent papers already establish the probability-knowledge / sampling gap and characterize protocol/bias effects; this paper adds an internal mechanism analysis.”

Under the current search doctrine, that is not a fresh parent. `They show behavior; we explain mechanism` is specifically prohibited when the object has already become an active program.

**Do not reopen by**

- exchangeability / IID terminology;
- batch vs independent requests;
- temperature or decoding changes;
- RPS vs random numbers vs agent actions;
- hidden-state probing, SAE, patching, steering;
- verbal vs numerical target distributions;
- another model family.

**Reopen only if**

An independent scientific law/quantity appears that is not reducible to native sampling fidelity or the cognition–behaviour gap and makes a new pre-result prediction.

---

## K247 — Architecture-conditioned factual recall mechanism

**Parent RQ**

> What structural condition determines whether factual recall is MLP-associative, attention-dominated, or implemented through distributed/geometric relational representations?

**Status:** KILL CURRENT PARENT  
**Primary failure:** `CROWDED_PARENT / NOVELTY_PARENT_COLLISION`  
**Secondary failure:** `A+B_GENERATION`

**Why it looked promising**

Several papers appear to disagree about the same broad object: how Transformers retrieve factual associations. A genuine hidden-condition law explaining the difference would be valuable.

**Decisive owner / program evidence**

1. Choe et al., EMNLP 2025, *Do All Autoregressive Transformers Remember Facts the Same Way? A Cross-Architecture Analysis of Recall Mechanisms*  
   https://aclanthology.org/2025.emnlp-main.1448/  
   Already makes architecture-dependence the central object and reports a Qwen-specific attention-heavy pattern relative to previous MLP-centered findings.

2. Ravfogel et al., 2026, *Geometric Factual Recall in Transformers*  
   https://arxiv.org/abs/2605.12426  
   Directly challenges the associative-key-value account with a geometric memorization theory in which embeddings store superpositions and an MLP acts as a relation-conditioned selector; derives capacity consequences and transfer.

3. Yan & Jia, EMNLP 2025, *Promote, Suppress, Iterate: How Language Models Answer One-to-Many Factual Queries*  
   https://aclanthology.org/2025.emnlp-main.815/  
   Already performs fine-grained mechanism decomposition for a more complex recall setting.

**Construct objection**

The proposed `hidden architecture variable` was not independently motivated before juxtaposing these papers. Without such a variable, the idea is exactly `Paper A finds MLP / Paper B finds attention / Paper C proposes geometry → we unify`, i.e. LLM bridge generation rather than scientific pressure.

**Reviewer compression**

> “A synthesis/successor paper in the rapidly developing factual-recall mechanism program.”

**Do not reopen by**

- adding more architectures;
- Qwen vs Llama vs GPT vs DeepSeek;
- editing instead of recall;
- one-to-many or multi-hop queries;
- geometric probes;
- `where is knowledge stored?` variants;
- causal tracing/patching as a novelty claim.

**Reopen only if**

A pre-existing architectural or representational quantity, independently measurable before factual probing, makes a falsifiable prediction about which recall mechanism must arise.

---

## K248 — Translation universals / translationese under pretrained LMs

**Parent RQ**

> Which classical translation regularities remain genuine translation laws under pretrained generative LMs, and which are artifacts of supervised translation policy rather than translation itself?

**Status:** KILL CURRENT PARENT  
**Primary failure:** `CROWDED_PARENT / NOVELTY_PARENT_COLLISION`

**Why it looked promising**

Foundation-model translation changes a load-bearing premise of classical MT: a model first learns a broad natural target-language distribution, then may acquire translation behavior through SFT. That could in principle distinguish a translation-induced law from a training-induced policy.

**Decisive owner / program evidence**

1. Li et al., ACL 2025, *Lost in Literalism: How Supervised Training Shapes Translationese in LLMs*  
   https://aclanthology.org/2025.acl-long.630/  
   Directly attributes LLM translationese to biases introduced during supervised training and intervenes on translation training data.

2. Jiang, 2025, *Does LLM translation align with translation universals? A cross-genre simplification study on English-Chinese translation based on dependency grammar*  
   https://doi.org/10.1371/journal.pone.0324830  
   Directly asks whether an LLM exhibits the simplification universal and compares LLM, human translation and original target-language text across genres.

3. 2025–2026 adjacent work already studies LLM translationese indices, explicitation, normalization and simplification.

**Reviewer compression**

> “Another translation-universal dimension or formation mechanism inside an already active LLM-translationese program.”

**Do not reopen by**

- switching simplification to explicitation/normalization/interference;
- changing language pair or genre;
- base vs instruct vs translation-tuned comparisons;
- adding a mechanistic representation analysis;
- using a more causal SFT intervention.

**Reopen only if**

A different old translation law has a load-bearing premise that modern LMs specifically break and that is not already part of the translationese/universals program.

---

## K249 — Training order / curriculum / critical-period parent

**Parent RQ**

> With total training evidence held fixed, does the temporal order of exposure merely change optimization speed, or does it permanently change what linguistic/computational structure a model learns?

**Status:** KILL CURRENT PARENT  
**Primary failure:** `NOVELTY_PARENT_COLLISION / CROWDED_PARENT`

**Why it looked promising**

This is a real scientific question: path dependence can separate `what data` from `when data`, and model checkpoints make developmental mechanisms observable. It also connects to old critical-period debates without requiring human confounds.

**Decisive owner / program evidence**

- TACL-era work already tests critical-period effects by delaying language exposure in neural LMs and asks whether statistical learning alone explains them.
- Zhang et al., EACL 2026, *Beyond Random Sampling: Efficient Language Model Pretraining via Curriculum Learning* studies data-order strategies at substantial scale.  
  https://aclanthology.org/2026.eacl-long.271/
- Dai et al., ACL 2026, *Demystifying Data Organization for Enhanced LLM Training* formalizes multiple data-order guidelines in pretraining/SFT.  
  https://www.microsoft.com/en-us/research/publication/demystifying-data-organization-for-enhanced-llm-training/
- Jia et al., ACL 2026, *What Makes a Good Curriculum? Disentangling the Effects of Data Ordering on LLM Mathematical Reasoning* already finds curriculum direction conditional on capability/task and separates output/internal effects.  
  https://aclanthology.org/2026.acl-long.1591/
- Dini et al., 2026, *On the impact of pretraining data ordering in transformer encoder- and decoder-only language models* reports architecture-dependent optimization, probing and representation effects.  
  https://www.sciencedirect.com/science/article/pii/S0950705126005769

**Reviewer compression**

> “A new ordering criterion / linguistic phenomenon inside the already active data-order and curriculum-dynamics program.”

**Do not reopen by**

- easy→hard vs hard→easy;
- another difficulty metric;
- multilingual exposure order;
- pretraining vs SFT;
- architecture comparison;
- U-shaped acquisition;
- checkpoint probing.

**Reopen only if**

A distinct developmental law with an independently motivated causal premise cannot be reduced to generic order/curriculum/path dependence.

---

## K250 — Transformer succinctness → learned algorithms

**Parent RQ**

> If Transformers can represent an algorithm exponentially more succinctly than competing architectures, does gradient-based learning actually discover that succinct computation, and is that what explains generalization?

**Status:** KILL  
**Primary failure:** `NOVELTY_PARENT_COLLISION`

**Why it looked promising**

This is the right kind of theory→empirical pressure: expressivity alone is insufficient; a compact representational solution only matters if optimization finds it.

**Decisive owner collision**

1. Bergsträßer, Cotterell & Lin, ICLR 2026, *Transformers are Inherently Succinct*  
   https://proceedings.iclr.cc/paper_files/paper/2026/hash/5f7804e8855efe5554025217abc49315-Abstract-Conference.html  
   Introduces succinctness as a formal measure and proves major description-size advantages.

2. Zhao, Findings ACL 2026, *Do Transformers Grok Succinct Algorithms? Mechanistic Evidence for Counting Circuits*  
   https://aclanthology.org/2026.findings-acl.1301/  
   Directly asks whether trained Transformers converge to the predicted succinct circuits rather than heuristics; studies grokking, complexity collapse and recovered circuit structure.

**Reviewer compression**

> “The exact empirical successor to the ICLR succinctness theory has already been published.”

**Do not reopen by**

- a different formal language;
- another algorithm such as parity/addition/sorting;
- larger pretrained models;
- another mechanistic method;
- training dynamics instead of final circuits;
- architecture family changes.

**Reopen only if**

A qualitatively different theoretical consequence of succinctness, not learnability/grokking/circuit discovery, forces a new question.

---

## K251 — Latent event schema vs local event associations

**Parent RQ**

> When an LLM predicts an omitted or next event in a familiar scenario, does it instantiate a reusable scenario-level event schema, or assemble predictions from local pairwise/multi-relational event associations?

**Status:** KILL CURRENT FORM  
**Primary failure:** `IDENTIFICATION / WHY_NOW_FAILURE`  
**Secondary failure:** `CROWDED_PARENT`

**Why it looked promising**

The distinction is scientifically real and predates LLMs. A structured schema and a collection of local event associations can make the same prediction on canonical scripts but differ under omissions, recombination and global consistency.

**Prior scientific ownership / pressure**

- Classical script-learning work already contrasts simple similarity/pairwise event representations with richer multi-relational script structure.
- ACL 2023, *Open-Domain Hierarchical Event Schema Induction by Incremental Prompting and Verification*, explicitly treats event schemas as hierarchical world knowledge available from LLMs.  
  https://aclanthology.org/2023.acl-long/
- Hong et al., *SEM 2024, *Do large language models and humans have similar behaviours in causal inference with script knowledge?*, directly manipulates stated/negated/omitted prerequisite events and finds an LLM–human divergence.  
  https://aclanthology.org/2024.starsem-1.34/

**Construct / identifying-operation objection**

The modern model does not yet provide a genuinely new operation that cleanly changes a *global schema* while preserving the local event relations being compared.

- reordering/deleting events changes evidence;
- using nonce scripts changes the object to in-context induction;
- learning a latent schema direction from target behavior is circular;
- patching a hidden state only shows that a constructed state matters;
- transfer/next-event tasks are competence tests.

Thus the question is attractive, but `foundation model as experimental system` currently adds convenience rather than a new inference.

**Reviewer compression**

> “A mechanistic replication of the old structured-schema-vs-association question using hidden-state interventions.”

**Do not reopen by**

- restaurant/airport/medical scripts;
- more models or long context;
- event reordering;
- hidden-state patching/SAE directions;
- hierarchical schema generation;
- narrative cloze.

**Reopen only if**

A natural same-quantity intervention appears that selectively alters a scenario-level schema variable while preserving matched local event evidence, with semantics defined independently of the model’s target behavior.

---

## K252 — Construction meaning as reusable semantic operator

**Parent RQ**

> When a grammatical construction contributes meaning beyond the verb, is that contribution implemented as a reusable construction-level semantic computation across lexical items, or as lexeme-specific reinterpretation/analogy?

**Status:** KILL CURRENT PARENT  
**Primary failure:** `CROWDED_PARENT / PROHIBITED_OWNER_SHRINK`  
**Secondary failure:** `NOVELTY_PARENT_COLLISION`

**Why it looked promising**

Construction Grammar offers a natural theoretical object: form–meaning pairings can contribute semantic content independent of individual lexical items. Novel-verb coercion appears to offer a direct test of reuse.

**Decisive owner / active-program evidence**

1. Oba & Sugawara, ACL 2026 Outstanding, *CxMP: A Linguistic Minimal-Pair Benchmark for Evaluating Constructional Understanding in Language Models*  
   https://aclanthology.org/2026.acl-long.2132/  
   Directly makes constructional form–meaning understanding a central LLM object across nine constructions and separates semantic understanding from grammatical acceptability.

2. Guo et al., 2026, *Do Language Models Know What Not to Say? Causal Evidence for Statistical Preemption in LLMs*  
   https://arxiv.org/abs/2605.23039  
   Directly dissociates competing Construction Grammar acquisition mechanisms using controlled fine-tuning intervention.

3. Bonial et al., 2026, *Linguistic Productivity in Large Language Models: Models Coerce, but do not Preempt*  
   https://arxiv.org/abs/2606.02953  
   Tests coercion/productivity/preemption with nonce lexical items across architectures.

4. Aljaafari et al., Findings ACL 2026, *Emergence and Localisation of Semantic Role Circuits in LLMs*  
   https://aclanthology.org/2026.findings-acl.1964/  
   Shows the surrounding predicate–argument semantic space has already moved into causal-circuit analysis.

**Reviewer compression**

> “The constructional-semantics program already owns the behavior and learning mechanism; this work changes the interpretability operation to test reuse.”

That is exactly `they do behavior, we do mechanism`, which current doctrine forbids as a novelty strategy.

**Do not reopen by**

- caused-motion vs dative vs locative;
- nonce verbs;
- multilingual Construction Grammar;
- patching/steering a construction vector;
- `shared circuit` wording;
- base/instruct/training-stage comparisons.

**Reopen only if**

A distinct scientific quantity outside generic constructional meaning/productivity is identified and the construction is only a natural substrate for that quantity.

---

# Surviving pressure (not registered as a kill)

The only pressure surviving this batch is **lexical event-structure factorization**:

> Do LMs implement verb meaning using reusable event-template computations such as ACT / CAUSE / BECOME shared across lexical roots, or do they only approximate decompositional event-structure theory behaviorally with holistic lexical/contextual representations?

It is **not L39**, not Selection-passed, and not pilot-authorized. Its blocker is a non-circular, theory-defined causal-abstraction test. See the search-round report for details.

---

**Next kill ID: K253.**
