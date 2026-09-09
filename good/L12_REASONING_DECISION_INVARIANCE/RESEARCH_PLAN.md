# L12 — Research Plan

## Core RQ

> **When reasoning training makes model decisions almost invariant to presentation, what actually takes control of the final answer?**

The current evidence suggests a natural mechanism:

> prompt information remains available  
> → a long self-generated reasoning trajectory is produced  
> → the trajectory controls final readout.

The next work tests whether that control belongs to the **reasoning process** or merely to its final explicit conclusion.

# L12-E07 — Conclusion-Stripped Trajectory Takeover

Reuse the natural Think-SFT trajectory setup from E05.

For each target cell, score the final A/B readout under four trajectory prefixes:

1. **own full** — complete natural trace;
2. **own stripped** — same trace with terminal explicit choice/conclusion removed;
3. **opposite stripped** — matched opposite-frame natural trace with its terminal choice/conclusion removed;
4. **empty** — no reasoning trace.

Primary contrasts:

- own stripped − empty;
- own stripped − opposite stripped.

Secondary descriptive quantity:

- own full − own stripped, which measures how much additional control comes from the terminal commitment.

### Interpretation

**Trajectory takeover:** own-stripped remains strongly target-directed and separates from both empty and opposite-stripped.

**Late self-commitment:** the large full-trace effect collapses after terminal conclusion removal.

Either result answers the scientific question. Do not rescue a failed trajectory-takeover account with additional controls.

# L12-E08 — Pre-Answer Decision-State Causal Substitution

Run only if E07 shows non-trivial trajectory-level control beyond the terminal conclusion.

Use the natural reasoning computation itself and intervene on the state immediately before answer decoding.

Question:

> **Has the reasoning trajectory constructed a causal decision state that now dominates the final readout?**

Use a matched target/donor substitution and measure whether the target-choice margin moves in the donor-consistent direction.

The layer is not the claim; the existence and construction of a causal decision state is.

# Optional later boundary

The current context-note semantic boundary scaffold is parked.

Run it only if E07/E08 create a concrete question about what kinds of information the trajectory accepts, suppresses, or overrides.

It is not required to “defend novelty.”

# Main-level shape

> established reasoning-induced invariance  
> → frame information remains present  
> → natural long reasoning takes over decision control  
> → distinguish distributed trajectory control from terminal self-commitment  
> → identify the pre-answer causal decision state  
> → explain what reasoning-oriented post-training changes about decision computation
