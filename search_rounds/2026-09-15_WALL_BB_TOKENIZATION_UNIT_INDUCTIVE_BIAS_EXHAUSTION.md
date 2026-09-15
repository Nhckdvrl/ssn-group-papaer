# WALL-BB — Are explicit linguistic units necessary, or are they mainly a computational shortcut?

Date: 2026-09-15  
Status: **EXHAUSTED / CONTINUOUS DIRECT PROGRAM EXISTS**  
Mode: old-unit question → token-free regime change → same-quantity explanation audit  
Candidate generation: **OFF**

## Mother question

Language models are normally handed a discrete segmentation of text before learning. But linguistic theory does not provide a single universally privileged unit: words, morphemes, subwords, characters and constructions overlap, and the notion of a cross-linguistically uniform `word` is itself contested.

The durable scientific question is therefore not `which tokenizer is best?` It is:

> **What does an explicit segmentation contribute to language learning? Is it a necessary representational/inductive bias, or mainly a computational device that a sufficiently capable learner could reconstruct from raw sequences?**

This question predates foundation-scale LMs and remains meaningful independent of any benchmark.

## Old intellectual ancestry

The problem sits at the intersection of:

- word segmentation and lexicon induction;
- morphology and compositionality;
- character/word/subword language modeling;
- compression-based segmentation;
- statistical learning from continuous/unsegmented input.

A central tension has always been that meaningful units help sample-efficient generalization, yet assuming the correct units in advance gives the learner information that real language learners and cross-linguistic systems may not possess.

## Early neural evidence already attacks necessity

**Hahn & Baroni, TACL 2019, _Tabula Nearly Rasa_** trained character-level language models on text with word boundaries removed. The models still acquired substantial morphological, syntactic and semantic knowledge and learned, to some extent, to track word-like boundaries internally.

This is already a direct scientific owner of the question:

> can useful supra-character linguistic units emerge without an explicit rigid word lexicon?

Their answer is broadly yes: explicit word boundaries are helpful but not strictly necessary for many forms of linguistic knowledge.

Character-aware and character-level work before/around this period likewise showed that useful morphology can be induced from finer-grained input, while oracle morphological analyses can still provide additional gains.

## Foundation-model regime change

The modern regime makes the question operational at scale because byte/character models can now be competitive with tokenized transformers.

### CANINE / ByT5

- **CANINE** (TACL 2022) removes an explicit input tokenizer and explicitly discusses subword prediction as a **soft inductive bias** rather than a hard input segmentation.
- **ByT5** (TACL 2022) shows that minimally modified byte-level transformers can be competitive with token-level counterparts while improving robustness to noise/spelling-sensitive tasks.

These works establish that fixed subword vocabularies are not a strict architectural necessity.

### BLT

**Byte Latent Transformer** (ACL 2025) scales byte-level modeling to 8B parameters / trillions of training bytes while introducing dynamically sized entropy-based patches. This changes the engineering regime again: raw bytes can be the external representation while higher-level computational chunks are allocated dynamically.

Thus the old assumption `a performant LM must be handed a fixed subword inventory` is genuinely broken.

## The apparent live tension

Two empirical facts coexist:

1. token-free models can learn strong language representations and can internally recover boundary-like structure;
2. carefully chosen tokenization/boundary priors still materially improve efficiency and sometimes generalization.

A tempting residual is therefore:

> **Why do explicit subword boundaries help if the learner can discover useful units itself?**

The first plausible explanation is pure compression/throughput: tokenization shortens sequences and lets a fixed compute budget process more text.

The second is a genuine linguistic/statistical prior: boundaries group recurring units and alter which dependencies are easy to learn.

This is the exact kind of SAME-QUANTITY disagreement the search protocol asks for.

## But the residual is already directly owned

### EMNLP 2024 — compression alone is insufficient

**Schmidt et al., _Tokenization Is More Than Compression_** construct PathPiece to minimize token count for a fixed vocabulary. Fewer tokens do **not** reliably yield better downstream performance. The paper explicitly concludes that compression alone does not explain effective tokenization and investigates pre-tokenization, vocabulary construction and segmentation choices.

This already rejects the naive `shorter sequence -> better tokenizer` law.

### 2025–2026 — linguistic alignment is tested separately

Recent morphology-aware tokenization work reports gains from linguistically aligned boundaries, including cases where the gain is not explained by materially shorter token sequences. This makes morphology/boundary information itself an active explanatory variable rather than an untested intuition.

### 2026 — the decisive decoupling paper

The most important owner is:

**Gigant, Peng & Quesnelle (2026), _Decoupling the Benefits of Subword Tokenization for Language Model Training via Byte-level Simulation_.**

This paper formulates almost exactly the residual question above. Inside a controlled byte-level pretraining pipeline it separately simulates/tests proposed benefits of subword tokenization, including:

- sample/training throughput;
- vocabulary scaling;
- the linguistic prior supplied by subword boundaries.

Its main conclusion is that increased throughput and incorporation of subword-boundary information as explicit priors or inductive biases are key contributors to the subword advantage.

Therefore the clean question

> `Is tokenization helping because of compute/compression, or because it supplies useful boundaries?`

is not open territory for us. The modern regime change has already generated its own causal-decoupling experiment.

## Residuals audited and rejected

### Residual A — Do byte LMs internally rediscover words/morphemes?

Directly anticipated by TACL 2019 and many later representation analyses. A larger Transformer plus probes would be `new model × old question` and probe-first.

### Residual B — Are linguistic boundaries better than entropy/compression boundaries?

This is now an active tokenizer/patching design axis (morphology-aware tokenization, BLT, dynamic/learned tokenization). Without a deeper scientific quantity it becomes method comparison.

### Residual C — Does tokenization change hypothesis class or only optimization speed?

Potentially deep, but the current operationalizations collapse to training-curve/throughput/architecture comparisons already targeted by the 2026 decoupling work. A theorem-level version would be an ML theory project, not a clean ACL Main descendant currently identified here.

### Residual D — Which linguistic unit should emerge?

There is no single universally agreed gold unit, especially across morphological typologies. Turning this into `word vs morpheme vs construction` quickly becomes a segmentation benchmark/annotation problem or another competence probe.

### Residual E — Token-free model as a cognitive learner

This falls into the already closed/held `LM as scientific model system` linking-hypothesis problem. Better resemblance to unsegmented human input does not by itself make the model evidence about human lexical acquisition.

## Reviewer compression

The harsh compression is:

> “Hahn & Baroni already asked whether word-like units emerge without segmentation; CANINE/ByT5/BLT establish token-free scaling; EMNLP 2024 rejects pure compression; Gigant et al. 2026 directly decouple throughput, vocabulary scaling and boundary priors. This paper changes the tokenizer, model, language or probe.”

No current residual survives that compression at Main-level magnitude.

## Verdict

**WALL-BB EXHAUSTED. No L-series. No K-series allocation.**

This wall is useful precisely because it initially looked unusually promising: old scientific ancestry, a genuine foundation-model regime change, and rival explanations on the same quantity all exist. It still closes because the exact causal decomposition has already become a continuous research program.

### Anti-resurrection

Do not reopen as:

- byte/character model learns morphology;
- learned word-boundary neurons/features;
- token-free vs BPE benchmark comparison;
- morphology-aware BPE on another language;
- compression ratio vs downstream accuracy;
- dynamic patches vs fixed tokens;
- tokenization effect on another benchmark/model scale;
- `linguistic prior vs throughput` unless a genuinely new quantity beyond the 2026 decoupling program is identified.

A reopening would require a different old scientific claim about linguistic units whose inference becomes possible specifically because modern token-free systems expose a new intervention—not another tokenizer ablation.

## Core references

- Kim et al. (AAAI 2016), *Character-Aware Neural Language Models*.
- Vania & Lopez (ACL 2017), *From Characters to Words to in Between: Do We Capture Morphology?*
- Vania, Grivas & Lopez (EMNLP 2018), *What do character-level models learn about morphology?*
- Hahn & Baroni (TACL 2019), *Tabula Nearly Rasa*.
- Clark et al. (TACL 2022), *CANINE*.
- Xue et al. (TACL 2022), *ByT5*.
- Schmidt et al. (EMNLP 2024), *Tokenization Is More Than Compression*.
- Pagnoni et al. (ACL 2025), *Byte Latent Transformer: Patches Scale Better Than Tokens*.
- Hudspeth, Burns & O’Connor (EACL 2026), contextual morphologically guided tokenization.
- Asgari et al. (ACL Findings 2026), *MorphBPE*.
- Gigant, Peng & Quesnelle (2026), *Decoupling the Benefits of Subword Tokenization for Language Model Training via Byte-level Simulation*.
