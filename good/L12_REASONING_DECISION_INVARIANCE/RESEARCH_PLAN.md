# L12 — Research Plan

## Core RQ

> **After reasoning-oriented post-training makes decisions almost invariant to framing, does the model’s own long reasoning trajectory take over causal control of the final answer?**

The current mechanism hypothesis is:

> prompt frame remains represented  
> → long self-generated reasoning performs the decisive computation  
> → a trajectory-built state controls final readout.

The paper should explain this control transfer through the smallest decisive mechanism sequence.

# Evidence already in hand

1. **Behavioral transition:** Instruct-SFT frame consistency ≈ 0.817 vs Think-SFT ≈ 0.992.
2. **No simple erasure:** frame identity remains decodable early/mid.
3. **Strong natural-trace causality:** own trace ≈ +9.34 margin, empty ≈ -0.08, opposite trace ≈ -9.07.
4. **Cheap snippet account weakened:** short arithmetic fragments do not reproduce the effect.

# E07 — Is the control distributed through the trajectory?

Compare:

1. own full;
2. own terminal-conclusion-stripped;
3. opposite-frame stripped;
4. empty.

Primary contrasts:

- own stripped − empty;
- own stripped − opposite stripped.

Secondary:

- own full − own stripped.

### Interpretation

**Distributed trajectory takeover:** stripped natural reasoning remains strongly target-directed.

**Late self-commitment:** the effect largely disappears after terminal conclusion removal.

Either outcome answers the mechanism question. No rescue battery.

# E08 — Does the trajectory build a causal decision state?

Run only if E07 supports distributed trajectory control.

For each matched target/opposite-frame pair:

1. construct the target prefix with its stripped natural trajectory;
2. construct the donor prefix with the matched opposite-frame stripped trajectory;
3. capture the donor’s final-token hidden state at every decoder layer;
4. substitute that state into the target forward pass one layer at a time;
5. score the A/B logits.

Primary quantity:

> **donor-consistent shift in the target answer margin.**

A coherent layer profile with substantial donor-consistent transfer supports a trajectory-built decision state.

This is a positive mechanism experiment. The layer index itself is not the paper claim.

# Stop rule

Finish E07, then E08 if gated in. Do not expand the experiment tree before those results.

After E08, decide between:

- **GO:** trajectory takeover + causal decision state gives a coherent Main-level mechanism;
- **RECONSTRUCT:** late self-commitment or a different mechanism emerges;
- **KILL/HOLD:** the causal story collapses or is fully compressed by prior work.
