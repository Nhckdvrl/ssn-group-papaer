# L12 — Reasoning-Induced Invariance

## When Reasoning Takes Control

**Status:** **A / CONTINUE-PILOT / Rank 2**  
**Paper mainline:** NOT APPROVED  
**Target:** NAACL Main  
**Last audited:** 2026-09-09

> **Natural question:** Why does reasoning-oriented post-training make decisions dramatically more invariant to framing and presentation? Does long reasoning merely accompany the answer, or does the self-generated reasoning trajectory become the dominant causal controller of the final decision?

---

# 1. Established behavioral substrate

ACL 2026 Outstanding **Mind the (DH) Gap!** establishes the broad phenomenon: reasoning-oriented models are far less sensitive to order, gain/loss framing, explanation, and description/history presentation.

Our matched OLMo sibling-branch pilot independently reproduces a strong contrast on the three published prospects:

- Instruct-SFT frame consistency ≈ **0.817**;
- Think-SFT ≈ **0.992**;
- difference ≈ **+0.175**, bootstrap CI **[0.025, 0.367]**.

These numbers are **frame-consistency measurements**, not generic task accuracy.

---

# 2. What is already known locally

### Supported

- Think-SFT is almost perfectly frame/order-consistent relative to sibling Instruct-SFT.
- Gain/loss frame identity remains recoverable in early/middle prompt representations.
- A complete natural Think-SFT reasoning trajectory has a very large causal effect on final A/B readout:
  - own trace correct margin ≈ **+9.34**;
  - empty trace ≈ **-0.08**;
  - matched opposite-frame trace ≈ **-9.07**.
- Short answer-free arithmetic snippets do **not** reproduce that large effect.

### Not yet established

- whether the whole reasoning process matters beyond its terminal explicit conclusion;
- whether a compact pre-answer decision state mediates the takeover;
- where along the reasoning trajectory that state is constructed.

---

# 3. Core scientific hypothesis

The current mechanistic picture is:

> prompt still carries framing information  
> → long reasoning transforms the computation  
> → the trajectory constructs a decision state  
> → final answer is controlled mainly by that trajectory-built state.

Call this **trajectory takeover** internally.

The competing explanation is much cheaper:

> the long trace matters only because its final sentence explicitly commits to an answer.

That distinction is the next load-bearing experiment.

---

# 4. Claim architecture

### C1 — Behavioral transition

Reasoning-oriented and instruction-oriented sibling branches exhibit a large difference in presentation invariance.

### C2 — Input information is not simply erased

Frame identity remains available in early/middle representations even after the Think branch becomes behaviorally invariant.

### C3 — Natural reasoning strongly controls the readout

Complete natural trajectories causally determine the final A/B margin.

### C4 — Trajectory takeover

The causal control survives removal of the terminal explicit choice/conclusion, showing that the effect is carried by the reasoning process rather than only a copied final commitment.

### C5 — Decision-state mediation

A pre-answer state constructed by the reasoning trajectory causally carries the decision into the final readout.

C4 is next. C5 is only run if C4 survives.

---

# 5. Next decisive experiment

## L12-E07 — Conclusion-Stripped Trajectory Takeover

Reuse the same three audited prospects and natural Think-SFT traces.

Compare forced A/B readout after:

1. the **full own natural trace**;
2. the **same trace with terminal explicit decision/conclusion removed**;
3. a **matched opposite-frame stripped trace**;
4. **empty trace**.

The key question is not whether a trace can affect an answer in general. That is already known.

The question is:

> **Does the reasoning trajectory retain strong decision control after the explicit terminal commitment is removed?**

If yes, proceed to E08.

If no, the current “trajectory takeover” story collapses toward **late self-commitment**, which is itself a clear scientific answer and forces reconstruction.

---

# 6. E08 — Pre-Answer Decision-State Causal Substitution

Only after E07.

Intervene on the state immediately before answer decoding and ask whether a donor trajectory can transfer its decision into the target readout without appending donor reasoning text.

The scientific object is the **trajectory-built causal decision state**, not a layer number.

---

# 7. Parked, not next

The matched relevant-vs-redundant contextual-note boundary scaffold remains in the repository, but it is **not a prerequisite and not the current paper identity**.

Use it only later if the trajectory mechanism creates a concrete semantic-boundary question.

Do not add a reviewer-defense battery before E07/E08 changes the scientific picture.

---

# 8. Paper identity

> established reasoning-induced invariance  
> → prompt frame information remains available  
> → long natural reasoning takes causal control of the final decision  
> → identify whether that control is distributed through the trajectory or only its terminal commitment  
> → localize the trajectory-built decision state  
> → reinterpret what reasoning training changes about decision computation

This is **not**:

- another framing benchmark;
- a probe paper;
- generic Thought Injection;
- answer-token attention analysis;
- “CoT influences answers”;
- a context-sensitivity benchmark.

---

# 9. Training-attribution boundary

`Olmo-3-7B-Instruct-SFT` and `Olmo-3-7B-Think-SFT` are sibling branches from a common base.

Current evidence supports a matched reasoning-oriented-vs-instruction-oriented branch contrast, not strict one-variable training causality.

That caveat does not require a defensive model battery before the core mechanism is established.
