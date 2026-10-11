# L35 — What Is the Unit of Repetition in Reasoning SFT?

**Date:** 2026-09-13  
**Target:** ACL / EMNLP / NAACL Main  
**Status:** **SERIOUS CANDIDATE — HOLD: RESOLUTION / COST AUDIT — NO COMPUTE AUTHORIZED**

## 1. Research question

> **When repeated long-CoT supervision generalizes better than more unique data, what is the load-bearing repeated unit: the same problem/procedure, or the same target reasoning trajectory?**

A more operational version is:

> If the model sees the **same 400 problems 16 times**, does the repetition advantage require replaying the **same CoT target** each time, or does it survive when each presentation uses a **different verified-correct reasoning path** for that same problem?

This is a training-dynamics question, not a data-scaling recipe question. The scientific object is the identity of the repeated supervised target.

## 2. Mother phenomenon

The mother is already strong and does not need to be invented.

Kopiczko et al. (COLM 2026), *Data Repetition Beats Data Scaling in Long-CoT Supervised Fine-Tuning*:

- under a fixed update budget, more epochs on a smaller long-CoT set beat one epoch on a larger unique set;
- Olmo3-7B, 400 samples × 128 epochs, beats 51,200 samples × 1 epoch by roughly 12–26 points on AIME/GPQA;
- the effect is already large at a **6.4k update budget**: on Qwen3-8B-teacher data, 6.4k unique ×1 gives Avg@n 10.6 while 400 ×16 gives 26.1; with the weaker teacher the corresponding numbers are 2.2 vs 20.6;
- gains plateau near full token-level memorization;
- the paper explicitly states that the causal mechanism of the repetition advantage remains unresolved.

Primary source: https://arxiv.org/abs/2602.11149  
Code/checkpoints: https://github.com/dkopi/data-repetition

The public evaluator extracts the final `\\boxed{}` answer even if the rollout does not emit EOS, while recording termination separately. Therefore the mother accuracy gain is **not reducible to an evaluator rule that requires successful termination**.

## 3. Why the question matters

The parent result is often summarized as “memorization can improve generalization.” That interpretation silently equates three different repeated objects:

1. the same **problem identity**;
2. the same **reasoning procedure / strategy**;
3. the same **token-level target trajectory**.

Those are not the same training quantity.

If exact target identity is necessary, long-CoT SFT has a target-stability / conditional-target-entropy property that ordinary “more diverse data is better” intuition misses. If exact target identity is unnecessary, then the parent’s full-token-memorization correlate is not the causal unit: repeated optimization on a small set of problems/procedures is sufficient. If varied paths are better, repetition and intra-problem diversity are complementary rather than opposing principles.

## 4. Scientific accounts

### A — Stable-trajectory consolidation

Repeatedly driving down error on the **same target path** is load-bearing. A stable long target lets the model consolidate a coherent trajectory/policy; swapping among several valid targets for the same problem weakens that effect.

Prediction:

`EXACT-REPLAY > VARIED-PATH`, despite identical problem identities and exposure counts.

### B — Problem/procedure consolidation

The benefit comes from revisiting the same underlying problems / procedural structures deeply. Exact token memorization is incidental.

Prediction:

`EXACT-REPLAY ≈ VARIED-PATH > BREADTH`.

### C — Intra-problem diversity

Repeated problem exposure is useful, but forcing one canonical path is unnecessarily restrictive. Diverse valid paths preserve or enlarge the reachable reasoning policy.

Prediction:

`VARIED-PATH > EXACT-REPLAY`; both may beat or differ from BREADTH depending on problem breadth.

## 5. Decisive operation

The intended E01, **if resolution/cost is first cleared**, is a three-arm fixed-exposure design:

1. **EXACT-REPLAY** — 400 problems; one verified-correct long-CoT per problem; each exact target shown 16 times.
2. **VARIED-PATH** — the same 400 problem IDs; 16 verified-correct long-CoTs per problem; each path shown once.
3. **BREADTH** — 6,400 different problems; one verified-correct long-CoT per problem.

All arms contain 6,400 supervised presentations / optimizer steps under the parent-style batch-1 regime.

The load-bearing contrast is **EXACT-REPLAY vs VARIED-PATH**. BREADTH anchors reproduction of the mother phenomenon and prevents a result from being interpreted without reference to the parent repetition advantage.

### Required controls before any authorization

- use an existing multi-trajectory reasoning corpus with independent answer gold; do not LLM-generate the load-bearing gold;
- every varied trajectory must pass the same correctness filter;
- identical 400 problem IDs in EXACT and VARIED;
- no outcome-driven trajectory selection;
- audit supervised response-token counts / length distributions across arms;
- choose the canonical EXACT path so that its repeated per-problem token budget is matched as closely as possible to the aggregate token budget of that problem’s varied paths, or otherwise pre-specify a token-budget correction;
- same optimizer, LR schedule, number of updates, ordering policy and tokenizer;
- primary inference must use independent held-out problems with direct answer gold, not an LLM judge.

Existing suitable data sources include OpenThought3-style collections with many Long-CoT solutions per problem, and the 2026 Rethinking-SFT release with ~44k questions × 32 teacher responses. Dataset choice is **not yet frozen**.

## 6. Closest owners and reviewer compression

### Parent 1 — repetition

Kopiczko et al. 2026 owns:

> many epochs on fewer examples can beat one epoch on more unique examples; token-level memorization correlates with saturation.

It does **not** vary target identity while holding problem identity and repeated exposure fixed.

### Parent 2 — one problem, multiple solutions

Ju et al. 2025/ICLR-2026-under-review, *Reasoning Path Divergence*, owns:

> at a fixed number of training instances in **one-epoch SFT**, 1-problem/multiple-solution data can improve output diversity and pass@k relative to 1-problem/1-solution data.

Their main 300-instance comparison is 300 problems ×1 solution versus 100 problems ×3 solutions; the larger experiment similarly compares 3,000 unique ×1 with 1,000 problems ×3, again for one epoch.

Source: https://arxiv.org/abs/2510.26122

It does **not** ask whether the repeated-epoch advantage depends on replaying the same target trajectory.

### Parent 3 — SFT generalization / under-optimization

Ren et al. 2026, *Rethinking Generalization in Reasoning SFT*, shows that long-CoT SFT generalization can be hidden by under-optimization and depends on data quality/structure and base-model capability.

Source: https://arxiv.org/abs/2604.06628

This kills the weak explanation “repetition merely trains longer,” but does not identify the repeated supervision unit.

### Strongest reviewer compression

> `Data Repetition Beats Scaling` + `one-problem/multiple-solutions helps` = “try multiple paths while repeating problems.”

This is the main novelty risk.

### Surviving contribution

Neither prior implies the **sign of the interaction** between repeated problem exposure and target-trajectory identity. The two priors actually pull in different directions: one shows exact repeated supervision is unusually strong under epoch scaling; the other shows intra-problem path diversity can outperform greater problem breadth under one-epoch SFT.

The proposed contribution is not the bridge itself. It is a causal identification of **which object must remain invariant under repetition for the repetition advantage to exist**.

Current ownership verdict: **PLAUSIBLE INDEPENDENT CONTRIBUTION**, subject to fresh search before any compute.

## 7. Anti-resurrection

### Not the old spacing route

Spacing asks whether temporal separation between repeated exposures changes learning. Here the schedule / exposure count is held fixed and **target identity** is manipulated. No spaced-vs-massed claim is available.

### Not L19

L19 asks whether long-context supervision produces a causal surplus on later short-context capability. Here context length is not the treatment; the treatment is repeated target identity inside reasoning SFT.

### Not L20

L20 asks how a **fixed pretrained model in context** assigns causal credit after a scalar reward to a multi-step trajectory. L35 is **gradient-based supervised fine-tuning with no reward** and asks which supervised object must be repeated.

### Not generic negative-trace learning

ACL 2026 already owns useful learning from negative reasoning traces and negative-signal distillation. Correctness is therefore not the new axis here; E01 should use verified-correct paths and keep the question about identity/diversity.

## 8. Successful-result test

### Outcome A — EXACT > VARIED

Observation:

> holding problem IDs and exposure count fixed, replaying the identical target path generalizes materially better than swapping among valid paths.

Inference:

> stable target identity is load-bearing for the repetition advantage; full memorization is not merely a stopping correlate but marks consolidation of a low-entropy supervised trajectory.

Growth path:

- separate surface/token identity from strategy identity using naturally available low- vs high-divergence trajectories;
- test whether target-path divergence predicts the loss of the repetition advantage;
- ask whether a simple target-entropy quantity predicts the optimal repetition regime across models/data.

This is potentially Main-level if the effect is robust and not reducible to token budget.

### Outcome B — EXACT ≈ VARIED > BREADTH

Inference:

> repeated **problem/procedure exposure**, not exact target memorization, is sufficient. The parent’s “full memorization” observation is a correlate of training depth rather than the causal repeated object.

This can remain important, but paper scale would require a principled predictor of which problem structures benefit from deep revisiting. Otherwise HOLD/KILL rather than narratively expanding.

### Outcome C — VARIED > EXACT

Inference:

> epoch scaling and intra-problem diversity are complementary; the parent’s strongest exact-replay recipe is not the causal optimum. Repeated problem identity plus multiple valid paths provides the stronger learning signal.

The paper must stay about the unit of repetition, not turn into a new data-curation method.

### Mother failure

If EXACT does not reproduce a material repetition advantage over BREADTH under the selected controlled substrate, **STOP**. Do not model-shop or change the scientific object.

## 9. Resolution / compute gate — current blocker

The parent mother is large and can appear at 6.4k updates, which is much more favorable than L19. Parent hyperparameters use one H100 per run, batch size 1, and long responses up to the filtering cap.

However, the **discriminating effect** `EXACT - VARIED` is unknown and could be only a few percentage points. The parent’s headline evaluation relies heavily on small AIME/GPQA sets, which is inadequate for declaring a small second-order difference without a power/resolution audit.

Before compute authorization, freeze:

1. a sufficiently large direct-gold held-out evaluation substrate;
2. independent-unit definition;
3. paired bootstrap / hierarchical estimate;
4. MDE for a scientifically meaningful EXACT–VARIED difference;
5. actual tokens/update and wall-clock throughput from the chosen dataset/model;
6. seed budget required to distinguish a training effect from run variance.

A no-claim throughput/MDE audit is permitted. Treatment outcomes are not.

If a 2–3 pp interaction requires parent-scale dozens of runs or cannot be resolved credibly, verdict becomes **NO-GO — RESOLUTION/COST**, not a narrowed claim.

## 10. Main-level growth path

If E01 clears the gate and shows a material interaction, the same paper can deepen without changing identity:

- **C1 — unit:** problem identity vs target-trajectory identity;
- **C2 — boundary:** within-problem trajectory divergence / target entropy determines when repetition helps;
- **C3 — prediction:** a pre-training-data quantity predicts the optimal repetition/diversity regime and explains why full token memorization is or is not diagnostic.

No benchmark construction, new data-selection algorithm, RL extension, or model zoo is authorized by this Selection.

## 11. Verdict

```yaml
natural_question: PASS
mother_phenomenon: PASS_STRONG
replication_risk: MODERATE_LOW
anti_resurrection: PASS
closest_owner_density: MEDIUM_HIGH
central_owner: NOT_FOUND
reviewer_compression: SERIOUS_BUT_SURVIVABLE
identification: PASS_CONDITIONAL_ON_TOKEN_BUDGET_CONTROL
successful_result_upper_bound: PASS
outcome_identity: PRECOMMITTED
resolution: UNRESOLVED
compute_cost: UNRESOLVED
pilot: NOT_AUTHORIZED
verdict: SERIOUS_HOLD_RESOLUTION_COST
```

**Do not run the three-arm training experiment yet.** First resolve the MDE/throughput gate without looking at treatment outcomes.