# Re-audit — Novelty Calibration (2026-09-18)

**Purpose.** Re-audit the existing `FAILED_TOPICS*` ledgers after correcting an overly strict novelty rule. The old ledgers remain useful negative/process evidence and are not overwritten. This file is an overlay: it records which old kills still stand, which should be reopened only as generators, and which deserve a fresh serious audit.

## 1. Corrected novelty rule

Do **not** kill a topic merely because:

- the broad parent question already has literature;
- the same scientific object has already been studied;
- related behavioral work exists and the proposed work is mechanistic;
- one half of the proposed contrast appears in one prior and the other half appears in another;
- the mechanism family, interpretability tool, or experimental paradigm is already known.

Instead ask:

> **Has the nearest prior already answered the same decisive unknown with evidence that can distinguish the same scientifically meaningful competing worlds?**

Overlap is normal. A topic can still be Main-level when it changes the explanatory question, identifies a quantity that prior work did not identify, explains a known effect, distinguishes previously conflated mechanisms, studies formation rather than endpoint behavior, or gives causal evidence that changes the scientific interpretation.

At the same time, this is **not** a general lowering of the bar. Keep killing topics when:

- the same decisive unknown is already directly answered;
- the proposed distinction is not identifiable;
- the tension disappears in the ideal-model limit;
- the project is mainly a new measurement/probe with no independent behavioral/computational question;
- the mother question is too narrow to carry a Main-level story even if the exact cell is novel;
- the proposed novelty is mostly a new model, dataset, modality, terminology, or cleaner replication.

### Calibration against real taste

The target is a **load-bearing knowledge delta**, not minimum overlap. Strong recent papers repeatedly reuse crowded scientific objects while changing the explanatory question: endpoint → formation dynamics, behavioral effect → causal source, decodability → deployment, known vulnerability → shared mechanism, or old debate → newly identifiable causal distinction.

This is consistent with Sasano's judgments: a natural extension of a prior idea can still have novelty if the new question is meaningful, while a technically novel result can still be weak if its central finding is unsurprising. Top-conference framing must both convince an average reviewer that the question is necessary and make the answer interesting.

---

## 2. Re-audit status vocabulary

### KEEP KILL
The topic remains dead after the corrected novelty audit. The reason may be same-unknown ownership, identifiability, weak mother-question width, ideal-model collapse, or methodological rather than scientific novelty.

### REOPEN-GENERATOR
The old kill reason was too broad or overly dependent on parent ownership, but the topic is **not yet a viable candidate**. Keep the underlying question-forming pressure as a generator. It must acquire a natural high-value instance, a clean identifying intervention, or a sharper law before becoming serious.

### REOPEN-SERIOUS
The old kill no longer stands. The mother question survives the same-unknown audit and deserves a new full prior/identification/feasibility audit. This status is **not** PILOT-AUTHORIZED and is not a claim that the topic is already a survivor.

---

# 3. REOPEN-SERIOUS

## RS1 — F45 + F62 merged: How does an autoregressive model revise a committed internal state?

**Old fragments.**
- F45: semantic retraction / mid-utterance repair in an append-only Transformer.
- F62: revision as local state update versus regeneration.

**Why the old kills were too strict.** Both were largely rejected because repair, belief revision, editing, and self-correction already had behavioral literatures, so a hidden-state/causal analysis was classified as a mechanistic follow-up to an occupied parent. Under the corrected novelty standard, that is insufficient. Behavioral evidence that a model can or cannot revise does **not** answer how an already established internal interpretation is transformed when later evidence contradicts it.

**Reconstructed mother question.**

> Once a model has committed internally to an interpretation, belief, plan, or state, what computation makes later contradictory evidence replace only the consequences that should change while preserving unaffected information?

This should not be framed narrowly as `Turn left—sorry, right`, nor as another self-correction benchmark. The broader scientific pressure is **selective state revision under append-only evidence**.

**Competing worlds.**
1. **Local update:** a structured state variable is edited while unrelated state is preserved.
2. **Suppression / gating:** the old state remains represented but is prevented from controlling downstream computation.
3. **Parallel states + selection:** old and new interpretations coexist and context selects which one is behaviorally active.
4. **Reconstruction / recomputation:** the model largely rebuilds the relevant state from the full prefix rather than editing a persistent state.

**Why current nearest priors do not obviously close it.** Recent belief-revision and self-correction work establishes when models update, when they resist correction, and which contextual factors trigger correction. That is adjacent but not identical to the decisive unknown above: the internal state transformation implementing selective revision. Some very recent projects are beginning to approach mechanistic belief revision, so this needs an immediate current-date collision audit before promotion.

**Identification requirement.** A useful design must make the four worlds predict differently. Merely probing whether the old/new fact is decodable is insufficient. The experiment needs interventions that separately alter the old state, the correction signal, and unaffected state variables, and then test downstream consequences that should selectively update.

**Status:** **REOPEN-SERIOUS.** Full novelty + identification audit required before any pilot authorization.

---

# 4. REOPEN-GENERATOR

## RG1 — F16 upgraded: Conditioning-only information → parameter writeability under response-only SFT

**Old question.** Can assistant-only / completion-only SFT learn new information that appears only in masked prompt/user tokens?

**Why the old kill was too broad.** Prompt-loss literature shows that adding direct loss over instructions changes generalization and memorization, but this does not by itself answer the more specific learning question. Separate extraction work shows that completion-only training can leave parameter traces of prompt-side information, so the simple yes/no `can it be learned?` is also no longer enough.

**Better generator.**

> **What determines whether information used only as a conditioning variable is written into parameters, versus merely used transiently to predict supervised outputs?**

The interesting object is a **selective writeability law**, not prompt masking itself. Candidate factors would need to be theoretically load-bearing (for example, whether the response causally depends on the input-side information) rather than a sweep over mask ratios or fact types.

**Status:** **REOPEN-GENERATOR.** Do not promote until a natural high-value contrast forces different predictions.

## RG2 — F07 upgraded: genuine training hysteresis, not ordinary curriculum effects

**Old question.** Same examples, different order → different final model.

**Why the old kill was too broad.** Existing curriculum/data-order work proves that order matters, but `order matters` is not identical to a true hysteresis/path-dependence law.

**What would make it distinct.** A closed-loop intervention in which the learner is brought through different paths and then returned to the **same data/objective regime**, yet remains in different stable computational states; ideally there should be a state variable or threshold that predicts the non-equivalent return paths.

Without that, the topic remains ordinary curriculum learning.

**Status:** **REOPEN-GENERATOR.** Low priority until a concrete natural capability exhibits a real hysteresis signature.

## RG3 — F09 upgraded: blocking-specific learning signatures beyond generic gradient starvation

**Old question.** Does an already learned cue block acquisition of another predictive cue?

**Why the old kill was too broad.** Generic feature competition / gradient starvation does not automatically subsume every signature of associative blocking.

**What would be needed.** A genuinely blocking-specific intervention—e.g. acquisition/recovery patterns that generic gradient starvation would not predict—and a modern-model reason for caring about it beyond importing a psychology term.

**Status:** **REOPEN-GENERATOR, low priority.** Do not revive as `does the LM show blocking?`.

## RG4 — F75a: represented-but-unused → causally deployed during adaptation

**Old question.** A variable is already decodable before fine-tuning but behavior does not use it. When fine-tuning makes behavior depend on it, did the representation, routing/transformation, or readout change?

**Why the old kill was too broad.** `Decodable ≠ causally used` and `fine-tuning repurposes features` are both active literatures, but neither automatically answers the developmental transition in a particular system.

**Why it is not serious yet.** In abstract form, it is still `representation → use` as a mechanistic template rather than an independently important mother question. It needs a natural behavior where the distinction changes our understanding and where representation-change, routing-change, and readout-change make opposing predictions.

**Status:** **REOPEN-GENERATOR.** The separate F75 `independent corroboration ≠ repeated evidence` remains killed.

## RG5 — F84: transient developmental scaffolds

**Old question.** Can a representation/computation that disappears by the final checkpoint nevertheless be causally necessary for the final capability to emerge?

**Why the old kill was too categorical.** A broad parent being visible in grokking/learning-dynamics theory does not make every developmental mechanism paper old.

**Why the generic topic still is not open.** Recent work now tracks feature emergence/maintenance/discontinuation over checkpoints, and grokking theory gives explicit cases where an early memorization phase creates gradients that enable later feature learning. Therefore `temporary stage helps later stage` is not enough.

**What could revive it.** A natural foundation-model capability in which a **specific transient computation** disappears from the final model yet training-time intervention shows it was necessary for the later mechanism to form. The result must teach a formation law not reducible to generic memorization→generalization dynamics.

**Status:** **REOPEN-GENERATOR.** Strong generator, not a topic yet.

## RG6 — F99: pretrained geometry as a constraint on downstream learnability

**Old question.** Are downstream mappings easier to learn when aligned with existing pretrained representational/computational manifolds than when equally complex targets require leaving them?

**Why the old kill was too broad.** Representation geometry, intrinsic dimension, and transfer all exist, but that does not by itself answer every causal geometry→learnability question.

**Why it is not serious yet.** Very recent theory directly studies how teacher geometry shapes optimization learnability, and adaptation/manifold work already links geometry to transfer. A foundation-model version needs more than a clean causal instantiation of that general relation.

**What could revive it.** A foundation-model-specific qualitative regime change or paradox—something stronger than `more aligned targets learn faster`—with an intervention that changes geometry while preserving target complexity/function.

**Status:** **REOPEN-GENERATOR.** Keep the pressure, do not pitch the current formulation.

---

# 5. Important re-audits that remain KEEP KILL

The corrected novelty standard does **not** rescue most old topics. Representative cases:

- **F01 uncertainty lost vs unreadable:** the latent-knowledge/readout separation is already directly demonstrated; another post-training recipe is not a different unknown.
- **F03/F04/F05:** schema evolution, ambiguous external-effect recovery, and token-vs-conversation SFT weighting have very close direct owners.
- **F08 student > teacher:** mature self-distillation puzzle and explanation space.
- **F10 success-only selection / accidental success:** sparse-reward and credit-assignment work already directly owns spurious successful trajectories.
- **F11–F14:** invariance from paraphrases, ordinal/cardinal reward, indirect negative evidence, and productive abstraction are mature parents with close modern instantiations.
- **F15 error→reflection→correction SFT:** existing partial-masking recipes directly target the contradiction; the remaining `full-loss can perhaps still help` variant currently lacks a broader scientific story.
- **F17–F23 except F16:** cross-document reset, interference, plasticity, instruction drift, feature reuse/drift, pragmatic post-training, and epistemic-qualifier factual acquisition all have close current owners. In particular, F21 is strongly covered by recent feature-drift work, and F23 by Negation Neglect-style acquisition studies.
- **F24–F44:** provenance binding, one-to-many SFT diversity, lexical/prosodic shortcuts, mutual exclusivity, gist/verbatim, coercion, priming, causal observation/intervention, rule-vs-local interpolation, encoding specificity, hidden conflict/readout, self-generated text, noisy-channel comprehension, cultural/model collapse, descriptive-vs-normative behavior, chunking, etc. remain either directly occupied or old-question-new-model transfers.
- **F46–F61 except F62:** prototype/exemplar, binding/entity tracking, ambiguity/multi-hypothesis, representation drift, obligation state, likelihood-vs-independent-quantity families, copy/recompute in CoT, diffusion coarse-to-fine, predictive-memory selection, steerability, negative constraints, fast/slow consolidation, uncertainty preservation, latent planning/pruning, paraphrase convergence, and trajectory stability remain covered or unidentifiable.
- **F58 specifically:** remains dead for **identifiability**, not novelty. The proposed intervention cannot cleanly vary latent uncertainty while holding the relevant causal context/history fixed.
- **F63–F74:** weight tying, prediction→action, normalized-confidence bypasses, internal evaluator, ICL-vs-in-weight learning, visual/text pathways, object permanence, speech timescales, invariant causal representations, latent intention, task-aware acoustic routing, update-order commutativity remain direct neighbors of strong current literatures. F64 also loses its headline tension in the ideal conditional-model limit.
- **F67 specifically:** recent ICL-vs-fine-tuning work directly compares inductive biases and internal representations, so this is not merely a case of `same broad parent`.
- **F76/F78/F79:** task-conditioned circuit selection, default/rule competition, and diffusion-token dependency propagation now have direct or extremely close current work. F78 stays dead even though `old behavioral question + mechanism` is no longer automatically disqualifying, because recent mechanistic work already studies competing default/rule pathways.
- **F80–F83/F85–F98 except F84/F99:** turn-taking cue integration, similarity metrics, prerequisite curricula, cyclic preference, played-vs-generated speech history, latent planning, conditional consistency, common-cause fusion, backup circuits, relational binding, representation convergence, understanding-vs-generation granularity, binding/superposition capacity, robustness allocation, counting, mixed selectivity, linear-representation theory remain close to existing decisive questions.
- **F89 circuit bootstrapping:** keep killed as a **topic**. ICML 2024 already gives a strong training-time causal formation study for induction heads, and later learning-dynamics work broadens the formation picture. Preserve `multi-component developmental dependency` only as a growth operator. A genuinely new natural formation paradox could generate a new topic later, but `another circuit bootstraps itself` is not enough.
- **F100–F109:** data examples teaching content vs computation, depth-vs-representation tradeoffs, sufficiency/halting, state-vs-operator, higher-order attention, circuit composability, attention-sink no-op, event segmentation, gauge-invariant interpretability, and information-seeking/dual control remain either directly occupied, too generic, or methodological.
- **F105 circuit composability:** stays dead because ACL 2025 directly asks whether learned circuits compose into more complex capabilities; this is same-unknown ownership, not mere parent overlap.
- **F106 attention-sink no-op:** stays dead because the functional role, architectural necessity, minimal construction, and constraint-removal test have effectively already been done.

---

# 6. Topics whose old kill reason was softened but that still do NOT reopen

These are important because the revised standard changes the reasoning without changing the verdict.

### F06 — omission/default semantics
The exact cell may be less owned than the old ledger implied, but the honest mother question remains too narrow/tool-API-specific and easily compresses to underspecified intent / argument completion. **KEEP KILL for width, not because every adjacent parent is occupied.**

### F15 — positive loss on bad steps
The old `partial masking exists, therefore done` argument was too fast. But a paper centered only on whether full positive loss can somehow avoid reproducing bad steps is currently too recipe-specific and lacks a larger explanatory tension. **KEEP KILL unless a broader learning law emerges.**

### F17 — EOS reset
Behavioral/cross-document and attention-sink work does not literally answer every EOS-reset mechanism. Nevertheless the current formulation is still an architecture micro-question with weakening practical centrality as explicit document masking/state resets become common. **KEEP KILL for importance/width.**

### F78 — rule/exception override
`Old cognitive question + mechanism` is no longer an automatic kill. However recent work now directly constructs default-vs-rule conflicts and identifies separate competing pathways, so the same decisive computation is being studied. **KEEP KILL after a stronger same-unknown audit.**

### F89 — circuit bootstrapping
A new circuit-formation paper is not forbidden merely because induction-head formation exists. The problem is that F89 as written contains no independent new formation puzzle beyond the general template. **KEEP KILL as a topic; retain as a generator pattern.**

### F100 — content vs reusable computation attribution
Motion-style causal decomposition is a valid growth pattern, but current reasoning/data-attribution and capability-provenance work already makes this lane active, and the topic would pull the search back toward a data-centric story the user does not prefer. **KEEP KILL.**

---

# 7. Re-audit outcome

**No old topic is automatically restored to PILOT-AUTHORIZED.**

The corrected audit yields:

- **1 REOPEN-SERIOUS family:** merged **F45 + F62** — selective internal state revision after contradictory evidence.
- **6 REOPEN-GENERATORS:** **F07, F09, F16, F75a, F84, F99**.
- **All remaining old kills stay killed**, although several now have a better reason than `the broad parent already exists`.

The main process correction is therefore **not** `be more permissive`. It is:

> **Preserve the width of a natural mother question, tolerate normal prior overlap, and kill only after checking whether the nearest work already answers the same decisive unknown—or whether the idea fails for an orthogonal reason such as identifiability, importance, or story width.**

A second correction is equally important:

> **Do not fragment one real scientific question into multiple exact-cell variants merely to escape prior work.** F45 and F62 become more credible when merged upward into selective state revision; F16 becomes more credible when upgraded from a yes/no masking corner case into a selective parameter-writeability question.

This overlay should guide the next search round. Old ledgers remain useful, but `parent occupied` by itself is no longer a sufficient kill reason.