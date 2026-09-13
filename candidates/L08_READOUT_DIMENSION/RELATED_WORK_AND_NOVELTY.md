# L08 — Related Work and Paper-Level Novelty

**Candidate:** Answer provenance, not capability, governs compression damage
**Last owner audit:** 2026-09-14. Sections 1-10 below are the historical audit, kept
for the record. **Section 0 is current and supersedes them where they disagree.**

---

## 0. Current owner audit  `2026-09-14`

Four papers bound what this package may claim. Two of them were missed by the
2026-09-13 fresh Selection.

### 0.1 Owned, and claimed nowhere: `evaluation protocol matters`

**Wen et al., "The Benchmark Illusion: Pruned LLMs Can Pass Multiple Choice but Fail
to Answer", arXiv 2606.17609 (June 2026).** Under high-sparsity pruning, especially
Wanda, models fail greedy open generation while still selecting the correct answer
under multiple-choice scoring on the same question; the answer is demoted rather than
erased and reappears under beam search, sampling or one in-context example.

**Song et al., "Demystifying the Roles of LLM Layers in Retrieval, Knowledge, and
Reasoning", ICASSP 2026, arXiv 2510.02091.** *This was missed by the fresh Selection
and is the more dangerous of the two.* Same MMLU benchmark, same intervention family
(layer pruning), three evaluation protocols — likelihood/default, likelihood
continuation, open `generation-until`. Likelihood evaluation makes most middle and deep
layers look nearly irrelevant; generation shows them to be essential for reasoning and
long-range coherence. Concludes that layer importance is task-, metric- and
model-dependent.

Together these own the generic statement

> `same content + same intervention, different readout protocol -> different conclusion`

**completely.** It is a level effect of protocol. The package's C1 reproduces it more
cleanly (same item, same prompt, only the readout rule varies) and reports it as the
identification step that makes C2 estimable. It is never presented as a contribution.
Venue is irrelevant to ownership; ICASSP does not make Song et al. ignorable.

Neither paper has a **depth axis inside generation**, and neither has the
**provenance contrast**. That is where L08 lives.

### 0.2 The target: UniComp

**"UniComp: A Unified Evaluation of Large Language Model Compression via Pruning,
Quantization, and Distillation", EMNLP 2026 Main, arXiv 2602.09130.** Wanda, SparseGPT,
GPTQ, AWQ, SmoothQuant, Minitron, Low-Rank Clone; 40+ datasets. Headline: a strong
**knowledge bias** — factual knowledge is largely preserved while reasoning,
multilingual and instruction-following degrade disproportionately. On Llama-3.1-8B,
Wanda retains 83.66% of knowledge and 40.15% of reasoning.

Verified against the paper, 2026-09-14:

- the knowledge set (MMLU, ARC-E/C, HellaSwag, PIQA, Winogrande) is **multiple-choice
  throughout**; the reasoning set (GSM8K 4-shot, MATH-500 4-shot, GPQA-Diamond 5-shot)
  is **free-form CoT throughout**;
- output/generation length is **not controlled or discussed anywhere**;
- the paper reports that GPQA-Diamond is notably more robust than GSM8K and MATH-500
  and conjectures this is "likely attributable to its multiple-choice format".

So the headline capability claim is read off a comparison in which capability, answer
format and answer depth are confounded by construction — and the paper's own unexplained
anomaly is our law's prediction, stated by them and left untested. If the conjecture is
right it does not save the headline; it dissolves it, because the same mechanism applies
to every row of the knowledge column.

This is the scientific pressure that makes the question worth asking, and it is why the
target is a live EMNLP 2026 Main conclusion rather than a 2025 appendix.

### 0.3 Partial owner of the accumulation half: RAC

**"Reasoning Models Can be Accurately Pruned Via Chain-of-Thought Reconstruction",
arXiv 2509.12464.** Pruning calibrated only on prompt activations suffers distribution
shift once the model generates its own chain, producing error accumulation; calibrating
on on-policy CoT activations mitigates it.

This owns **"damage accumulates along a self-generated chain after pruning"** as a
motivating observation. L08 must not present that as new. What RAC does not have is the
**dissociation**: that under the same intervention and the same free-generation protocol
there is *no* decay with depth when the answer stays prompt-recoverable. The
accumulation is the known half; the flat half is the finding.

E12 therefore fixes calibration data across all arms and does not task-match it —
task-matched calibration is RAC's paper.

### 0.4 Neighbours that do not collide

- **ICLR 2026, "When Reasoning Meets Compression"** — reports weight count affecting
  knowledge memorization more than reasoning, the opposite ordering to UniComp. The two
  are **not** a formal contradiction: intervention, task, model and estimand all differ,
  and the repo's SAME-QUANTITY rule forbids presenting them as one. They are cited
  together as evidence that the field's fragility ordering is not stable, which is the
  motivation for asking whether it is identified at all.
- **ThinkSLM, EMNLP 2025 Main** — quantization and pruning affect reasoning differently
  in small models. Supports the mother phenomenon; no protocol or depth control.
- **"Evaluating Zero-Shot Long-Context LLM Compression", arXiv 2406.06773** — pruning
  stays robust as *input* context grows while quantization degrades. Input length, not
  self-generated answer depth. Different axis; cite to keep the two separate.

### 0.5 The strongest reviewer compression, and the answer

> *"Song et al. already showed pruning conclusions depend on likelihood vs generation.
> Wen et al. already showed recognition-generation dissociation after pruning. UniComp
> already studies capability-specific compression across three families. RAC already
> showed CoT error accumulation after pruning. This paper is those four observations
> with more controls."*

If L08 ends at "MMLU ranking is high and generation is low", **this compression holds
and the paper is dead.** That is why C1 is a prerequisite and the `C3.2` sign boundary
was demoted on 2026-09-14.

The compression fails only against the depth-by-provenance law, because A+B+C+D do not
imply it: none of the four has a depth axis inside generation, and none compares
prompt-recoverable against trajectory-carried answers at matched depth on the same
items. Wen et al. and Song et al. predict a *level* shift; our result is a **slope**,
and a slope that is zero on one side.

### 0.6 Novelty accounting, as of 2026-09-14

| component | status |
|---|---|
| protocol changes the conclusion | **owned** — P0.2, P0.3. Prerequisite only |
| capability-specific compression damage exists | **owned** — P0.4, mother phenomenon |
| CoT error accumulates after pruning | **owned** — P0.5 |
| retention decays with answer depth **only** for trajectory-carried answers | **no owner found** — load-bearing |
| provenance manipulated within item, capability held fixed | **no owner found** — E12, not yet run |
| published capability orderings re-estimated at matched provenance | **no owner found** — C3, conditional on E12 |

---

## Historical audit (pre-2026-09-14), retained for the record

**Candidate title at the time:** Low-Dimensional Readout Preserves Knowledge but Breaks Reasoning

---

## 1. Direct parent — EMNLP 2025 People’s Choice

Takeshita et al., **“Randomly Removing 50% of Dimensions in Text Embeddings has Minimal Impact on Retrieval and Classification Tasks”**:
- 6 text encoders;
- 26 embedding tasks;
- up to 50% random dimension removal with <10% drop on many retrieval/classification tasks;
- identifies many “degrading dimensions” for text embeddings;
- includes Llama 3.1 8B and Qwen 2.5 7B causal-LM experiments;
- reports severe task dependence, including near-collapse on GSM8K;
- explicitly says dedicated study of the LLM case is future work.

Source:
- https://aclanthology.org/2025.emnlp-main.1410/

What it owns:
- the dimension-removal phenomenon;
- degrading dimensions in text embeddings;
- the first causal-LM observation;
- the statement that LLM sensitivity is task dependent.

We cannot claim any of these as new.

## 2. Compression/pruning neighborhood

ICLR 2026 **“When Reasoning Meets Compression”** studies quantization/distillation/pruning of reasoning models and mechanistically localizes compression-sensitive weights.

It reports, among other findings, that weight count can hurt knowledge memorization more than reasoning.

Source:
- https://proceedings.iclr.cc/paper_files/paper/2026/hash/665654759cdf2114c0cbe2b8e501e00e-Abstract-Conference.html

This is useful because it shows:
> compression location matters.

It does **not** answer our question:
- weight compression changes model parameters/computation;
- our intervention changes the final hidden-to-vocabulary readout channel while leaving transformer weights/computation intact.

The potentially opposite knowledge-vs-reasoning patterns strengthen the question rather than collide with it.

## 3. Reasoning-token compression/pruning

ACL 2026 contains multiple papers on:
- pruning redundant CoT;
- identifying functionally important reasoning tokens;
- reducing reasoning length;
- pruning reasoning models.

Examples:
- https://aclanthology.org/2026.acl-long.25/
- https://aclanthology.org/2026.acl-long.1419/
- https://proceedings.iclr.cc/paper_files/paper/2026/hash/e70ffb3f05096e62b5077d8e1b62e668-Abstract-Conference.html

These own:
- CoT token importance;
- efficiency-oriented reasoning compression;
- weight-level reasoning pruning.

They do not own:
> final-readout dimensional bottleneck vs autoregressive accumulation.

## 4. Representation / subspace work

A broad literature studies:
- linear probes;
- low-dimensional task subspaces;
- safety/alignment directions;
- intrinsic dimensionality.

Example:
- ICML 2025 “The Hidden Dimensions of LLM Alignment” studies multi-dimensional safety directions.

Source:
- https://proceedings.mlr.press/v267/pan25f.html

These works show that capabilities can be represented in structured subspaces, but do not establish our cross-capability readout necessity question.

## 5. New paper-level story

The paper must own:

1. established final-readout truncation creates large cross-capability differences;
2. “reasoning needs more dimensions” is only one explanation;
3. matched teacher-forced/free-running interventions separate local readout loss from sequential accumulation;
4. dimension-selection transfer tests task-specific geometry;
5. length/output-format controls test whether the effect is really reasoning-specific;
6. conclusion clarifies the relation between low-dimensional representation and autoregressive computation.

## 6. Reviewer compression

### Attack 1
> “EMNLP 2025 plus more benchmarks.”

Fatal if true.

### Attack 2
> “Another reasoning compression paper.”

Rebuttal:
> no parameter pruning or efficiency objective; the target is where capability bottlenecks live.

### Attack 3
> “GSM8K exact-match is just long generation.”

This is a serious scientific alternative, not a nuisance.

The paper must test:
- teacher forcing;
- length-matched generation;
- multiple-choice/short-answer variants;
- token-level KL/margin.

If generation length explains everything, that is still a valid corrective conclusion but the paper may need reconstruction in scope.

## 7. Kill-level collision definition

KILL if a paper already:
- performs the same final hidden/unembedding dimensional intervention;
- compares reasoning vs knowledge/QA;
- separates teacher-forced local degradation from free-running accumulation;
- tests dimension/subspace transfer;
- and reaches the same capability-bottleneck conclusion.

Generic pruning/intrinsic-dimension work does not kill.

## 8. Top-conference alignment

Strong alignment comes from:
- starting from a surprising established Main/award result;
- asking a simple mechanism question;
- using causal intervention rather than correlation;
- allowing competing explanations and a corrective result.

This resembles strong mechanistic Main papers more than an efficiency benchmark.

## 9. Current verdict

**SERIOUS / A-.**

Novelty is real only if the study explains the asymmetry, not if it maps more truncation curves.

---

# 10. Live novelty check — 2026-09-10 (execution stage)

Run against the reframed RQ in `README.md` (protocol vs capability), not the
candidate-stage one. Searches covered readout/unembedding truncation, hidden-state
dimensionality and reasoning, and evaluation-protocol confounds.

## 10.1 Nearest live neighbour: the MC-vs-generation validity literature

There is an active line arguing that multiple-choice evaluation is a poor proxy for
generative ability, e.g. Balepur et al., *Which of These Best Describes Multiple
Choice Evaluation with LLMs? A) Forced B) Flawed C) Fixable D) All of the Above*
(https://arxiv.org/abs/2502.14127), work showing answer matching outperforms
multiple choice, and MC robustness studies under option-order and phrasing
perturbations.

**What they own.** That MC accuracy and generative accuracy differ, that MC is
sensitive to surface perturbations, and that MC overstates capability.

**What they do not own, and what we would claim.** Those results are about *task
scores*. Ours is about what an *interventional, representation-level* result means:
that the sensitivity of a model to a causal intervention in its representation space
is itself protocol-bound, so redundancy and compression conclusions collected under
ranking protocols do not license claims about the model's computation. The relevant
quantity is not "MC is easier" but "a fixed perturbation of the readout is survivable
by a K = 4 decision and not by a length-L arg-max over V".

**Compression risk this creates.** A reviewer may try: *"known that MC ≠ generation."*
The rebuttal must be carried by C2 (the survival law), not by C1 alone. C1 without
C2 is compressible; that is why the mainline treats C2 as load-bearing rather than
as a nice-to-have mechanism section.

## 10.2 Hidden-state / latent-reasoning work (2026)

Latent CoT and hidden-state refinement work (e.g. hidden-state recurrence for latent
reasoning; reinforcement-guided latent refinement) shares the object "final hidden
state" but has an engineering objective — improving or compressing reasoning — and
does not study the readout channel's dimensional budget as a measurement question.
No collision.

## 10.3 Kill check

The KILL condition in §7 requires a paper that performs the same final-readout
dimensional intervention, compares reasoning against knowledge/QA, **and** separates
the protocol/depth/content factors. Nothing found does the decomposition. **Not
killed.** Re-check before the C2 experiments are finalised.

---

# 11. Live novelty check — 2026-09-10, against the reconstructed mainline

Run against `MAINLINE.md`, not the candidate-stage or the intermediate framing.

## 11.1 A real collision, stated plainly

**Ozdemir et al. (?), "The Benchmark Illusion: Pruned LLMs Can Pass Multiple Choice
but Fail to Answer", arXiv 2606.17609 (June 2026).**
https://arxiv.org/abs/2606.17609

Abstract, verbatim in part: *"A pruned model may still perform well on
multiple-choice evaluations, yet fail to answer the same question in open generation
[...] Under high-sparsity pruning, especially Wanda, models often fail in greedy open
generation while still selecting the correct answer under multiple-choice scoring. In
these recognition-only errors, the answer is usually not gone, but demoted: it often
reappears with beam search, sampling, or one in-context example. [...] Compressed
models should be tested on what they can produce, not only on what they can recognize."*

**What this owns, and what we must therefore stop claiming.** The bare observation
that a compressed model passes ranking-scored evaluation while failing open generation
on the same questions is **theirs**, for pruning, on multilingual QA, as of June 2026.
Our project must not present "ranking survives, generation collapses" as a new
finding. It is prior work, and it independently corroborates our protocol effect on a
different task family and a different pruning method — which is a strength for the
replication argument and a loss for the novelty argument. It is cited as support, not
as background.

**What it does not own.**

1. **Capability attribution.** They make no knowledge-versus-reasoning claim. Our
   central result — that controlling protocol *and output length* removes 49.7-111% of
   the evidence for capability-selective damage — is a claim about which capability
   compression damages, not about whether benchmarks overstate usability.
2. **The content axis at matched protocol.** They compare protocols. They never
   compare knowledge content against reasoning content *within* a protocol and at
   matched length. That factorial is the object of our paper.
3. **Output length as a separate factor.** They do not control it. In our data the
   length axis is larger than the protocol axis: the same MMLU items go 0.889 (rank)
   -> 0.837 (one generated token) -> 0.030 (a generated chain).
4. **The intervention-family boundary.** They study pruning only. Our separation —
   across 15 estimable conditions, five model families and three intervention families,
   six of eight readout conditions make reasoning *significantly more robust* than
   knowledge at matched protocol and length and none makes it more fragile, while five
   of seven parameter conditions make it significantly more fragile and none makes it
   more robust — has no counterpart in their work and is the paper's positive
   contribution.
5. **Readout truncation and the parent correction** (three dissolved conclusions, the
   `best_exact` floor, the mask-identity result) are untouched by them.

Their "demoted, not erased" diagnostic concerns where an answer sits in the ranking.
Ours concerns what kind of damage an intervention did — computation or expression.
Different objects, and ours requires the factorial theirs does not run.

## 11.2 Adjacent, non-colliding

- **Balepur et al., arXiv 2502.14127**, and the answer-matching literature: multiple
  choice is a poor proxy for generative ability. About task scores and model ranking,
  not about what an intervention reveals.
- **KV-cache compression and reasoning faithfulness** (arXiv 2608.01631, 2604.10900):
  a different intervention, and the question is faithfulness of the trace to the
  answer, not capability attribution.
- **"On the Limits of Layer Pruning for Generative Reasoning"** (arXiv 2602.01997):
  accepts the classification-versus-generative-reasoning framing and argues that
  degeneration does not fully explain the failure. We invalidate that framing, and we
  show the degeneration point causally (E05) rather than by assertion.
- **ICLR 2026 "When Reasoning Meets Compression"**: draws capability-selective
  conclusions from exactly the confounded comparison.

## 11.3 Effect on the claim

The reconstruction stands, with one leg removed and reassigned to prior work. The
mainline sentence is now:

> Controlling evaluation protocol **and output length** removes most or all of the
> evidence for capability-selective compression damage; what survives the controls
> separates interventions that damage a model's computation from interventions that
> damage only its ability to express that computation.

Not: "multiple choice overstates compressed models." That sentence is taken.
