# 2026-09-12 — Award-Provenance Concrete-Hook Search

**Target:** ACL / EMNLP / NAACL Main  
**Outcome:** no new candidate promoted. No compute authorized.

## Search rule used this round

Do **not** start from an abstract distinction such as `X != Y`, `proxy != target`, or a missing schema field.

Start from a concrete hook of the kind repeatedly seen in Best / Outstanding papers:

- a stable, surprising empirical anomaly;
- an old community claim that may no longer be true for modern models;
- a simple sanity baseline that overturns an accepted conclusion;
- a real expert workflow that naturally produces better supervision/evaluation data;
- a strong public claim with weak direct evidence;
- two evaluation/training procedures that are supposed to measure the same thing but visibly disagree.

Only after the hook is independently interesting should a larger scientific question be formulated.

## Award-paper provenance patterns mined

- **ACL 2026 Best — Imperfective Paradox:** textbook-clean old phenomenon first; systematic LLM bias and larger theory grow out of it.
- **NAACL 2025 Outstanding — AdvScore:** concrete measurement contradiction: a benchmark is called adversarial even after models learn to solve it.
- **NAACL 2025 Outstanding — PeerQA:** real peer-review questions provide naturally expert-authored scientific QA.
- **TACL 2024 Best / ACL 2025 recognition — Reading Subtext:** original authors are a natural authority for intended story subtext.
- **ACL 2025 Outstanding — GEC evaluation:** human and automatic evaluation pipelines aggregate judgments differently despite aiming at the same ranking.
- **ACL 2025 Outstanding — All That Glitters:** expert inspection of AI-generated research ideas revealed suspicious overlap with existing work during novelty hype.
- **ACL 2026 Best — Local Attention:** restricting access for efficiency can paradoxically improve quality; the anomaly motivates the mechanism question.
- **ACL 2024 Best — Mission: Impossible Language Models:** a widely repeated theoretical claim had little direct experimental support, so the paper tested it.
- **ACL 2025 — Did Translation Models Get More Robust Without Anyone Even Noticing?:** revisits an old accepted weakness and finds the modern model regime has changed.
- **ACL 2026 visual-token compression work:** a very simple downsampling baseline exposes that the benchmark may not measure the intended compression problem.

## Concrete hooks investigated and rejected

### Modern LLM exposure bias / self-recovery

**Hook:** Do modern instruction/reasoning LLMs still snowball after one self-generated error, or have they quietly learned to recover from bad prefixes?

**Why not:** 2023 *How Language Model Hallucinations Can Snowball* already directly studies early-error overcommitment in ChatGPT/GPT-4; ACL 2026 DiffCoT explicitly treats early-error propagation / exposure bias as a central modern reasoning problem. A new model sweep would compress to an update of this line.

### Pruning makes models hallucinate less

**Hook:** A pruned model can become worse at summarization yet more faithful to the source. Why does removing capacity make it less willing to invent?

**Why not:** the anomaly is real and interesting, but 2025 work such as PruneCD already exploits pruned-model factuality for decoding, while other work studies pruning effects on truthfulness / truth representations. Compression x factuality is becoming a dedicated local mechanism line; the remaining gap is too incremental for current search priority.

### More demonstrations, higher accuracy, less attention to the actual input

**Hook:** With more in-context demonstrations, accuracy can improve while measured attentiveness to the test input falls.

**Why not:** recent many-shot ICL work shows large demonstration sets can be compressed into short task-level cheat sheets and that broad/random many-shot examples are already strong. The natural question therefore collapses into the crowded central problem of what many-shot ICL represents/uses.

### External background information contaminates stance judgment

**Hook:** Adding relevant Wikipedia/Web context can make stance detection substantially worse because the model adopts the background source's stance or sentiment instead of judging the target text.

**Why not:** this lands in the already-crowded semantic/expression-leakage and irrelevant-context-interference parent, and overlaps an internally killed route. Changing the target classification task does not create a new scientific object.

### Eighteen token embeddings teach translation

**Hook:** NAACL 2025 KS-Lottery reports that tuning only 18 token embeddings can approach full fine-tuning for multilingual translation. How can so few embedding parameters unlock a large translation capability?

**Why not:** the same author line already studies vocabulary sharing / embedding adaptation as the mechanism enabling multilingual capability, and KS-Lottery itself gives a theoretical/certified winning-ticket account. The remaining mechanism question is too close to the mother line rather than a new paper identity.

### Simple-baseline / wrong-benchmark search

**Hook class:** Can a cheap sanity baseline overturn a recent sophisticated NLP method or benchmark conclusion?

**Result:** several real examples exist, but the promising cells found in this round were already owned (visual-token compression benchmark mismatch, compute-controlled library learning, benchmark/evaluation artifacts). No open Main-level target survived.

## Search lesson

The correction from previous rounds is important:

> **A good research question should usually be generated from a concrete thing that is already strange, inconsistent, weakly evidenced, or naturally observable — not from an abstract distinction that we then try to instantiate.**

Also, a good hook is not enough. Immediate follow-ups to recent Award papers are often already crowded within a year. A better next search source is:

> **trace Award papers backward to the older empirical claims, classic limitations, and anomalies they cite; identify claims from roughly 2018–2023 that the field still repeats but that have not been systematically re-tested under modern instruction/reasoning LLMs.**

This is the next preferred search generator.
