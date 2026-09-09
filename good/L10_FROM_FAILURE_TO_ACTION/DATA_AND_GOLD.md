# L10 — Data, Gold, and Identification Contract

**Core rule:** load-bearing truth comes from explicit environment/action state, not an LLM judge.

# 1. Primary released substrate

Start from public **ImplicitMemBench** artifacts:

- paper: <https://aclanthology.org/2026.acl-long.1301/>
- code/data: <https://github.com/qinchonghanzuibang/ImplicitMemBench>
- pinned upstream commit: `927413bf3f5389bb47c94c2a0ba987e435b101b8`

The first pilot uses only:

> `dataset/classical_conditioning/conditioned_api_aversion.json`

It contains **10 released instances**. Each has repeated use of a named tool B followed by explicit failure, a distinct named alternative A followed by success, interference, and a later related request.

## Why not start with Tool Use with Side-Effects?

Many released side-effect items permit multiple valid responses: warning, safe mode, parameterized use of the same tool, or an alternative tool. That weakens strict first-action gold. Keep that family for later boundary/natural validation.

# 2. Pilot action contract

The manually audited action pairs are frozen in `data/audit_manifest.json`.

For the actual-action branch, use the original test request and append only:

> Take the next action now. Respond with the tool name you would use first; do not explain.

Primary action gold is the released successful alternative **A**. If output is not exactly one of the two audited tool names, record it as **other/invalid for strict action identity** and retain raw text. Do not post-hoc judge free-form warnings as correct.

# 3. Untouched-history fork contract

For each item construct one canonical history **H** from the released learning phase + interference phase. Preserve source roles by default and record the rendered prompt hash.

Fork H independently:

- **M — outcome memory:** did B repeatedly succeed or fail? Gold = FAILURE.
- **C — attribution:** which tool was repeatedly associated with errors? Gold = B.
- **P — executable policy:** which tool should be used first next time? Gold = A.
- **A — actual first action:** original test request + action instruction. Gold = A.

**M/C/P outputs never enter A.**

# 4. Stage-completion interventions

From the same untouched H:

- **A0 raw**
- **A1 outcome:** “B failed in the earlier attempts.”
- **A2 causal binding:** “The earlier failures were caused by using B.”
- **A3 negative policy:** “Do not use B for this request.”
- **A4 positive replacement:** “Use A instead for this request.”

All notes appear in the same location/role.

Primary causal quantities:
- change in strict A selection;
- change in strict B repetition.

# 5. Metrics

Report:
- M/C/P accuracy;
- A0 strict good-action rate;
- A0 strict bad-repeat rate;
- strict validity rate;
- **P-correct + A0-bad-repeat** dissociation;
- paired A1–A4 recovery relative to A0.

Uncertainty is over the **10 released item templates**.

# 6. First model

`Qwen/Qwen2.5-7B-Instruct@a09a35458c702b33eeacc393d103063234e8bc28`

Use greedy first-action decoding for route selection. Add another family only after the design has leverage.

# 7. Data kill / reconstruct

Stop/redesign if the template cannot faithfully render H, strict action identity is not identifiable, A/B truth is not objective, no stage/completion moves behavior, or only subjective warning quality remains.
