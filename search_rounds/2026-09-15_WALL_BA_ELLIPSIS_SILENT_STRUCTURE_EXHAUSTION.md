# WALL-BA — Does ellipsis require silent syntactic structure?

Date: 2026-09-15  
Status: **EXHAUSTED FOR CURRENT SEARCH / DIRECT HUMAN IDENTIFICATION EXISTS**  
Mode: classic-theory lineage + disagreement + identifying-leverage audit  
Candidate generation: **OFF**

## Mother question

Ellipsis creates one of the oldest form–meaning puzzles in linguistics: listeners recover content that was never pronounced.

> Does the ellipsis site contain unpronounced syntactic structure, or can interpretation be recovered by semantic/discourse anaphora or antecedent reactivation without building that silent structure?

This is a genuine linguistic-theory question, not an LLM benchmark question. It remains important even if all current language models disappear.

## Long intellectual lineage

The dispute is mature and has multiple genuinely different theories.

### Structural / deletion family

Work from Sag, Williams, Fiengo & May, Chung/Ladusaw/McCloskey, Merchant and others posits syntactic structure inside at least important classes of ellipsis sites, with pronunciation suppressed by deletion or related mechanisms.

Classic evidence includes:

- syntactic connectivity effects;
- case/preposition/binding effects in fragments and sluicing;
- voice and structural identity restrictions;
- extraction and island diagnostics;
- interpretations that appear to require internal structure.

### Non-structural / semantic / discourse family

Keenan, Hardt, Dalrymple–Shieber–Pereira, Ginzburg & Sag, Culicover & Jackendoff and others develop analyses in which the recovered meaning need not come from a full silent syntactic copy at the ellipsis site.

A central example is **Dalrymple, Shieber & Pereira (1991), Ellipsis and Higher-Order Unification**, which derives ellipsis interpretations through a semantic unification problem rather than hidden ambiguity in a full syntactic source.

### Processing / hybrid accounts

The empirical record forced a third family of explanations. Some mismatched antecedents judged acceptable are problematic for strict syntactic identity, while unconstrained semantic accounts overgenerate.

**Arregui, Clifton, Frazier & Moulton (2006)** therefore proposed VP recycling: grammar can require structural parallelism while the processor repairs/recycles imperfect antecedents. This is important because it breaks the naive inference

> acceptable mismatch -> grammar has no syntactic identity requirement.

**Kehler-style coherence** and **Kertz (2013)** further argue that some mismatch penalties attributed to ellipsis licensing can instead arise from discourse coherence or information structure. Kertz specifically argues that sizeable voice-mismatch penalties can be driven by contrastive-topic structure rather than the ellipsis licensing condition itself.

Thus the mature dispute is not `syntax vs semantics` in one scalar. Structure, identity, discourse licensing and processing repair are separable axes.

## Classic SAME-QUANTITY disagreements

Several observables have repeatedly been treated as diagnostic:

- acceptability under voice mismatch;
- availability of strict/sloppy interpretations;
- island/extraction behavior;
- syntactic connectivity under silence;
- processing cost when antecedent structure differs;
- reactivation or reconstruction signatures during comprehension.

But decades of work show why each behavioral diagnostic is difficult to interpret. For example, acceptability is not equivalent to grammaticality because repair can rescue structurally imperfect antecedents; discourse/information structure can modulate mismatch penalties; and different ellipsis constructions need not share one mechanism.

The 2019 *Oxford Handbook of Ellipsis* therefore still organizes the field around two independent questions—whether structure exists inside ellipsis sites and what kind of identity relates ellipsis to its antecedent—and concludes that evidence is mixed even though the full fact pattern overall favors reference to syntactic structure.

## Modern LLM literature does NOT create the wall

Current NLP/LLM papers on ellipsis mostly study competence, reconstruction, datasets, or human–model similarity:

- ACL 2023 *Ellipsis-Dependent Reasoning* shows that models can succeed on non-elliptical controls while failing ellipsis-dependent reasoning.
- SIGTYP 2024 builds a cross-linguistic ellipsis corpus and tests detection/reconstruction/parsing.
- 2026 work comparing LLMs and humans on silent-structure phenomena reports divergences in grammaticality/interpretation.

These are evidence about model behavior, not a new identification of the classic linguistic theories.

A tempting project would be to ask whether model internals instantiate silent syntax. That route is rejected here. A shared or causally useful internal representation after an ellipsis licensor would not by itself distinguish:

- generated silent syntax;
- semantic recovery whose downstream representation converges on similar features;
- antecedent reactivation;
- a task-specific predictive state.

This would repeat the repository’s earlier lesson: **access to internals is not automatically a new identifying operation**.

## Decisive 2026 update: the most natural identifying move is already owned in humans

The key owner is:

**Bruening, Koppy, Palaz, Tomioka & Tollan (2026), _How to understand silence: Voice mismatches in ellipsis in English_, Glossa Psycholinguistics.**

The paper explicitly states the rival hypotheses:

1. **structure generation** — comprehenders build silent syntactic structure at the ellipsis site;
2. **reactivation** — the ellipsis points back to/reactivates the antecedent, without generating that silent structure.

It also explicitly notes that prior psycholinguistic findings had not distinguished them.

Their identifying move uses **voice mismatch while holding the antecedent identical**. In the critical comparison, the ellipsis clause differs in voice while the antecedent does not. A word-recognition interference signature is stronger for active than passive ellipsis; because the antecedents are identical, antecedent reactivation alone cannot explain the contrast. A second experiment contrasts VP ellipsis with an overt pro-form. The authors conclude that ellipsis processing requires more than antecedent reactivation and that the results are most consistent with structure generation.

This matters enormously for our search. The clean research-question form

> `Does ellipsis comprehension build silent structure, or merely reactivate the antecedent?`

is no longer waiting for foundation-model internals to make it identifiable. A direct human psycholinguistic experiment has already attacked exactly that residual uncertainty with a theory-targeted operation.

## Residuals audited and rejected

### Residual A — Repeat the 2026 identification in LLMs

Reviewer compression:

> “Bruening et al.’s human structure-generation vs reactivation experiment, but with LLM hidden states.”

That is `linguistic phenomenon × mechanistic interpretability`, one of the repository’s explicitly banned default routes. Model internals do not improve the linguistic identification unless a new linking hypothesis is independently justified.

### Residual B — Ask whether LLMs have silent syntax at all

This is a model-competence / representation question, not the original scientific dispute. Behavioral success cannot identify silent syntax; probing/patching first is method-driven; causal reuse can be produced by downstream semantic convergence.

### Residual C — Voice mismatch under LLMs

Voice mismatch has decades of syntax/discourse/processing theory and current human experimental work. Running the same factorial contrast on LMs is a replication/model-system question, not an unowned Main-level parent.

### Residual D — Use scaling or post-training as a regime change

Scale/reasoning ability may change competence, but it does not break a load-bearing premise of the structural vs reactivation theories. It changes the learner, not what the human linguistic evidence identifies.

### Residual E — Pick another ellipsis construction

Sluicing, gapping, fragments, null-complement anaphora and argument ellipsis genuinely differ. Swapping construction therefore does not provide a clean replication of the same theory; it opens construction-specific literature and quickly becomes a benchmark/phenomenon cell.

## Reviewer compression

The strongest compression is:

> “Human syntax/psycholinguistics already has explicit structural, semantic, discourse and processing theories, and a 2026 experiment directly distinguishes structure generation from reactivation. The proposed LM experiment either replicates that contrast in another learner or uses model internals whose relation to the linguistic theory is itself underidentified.”

I do not see a prior-work-impossible inference left after this compression.

## Verdict

**WALL-BA EXHAUSTED FOR CURRENT SEARCH. No L-series. No K-series allocation.**

Important nuance: this verdict does **not** claim that the scientific theory of ellipsis is globally solved. The literature remains rich and contested. The verdict is narrower:

> the most attractive unresolved structural question either already has direct human identification work, or becomes non-identifying when transferred to LLM internals.

That is enough to close it as a generator for this project search.

### Anti-resurrection

Do not reopen as:

- silent syntax in GPT/Qwen/etc.;
- activation patching/probing of ellipsis representations;
- voice mismatch × LLM;
- another ellipsis benchmark;
- scaling/reasoning-model effects on ellipsis;
- causal transfer between overt and elliptical syntax without a new linking theorem;
- `LLMs support/refute deletion theory` based only on behavioral similarity.

A reopening would require a linguistic theory that makes a new **model-accessible but human-inaccessible** prediction on the same observable, with a justified linking hypothesis that rules out semantic convergence/reactivation alternatives.

## Core references

- Hankamer & Sag (1976), surface/deep anaphora tradition.
- Dalrymple, Shieber & Pereira (1991), *Ellipsis and Higher-Order Unification*.
- Merchant (2001), *The Syntax of Silence*.
- Arregui, Clifton, Frazier & Moulton (2006), *Processing Elided Verb Phrases with Flawed Antecedents: The Recycling Hypothesis*.
- Frazier & Clifton (2006), *Ellipsis and Discourse Coherence*.
- Merchant (2008/2013), *Voice and Ellipsis*.
- Kertz (2013), *Verb Phrase Ellipsis: The View from Information Structure*.
- Phillips & Parker (2014), psycholinguistics of ellipsis review.
- Merchant (2019), *Ellipsis: A Survey of Analytical Approaches*, Oxford Handbook.
- Frazier (2019), *Ellipsis and Psycholinguistics*, Oxford Handbook.
- ACL 2023, *Ellipsis-Dependent Reasoning: a New Challenge for Large Language Models*.
- SIGTYP 2024, *The Typology of Ellipsis: A Corpus for Linguistic Analysis and Machine Learning Applications*.
- Bruening et al. (2026), *How to understand silence: Voice mismatches in ellipsis in English*.
