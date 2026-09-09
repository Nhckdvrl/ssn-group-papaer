# L12 — Reasoning-Induced Invariance

## Trajectory Takeover — the “Puppet-String” Effect

**Status:** **A / CONTINUE-PILOT / Rank 2**  
**Paper mainline:** NOT APPROVED  
**Target:** NAACL Main  
**Last audited:** 2026-09-09

> **Natural question:** After reasoning-oriented post-training, why do decisions become almost invariant to framing and presentation? Does the model’s self-generated long reasoning trajectory become the causal controller of the final answer even though the original frame information is still present?

“Puppet-string effect” is only an intuitive nickname. It does **not** mean the reasoning is fake. The hypothesis is the opposite: the long trajectory may be the computation that constructs the state controlling the answer.

---

# 1. Established behavioral substrate

ACL 2026 Outstanding **Mind the (DH) Gap!** establishes the broad phenomenon: reasoning-oriented models are far less sensitive to order, gain/loss framing, explanation, and description/history presentation.

Our matched OLMo sibling-branch pilot reproduces a large contrast on the three published prospects:

- Instruct-SFT frame consistency ≈ **0.817**;
- Think-SFT frame consistency ≈ **0.992**;
- difference ≈ **+0.175**, bootstrap CI **[0.025, 0.367]**.

These are **frame-consistency measurements**, not generic task-accuracy scores.

---

# 2. What we already know

### Input information is still there

Gain/loss frame identity remains recoverable through early/middle prompt representations.

So the behavioral invariance is not well described as “the model simply forgot the frame.”

### The long reasoning trajectory strongly controls the answer

With the same target prompt, forced A/B readout changes dramatically depending on the inserted natural Think-SFT trajectory:

- own natural trace: correct-option margin ≈ **+9.34**;
- empty trace: ≈ **-0.08**;
- matched opposite-frame trace: ≈ **-9.07**.

This is a large causal effect of the natural trajectory on final readout.

### A cheap arithmetic-fragment account is weak

Short answer-free arithmetic snippets do not reproduce the large trajectory effect:

- correct vs rule-only: **+0.32 [-3.92, 4.33]**;
- correct vs swapped: **+0.39 [-0.13, 0.96]**.

So the current live mechanism is not “one tiny calculation snippet determines the answer.”

---

# 3. Core mechanism

The working picture is:

> prompt frame remains represented  
> → Think-SFT generates a long self-conditioned reasoning trajectory  
> → that trajectory progressively constructs a decision state  
> → the trajectory-built state becomes the dominant controller of final A/B readout.

This is the **trajectory takeover** hypothesis.

The only unresolved fork that matters now is:

> **Is control genuinely carried by the reasoning trajectory, or does almost all of it collapse into the final explicit self-commitment?**

That is a mechanism question, not a reviewer-defense question.

---

# 4. Claim architecture

### C1 — Behavioral transition

Think-SFT is far more presentation-invariant than sibling Instruct-SFT on the audited parent stimuli.

### C2 — No simple frame erasure

Frame identity remains recoverable in early/middle prompt representations.

### C3 — Natural trajectory control

Complete natural Think-SFT trajectories exert large causal control over the final A/B readout.

### C4 — Distributed trajectory takeover

After removing the terminal explicit decision/conclusion, the remaining natural trajectory still controls readout.

### C5 — Trajectory-built decision state

A pre-answer hidden state constructed by the trajectory causally carries that control into the final answer.

C4 is the next decisive claim. C5 is tested only if C4 survives.

---

# 5. Next decisive experiment — E07

## Conclusion-Stripped Trajectory Takeover

For each natural Think-SFT trace compare:

1. **own full trace**;
2. **own terminal-conclusion-stripped trace**;
3. **matched opposite-frame stripped trace**;
4. **empty trace**.

Primary question:

> **After the explicit final commitment is removed, does the remaining long reasoning still strongly determine the answer?**

If yes, the “puppet strings” are distributed through the trajectory rather than being only the last sentence.

If no, the mechanism is **late self-commitment**. That is a scientific answer; do not add rescue controls.

Runnable:

`scripts/run_trajectory_takeover.sh`

---

# 6. E08 — Pre-Answer Decision-State Causal Substitution

Only if E07 supports C4.

Take the hidden state immediately before A/B decoding from a matched opposite-frame stripped trajectory and substitute it into the target computation, one layer at a time.

Primary signature:

> the target answer margin moves toward the donor decision **without appending donor reasoning text**.

The claim is not “layer 17 matters.” The claim is:

> **the long reasoning trajectory constructs an internal decision state that can causally transfer control of the final answer.**

Runnable scaffold:

`scripts/run_state_substitution.sh`

---

# 7. Paper identity

> established reasoning-induced invariance  
> → frame information remains present  
> → natural long reasoning takes causal control of the decision  
> → determine whether control is distributed through the trajectory or only terminal self-commitment  
> → identify the trajectory-built pre-answer decision state  
> → explain what reasoning-oriented post-training changes about decision computation

This is not a generic “CoT helps” or “CoT affects answers” paper. Recent work already owns generic trace causality, token-level causal contribution, and CoT activation patching. L12 must explain a **training-associated control transfer tied to the established invariance transition**.

---

# 8. Scope discipline

Do **not** add semantic-boundary, irrelevant-context, reviewer-defense, or broad model-battery experiments before E07/E08 changes the scientific picture.

Do **not** claim strict one-variable training causality from the two OLMo sibling branches.

Do **not** promote L12 to approved mainline until the trajectory mechanism survives the decisive causal tests.
