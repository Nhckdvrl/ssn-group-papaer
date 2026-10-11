# L10 — Minimum Decisive Pilot

**L10-E01 + L10-E02**

Use the **10 released Conditioned API Aversion items** from ImplicitMemBench commit:

> `927413bf3f5389bb47c94c2a0ba987e435b101b8`

Model:

> `Qwen/Qwen2.5-7B-Instruct@a09a35458c702b33eeacc393d103063234e8bc28`

# E01

Fork the same untouched history H into:
- outcome memory
- causal attribution
- policy knowledge
- actual next action

Never let diagnostic answers enter the action branch.

Primary question:

> **Where does the chain first break?**

# E02

From H add exactly one completion:
- outcome reminder
- causal binding
- “do not B”
- “use A instead”

Primary question:

> **Which missing piece changes the actual first action?**

# Decision

Continue if E01 identifies a stable stage dissociation and/or E02 reveals a clear causal completion.

If not, reconstruct or demote. Do not respond by adding a large battery of defensive tests.

Runnable:
- `scripts/fetch_parent_data.sh`
- `scripts/run_pilot.py`
- `scripts/summarize_pilot.py`
- `scripts/run_pilot.sh`
