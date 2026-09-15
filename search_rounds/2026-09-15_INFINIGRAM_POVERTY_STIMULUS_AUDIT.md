# 2026-09-15 — Infini-gram / Poverty-of-Stimulus Audit

**Target:** ACL / EMNLP / NAACL Main; calibrated against TACL / ICLR / ICML / NeurIPS.

## Question

> Does internet-scale exact local distributional evidence eliminate the apparent need for abstract inductive bias in linguistic generalization?

A more careful version considered was:

> For classic poverty-of-the-stimulus cases, how much of a model's successful structural generalization exceeds the strongest exact local evidence available in trillion-token corpora?

**Final verdict:** **KILL CURRENT FORM / DO NOT REGISTER AS L-SERIES / DO NOT PILOT.**

The mother problem is important and the Infini-gram instrumentation is genuinely new leverage, but the proposed instrument does not identify the scientific estimand. Exact unbounded n-gram evidence is only one class of distributional evidence, whereas poverty-of-the-stimulus arguments concern what a suitably general learner could infer from the learner's actual input. A Transformer outperforming an infinity-gram does not establish abstract-rule learning; an infinity-gram matching the behavior does not establish that the Transformer used local evidence.

---

## 1. Why the route looked promising

EMNLP 2025 Best Paper **Infini-gram mini** extends an instrumentation lineage that makes exact n-gram search at Internet scale practical. The original Infini-gram work builds unbounded-order n-gram models over trillions of tokens and can retrieve counts for arbitrarily long contexts quickly.

This suggests a Hamming-style opportunity: revisit an old important question whose empirical premise has historically been hard to measure.

Poverty-of-the-stimulus arguments rely on a claim that relevant linguistic evidence is too sparse or absent for a general learner to infer the adult generalization. Structure dependence, wh-movement, island constraints, one-anaphora, and related cases have long been debated in terms of whether direct or indirect statistical evidence exists in realistic input.

A trillion-token exact search engine therefore appears to offer a new attack on the empirical premise:

> perhaps apparent abstraction is explainable by very large-scale local distributional evidence that older corpus studies simply could not observe.

---

## 2. Why the scientific object fractures into two different questions

### Human language acquisition

The relevant distribution is **developmentally realistic child input**, not Internet-scale web text.

Lan, Chemla & Katzir (Linguistic Inquiry 2026) explicitly frame the modern APS question as whether a sufficiently general learner exposed to approximately human-accessible input can acquire the target linguistic pattern. They emphasize that current LMs are simultaneously over-informed in text volume and under-informed in multimodal/social evidence relative to children.

Thus a 5T-token Infini-gram cannot directly adjudicate the human APS. Finding decisive examples at web scale would show that *foundation-model pretraining* is not poor in that sense, not that child input is rich enough.

### Foundation-model generalization

For LMs, Internet-scale local evidence is relevant. But now the question changes to:

> does successful LM generalization require structure beyond local contiguous statistics available in its pretraining distribution?

That is a legitimate model-science question, but Infini-gram still does not identify the answer.

---

## 3. The decisive identification failure

Poverty / sufficiency is about **all information a learner could exploit**, not just exact contiguous n-gram evidence.

Reali & Christiansen (2005), *Uncovering the Richness of the Stimulus*, is already a canonical warning: for subject-auxiliary inversion, the critical examples can be rare or absent while **indirect statistical cues** elsewhere in the distribution nevertheless distinguish the grammatical and ungrammatical generalizations. A simple learner can exploit those cues.

Infini-gram gives extraordinarily strong measurement of one family of signals:

- exact occurrences;
- arbitrarily long contiguous contexts;
- local next-token distributions;
- longest matching suffixes.

It does **not** enumerate all nonlocal, paradigmatic, semantic, cross-context, or shared-parameter evidence available to a neural learner.

Therefore the central comparisons are not identifying:

### Transformer succeeds, Infini-gram fails

This does **not** imply the Transformer learned an abstract grammar. The neural model may exploit indirect distributional cues not expressible by contiguous n-gram lookup.

### Infini-gram succeeds

This shows local evidence can support the judgment, but does **not** show the Transformer actually relied on that local evidence.

### Both fail

This does not establish genuine poverty either: both instruments may miss another exploitable cue family.

The new instrument is powerful, but the estimand is broader than the instrument.

---

## 4. Owner / lineage audit

The mother debate is highly mature:

- classical poverty-of-the-stimulus / structure-dependence literature;
- Reali & Christiansen's indirect-evidence challenge;
- decades of replies and counter-replies;
- modern neural-language-model work on structure dependence and filler-gap dependencies;
- Lan, Chemla & Katzir (2026), which directly evaluates whether modern neural learners undermine an APS for wh-movement and stresses learner neutrality plus realistic input;
- current work on possible/impossible language learnability and inductive bias.

No exact owner was found for `Infini-gram × APS`, but novelty cannot be established by inserting a new instrument into this mature debate when the instrument cannot settle the central inference.

---

## 5. Main-level calibration

The strongest recent papers used for taste calibration do more than provide a stronger baseline:

- ACL 2026 local-attention Best Paper produces formal predictions explaining a genuine counterintuitive architectural result;
- ICLR 2026 succinctness changes the conceptual quantity used to compare architectures;
- ICML 2026 Flexibility Trap shows a celebrated advantage itself causes a non-obvious failure mode;
- NeurIPS 2025 RLVR runner-up changes the inference from score gain to capability-boundary expansion.

The current route would reviewer-compress to:

> **Use an Internet-scale n-gram baseline to check whether linguistic generalization might be explained by memorized/local corpus statistics.**

That is useful analysis, but not yet a belief-changing Main-level contribution.

The key issue is not compute or novelty search. It is construct validity: `exact local evidence` is not `all evidence available to a general learner`.

---

## 6. Why obvious repairs do not rescue it

### Add many syntactic phenomena

This makes a broad benchmark/analysis paper, not a sharper scientific inference.

### Restrict the claim to direct evidence

Then the question becomes easy and descriptive: how often do direct/near-direct patterns occur at Internet scale? Scientifically useful, but too data-centric and below current taste.

### Compare many n-gram orders

This does not address indirect non-contiguous evidence.

### Add probes/patching to see whether the Transformer uses local cues

That turns the project into a mechanistic sequel with an extremely difficult causal identification problem; Layer-3 becomes more interesting than Layer-1.

### Use the exact training corpus of an open model

This improves provenance but not the fundamental inference: absence of local evidence is not absence of learnable statistical evidence.

---

## 7. What could reopen the pressure

Do not reopen by simply running BLiMP / SyntaxGym against Infini-gram.

A qualitatively stronger attack would need, for example:

1. a theory characterizing a broad, independently motivated class of **distributional evidence** and proving that a target generalization is or is not identifiable from that class;
2. a natural linguistic phenomenon for which existing acquisition theories make genuinely conflicting predictions about which evidence families suffice, with a modern instrument that measures those exact families;
3. a controlled training result showing that removing a precisely identified evidence family changes the generalization while preserving the rest of the natural distribution, thereby moving from correlation/counting to causal evidence sufficiency;
4. a surprising law across multiple phenomena predicting when local evidence is sufficient versus when structural bias is necessary.

Until such leverage exists, keep the APS / evidence-sufficiency problem as a standing scientific issue, but do not paperize Infini-gram as the answer.

---

## 8. Final decision

**KILL CURRENT FORM / ARCHIVE.**

No L-series candidate.
No pilot.
No `Infini-gram + grammatical benchmark` experiment.

Durable searcher lesson:

> A new instrument creates a paper only when it measures the causal/scientific object that the old question is actually about. Vastly improving measurement of one proxy (`local exact evidence`) does not identify a broader construct (`all evidence sufficient for a learner`).

And preserve the workflow discipline:

> Once a lead enters SERIOUS-LOOK, finish identification, ownership, consequence, and Main-level calibration before switching scientific objects.
