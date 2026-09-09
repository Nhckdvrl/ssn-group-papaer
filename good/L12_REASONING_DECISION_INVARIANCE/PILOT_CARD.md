# L12 — Next Decisive Pilot

**Experiment:** L12-E07  
**Status:** CONTINUE-PILOT

# Question

> **Does reasoning-oriented post-training make the model selectively invariant to irrelevant context, or broadly less responsive to context?**

# Design

Use the three audited parent prospects.

Keep the displayed option lines fixed. Append one of three context conditions:

1. **none** — no extra note;
2. **redundant** — a note says one probability was rechecked and is unchanged;
3. **correction** — the same note structure updates that probability to a value that flips the EV-optimal action.

Example:

> Additional context: the probability associated with Option B was rechecked and remains 0.34.

versus

> Additional context: the probability associated with Option B has been updated from 0.34 to 0.36.

The exact updates are frozen in `configs/boundary.json`. Continue crossing gain/loss and option order.

# Models

- OLMo-3 Instruct-SFT
- OLMo-3 Think-SFT

Use the already audited revisions and native templates.

# Readout

Report:

- original no-note frame consistency;
- **redundant-context consistency** — does irrelevant context leave the decision unchanged?
- **correction EV accuracy** — does the model use context when it genuinely changes the decision?

# Scientific outcomes

### Selective abstraction
Think-SFT ignores redundant context but follows decision-relevant corrections.

### Context flattening
Think-SFT ignores redundant context and also underuses decision-relevant corrections.

### Neither
The current explanation is wrong or incomplete; reconstruct from the observed boundary.

# Next step

Only if E07 yields a stable scientific distinction, run E08 to ask where the decision state is constructed.

Runnable files:

- `configs/boundary.json`
- `scripts/run_boundary.py`
- `scripts/summarize_boundary.py`
- `scripts/run_boundary.sh`
