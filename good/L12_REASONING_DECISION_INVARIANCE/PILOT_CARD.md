# L12 — Next Decisive Pilot Card

**Experiment:** L12-E07  
**Status:** CONTINUE-PILOT

# Scientific question

> **Is the final answer controlled by the long reasoning trajectory itself, or only by the trajectory's final explicit commitment?**

This is the next load-bearing question for L12.

# L12-E07 — Conclusion-Stripped Trajectory Takeover

Use the three already-audited parent prospects and Think-SFT natural traces.

For each prospect × frame × order, compare the forced A/B readout after:

1. **own full trace**
2. **own trace with terminal explicit choice/conclusion removed**
3. **matched opposite-frame stripped trace**
4. **empty trace**

## Primary evidence

### Own stripped vs empty

Does the non-terminal reasoning trajectory still create a strong target-directed margin?

### Own stripped vs opposite stripped

Can two matched long trajectories push the same target prompt toward different decisions even after their explicit terminal commitments are removed?

## Outcome logic

- **Both contrasts strong:** trajectory-level takeover survives → proceed to E08.
- **Effect collapses after stripping:** the current mechanism is late self-commitment, not distributed trajectory control → reconstruct around that result.
- **Trace surgery itself is not identifiable:** repair the surgery once; do not launch a control battery.

# E08 — only after E07

Causally substitute the pre-answer decision state between matched trajectories.

Goal:

> show that a trajectory-built internal state, rather than appended donor text, carries decision control.

# Runnable scaffold

- `configs/trajectory_takeover.json`
- `scripts/run_trajectory_takeover.py`
- `scripts/summarize_trajectory_takeover.py`
- `scripts/run_trajectory_takeover.sh`

The older context-boundary scaffold is parked and is not a prerequisite.
