# L10 — Minimum Decisive Pilot Card

**Experiment:** L10-E01 + gated L10-E02  
**Status:** PILOT-AUTHORIZED

# Data

Use exactly the **10 released Conditioned API Aversion items** from ImplicitMemBench commit:

> `927413bf3f5389bb47c94c2a0ba987e435b101b8`

The frozen bad/good action mapping is in `data/audit_manifest.json`.

Do **not** include Tool Use with Side-Effects in E01; multiple valid action forms weaken strict gold.

# Model

`Qwen/Qwen2.5-7B-Instruct@a09a35458c702b33eeacc393d103063234e8bc28`

Greedy decoding, native chat template, strict tool-name parsing.

# E01

From one untouched history H independently run:
1. **M** outcome memory;
2. **C** attribution;
3. **P** executable policy;
4. **A0** actual first action.

**M/C/P responses never appear in A0.**

Primary dissociation:

> **P correct, but A0 strictly repeats B.**

An earlier M/C/P break is also valid.

# E02

From H run A1 outcome reminder, A2 causal binding, A3 “do not B”, A4 “use A instead”.

Primary evidence is paired recovery of **actual action**.

# Continue

Continue if a stable stage dissociation and/or preregistered completion has clear behavioral leverage.

# Stop / reconstruct

Stop if action gold/parser is ambiguous, the template invalidates history, effects are wording artifacts, or no stage/completion changes behavior.

Runnable scaffold:
- `scripts/fetch_parent_data.sh`
- `scripts/run_pilot.py`
- `scripts/summarize_pilot.py`
- `scripts/run_pilot.sh`
