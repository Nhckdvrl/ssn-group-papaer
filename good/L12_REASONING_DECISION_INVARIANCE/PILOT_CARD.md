# L12 — Next Decisive Pilot Card

**Experiment:** L12-E07  
**Status:** CONTINUE-PILOT

# Scientific question

> **Does the long reasoning trajectory itself control the final answer, or is the apparent control mostly the final explicit self-commitment?**

This is the central unresolved mechanism behind the L12 “trajectory takeover / puppet-string” hypothesis.

# E07 — Conclusion-Stripped Trajectory Takeover

Use the three audited parent prospects and natural Think-SFT traces.

For each prospect × frame × order compare:

1. **own full trace**
2. **own terminal-conclusion-stripped trace**
3. **matched opposite-frame stripped trace**
4. **empty trace**

## Primary evidence

### Own stripped vs empty

Does the non-terminal reasoning trajectory still create a large target-directed A/B margin?

### Own stripped vs opposite stripped

Can two matched long trajectories still push the same target prompt toward opposite decisions after explicit terminal commitments are removed?

## Outcome logic

- **Both contrasts strong:** distributed trajectory takeover survives → run E08.
- **Effect collapses:** mechanism is late self-commitment → reconstruct around that answer.
- **Trace surgery is genuinely invalid:** repair the surgery once; do not launch a control battery.

# E08 — only after E07 succeeds

Substitute the matched opposite-frame **pre-answer hidden state** into the target computation, layer by layer.

Goal:

> establish whether the natural trajectory has constructed a causal decision state that transfers answer control without donor text.

Runnable:

- `configs/trajectory_takeover.json`
- `scripts/run_trajectory_takeover.py`
- `scripts/summarize_trajectory_takeover.py`
- `scripts/run_trajectory_takeover.sh`
- `configs/state_substitution.json`
- `scripts/run_state_substitution.py`
- `scripts/summarize_state_substitution.py`
- `scripts/run_state_substitution.sh`
