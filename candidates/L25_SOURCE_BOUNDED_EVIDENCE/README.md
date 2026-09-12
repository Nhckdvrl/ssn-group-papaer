# L25 — Evidence Exists Somewhere ≠ One Source Establishes It

**Subtitle:** Rule-Conditioned Evidence Fusion in Large Language Models  
**Status:** **SERIOUS / PRE-PILOT — DATA-CONSTRUCTION AUDIT — NO COMPUTE AUTHORIZED**  
**Date:** 2026-09-12  
**Target:** ACL / EMNLP / NAACL Main

## One-sentence RQ

> **When all required facts are present somewhere across several valid documents, can an LLM preserve which source supports which fact when the decision rule requires one source to establish the whole claim, or does it fuse the context into a single bag of evidence?**

## Plain example

Suppose a new patent claim requires three features:

> **A + B + C**

Prior-art document 1 contains **A + B**.  
Prior-art document 2 contains **C**.

The union of the two documents contains every feature. But that does **not** mean that one earlier document already disclosed the claimed invention.

This distinction is not an invented benchmark rule. Patent examination gives a natural real-world version:

- for **novelty / anticipation**, a single prior-art reference normally must disclose all claim elements;
- for **obviousness / inventive step**, multiple references may be combined when the combination is justified.

The modern LLM tension is therefore simple:

> **LLMs are built to synthesize complementary evidence across documents. Can they turn that synthesis on and off when the governing inference rule changes?**

## Why this question exists — topic provenance

This lead did not come from a fashionable Agent/RAG problem or from one paper's unexplained table cell. It came from a distinction that several generations of patent-NLP work have repeatedly simplified away.

### 1. Classical scientific / professional ancestry

Patent law has long distinguished **single-source anticipation** from **multi-source obviousness**.

USPTO MPEP §2131 states that anticipation requires each claim element to be found in a **single prior-art reference**, subject to narrow exceptions where extra references explain enablement, terminology, or inherency.

UKIPO and EPO guidance likewise distinguish standalone prior art from combinations: UKIPO explicitly says disclosures cannot be mosaiced to demonstrate lack of novelty but can be combined for inventive step; EPO search reports mark a document as **X** when it is prejudicial taken alone and **Y** when it is particularly relevant only in combination with another Y document.

### 2. An older NLP benchmark discarded the decisive category

**PatentMatch** (PatentSemTech/SIGIR 2021) built a 6.26M-pair claim–prior-art dataset from EPO search reports. Its raw parser exposes `Category_X` and `Category_Y`, but the released learning task uses **X versus A**. The paper explicitly says **Y citations were not used because they seemed too close to X citations in semantic relevance to provide a good training signal**.

That is exactly the scientific pressure: **X and Y may look similarly relevant semantically while having different inferential roles.**

### 3. A new fine-grained novelty paper again removes inventive-step cases

**Knappich et al., SIGIR 2026, _Is It Novel and Why? Fine-Grained Patent Novelty Prediction Based on Passage Retrieval_** introduces FiNE-Patents with 3,658 claims and feature-level prior-art references. Its construction explicitly **filters out rejections due to lack of inventive step** before forming the novelty dataset. It studies claim features against a single prior-art document very carefully, but intentionally does not answer how evidence must be composed across documents under different rules.

### 4. A separate benchmark now exposes the behavioral pressure

**PANORAMA (NeurIPS 2025 Datasets & Benchmarks)** preserves 8,143 USPTO examination records and directly evaluates §102 novelty and §103 non-obviousness. It reports that LLMs are relatively effective at retrieving relevant prior art and locating pertinent paragraphs, yet struggle more with the final novelty/non-obviousness judgment. Its task definition itself distinguishes §102 as anticipation by a **single cited reference** and §103 as obviousness over the cited art.

PANORAMA therefore shows that the hard part is not merely finding relevant text. But it does **not** causally identify whether models fail because they fuse complementary sources under the wrong rule.

## Modern scientific object

The candidate is **not** “can an LLM do patent law?” and not “classify §102 versus §103.” PANORAMA already owns that benchmark-level question.

The scientific object is:

> **rule-conditioned evidence aggregation** — whether the model's conclusion depends only on the union of facts available in context, or also on the partition of those facts across evidence units when that partition is load-bearing for the inference rule.

Two accounts:

### Account A — Content-union reasoning

Once facts A, B and C are all somewhere in context, the model effectively reasons over their union. Source identity is metadata and complementary support is silently fused.

Prediction: splitting the same atomic support across two documents will not reliably protect a single-source decision from being triggered.

### Account B — Rule-conditioned evidence reasoning

The model represents support as something like `fact × source`, and the governing rule controls whether sources may be composed.

Prediction: the same total evidence can license different decisions depending on its source partition and the stated decision rule.

## Not K010

Closest killed parent: **K010 — Dependent/copied-source corroboration**.

K010 asks whether **dependent or copied evidence is over-counted as independent corroboration**. L25 is different in the load-bearing variable:

- the sources may be fully **independent**;
- every individual fact may be true and correctly grounded;
- the error occurs because **composing valid complementary sources is forbidden for one inference but allowed/relevant for another**.

The estimand is therefore rule-conditioned source composition, not dependence-aware evidence weighting.

## Prior work owns

- Patent prior-art retrieval and claim–document matching.
- X-vs-A semantic matching (PatentMatch).
- Fine-grained single-document novelty analysis and feature-level passage retrieval (FiNE-Patents).
- End-to-end §102 / §103 / ALLOW classification with real USPTO office actions (PANORAMA).
- Generic multi-source fact verification and evidence aggregation.
- Generic source-admissibility failures in long-context systems are also beginning to be discussed, including a 2026 working manuscript on “Context Is Not Control.”

## Prior work does NOT yet appear to own

After direct searches for `single-reference rule`, `mosaicing`, `multiple prior art`, `source boundary`, `evidence fusion`, §102/§103 and LLM/patent variants, no peer-reviewed paper was found that performs the following causal test:

> hold **atomic evidence content** fixed, manipulate only **which source contains which evidence** and/or **which inference rule governs aggregation**, and measure whether an LLM's conclusion tracks the legal/evidential topology rather than the union of context content.

This must be refreshed immediately before any compute authorization.

## Natural data / gold

### Primary substrate — PANORAMA

Released dataset: `LG-AI-Research/PANORAMA` on Hugging Face.

- 8,143 USPTO examination records in the parent dataset.
- NOC4PC gives claim-level §102 / §103 / ALLOW decisions and examiner rationales.
- Test breakdown reported in the paper: **1,115 §102** and **2,257 §103** cases after excluding a small both-ground subset.
- For §102, the data construction uses one cited reference; §103 can contain two or more.
- Prior-art specifications and cited paragraphs are supplied for the decision task.

Known limitation: a small subset relies on non-patent literature missing from the released prior-art specifications. Filter these rather than reconstructing them for the first audit.

### Cross-jurisdiction / scaling substrate — EPO

EPO/PCT search reports provide expert-authored citation categories:

- **X:** particularly relevant when taken alone;
- **Y:** particularly relevant when combined with another Y document.

PatentMatch's data-collection code already parses both `Category_X` and `Category_Y`, even though its final X-vs-A benchmark discards Y. FiNE-Patents also publishes EPO extraction code and its construction starts from records that include inventive-step cases before filtering them out.

Do **not** rebuild the full EPO corpus before the PANORAMA data gate passes.

## Decisive operation

The pilot should separate **legal/domain difficulty** from **evidence-fusion structure**.

### E00 — data-only gate

From PANORAMA §103 cases, identify a clean subset where:

1. exactly two patent references are cited;
2. examiner rationale clearly maps different claim limitations to different references;
3. neither cited reference alone is asserted to disclose all limitations;
4. both prior-art texts are present in the released dataset;
5. the claim and rationale are parseable without inventing gold.

Also sample matched §102 cases where one reference supports the full anticipation rationale.

If this cannot be obtained at useful scale with high-confidence automatic extraction plus a small manual audit, **kill before model experiments**.

### E01 — natural contrast

Ask a model the narrow novelty question on:

- real single-reference §102 cases;
- real split-reference §103 cases in which the union covers the relevant limitations but no one cited reference does.

The key error is not ordinary wrong legal classification. It is specifically:

> **novelty rejected because support exists collectively across sources.**

### E02 — source-partition intervention

Use examiner-cited passages as fixed atomic evidence. Create paired presentations that preserve wording and total information while varying source grouping / source labels. Include order and token-budget controls.

Measure whether a source-boundary manipulation changes the single-source judgment in the predicted direction.

### E03 — same evidence, different aggregation rule

With the same claim and source-partitioned evidence, ask two explicitly formalized questions:

1. **single-source sufficiency:** does any one source cover every required limitation?
2. **union coverage / combination eligibility:** are all limitations covered somewhere across the allowed evidence set?

This avoids conflating the core mechanism with the full doctrinal complexity of obviousness. The real §102/§103 decision remains the external consequence test.

## Successful-result test

### Result A — content-union bias

Models often reject novelty on split-source cases, and causal regrouping shows that the mistake follows evidence union rather than source boundaries.

Strong paper identity:

> LLM multi-document synthesis is not automatically valid reasoning; models can erase evidential topology that the decision rule treats as causal.

### Result B — explicit rules repair the failure

If raw behavior fuses sources but an explicit source-aware decision rule repairs it, the paper becomes a **representation / control bottleneck** rather than a generic competence result. Test whether a minimal source×feature table or source-preserving output contract provides the necessary intermediate state.

Re-select before developing this identity.

### Result C — strong models preserve source boundaries

A near-null failure result is only worth continuing if preservation is non-trivial: source-sensitive behavior must remain stable under source permutation, document order changes, semantic matching pressure, and transfer between USPTO and EPO formulations, while content-only/pairwise baselines cannot express the distinction. Then the result is that modern LLMs implement a rule-conditioned composition operation that older semantic-match formulations miss.

If all competent models are simply at ceiling and no consequential benchmark conclusion changes, **kill**; do not manufacture a story.

### Result D — heterogeneous boundary

If failure depends systematically on number of sources, feature distribution, reasoning model status, context length, or whether the rule is implicit versus explicit, the boundary itself can be the scientific result if it predicts errors out of sample.

## Development path

1. **C1 — establish the law:** same total evidence does not imply the same valid inference; quantify source-fusion behavior on natural §102/§103 records.
2. **C2 — causal identification:** source-partition intervention separates content coverage from evidence topology.
3. **C3 — rule conditioning:** test whether the same model can switch between single-source and union-permitted reasoning on identical evidence.
4. **C4 — consequence:** show whether source-aware reasoning changes conclusions/rankings on real patent examination, and validate the pattern on EPO X/Y structure if feasible.
5. **Optional explanation:** only after the behavioral identity survives, investigate whether source identity is represented but ignored versus lost during long-context integration. This is not required for candidate authorization.

## Strongest reviewer compression

> **“This is PANORAMA §102-vs-§103 with a source-count ablation.”**

That compression wins if we merely compare accuracy by rejection code or number of references.

The paper survives only if the load-bearing result is a **matched causal intervention**:

> the atomic evidence is held fixed while source partition and aggregation rule are manipulated, directly identifying whether the model reasons over evidence topology or only over content union.

Second compression:

> **“This is generic source-boundary / admissibility work moved to patents.”**

The distinction is that all sources here may be valid, current, independent, relevant evidence. The question is not which source is admissible at all; it is **whether valid sources may be composed for a particular inference**. Patent doctrine supplies natural expert gold for that operation.

## Why this fits the current search preference

- Not Agent / memory / RAG / RL / judge.
- No harness is required.
- No speech/audio.
- Not a pure linguistic competence test.
- The question survives deletion of model names and benchmark names.
- It comes from a **classical, consequential inference rule** plus a modern LLM strength—multi-document synthesis.
- It has natural professional-process data and expert-authored decisions.
- It combines multiple lines of work rather than betting on one paper's anomaly.
- The topic provenance is especially attractive: the key Y/inventive-step category is precisely what earlier novelty datasets repeatedly **discarded to make the benchmark cleaner**.

## Kill conditions before compute

- A direct peer-reviewed owner is found that already performs matched source-partition / rule-conditioned evidence-fusion interventions for novelty vs obviousness.
- PANORAMA examiner rationales do not permit a trustworthy subset where feature-to-reference coverage can be identified without author-created gold.
- The apparent split-source effect is fully reducible to context length, number of documents, or general legal-knowledge errors under matched controls.
- The only surviving contribution is “patent LLMs confuse §102 and §103,” which PANORAMA already owns.
- The study cannot escape a narrow legal-classification identity and fails to support the broader claim about rule-conditioned evidence composition.
