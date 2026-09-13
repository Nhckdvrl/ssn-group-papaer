# 2026-09-13 — Pressure-First Search XXI

Continuation after `PRESSURE_FIRST_SEARCH_XX.md`. This batch keeps switching scientific objects: constructional negative evidence, presupposition triggering, semantic-composition explanations, and dual-task resource claims. Only `PILOT-AUTHORIZED — E01 ONLY` counts as a survivor.

---

## P104 — Learning from absence: does an LM use opportunity-conditioned negative evidence?

**Status:** `DROP / DIRECT 2026 RESEARCH PROGRAM`

### Pressure
A cognitively and linguistically attractive question is whether a model learns that a form is disfavored because it repeatedly had an opportunity to occur but did not. Construction-learning theory calls the relevant effect statistical preemption and distinguishes it from generic entrenchment. This initially looked like a genuinely different scientific object from ordinary positive-frequency learning.

### Why dead
The question is already an active, direct 2026 program rather than an unowned pressure:

- *Do Language Models Know What Not to Say? Causal Evidence for Statistical Preemption in LLMs* (arXiv:2605.23039) directly manipulates the frequency of competing forms in controlled fine-tuning while separating preemption from entrenchment.
- *Linguistic Productivity in Large Language Models: Models Coerce, but do not Preempt* (arXiv:2606.02953) reports that larger models exhibit entrenchment/coercion patterns yet fail to productively extend preemption to nonce items.
- *Disentangling Statistical Preemption from Entrenchment in Language Models* (arXiv:2609.01794, 2026-09-01) uses controlled rearing and finds little evidence for verb-specific preemption, with at most weaker abstract preemption.

The obvious hidden condition—familiar lexical item versus productive novel-item generalization—is therefore already inside the direct literature.

**Anti-resurrection:** do not reopen `can LMs learn from absence`, `preemption vs entrenchment`, opportunity-conditioned negative evidence, or familiar-vs-nonce preemption with a new construction/model.

---

## P105 — Productive presupposition triggering for novel lexical meanings

**Status:** `DROP CURRENT SUBSTRATE / HUMAN MOTHER DESTABILIZED; IDENTIFICATION WEAK`

### Pressure
Bade, Schlenker & Chemla (2024), *Word learning tasks as a window into the triggering problem for presuppositions*, report that human participants given neutral exposure to a novel change-of-state word spontaneously factor its bivalent meaning into a presupposed initial state and asserted change. Together with Tieu, Schlenker & Chemla's novel-animation work, this was used to argue for a productive triggering algorithm rather than memorized lexical presupposition flags. Roberts & Simons (2024) likewise argue that non-anaphoric projectivity follows from semantic/event content plus broad pragmatic principles.

A tempting LLM question is whether a modern LM, after learning only the ordinary event semantics of an unfamiliar predicate, productively derives its projective component or requires trigger-specific distributional history.

### Why not a candidate
Two blockers became clear.

1. **The strongest human word-learning mother is now unstable.** A March 2026 Harvard semantics talk, *A cautionary note on word learning tasks and presupposition triggering*, reports failure both to generalize the Bade et al. effect to a second nonce predicate and to replicate the original effect, and argues that adult artificial-word learning may not identify triggering mechanisms. A mechanism project should not anchor itself to a disputed mother while claiming a strong cognitive/semantic inference.
2. **The LLM experiment is non-identifying in its obvious form.** Positive projection after nonce-word exposure could arise because the LM analogically classifies the new word with familiar change-of-state/factive lexical classes; a negative result could simply mean the novel semantics were learned poorly. Running the human paradigm on an LLM therefore risks becoming model-as-human competence rather than a decisive computation test.

The broader theoretical question—semantic-content-driven projectivity versus trigger-specific lexical encoding—remains important, but this word-learning substrate does not currently give a clean operation.

**Anti-resurrection:** do not promote `does an LLM learn presuppositions for wug?`, novel-factive word learning, or human-paradigm replication without a selective way to separate analogical lexical classification from productive semantic/pragmatic derivation.

---

## P106 — Dual-task comprehension: shared computational interference or instruction-induced strategy switching?

**Status:** `DROP CURRENT MECHANISTIC ROUTE / MOTHER × ACCESS FEASIBILITY FAILURE`

### Pressure
ACL 2026 Main *A Dual-Task Paradigm to Investigate Sentence Comprehension Strategies in Language Models* reports that some LMs become more plausibility-driven when required to solve interleaved arithmetic while comprehending a sentence, and interprets this as evidence that limited memory/processing resources produce human-like rational comprehension. The paper includes a strong `Noisy Single Task` control with the same arithmetic tokens but an instruction to ignore them, so simple token-noise explanations are not sufficient for the headline models.

A deeper theoretical distinction remains natural:

> Does concurrent arithmetic actually interfere with the sentence computation through shared internal processing, or does the extra task instruction simply switch the model into a different task-set/comprehension strategy?

Classic human dual-task theory itself distinguishes capacity sharing/bottlenecks from task-set interference, making both accounts live.

### Candidate identifying idea examined
A decoder-specific path operation could keep the original tokens and dual-task instruction fixed while directionally isolating streams during sentence encoding: sentence-token states would be prevented from reading arithmetic-token states, arithmetic tokens could still read their own arithmetic history, and final answer states could later access both. If arithmetic remains correct while the plausibility shift disappears, this would implicate actual cross-stream computational interference; persistence would favor a top-down task-set/strategy account. This is more selective than adding another distractor condition.

### Why no compute / no candidate
The behavioral mother and mechanistic accessibility do not coexist in an appropriate open model.

The ACL paper's own full results state that the distinctive `Dual > Noisy` plausibility effect is robust primarily for GPT-4o, o3-mini, and o4-mini. GPT-4.1, DeepSeek-V3, Llama-3.3, and Gemma-3 generally degrade in both Noisy and Dual conditions without a significant Dual-vs-Noisy distinction. Llama-3.3 additionally achieves below 80% arithmetic accuracy even on the easiest dual-task condition. Thus:

- the clearest mother is in closed models whose internal attention/cache paths cannot be intervened on;
- mechanistically accessible open models do not supply a pre-established robust mother;
- searching Qwen/Gemma/Llama variants until one exhibits the desired effect would be prohibited model-shopping;
- DeepSeek-V3 is computationally impractical for the intended path-level audit and itself only shows a trend in the parent.

This is a **mother × mechanistic-access feasibility failure**, not evidence against the scientific distinction.

**Anti-resurrection:** do not model-shop an open checkpoint for `dual cognitive load`, or report a path intervention on a model lacking the published Dual-vs-Noisy phenotype. A future reopening requires an independently established strong mother on a tractable open model.

---

## P107 — Deferred semantic composition is caused by next-token training

**Status:** `DROP CURRENT FORM / CLAIM-LOCAL BUT EXPENSIVE AND OBJECTIVE-CONFOUNDED`

### Pressure
EACL 2026 *Where Do LLMs Compose Meaning?* finds distributed/fragmented semantic composition under constituent-aware pooling and proposes an information-theoretic explanation: token-level autoregressive training incentivizes deferred integration in order to preserve token-level throughput.

The explanation is stronger than the paper's direct intervention: CAP establishes sensitivity/distribution across depth, not a causal effect of the training objective. A natural question is whether autoregressive token-level supervision causes deferred composition, rather than architecture, data, or generic residual-stream computation.

### Why not pursue
A decisive treatment must alter the training objective while holding architecture/data/training budget sufficiently matched (causal next-token vs masked/span/sentence-level or hybrid objectives). This pushes the project into controlled pretraining and creates multiple simultaneous changes in information availability and optimization target. Existing causal-vs-masked/hybrid pretraining work already studies objective-dependent behavior, while the strongest cheap fixed-checkpoint analysis cannot identify training-objective causality. The route would therefore be costly and method/architecture-adjacent relative to the explanatory remainder.

**Anti-resurrection:** do not infer `next-token loss causes delayed composition` from another layerwise probe/patch or cross-family GPT-vs-BERT comparison. A genuine test requires controlled training and would need fresh Selection as a substantially different project.

---

# Round checkpoint

**New survivor: 0.**

P73 remains the only object in full Selection audit. P69 remains HOLD due opaque ownership. Broad search continues.