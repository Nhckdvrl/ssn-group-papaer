# L12 Claim Novelty Delta

**Audit date:** 2026-09-11

**Trigger:** E18-E20 changed the paper from a behavioral-invariance explanation to
selective sensitivity; a subsequent proposal would change it again to
invariance-causality alignment. Under `RESEARCH_EXECUTION.md`, both are material
claim mutations and neither inherits the original topic-selection approval.

## Verdict

**HOLD / RECONSTRUCT.**

The research question remains strong and E01-E22 remain a valuable evidence
inheritance. The current paper identity has not, however, re-earned Main-level
novelty. The proposed replacement, **Reasoning closes the invariance-causality
gap**, is a useful competing account but is not yet a novelty-sufficient paper
idea. Do not scale models, domains, layers, or confirmation under that label.

## 1. Old and mutated identities

### Original selected question

> Why does reasoning-oriented post-training make risky choices more invariant to
> framing and presentation: representational canonicalization, policy override,
> or inference-time deliberation?

This was novel relative to the original parent package because *Mind the (DH)
Gap!* established the behavior but did not explain its mechanism.

### E07-E09 mutation

> Natural reasoning progressively constructs a decision and reallocates causal
> control from prompt presentation toward a trajectory-built pre-answer state.

This changed a canonicalization/override question into a causal-route claim.
Trace causality, iterative answer formation, and reasoning-induced latent policy
states are now heavily owned by direct work. The fact that L12 connects them to
the parent behavior is real but does not automatically make the mechanism ours.

### E18-E20 mutation

> Reasoning reallocates sensitivity from presentation form to decision evidence.

E18 falsified blanket description/history invariance. E20 repaired the construct
by orthogonalizing form and finite-sample evidence. This is a better and more
accurate explanation of the data, but its ingredients have direct owners:
robustness to irrelevant/surface factors versus sensitivity to task-relevant
factors; finite-history sampling differences; trajectory/state control; and
reasoning-related control shifts.

### Proposed new mutation

> Reasoning does not primarily create invariant representations; it makes
> abstract, task-relevant representations causally actionable, thereby closing
> an invariance-causality gap.

Proposed short identity:

> **Reasoning Aligns Causal Decision Control with Task-Relevant Invariance.**

This proposal is broader than “trajectory takeover,” but broad wording is not the
same as broad novelty.

## 2. What evidence forced the latest reconsideration

The trigger is chiefly a fresh ownership audit, not a new L12 result.

- E03 shows that form/frame information remains decodable. It does not measure an
  invariant task representation or its causal use.
- E20 shows behaviorally selective form/evidence sensitivity. It does not by
  itself establish representational abstraction.
- E21 shows that a late donor state has more causal leverage for evidence than
  form. It does not show that this state is invariant across form, that an
  invariant subspace causes the choice, or that reasoning reduced a measured
  invariance-causality gap relative to a standard regime.
- Fresh work directly separates invariant representations from causal drivers,
  causally validates format-agnostic reasoning subspaces, and studies alignment
  at semantic bottlenecks. Reinterpreting E03/E20/E21 through those concepts
  therefore creates a new claim that requires a new novelty and identification
  audit.

## 3. Closest direct owners

| Work | What it already owns | What remains potentially open |
|---|---|---|
| [*Mind the (DH) Gap!* (ACL 2026 Outstanding)](https://aclanthology.org/2026.acl-long.479/) | Reasoning/conversational differences in risky-choice invariance over framing, order, explanation, and description/history. | A mechanism that survives current MI ownership. |
| [*A Causal Framework to Quantify the Robustness of Mathematical Reasoning with Language Models* (ACL 2023)](https://aclanthology.org/2023.acl-long.32/) | The normative distinction between robustness to surface form and sensitivity to operands/operators, formalized through input interventions. | Internal causal implementation and reasoning-post-training change. |
| [*Causality != Invariance: Function and Concept Vectors in LLMs* (ICLR 2026)](https://arxiv.org/abs/2602.22424) | Abstract, format-invariant concept representations differ from the representations that causally drive ICL behavior; causal vectors are format-bound while invariant vectors transfer better across format/language. | Whether a controlled training regime systematically changes this relationship. |
| [*Beyond Language: Format-Agnostic Reasoning Subspaces* (2026)](https://arxiv.org/abs/2605.09496) | Format-agnostic reasoning structure using RSA, cross-form probes, cross-form activation patching, targeted ablation, held-out concepts, and five models/three families. | A clean training-axis change in causal use, if independently identified rather than inferred from patch compatibility. |
| [LASA (ACL 2026)](https://aclanthology.org/2026.acl-long.1913/) | Identification of a semantic bottleneck organized by shared semantics rather than language identity, then anchoring downstream safety alignment to that abstract space. | Whether reasoning training naturally produces an analogous change, rather than a designed method doing so. |
| [*Reasoning Fine-Tuning Induces Persistent Latent Policy States* (COLM 2026)](https://arxiv.org/abs/2607.18532) | Reasoning fine-tuning globally reorganizes latent dynamics; states are stage-specialized, causally functional, and transferable across 1.5B-32B models and four benchmarks. | The content-specific relationship between abstraction and causal control, if sufficiently broad and separately measured. |
| [*Hidden APIs in Language Models* (2026)](https://arxiv.org/abs/2607.27617) | Hidden-state equivalence defined by downstream future operations, empirical causal quotients, reusable interfaces, transplantation, and backbone breadth. | Do not claim a new causal quotient/interface merely because cross-form states are interchangeable. |
| [*State Commitment Learning* (2026)](https://arxiv.org/abs/2606.05201) | Persistent-state sufficiency as a counterfactual criterion and a training method that commits future-relevant information while discarding scratch computation. | Do not sell decision-state sufficiency or commitment as L12's center. |
| [*Readable but Not Controllable* (2026)](https://arxiv.org/abs/2607.00158) | A concrete decodability-controllability gap across 16 medical model-dataset settings. | The general “information exists but lacks causal actionability” framing is not unowned. |
| [*Scaling Reasoning, Losing Control* (ACL 2026)](https://aclanthology.org/2026.acl-long.1878/) | Reasoning-oriented training can improve reasoning while reducing external instruction control, especially with longer generation. | A distinct causal account of which representations gain control. |

Other nearby ownership includes generic injected-trace causality, iterative answer
formation during CoT, causal state transplant, long-context “know but do not use,”
and explanation-based robustness to spurious cues. These are not merely shared
methods; together they occupy much of the proposed scientific abstraction.

## 4. What is genuinely new in the proposed alignment version

The narrow remainder is:

> Compare a reasoning and standard regime and test whether the relationship
> between format invariance and causal actionability changes, using risky
> decisions where form and evidence can be orthogonalized.

This is not zero novelty. Neither the ICLR paper nor FARS reports this exact
reasoning-versus-standard training/mode comparison. However, at present the
remainder is primarily **a new axis applied to an already defined gap**, not yet a
new explanatory principle.

The phrase “reasoning makes abstract representations causally actionable” also
smuggles in three facts that L12 has not measured:

1. the relevant representation is genuinely abstract/invariant;
2. the same representation, rather than a correlated answer direction, controls
   behavior;
3. reasoning caused a change in the relation between abstraction and control.

Current evidence establishes none of these jointly.

## 5. Strongest reviewer compression

> *Mind the DH Gap* supplies the reasoning-invariance phenomenon; Stolfo et al.
> supply form-robust/task-relevant sensitivity; *Causality != Invariance* and
> FARS supply the invariant-versus-causal representation distinction and
> cross-form patching; LASA supplies alignment to a semantic bottleneck;
> Persistent Latent Policy States supplies reasoning-fine-tuning reorganization.
> L12 checks whether these known ideas coincide on CPC18 and a few reasoning
> checkpoints.

After removing those owners, the surviving statement is:

> reasoning-versus-standard regimes may differ in cross-form causal transfer on
> risky-choice decision states.

That is understandable, but currently too close to “known object + new model axis
+ our domain/intervention” to carry an ACL/EMNLP/NAACL Main paper by itself.

## 6. Main-level width test

| Test | Assessment |
|---|---|
| Natural question after removing model/layer/method names | **Pass.** Do models act on the abstract information they encode, and does reasoning change that? |
| Non-obvious answer | **Conditional pass.** Either closure or persistence of the gap is not guaranteed. |
| New scientific object rather than conjunction | **Fail at present.** Invariance-causality gap, format-agnostic subspaces, semantic alignment, and reasoning-state reorganization are already separately and substantially developed. |
| Clean gap after naming strongest priors on page one | **Fail/HOLD.** The defensible gap becomes the reasoning-axis comparison. |
| Existing evidence identifies the claim | **Fail.** E03/E20/E21 do not independently measure representational invariance and causal actionability in both regimes. |
| Main-scale evidence burden | **Not met.** A general post-training/representation claim would need controlled lineage, multiple natural transformation families, independent invariance and causality measures, and a mechanism-consequence link. |

Result: **HOLD**, not pilot-approved as a paper mainline.

## 7. Why the proposed cross-form transplant is not decisive as written

Proposed operation:

```text
same evidence: raw state -> summary target
same evidence: summary state -> raw target
opposite evidence: donor state -> target
compare reasoning vs standard regimes
```

This is a useful diagnostic, but success does not uniquely identify alignment.

### Confound 1: late answer commitment

A late state can transfer across forms because it already contains an A/B choice
direction. That does not show an abstract evidence representation became causally
actionable.

### Confound 2: residual-interface compatibility

Cross-form patch success can reflect compatible activation scale, token position,
or downstream decoder geometry. FARS already shows that cross-form activation
replacement can work. A branch difference does not automatically identify why.

### Confound 3: unequal computation

Raw and summary prompts differ in length and induce different trajectories.
Reasoning and standard regimes also differ in generation route, commitment
strength, and validity. A larger transfer effect may reflect stronger or later
commitment rather than smaller invariance-causality gap.

### Confound 4: E21 near-duplication

Opposite-evidence state transfer is already strongly predicted by E21. Repeating
it under cross-form cells can improve construct detail, but it cannot by itself
create the new paper identity.

Therefore this experiment must not be preregistered as “the alignment test.” At
most it can neutrally distinguish candidate implementations after a novelty-
sufficient claim is found.

## 8. Candidate reconstructions considered

### A. Invariance-causality alignment

> Reasoning closes the gap between abstract representation and causal control.

**Status: HOLD.** Broad and interesting, but presently a direct follow-up axis to
ICLR 2026 plus FARS/LASA, and not identified by current evidence.

### B. Post-training changes use, not content

> Reasoning post-training leaves abstract content largely intact but changes which
> pre-existing distinctions control behavior.

**Status: HOLD.** Potentially broader, but generic “encoded but unused,”
post-training representation change, latent-policy reorganization, and feature-
level causal intervention are crowded. L12 lacks a clean before/after training
operation and cannot currently establish “content unchanged.”

### C. Online causal abstraction

> Reasoning dynamically constructs a task-relevant causal abstraction rather than
> retrieving a static invariant representation.

**Status: HOLD / collision-prone.** It is close to progressive trajectory work,
persistent policy states, state commitment, and causal quotient/interface work.
Calling it “online” does not create a distinct scientific object.

### D. Behavioral invariance via multiple format-specific causal routes

> Reasoning may produce the same answer from form-specific causal states rather
> than a shared abstraction.

**Status: diagnostic alternative, not a paper identity.** It is a valuable foil to
alignment and could be surprising, but it is readily compressed as
*Causality != Invariance* applied to reasoning-induced risky-choice robustness.

None currently passes the novelty reset.

## 9. What would be required to revive the alignment direction

The direction should be reconsidered only if a minimal diagnostic exposes a
scientific fact stronger than “cross-form patching is larger in Think.” A viable
claim would need all of the following:

1. independent, non-circular measures of representational invariance and causal
   actionability;
2. a controlled reasoning-training or route axis on which their relationship, not
   merely each marginal metric, changes;
3. controls separating evidence representation from terminal answer commitment;
4. at least two natural transformation families with answer-preserving form edits
   and answer-changing semantic edits;
5. an intervention showing that changing the proposed alignment predicts or
   changes the selective robustness consequence;
6. a renewed literature audit showing that the resulting statement is more than
   *Causality != Invariance* on reasoning checkpoints.

This is a new Main-scale research program, not a cheap extension of E21. Existing
E01-E22 can motivate and support it, but cannot pre-authorize it.

## 10. Authorized next action

Under the novelty stop rule:

- no model zoo;
- no second domain merely for breadth;
- no layer scan;
- no large cross-form confirmation;
- no rewrite that presents alignment as established.

The only admissible technical work is a **small, neutral identification diagnostic**
whose outcomes discriminate shared causal abstraction from format-specific causal
routes and which explicitly controls late answer commitment. Even that diagnostic
should be run only after its estimand is written without using “alignment” as an
interpretive shortcut.

Until such a result creates a genuinely new claim and that claim passes another
novelty reset, L12 remains:

> **Good RQ, strong evidence inheritance, no novelty-sufficient current answer.**
