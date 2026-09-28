# CT05 — Shape-blog exploration lineage

Opened 2026-09-27 from Alex Zhang, *Language Model "Shape"*.

**Current status:** **ARCHIVED / KILLED LINEAGE.**  
**Registry rule:** the historical CT06–CT09 labels are retired as independent topic IDs. Their full artifacts are preserved under `lineage/` only for provenance. **CT06–CT09 are free for future registrations.**

This package records one continuous exploration lineage around the same broad Shape-blog neighborhood: hybrid attention/recurrent memory, agent-history representation, query-timed KV access, RLM information hiding, and attention→recurrent handoff. None is an active paper candidate.

## Why the lineage is closed

The common failure was not merely “five negative results.” The search repeatedly did:

> blog/architecture intuition → plausible hidden mechanism → cheap decisive test.

That is useful for falsification, but it registered a paper question **before a stable, manipulable mother phenomenon had been established in our regime**. Future Shape work must not revive this lineage by changing model, prompt, threshold, or training recipe. New work needs an independent observed pressure first.

## Empirical inheritance

### A. Exact vs compressed memory in real agent trajectories — original CT05

Natural SWE-smith / APIGen-MT checkpoints; Qwen3.5-9B hybrid with Qwen3-8B Transformer control.

- `rho_2 = -0.005 [-0.034, 0.024]`: evicting old-event KV costs essentially as much as deleting the text.
- Hybrid-specific compensation relative to the Transformer: `-0.03 [-0.07, 0.03]`.
- Median single-event recurrent compensation: `0.001 nats`.
- Copy tokens are ~11% of target tokens but carry ~60% of KV-eviction damage; recurrence restores ~1% of copy-token damage vs ~26% on other tokens.
- Exact-memory demand is concentrated (top 10% events ≈92%), but deployable hybrid-native signals are weak; the future action query is strong only because it can see what will be generated.

**Conclusion:** current Qwen3.5 recurrence is not a useful substitute for exact historical KV in these agent decisions. The surviving problem collapses toward query-aware KV retrieval, already occupied by AgentKV / Quest / lookahead-cache work.

Canonical files remain at the CT05 root: `docs/E01_PROTOCOL.md`, `docs/E01_RESULTS.md`, `results/e01/`.

### B. Training-pressure specialization — historical CT06

Audit only; no GPU experiment. SWAX and *Rethinking the Role of Efficient Attention in Hybrid Architectures* already show that attention availability changes how recurrent/efficient paths learn long-range behavior and mainly changes emergence/optimization. The residual “post-hoc respecialize a pretrained hybrid until agent-copy rho becomes positive” was a recipe search without an independent observation.

Preserved at `lineage/CT06_TRAINING_PRESSURE_MEMORY_SPECIALIZATION/`.

### C. Intra-action memory-query timing — historical CT07

178 CT05 checkpoints, inference only.

- Pre-value recovery stayed low: tau `0.16/0.13`, SWE `0.21/0.22` at 25%/50% budgets.
- In tau, tool name / argument key did not form a useful retrieval query.
- Critical-block hit@1 rose only after the first value token itself was written (about `0.13 → 0.42`).

**Conclusion:** the strong future query emerges during exact binding/copying, not at a clean “decide → retrieve → fill” boundary.

Preserved at `lineage/CT07_MEMORY_QUERY_TIMING/`.

### D. RLM information hiding / compositionality — historical CT08

400 OOLONG-synth items at 16k/32k.

- trained RLM-Qwen3-8B: `0.274`
- untrained Qwen3-8B in same RLM harness: `0.346`
- flat full-context Qwen3-8B: `0.515`
- trained-minus-untrained RLM: **−7.2 points**, 95% CI `[-12.8, -1.7]`
- no cross-domain skeleton-isomorphism advantage.

The published RLM transfer effect lives in a much larger RL / long-context regime; the visibility manipulation is feasible only where that mother effect did not reproduce. Effect and manipulation therefore lived in disjoint regimes.

Preserved at `lineage/CT08_INFORMATION_HIDING_COMPOSITIONALITY/`.

### E. Attention→recurrent handoff — historical CT09

Qwen3.5-4B, 400 paired items; same donor recurrent state, A/B difference only in context KV before the query. Query reads with attention, then all KV is removed.

- FULL continuous-KV contrast: `16.36 nats`
- POST one-read-then-no-KV contrast: `1.79 nats`
- NOREAD unrelated query: `0.03 nats`
- RECENT plain-text value ~20 tokens earlier with no KV: `0.02 nats`
- RECONLY: `0.05 nats`
- frozen normalized `H = 0.108 [0.104, 0.112]`, below the pre-registered 0.20 continuation threshold.
- Raw re-audit: POST−NOREAD is positive on **399/400** items; median ≈`1.72 nats`; 98.25% exceed 0.5 nat.

**Important interpretation:** the frozen continuation gate failed, but the scientific result is **not a null**. There is a robust retrieval-triggered trace in the recurrent channel. The original `H` denominator compares one-shot read+carry against continuous KV re-access, so it is a utility/continuation ratio, not “fraction of information transferred.” The carrier/persistence (short convolution vs matrix state) remains unresolved and is not pursued here under stop-loss.

Preserved at `lineage/CT09_CROSS_CHANNEL_HANDOFF/`.

## Anti-resurrection

Do **not** create a new CT by:
- moving CT05/07 to Falcon-H1, larger Qwen3.5, or free-running trajectories;
- training recurrence with KV dropout / stochastic windows merely to manufacture the missing carry;
- turning CT07 into skeleton→retrieve→fill or argument-slot KV routing;
- repairing the released 8B RLM until CT08’s mother effect appears;
- sweeping CT09 probe wording, gaps, layers, models, or training it to hand off;
- renaming any of the above as a “model-shape” method.

A reopen requires an **independently observed behavior or failure** that needs one of these mechanisms; the old experiments may then serve only as legacy evidence.

## Durable lessons for future Shape work

1. A blog/design intuition is a provenance source, not mother evidence.
2. Establish that the target phenomenon exists **in the same model/length/training regime in which the identifying intervention is possible**.
3. Keep exploratory analysis separate from confirmatory gates.
4. A continuation/utility threshold is not the same thing as a scientific null.
5. Unexpected stable results are observations to archive, not automatically new paper candidates.
6. Prefer a strong open baseline with matched controls and many released checkpoints; learn its real failure gradients before registering another CT.
