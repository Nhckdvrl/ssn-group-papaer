# L08 — Fresh Selection Recheck (2026-09-13)

**Target:** ACL / EMNLP / NAACL Main  
**Status:** **REOPEN — SERIOUS / PAPER-LEVEL SELECTION PASS — NO NEW EXPERIMENT AUTHORIZED**

## Why this file exists

L08 was archived on 2026-09-11 because the paper identity had been reconstructed during execution. The archive decision explicitly required any reconstructed identity to independently re-earn novelty and Main-level contribution; it was **not** a null result and was **not** a direct-owner kill.

This recheck applies the current 2026-09-13 Selection standard to the evidence already collected plus fresh 2026 ownership.

## 1. Reconstructed research question

> **When compression appears to damage one language-model capability more than another, is that selectivity intrinsic to the damaged computation, or can it be created by the readout protocol and output depth used to measure the capability?**

The deeper boundary is:

> **Do parameter-damaging interventions and readout-channel interventions produce the same capability-selectivity law, or are they qualitatively different objects?**

This is not the old question “which dimensions matter?” and not the generic question “is multiple choice a bad benchmark?”.

## 2. Existing evidence inherited from L08

The package already contains a matched factorial that holds content/model/intervention fixed while changing readout protocol and generation depth.

Key result:

- on the same MMLU content, retention under the same intervention moves from roughly **0.889** under ranking, to **0.837** under a one-generated-token readout, to roughly **0.030** under a generated-chain protocol;
- after matching protocol and output length across capability comparisons, the apparent “reasoning is more fragile than knowledge” story changes sharply;
- critically, the direction of selectivity separates by intervention family: readout-damaging interventions can make reasoning look relatively robust while parameter-damaging interventions make reasoning look relatively fragile.

These are preserved historical results; this recheck does not retrospectively convert exploratory work into confirmatory evidence.

## 3. Fresh ownership audit

### ICLR 2026 — When Reasoning Meets Compression

This paper benchmarks quantization, distillation and pruning on AIME/FOLIO/Temporal Sequences/MuSiQue and reports that weight count has greater impact on “knowledge memorization” than on reasoning.

Primary source: https://proceedings.iclr.cc/paper_files/paper/2026/hash/665654759cdf2114c0cbe2b8e501e00e-Abstract-Conference.html

Load-bearing limitation for the present RQ:

- reasoning and knowledge are instantiated by **different tasks**, with different answer spaces, generation protocols, difficulty distributions and output lengths;
- therefore capability label and readout/task structure are not orthogonalized.

It owns a compression/capability comparison, not the matched estimand rewrite.

### 2026 — The Benchmark Illusion

This work shows that highly pruned LLMs can retain multiple-choice recognition while failing open generation on the **same question**; correct answers are often demoted rather than erased and can reappear under beam/sampling/one-shot support.

Primary source: https://arxiv.org/abs/2606.17609

This directly owns the generic statement:

> `multiple-choice success != open-generation usability after pruning`.

L08 must not claim that as new.

It does **not** own the stronger cross-intervention boundary:

> after controlling the readout on the same underlying content, the direction of apparent capability selectivity depends on whether the intervention damages the computation/parameters or mainly damages the expression/readout channel.

## 4. Strongest reviewer compression

> `When Reasoning Meets Compression` already studies reasoning-vs-knowledge under compression, and `Benchmark Illusion` already shows MC-vs-generation dissociation after pruning. L08 is those two observations combined with more controls.

This is a serious compression and removes several historical L08 claims.

## 5. Surviving contribution

The reviewer compression does **not** imply the observed intervention-family boundary.

The surviving scientific statement is:

> **Capability-selective compression damage is not a single intrinsic property of a capability. The observed ordering can change when readout protocol/output depth changes, and the direction of this dependence differs between interventions that damage the underlying parameterized computation and interventions that primarily damage the readout/expression channel.**

That statement changes what can be inferred from a large body of compression comparisons. It is a model-science claim about the **meaning of the intervention × readout estimand**, not merely an evaluation warning.

Current ownership verdict: **PLAUSIBLE INDEPENDENT CONTRIBUTION**.

## 6. Identification

The strongest inherited design is valuable precisely because it uses the **same underlying items** and varies readout dimensions directly rather than comparing unrelated “knowledge” and “reasoning” datasets.

The intended causal/measurement decomposition is:

`intervention family × content/capability × readout protocol × output depth`.

To support the reconstructed claim, any future confirmatory study must preserve:

- matched underlying item/content wherever possible;
- matched output length when capability selectivity is compared;
- explicit separation of ranking / one-token generation / free generation;
- multiple intervention families with a principled `parameter damage` vs `readout/channel damage` distinction fixed before outcomes;
- identical post-processing / stopping rules across the compared arms.

No new benchmark construction is needed.

## 7. Successful-result test

The inherited strongest pattern is already nontrivial:

> same content + same intervention, but changing the readout/depth changes the apparent damage by nearly an order of magnitude; then, under matched readout, different intervention families produce opposite capability-selectivity tendencies.

If independently confirmed, the inference is not merely “evaluation matters.” It is:

> **what compression appears to preserve depends on which computational channel the intervention damages and how the surviving state must be converted into an output.**

That is a materially different interpretation from assigning an intrinsic fragility ranking to “reasoning” and “knowledge.”

## 8. Outcome identity / kill rules

A future confirmation, if selected for execution later, should be killed as a Main route if:

- protocol matching removes the historical intervention-family boundary;
- the boundary appears only for one model or one extreme sparsity setting;
- parameter-damaging vs readout-damaging cannot be defined independently of the observed result;
- after exact-output controls, the contribution collapses to the already-owned `MC != generation` statement.

Do not rescue a failure by broadening into benchmark auditing.

## 9. Main-level growth path

A paper-scale route exists without padding:

- **C1 — estimand rewrite:** capability selectivity changes under matched readout/output depth;
- **C2 — causal boundary:** parameter damage and readout-channel damage produce systematically different selectivity signatures;
- **C3 — consequence:** show how this boundary changes which compression conclusion is valid for deployed generation versus recognition-style evaluation, using pre-existing tasks rather than a new benchmark.

The contribution should be framed as a law about interpreting compression interventions, not as a leaderboard correction.

## 10. Fresh verdict

```yaml
old_archive_reason: PAPER_IDENTITY_MUTATION_REQUIRES_FRESH_SELECTION
old_result_killed: false
direct_owner: NOT_FOUND
generic_mc_vs_generation_owner: OWNED_DO_NOT_CLAIM
matched_estimand_rewrite: PLAUSIBLE_INDEPENDENT_CONTRIBUTION
intervention_family_boundary: PLAUSIBLE_INDEPENDENT_CONTRIBUTION
successful_result_upper_bound: PASS
main_level_growth_path: PASS
new_compute_authorized: false
verdict: REOPEN_SERIOUS_SELECTION_PASS
```

**L08 is legitimately reopened for paper-level consideration.** This does not authorize continuation of the old E-series. Any new confirmatory compute must receive a separate bounded authorization under the current workflow.