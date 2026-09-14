# 2026-09-14 — WALL-E Disagreement Map

**Wall:** developmental state / path dependence  
**Mode:** RIVAL-EXPLANATION MAP — **NO CANDIDATE GENERATION**  
**Input:** `2026-09-14_STANDING_STATE_EXPANSION_II.md`  
**Purpose:** distinguish the different scientific mechanisms that can make two behaviorally similar learners respond differently to the same later experience.

---

# 0. The first correction: "history matters" is not an explanation

WALL-E can easily collapse into a trivial statement:

> neural training is path dependent; different update orders produce different parameters.

That is not the scientific problem.

For a fixed architecture, exact parameter state, optimizer state and future minibatch sequence, future deterministic updates are already determined. There is no mysterious extra variable called "history" floating outside the current physical state.

The substantive question is instead:

> **Which scientifically meaningful description of the learner's current state is sufficient to predict its response to future evidence?**

In particular:

- current task behavior may be insufficient;
- current input–output function on a focal domain may be insufficient;
- current representations may still be insufficient;
- one scalar "plasticity" may be insufficient.

History matters only insofar as it leaves **latent state** not captured by the observable description we were using.

This makes WALL-E a state-identification problem, not a training-order problem.

---

# 1. Canonical identifying shape from old learning theory

The classical path-dependence experiment has an unusually clean logic:

1. give learners different histories H1 and H2;
2. bring them to the **same current behavioral baseline** on the focal observable;
3. give them the **same new treatment T**;
4. observe whether their future responses diverge.

If they diverge, the matched behavioral baseline was not a sufficient state description.

Ghirlanda & Enquist (2007) explicitly use this logic when discussing path dependence in generalization.

Source:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC2323563/

Associative-learning reviews give even stronger examples: acquisition→extinction can produce the same visible response level as a different history, yet reinstatement or reacquisition reveals different latent state.

Sources:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC1987335/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC2746498/

This logic is useful because it tells us what **must** be explained. But it does not identify why the paths diverge.

---

# 2. Inferential levels that must be kept separate

A future WALL-E descendant can fail if it jumps between these levels.

## L1 — current performance

Do the learners currently produce the same focal response / accuracy / distribution?

## L2 — stored content / latent memory

Do the learners retain different information despite the same current response?

## L3 — representation / computational organization

Do they encode the same information using different features, abstractions, circuits or decomposition?

## L4 — update rule / associability / plasticity

Does the same new evidence have a different effective learning rate or eligibility because prior experience changed the learner's capacity to update?

## L5 — global optimization state

Are differences in future learning caused by generic parameter geometry, conditioning, dormant units, curvature or feature diversity rather than a theory-specific learning state?

## L6 — development / maturation

Is the change caused by experience, or by an exogenous stage variable correlated with experience/time?

## L7 — systems / consolidation

Is history distributed across fast and slow learning systems whose relative contribution changes over time or replay?

A behavioral path-dependence effect at L1 does not uniquely identify any of L2–L7.

---

# 3. Rival account R1 — latent trace / multiple-memory account

## Core claim

Two learners can behave identically now because an older association / computation is **suppressed**, not erased. Their stored contents are therefore different even though the current response is the same.

Extinction is the canonical scientific lineage.

A large literature distinguishes:

- unlearning / erasure of the original association;
- new inhibitory learning that competes with the original association.

Return-of-response phenomena — spontaneous recovery, renewal, reinstatement and savings — are used precisely because ordinary endpoint behavior cannot distinguish the accounts.

Sources:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC4972342/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC3355659/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC523074/

## What it explains

- same current response after different histories;
- rapid reacquisition;
- context-dependent recovery of apparently lost behavior;
- "silent" knowledge that reappears.

## What it does NOT require

It does not require a general change in future plasticity. The learner can have the same learning machinery but different latent stored content.

## Theory-level prediction

A common future treatment should diverge specifically when it re-engages the latent trace / context that differs between histories.

## Relevance to WALL-E

This account warns against interpreting every future-learning divergence as a changed **update operator**. Sometimes the update rule is unchanged and the histories differ only in what remains stored but currently unexpressed.

---

# 4. Rival account R2 — associability / metaplasticity account

## Core claim

Prior learning changes **how learnable something is next**. The history is carried forward in the learner's update rule / eligibility, not merely in stored task content.

Two mature lineages support this idea.

### Associability in behavioral learning

Pearce–Hall-style theories use prediction error to alter a cue's associability — the ease/rate with which it enters into new learning. Thus prior surprise history changes future learning rate.

Review:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC4862921/

### Metaplasticity in neuroscience

Metaplasticity is literally the plasticity of plasticity: prior activity changes the threshold / capacity for later synaptic change, sometimes without changing baseline response.

Sources:
- https://www.nature.com/articles/nrn2356
- https://pmc.ncbi.nlm.nih.gov/articles/PMC3180909/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC4157609/

A particularly useful conceptual definition from this literature is:

> an earlier event leaves a lasting effect on the capacity to change later, rather than merely on current performance.

## What it explains

- equal current response but different later learning rates;
- history-specific sensitivity to new evidence;
- learning-to-learn or learning-to-ignore effects.

## Theory-level prediction

If the key difference is associability / metaplasticity, divergence should appear in **new learning induced by the common treatment**, not only in retrieval of an old latent trace.

## Relevance to WALL-E

This is closer to the wall's central quantity than generic transfer. It suggests that the learner has a **second-order state** controlling how first-order parameters respond to evidence.

---

# 5. Rival account R3 — representation / feature entrenchment account

## Core claim

History changes the features or abstractions through which later evidence is interpreted.

The future update differs because the same datum is effectively represented differently by the two learners.

This account is adjacent to WALL-B but not identical to it. A learned representation can change:

- which distinctions are easy to express;
- which gradients are available;
- which new categories can be separated;
- which rules count as simple;
- which generalizations appear natural.

Critical-learning-period work in deep networks is relevant evidence: early data can leave lasting representational consequences, and later training may not fully recover the solution reached by an unperturbed developmental path.

Representative lineage:
- Achille, Rovere & Soatto, *Critical Learning Periods in Deep Neural Networks*: https://arxiv.org/abs/1711.08856
- Kleinman, Achille & Soatto, *Critical Learning Periods Emerge Even in Deep Linear Networks*: https://arxiv.org/abs/2308.12221

## What it explains

- history-specific generalization under matched training performance;
- different transfer to related tasks;
- difficulty learning distinctions that conflict with an entrenched representation.

## Theory-level prediction

Future divergence should be **structured by the representational relation** between earlier and later tasks, not simply by elapsed training time or global trainability.

## Main danger

This account can become a vague post-hoc statement: "representations changed."

A valid use requires an independently motivated feature / abstraction distinction and a qualitative prediction about which future evidence should be easier or harder.

---

# 6. Rival account R4 — optimization geometry / generic plasticity account

## Core claim

The histories leave different optimization states even when focal predictions are similar.

Examples include differences in:

- curvature / conditioning;
- gradient magnitudes;
- dormant or overcommitted units;
- feature diversity;
- parameter mobility;
- effective rank / dimensionality;
- optimizer moments.

Modern plasticity-loss work makes this account unavoidable.

### Evidence

Lyle et al., ICML 2023, find plasticity loss connected to loss-landscape curvature and show that simple saturated-unit explanations are insufficient.

Dohare et al., Nature 2024, show severe loss of plasticity under continual deep learning and distinguish it from catastrophic forgetting.

Lyle et al., CoLLAs 2025, show that plasticity loss decomposes into multiple independent mechanisms.

Sources:
- https://proceedings.mlr.press/v202/lyle23b.html
- https://www.nature.com/articles/s41586-024-07711-7
- https://proceedings.mlr.press/v274/lyle25a.html

## What it explains

- broad reduction in ability to fit new evidence;
- later-stage training becoming less responsive;
- rescue by generic interventions such as resets / normalization / weight-control methods.

## Theory-level prediction

Divergence should generalize across many future tasks that demand similar parameter mobility, even when those tasks are semantically unrelated to the historical content.

## Relevance to WALL-E

This is a strong null explanation for any language-specific developmental story:

> perhaps the two histories do not install different linguistic states at all; one simply leaves a more/less trainable optimization geometry.

Any substantive NLP descendant would need to beat this explanation.

---

# 7. Rival account R5 — maturation / exogenous plasticity schedule

## Core claim

The learner's future learnability changes because of a developmental program or stage variable that is **not reducible to accumulated experience**.

This is central to the critical-period debate in language acquisition.

Constantinescu et al., TACL 2025, explicitly test whether L1 experience alone induces human-like critical-period effects in LMs. It does not in their setup; explicitly imposing reduced plasticity with EWC can produce the relevant effects.

Source:
- https://aclanthology.org/2025.tacl-1.5/

## What it explains

- age/stage-dependent learning differences not recreated by simply giving more early experience;
- simultaneous changes in new-language learning and resistance to attrition.

## Theory-level prediction

Holding experience content constant but changing the exogenous plasticity schedule can alter future learning. Conversely, different experience histories need not diverge if they do not change the relevant developmental stage.

## Relevance to WALL-E

This account forces a distinction between:

> history changes the learner

and

> a separate developmental process changes the learner while history happens alongside it.

Modern neural models are useful precisely because these causes can be experimentally separated.

---

# 8. Rival account R6 — complementary learning systems / consolidation account

## Core claim

A learner is not one homogeneous storage/update system. Fast and slow systems can hold different parts of the learning state, and consolidation/replay changes how new information is integrated.

Complementary Learning Systems (CLS) was developed partly as a solution to the stability–plasticity dilemma: fast hippocampal-like learning and slower neocortical integration serve different roles.

Sources:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC7209926/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC6794196/

## What it explains

- time / replay-dependent integration;
- fast acquisition without catastrophic rewriting of slow structure;
- prior knowledge allowing some new information to integrate faster than a purely slow system predicts.

## Theory-level prediction

Future learning differences can depend on what was consolidated, replayed or integrated, even when immediate performance is matched.

## Relevance to WALL-E

This account suggests that the relevant state may be **where** information is stored and how learning systems interact, not only which representation exists at one checkpoint.

For current transformers, the biological decomposition itself cannot be imported literally. The useful scientific coordinate is the distinction between fast/local traces and slower reusable structure.

---

# 9. Rival account R7 — contextual retrieval / expression account

## Core claim

Histories may produce the same stored knowledge and even the same basic learning machinery, but current / future behavior differs because contextual cues control **which state is expressed**.

Extinction and renewal literatures make context dependence central: the original association can survive while extinction learning is expressed only in some contexts.

Sources:
- https://pmc.ncbi.nlm.nih.gov/articles/PMC3355659/
- https://pmc.ncbi.nlm.nih.gov/articles/PMC541370search12/  
  *(note: use the first URL above as canonical; this line records the retrieval/context family, not a separate source identity.)*

## What it explains

- recovery without new acquisition;
- response shifts after context changes;
- apparent path dependence caused by retrieval gating rather than different stored content or update capacity.

## Relevance to WALL-E

A future neural-model experiment can falsely infer altered learning when a history merely changes **which computation is recruited** during training or evaluation.

This is especially dangerous in LMs where prompt / context can change routing without changing stored parameters.

---

# 10. Evidence matrix

Legend: **✓** naturally explains; **~** compatible; **×** not sufficient on its own.

| Signature | latent trace / multiple memory | associability / metaplasticity | representation entrenchment | optimization geometry | maturation | consolidation / multi-system | contextual retrieval |
|---|---:|---:|---:|---:|---:|---:|---:|
| same current response, later old behavior returns | **✓** | ~ | ~ | × | ~ | ✓ | **✓** |
| same current response, identical *new* learning differs | ~ | **✓** | ✓ | **✓** | ✓ | ✓ | ~ |
| divergence is specific to related structures/tasks | ✓ | ✓ | **✓** | ~ | ~ | ✓ | ✓ |
| broad loss of ability to learn unrelated tasks | × | ✓ | ~ | **✓** | ✓ | ~ | × |
| history effect disappears under context change | ✓ | ~ | ~ | × | × | ~ | **✓** |
| explicit plasticity schedule recreates effect | × | ✓ | ~ | ✓ | **✓** | ~ | × |
| replay/time after experience changes later integration | ✓ | ~ | ~ | ~ | ~ | **✓** | ✓ |
| generic reset / geometry intervention rescues later learning | × | ~ | ~ | **✓** | ~ | ~ | × |

The matrix shows why "same endpoint → different later trajectory" is not enough. Multiple mature accounts predict it.

---

# 11. The most important construct split: **stored state** vs **learning state**

The literature reveals two fundamentally different reasons history can matter.

## Stored-state account

> What the learner currently contains differs, even if current behavior hides the difference.

Examples:
- old association survives extinction;
- multiple memories compete;
- context gates which memory is expressed.

## Learning-state account

> What the learner will do with *new evidence* differs because its update capacity / representation / associability changed.

Examples:
- metaplasticity;
- critical-period / maturation effects;
- plasticity loss;
- representational entrenchment.

This distinction is more useful than generic "memory vs learning" rhetoric because it produces different common-treatment predictions.

A future WALL-E project must say which one it is about **before** designing the manipulation.

---

# 12. A second construct split: **global plasticity** vs **theory-specific developmental state**

Suppose history H1 makes a model learn future linguistic relation Y more slowly than H2.

At least two explanations exist:

### Global account

H1 simply left the network harder to optimize / less plastic overall.

### Structured account

H1 specifically changed the representation, prior or associability relevant to Y.

A meaningful scientific explanation must distinguish them.

This is likely the most important null explanation for any future NLP descendant of WALL-E.

---

# 13. What modern foundation models genuinely improve

The new regime offers several identifying operations that older biological work often could not perform jointly:

1. **Exact history control** — multiple learners can receive precisely specified histories.
2. **Checkpoint access** — latent state can be measured throughout formation, not reconstructed from endpoints.
3. **Common-treatment interventions** — after matching a theory-defined behavior, learners can receive byte-identical new evidence.
4. **Update observability** — gradients / parameter changes / representation changes can be read after the same event.
5. **Matched architecture** — developmental histories can vary while architecture stays fixed.
6. **Counterfactual intervention** — candidate latent states can sometimes be manipulated before the common treatment.

But none of these automatically identifies the scientific state.

### The key warning

> **Parameter differences are not the discovery.**

Different histories almost guarantee different parameters.

The scientific gain would be finding a theory-defined state variable whose manipulation / measurement predicts the **future learning divergence** better than current behavior and rules out mature rivals.

---

# 14. Direct-owner density after importing modern work

## Highly active / dangerous to generate from directly

- generic loss-of-plasticity mechanisms;
- critical periods in neural networks;
- continual-learning stability–plasticity solutions;
- primacy bias / reset methods;
- curriculum / data-order effects;
- catastrophic forgetting;
- unlearning path dependence.

These are not empty niches.

## Still broad enough to remain a standing problem

What is not reduced to one of those programs is the higher-level scientific question:

> **Which description of a learner's hidden developmental state is necessary and sufficient to predict how the same next evidence will change it?**

That question has ancestry in associative learning, metaplasticity, developmental critical periods, representation learning and continual adaptation, but no one frontier paper owns the entire inferential object.

This is exactly what standing problems are for: important enough to keep even when the immediate publication route is uncertain.

---

# 15. What is actually unresolved after the disagreement map?

## U-E1 — What is the smallest scientifically meaningful learning state beyond current behavior?

The full parameter / optimizer state is algorithmically sufficient but scientifically useless as an explanation.

We do not have a general account of which lower-dimensional state variables predict response to future evidence.

Potential classes — not candidate claims — include:

- associability;
- plasticity / curvature;
- representational commitments;
- latent competing memories;
- feature diversity;
- consolidation state.

---

## U-E2 — When does path dependence reflect stored content versus a changed update operator?

Both can produce the same common-treatment divergence.

This is a true theory-discrimination problem inherited from mature learning science.

---

## U-E3 — Is developmental state global or computation-specific?

Loss-of-plasticity work often measures broad trainability. Language-learning / representation theories predict structured, task-dependent entrenchment.

The field lacks a clean general law for when prior learning reduces plasticity globally versus selectively changing particular future generalizations.

---

## U-E4 — Does behavioral/function matching erase the scientifically relevant history?

Classical path-dependence experiments match a small behavioral observable. Neural models let us match much richer function classes, but exact full-function equivalence is infeasible.

The identification problem becomes:

> how much matching is enough before a later divergence is evidence about hidden developmental state rather than an unnoticed current-function difference?

This is a severe methodological constraint.

---

## U-E5 — Which current mechanistic observables are causal state variables rather than correlates of age/history?

Curvature, dormant units, Fisher information, representation similarity and gradient norms can all correlate with training age.

A useful developmental variable must predict / mediate future learning under a common treatment, not merely track time.

---

# 16. Anti-resurrection / anti-autocomplete constraints

WALL-E does **not** authorize any of the following:

- L34 repaired with a better curriculum;
- L19 transfer with a different dataset;
- "pretrain order A vs B";
- "same accuracy, different weights";
- catastrophic-forgetting benchmark work;
- unlearning-history follow-up;
- plasticity metric invention;
- "early layers freeze first" descriptive training dynamics;
- base vs instruct / SFT vs RL checkpoint comparison without a mature rival account.

The common-treatment logic is necessary but not sufficient.

A future question would also need:

1. a mature theory-defined hidden state;
2. a rival account at the same inferential level;
3. a common treatment with divergent qualitative predictions;
4. a global-plasticity null control;
5. a reason the result matters beyond one curriculum or task.

---

# 17. Pressure maturity after the map

### Importance

**VERY HIGH.** The wall asks what the state of a learner actually is, not merely what it can currently do.

### Research intimacy

**VERY HIGH.** Controlled training histories, post-training, gradients, internal states and checkpoint analysis are core strengths.

### Scientific ancestry

**VERY HIGH.** Path dependence, extinction, associability, metaplasticity, critical periods and stability–plasticity are old mature programs.

### Immediate search headroom

**MODERATE.** Many obvious descendants are active owner programs.

### Identification readiness

**MEDIUM.** The disagreement map produces real rival accounts, but a clean natural NLP object has not yet been selected.

## Decision

**WALL-E remains ACTIVE. Candidate generation remains OFF for one more step.**

The next step should not be "invent 20 WALL-E topics."

It should search for **natural NLP / language-learning phenomena in which two of the mature accounts above make genuinely different predictions under the same common-treatment operation**.

The phenomenon must already matter independently of WALL-E; we must not fabricate a synthetic task merely to instantiate path dependence.

---

# 18. Searcher lesson

WALL-E shows why standing-state search differs from paper-gap search.

A frontier-first search would likely produce:

> "Plasticity loss is hot; study plasticity loss in LLM post-training."

The lineage-first state instead says:

> For decades, learning science has known that equal current behavior can hide different histories. The unresolved question is **which hidden state carries that history forward into future learning**. Plasticity loss is one modern explanation family, not the question itself.

That distinction is the whole point of the new searcher.

---

# 19. Current decision

**New RQ seeds:** 0.  
**New L-series:** 0.  
**New K-series:** 0.  
**Pilot:** none.

WALL-E now has enough scientific ancestry and disagreement structure to remain on the long-term wall. It is **not yet authorized to autocomplete into a project**.
