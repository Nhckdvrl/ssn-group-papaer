# L08 — FINAL ARCHIVE / SCIENTIFIC AUTOPSY

**Date:** 2026-09-14  
**Target venue during development:** ACL / EMNLP / NAACL Main  
**Final status:** **KILL FOR MAIN — DO NOT RECONSTRUCT**  
**Kill ID:** intentionally not assigned here because the authoritative local kill ledger is ahead of the currently visible GitHub `main`; assign only when the ledger is synchronized.  
**Scope:** this file is the final scientific record for the L08 Main route. It supersedes every earlier `REOPEN`, `SERIOUS`, `HIGH-UPSIDE`, `PILOT`, or reconstructed-mainline status for Main-paper purposes.

> **Permanent anti-resurrection rule:** L08 may not be reopened as a Main candidate by renaming the same remainder as `readout`, `expression`, `trajectory mediation`, `external re-groundability`, `state carry`, `error propagation`, `knowledge bias`, `reasoning fragility`, `prefix quality`, or a new compression family. A new model, benchmark, compressor, prompt, decoding method, causal vocabulary, or cleaner implementation does not reopen this scientific parent.

---

# 1. One-sentence final verdict

L08 began as a claim about capability-selective compression damage, survived several rounds of reconstruction, and ultimately reduced to a clean but already-owned fact: **under model perturbation, replacing a perturbed self-generated trajectory with a clean trajectory can rescue downstream generation because errors propagate autoregressively; the proposed novel state-carry / re-groundability mechanism was directly tested and returned a null result.**

That remainder is not sufficient for ACL / EMNLP / NAACL Main.

---

# 2. Why this archive exists

L08 is unusually dangerous for future search because it repeatedly produced large, visually compelling effects and repeatedly invited a new mechanism story after the previous story failed. The project therefore accumulated substantial sunk cost while its Main-level novelty kept shrinking.

The purpose of this archive is not merely to record the last null result. It records the **entire sequence of claim mutations**, why each mutation was scientifically reasonable at the time, why it nevertheless failed, which measurements remain valid, which controls were invalid, and which rescue routes are permanently forbidden.

Future agents should read this file before spending any time on:

- capability-selective compression damage;
- MMLU-vs-GSM8K compression comparisons;
- ranking-vs-generation under pruning / quantization / readout truncation;
- output-depth effects under compression;
- clean-prefix clamping under model perturbation;
- trajectory-mediated compression failure;
- state refresh / state re-grounding under compression;
- claims that knowledge is robust while reasoning is fragile under compression.

---

# 3. Historical arc: every Main identity and why it died

## 3.1 Identity A — representation/readout dimensions

The original project grew from the observation that removing a large fraction of final representation dimensions could leave MMLU-style ranking relatively intact while destroying GSM8K/free generation. Early results looked like a capability-selective representational phenomenon.

This route became untenable because the measured damage depended strongly on **how the answer was read out**. Same-content comparisons showed that ranking, short generation, and long generation could produce radically different apparent retention under the same intervention.

### What remained true

- ranking and open generation can disagree dramatically under compression;
- generative scoring rules can expose failures hidden by bounded ranking;
- which representation coordinates survive can matter much more under generation than ranking.

### Why this cannot carry novelty

The generic scientific claim that evaluation protocol changes pruning/compression conclusions is owned by prior work, including Wen et al. / `The Benchmark Illusion`-style recognition-vs-generation results and Song et al. (ICASSP 2026), which directly studies protocol-dependent conclusions under layer removal/pruning-like interventions.

**Permanent status:** C1 / protocol effect = **OWNED / prerequisite only**.

---

## 3.2 Identity B — capability-selective damage after protocol matching

The project then asked whether the apparent knowledge-vs-reasoning fragility gap survived after matching readout protocol and nominal output regime. Historical E10 appeared to show a striking family boundary: readout-locus interventions tended to produce ratios below 1 while parameter interventions tended to produce ratios above 1, with no wrong-direction crossings.

This looked like a possible Main-level conditional law.

### Fatal audit

The supposedly controlled MMLU-CoT vs GSM8K-CoT comparison did **not** match the causal variable that E07 had already shown to matter: **answer position / answer-bearing trajectory depth**.

Pre-treatment full-model answer-position medians were systematically much later for MMLU than GSM8K:

| model | MMLU median answer position | GSM8K | ratio |
|---|---:|---:|---:|
| Llama 3.1 8B | 84 | 40 | 2.1x |
| Mistral 7B | 76 | 34 | 2.2x |
| OLMo-3 7B | 128 | 44 | 2.9x |
| Phi-4-mini | 132 | 39 | 3.4x |
| Qwen 2.5 7B | 138 | 80 | 1.7x |

The bias direction was exactly the direction needed to push the readout-locus ratio below 1.

After answer-depth matching:

- readout conditions significantly `< 1`: **7/10 -> 2/8**;
- the mild-pruning severity control lost significance: `1.34 [1.19, 1.50] -> 1.24 [0.96, 1.47]`;
- the remaining significant `> 1` cells were concentrated in stronger parameter interventions;
- the strongest surviving statement became merely a no-wrong-direction count with severity confounding reopened.

### Verdict

The intervention-family boundary did not survive identification.

**Permanent status:** old C2 / intervention-locus selectivity = **KILLED BY DEPTH CONFOUND**.

Do not rescue it with additional models, stronger pruning, different quantization, or a new capability pair.

---

## 3.3 Identity C — prompt-recoverable vs trajectory-carried information

The depth audit exposed a new observational pattern. Per-item retention was modeled against `log2(1 + L)`, where `L` was the full-model pre-treatment answer position. Depth sensitivity looked very different on the two sides:

- MMLU / initially called `prompt-recoverable`: negative slope in **1/15** conditions;
- GSM8K / initially called `trajectory-carried`: negative slope in **14/15** conditions;
- significant slope difference in the predicted direction: **8/15**;
- significant reverse-direction difference: **0/15**.

This seemed to suggest that compression damage depends on whether answer-relevant information must be carried through the generated trajectory.

### Why the binary was retired immediately

The names were not scientifically valid:

- in MMLU, the identity of the correct candidate is **not** contained in the prompt;
- in GSM8K, the original problem remains in the prompt and can in principle be re-read/re-solved.

The binary therefore conflated answer-string presence, computation, retrieval, and generated-state dependence.

The `14/15 vs 1/15` pattern was correctly downgraded to **motivation only** and placed on the forbidden-rescue list.

**Permanent status:** `prompt-recoverable` / `trajectory-carried` taxonomy = **RETIRED CONSTRUCT**.

---

## 3.4 Identity D — capability × provenance 2×2

A proposed factorial attempted to orthogonalize capability and answer provenance:

- GSM8K reasoning with self-generated chain;
- GSM8K reasoning with solution chain supplied in the prompt;
- MMLU knowledge with standard prompt;
- MMLU knowledge forced to generate a missing intermediate quantity.

This design was rejected **before treatment compute** because the operation did not isolate provenance:

- supplying the GSM8K solution changed `solve` into `read/verify`;
- forcing MMLU to derive an intermediate quantity added sequential computation to the knowledge condition.

A perfect crossover would still be explained by `more sequential computation is more fragile`.

The design was moved to a superseded construct-probe file and lost identification status.

**Permanent status:** capability × provenance factorial = **SUPERSEDED / NON-IDENTIFYING**.

---

## 3.5 Identity E — trajectory mediation / external re-groundability

The project then switched scientific object from capability labels to a mediation view:

- treatment `T`: compression / model perturbation;
- generated trajectory `Z(T)`;
- final outcome `Y`;
- direct path: `T -> Y`;
- mediated path: `T -> Z(T) -> Y`.

The key instrument became **prefix clamp**: keep the model compressed on every forward pass, but replace appended tokens for a controlled prefix fraction with tokens from a reference trajectory. This cleanly separates persistent local treatment from trajectory contamination better than E07, whose intervention-window manipulation changed direct treatment dose and trajectory state together.

### Instrument validation

The clamp runner passed a strong validation suite:

- **V1 free-running equivalence:** historical free run `0.0860` vs new runner `0.0880`;
- **V2 positive control:** clamp through the answer approximately reproduces full-model performance (`0.7860` vs `0.7660` in the validation setting);
- **V3 treatment coverage:** compared arms had equal `lm_head` treatment coverage (`25200` forward passes in the relevant validation);
- **V4 self-clamp no-op:** self-clamp `0.0967` vs free `0.0941`, absolute difference `0.0025`;
- reference table parsing: `500/500`;
- reference lengths spanned `15–241` tokens;
- no tokenization drift in the audited sample (`0/200`).

A preregistered invariant was also corrected before interpretation: post-release arms are allowed to have different free-generation lengths; the true invariant is that the model intervention remains active at every language-model forward pass.

### Stage-1 result: trajectory mediation is real

At prefix clamp fraction `f = 0.5`:

| intervention | locus | free-running | reference clamp | rescue `Y(R)-Y(F)` | 95% CI |
|---|---|---:|---:|---:|---|
| readout:first | readout | 0.0941 | 0.3995 | +0.3053 | [0.247, 0.361] |
| prune:0.4 | parameter | 0.0585 | 0.1628 | +0.1043 | [0.061, 0.148] |
| quant:4 | parameter | 0.4071 | 0.6667 | +0.2595 | [0.193, 0.326] |

For the readout intervention, reference-clamp dose response was monotonic:

| clamp fraction `f` | 0 | 0.25 | 0.50 | 0.75 | 1.00 |
|---|---:|---:|---:|---:|---:|
| retention | 0.094 | 0.221 | 0.400 | 0.725 | 0.972 |

This is the cleanest positive result in the project. It establishes that downstream failure is substantially mediated by the generated trajectory under multiple perturbation families.

### Why this still does not provide Main novelty

Clean-prefix replacement is not a new causal instrument in the broader autoregressive-error literature. Exposure-bias / self-recovery work has already used clean or ground-truth prefixes to diagnose self-generated-error propagation. RAC and AYOT additionally own the modern compression-side observation that reasoning/decode trajectories matter and provide reasoning-aware/on-policy calibration remedies.

Therefore `clean trajectory rescues perturbed generation` is a valid result but not a sufficient Main-level scientific contribution by itself.

**Permanent status:** C2a trajectory mediation = **SUPPORTED PHENOMENON, INSUFFICIENT NOVELTY FOR MAIN**.

---

# 4. Failed attempt to distinguish same-perturbation trajectory effects from generic prefix quality

The project correctly recognized that reference clamp confounds two properties:

1. the prefix is untreated / not generated under the current perturbation;
2. the prefix is also higher quality / more correct.

Several control arms attempted to distinguish these.

## 4.1 Temperature-sampled corrupted reference

This arm initially produced an unexpected negative rescue. It was later invalidated for two reasons.

First, prefix-quality audit showed it was off-task / degenerate. Second, a more serious implementation bug was discovered: `load_items` generated IDs that depended on `n`, so some control files could clamp an item using a trajectory belonging to a different question.

Contaminated outputs were isolated and removed from the evidential record; both runners were hardened with `assert_item_identity()`.

**Lesson:** item identity is a causal invariant, not bookkeeping. IDs must be stable across sample size, arm construction, reruns, and cached reference generation.

## 4.2 Foreign-perturbation prefixes

Using a prefix generated under another perturbation also produced a negative effect, but the candidate control prefix was lower quality than the target perturbation trajectory (e.g. `on_task` approximately `0.276` vs `0.415` in one key audit). It therefore did not identify perturbation provenance separately from prefix quality.

**Status:** invalid as a causal residual control.

## 4.3 Surgical corruption

A more controlled corruption operation altered arithmetic results while preserving most surface structure and on-task behavior. It was the only quality-audited control with a plausible interpretation for severe interventions.

However, the design exposed a structural limitation:

- severe interventions require large corruption to approximate their bad-prefix quality;
- mild interventions, especially quantization, have mostly correct intermediate spans, so full corruption makes the control strictly worse;
- rate matching for mild interventions leaves very few changed items and correspondingly low power.

This is not merely an implementation inconvenience. It means there is no single synthetic-prefix control that simultaneously matches quality, realism, error rate, and treatment provenance across intervention severities.

### Resulting decision

Do **not** continue inventing increasingly elaborate corrupted-prefix controls. This route is closed.

---

# 5. Identity F — selective state re-grounding / state carry

Because prefix-level residual controls were structurally confounded, the final Main route proposed a stronger mechanism:

> perhaps compression does not merely create a bad chain; perhaps it specifically makes an already-computed load-bearing intermediate state fail to remain effectively usable through the later autoregressive trajectory.

The discriminating intervention was **self-state refresh**: on trajectories where the model had already correctly produced a load-bearing intermediate value, replay that same already-produced state at a causally relevant point. Compare against a matched placebo and use a treatment-specific difference-in-differences:

`Delta_refresh = [Y_T(state) - Y_T(placebo)] - [Y_0(state) - Y_0(placebo)]`.

This was explicitly designated the load-bearing Main-level gate. The standing rule was: if selective refresh does not rescue perturbed trajectories beyond placebo, the mechanistic Main route dies; do not retreat to clamp magnitude, dose response, protocol effects, or UniComp auditing.

## 5.1 Important implementation error caught before the final conclusion

The first refresh location was incorrectly placed after the last annotated state, at a point where the answer computation was effectively complete. That would make the intervention constructively unable to test the proposed mechanism.

The location was corrected, and the relevant E13 runs were redone before the final conclusion.

This error and correction must remain part of the permanent record.

## 5.2 Final decisive result

Primary preregistered estimand:

`Delta_refresh = +0.0000  [−0.102, +0.102]`.

| arm | n | state | placebo | within-arm difference | 95% CI |
|---|---:|---:|---:|---:|---|
| full precision | 101 | 0.7723 | 0.7723 | +0.0000 | [−0.050, +0.050] |
| quant 4-bit | 112 | 0.2946 | 0.2768 | +0.0179 | [−0.045, +0.080] |
| readout keep=0.75 | 3 | — | — | — | not estimable |

The CI can exclude a refresh effect larger than roughly 0.10 in magnitude. The proposed mechanism was motivated by reference-clamp rescue of roughly +0.26 under quantization, so the test had enough resolution to reject a mechanism expected to explain a substantial fraction of the clamp effect. It does not exclude tiny refresh effects, but a tiny effect cannot carry the proposed Main-level mechanism.

## 5.3 The decisive within-model contrast

Same model, same task, quantization treatment:

| operation | effect on quant 4-bit |
|---|---:|
| replace a substantial prefix with the correct/reference trajectory | `+0.2595 [0.191, 0.326]` |
| replay the model's own already-correct, downstream-relevant intermediate state once | `+0.0179 [−0.045, 0.080]` |

The difference is an order of magnitude.

### Interpretation

The evidence does **not** support the proposed state-carry / state-loss account.

The simple account is sufficient:

> compression perturbs local generation; the perturbed model writes a worse trajectory; later predictions condition on that worse trajectory; replacing enough of the bad trajectory with a good trajectory helps.

That is ordinary autoregressive error propagation under a model perturbation. The trigger is compression rather than sampling/model mismatch, but the causal shape is not a new Main-level mechanism.

**Permanent status:** C2b state re-grounding / selective state carry = **FALSIFIED AT THE PRE-REGISTERED MAIN GATE**.

---

# 6. Why the readout-locus version cannot rescue the state-refresh mechanism

The self-state-refresh design requires the perturbed model to first generate a correct intermediate state. Availability collapsed under strong interventions:

| intervention | usable trajectories / 500 |
|---|---:|
| full precision | 101 (20%) |
| quant 4-bit | 112 (22%) |
| prune 40% | 11 (2%) |
| readout keep=0.75 | 3 (0.6%) |
| readout keep=0.5 | 0 (0%) |

Thus the readout anchor is not estimable under this instrument. This does **not** justify weakening the gate. The parameter-locus test was estimable and returned a null.

Do not model-shop for a readout severity that merely yields enough usable trajectories unless there is a new, independently motivated scientific question. Doing so would be post-hoc rescue.

---

# 7. Final novelty accounting

| layer | final status | reason |
|---|---|---|
| C1 — protocol / readout effect | **OWNED** | recognition-vs-generation / protocol-dependent compression conclusions already in prior work, including Wen/Song neighbors |
| old C2 — intervention-locus capability selectivity | **KILLED** | answer-depth confound; severity control collapses after correct matching |
| observational depth dissociation | **MOTIVATION ONLY** | between-task / construct confounds; old binary taxonomy invalid |
| C2a — trajectory mediation by clean-prefix clamp | **SUPPORTED BUT NOT MAIN-NOVEL** | causal and reproducible, but clean-prefix error-propagation diagnostics are prior-owned; RAC/AYOT already establish trajectory-aware compression remedies |
| C2b — selective state re-grounding | **FALSIFIED** | preregistered `Delta_refresh` is 0 within ±0.10; state replay is tiny relative to +0.26 reference clamp rescue |
| C3 — reinterpret published knowledge/reasoning robustness | **UNREACHABLE AS MAIN CONTRIBUTION** | depended on a novel mechanism beyond ordinary error propagation; without C2b it becomes auditing/measurement commentary |

There is no remaining Main-level scientific quantity whose ownership and identification are both defensible.

---

# 8. Final reviewer compression

A strong reviewer can summarize the surviving project as:

> `Compression causes local generation errors. In autoregressive generation, those errors enter the future prefix and propagate. Replacing the bad prefix with a clean prefix helps. A more selective attempt to rescue an already-computed state does not help. Prior exposure-bias work already uses clean-prefix replacement, while RAC / AYOT already show that reasoning-time trajectories matter for compression and provide trajectory-aware calibration.`

That compression is accurate enough that no ACL / EMNLP / NAACL Main contribution remains.

This is the final reason for the kill.

---

# 9. Explicit forbidden-rescue list

The following are **not allowed** as routes to reopen L08 for Main:

1. `MC vs generation` or `ranking vs open generation` under compression.
2. More models showing protocol sensitivity.
3. More compressors showing reference-clamp rescue.
4. Returning to `readout-locus vs parameter-locus` no-crossing counts.
5. Reusing the pre-depth-matching mild-pruning severity control.
6. Claiming `knowledge is robust / reasoning is fragile` from benchmark families whose format/depth differ.
7. Renaming clean-prefix rescue as `trajectory dependence`, `trajectory mediation`, `external re-groundability`, `prefix contamination`, or `autoregressive amplification` without a new scientific estimand.
8. Returning to the `prompt-recoverable vs trajectory-carried` binary.
9. Rebuilding the superseded capability × provenance 2×2.
10. Creating more synthetic corrupted-prefix arms to recover a same-perturbation residual.
11. Weakening the state-refresh null into `there may be a <10pp effect` and treating that as the Main mechanism.
12. Model-shopping / task-shopping for a readout intervention that yields enough correct intermediate states for refresh.
13. Turning UniComp / GPQA / MMLU auditing into the main paper after the mechanism route has failed.
14. Falling back to `0/15 wrong-direction crossings` or similar descriptive counts.
15. Treating the monotonic clamp dose response as novel by itself.
16. Recasting the same result as a new compression method paper unless there is independently new algorithmic substance; the present project was selected as model science, not method optimization.

If any future proposal resembles one of these, cite this archive and reject it unless a genuinely different parent scientific question has emerged in the literature.

---

# 10. What remains scientifically valid and reusable

Killing the Main route does **not** invalidate every result.

## 10.1 Valid empirical findings

- evaluation/readout protocol can radically alter apparent compression damage;
- answer-bearing depth is a real causal variable and must not be approximated by `has CoT` or raw output length;
- under several perturbations, clean/reference-prefix clamping yields large recovery while the perturbation remains active on every forward pass;
- clamp fraction produces a monotonic trajectory-mediation dose response in the tested readout setting;
- long-generation collapse is not explained simply by repetition loops;
- a fixed vocabulary-bias hypothesis was causally rejected;
- vocabulary-set size/extreme-value competition was rejected as the generic explanation;
- next-token margin explains part, but not all, of local survival;
- supplied answer markers can rescue a component of failure but not the whole task;
- state refresh of an already-correct intermediate does not produce the large rescue predicted by the proposed state-carry mechanism.

These are useful facts. They are **not a Main paper when assembled under the current novelty landscape**.

## 10.2 Reusable instrumentation

Preserve, audit, and reuse where scientifically appropriate:

- per-forward-pass intervention coverage validation;
- self-clamp no-op validation;
- token-ID clamp to avoid retokenization drift;
- stable item identity assertions across cached/reference/control datasets;
- answer-position / answer-depth extraction;
- prefix-quality audits;
- paired/item-level bootstrap for retention differences;
- clamp dose-response machinery;
- fixed-prefix / teacher-forced per-step diagnostics as secondary analysis;
- explicit separation of reference-prefix rescue from selective state intervention.

Reuse the tools, not the dead scientific claim.

---

# 11. The four implementation / analysis errors that must never be forgotten

## Error 1 — `controlled` did not mean causally matched

The E10 long-generation comparison was labeled protocol/length controlled but did not match answer-bearing depth. Because E07 had already shown positional sensitivity, this invalidated the central selectivity inference.

**Permanent lesson:** define the causal quantity, then measure/match it directly. Labels such as `CoT`, `long`, or `same protocol` are not substitutes.

## Error 2 — unstable item identity

`load_items` IDs changed with `n`; cached/control trajectories could be joined to the wrong question. Some apparently pathological corrupted-reference behavior was therefore misdiagnosed before the bug was found.

**Permanent lesson:** item IDs must be content-stable and asserted at every cross-file join. Never infer identity from row order or sample-size-dependent enumeration.

## Error 3 — refresh after the causal event

The first state-refresh point occurred after the last annotated state / after the answer-relevant computation was effectively complete. A null there would have been structurally meaningless.

**Permanent lesson:** every intervention needs a manipulation-validity proof that it occurs **before** the outcome-relevant decision it is supposed to affect.

## Error 4 — wrong invariant in preregistration

An early preregistration required equal step counts between free and clamp-release arms. That was conceptually wrong: once clamp is released, generation length is an outcome and may diverge. The real invariant is treatment coverage at each actual model forward pass.

**Permanent lesson:** distinguish controlled treatment exposure from downstream behavioral variables. Do not freeze an outcome as if it were an instrument invariant.

All four errors were detected and corrected before the final Main kill conclusion. Contaminated runs must stay isolated and must not be resurrected as evidence.

---

# 12. The deeper project-selection failure

The most important failure happened **before** the last experiment.

L08 repeatedly had this structure:

1. a large stable observation appears;
2. the obvious interpretation is found to be owned or confounded;
3. a narrower residual mechanism is proposed;
4. because the observation is large, the residual mechanism is treated as promising;
5. a selective experiment later shows that the residual does not exist or is not identified.

This happened multiple times:

- representation-dimension story -> protocol ownership;
- capability-selectivity story -> depth confound;
- prompt-vs-trajectory story -> construct invalidity;
- trajectory mediation -> prior-owned error propagation;
- state re-groundability -> direct null.

The search mistake was to infer:

> `large unexplained phenomenon` -> `high probability of novel mechanism`.

That implication is false.

A phenomenon can be large because a known generic process is large. Once prior work owns the generic process, **the burden is on the candidate to identify the residual mechanism before substantial compute**, not after.

---

# 13. New mandatory selection rule derived from L08

Add the following doctrine to future Main-level selection:

> **Residual-Mechanism Gate.** If the motivating phenomenon is already substantially explained by an owned parent mechanism, and Main novelty requires a narrower residual mechanism, the candidate is not compute-authorized merely because the mother effect is large. Before expansion, specify one selective intervention for which:
>
> 1. the owned mechanism and proposed new mechanism make different predictions;
> 2. a null kills the Main route;
> 3. the operation does not simultaneously change task difficulty, sequential-computation burden, answer information, or evaluator construct;
> 4. the predicted effect size is large enough to resolve cheaply.
>
> If such an intervention cannot be written cleanly, kill at Selection.

L08 should be the canonical negative example for this rule.

---

# 14. Additional durable methodological lessons

1. **A matched contrast is only as good as the matched causal variable.** Output length, CoT presence, and answer depth are not interchangeable.
2. **Pre-treatment quantities should define matching whenever possible.** Using post-treatment length or success can induce conditioning bias.
3. **A positive-control rescue is not a mechanism.** Reference clamp showed that good context helps; it did not tell us what property of the context mattered.
4. **A mediator can be real without being novel.** Causal mediation is not automatically a contribution if the mediator is already the standard error-propagation channel in the literature.
5. **Do not confuse `instrument is new to this subfield` with `scientific inference is new`.** Clean-prefix replacement was informative for compression, but the inferential pattern already existed in exposure-bias work.
6. **Control-arm quality is part of identification.** A corrupted control that is off-task, degenerate, or substantially worse than the treatment prefix does not isolate provenance.
7. **Rate matching can destroy power.** If the scientifically necessary control leaves only a tiny manipulated subset, resolution must be audited before treatment runs.
8. **Severe and mild perturbations may require incompatible controls.** When control construction depends on treatment severity, a single broad mechanism claim becomes suspect.
9. **Sunk cost must never raise a candidate's evidential prior.** More completed E-series is not a reason to preserve the paper identity.
10. **When a preregistered Main gate fails, obey it.** The correct response to `Delta_refresh ≈ 0` is kill, not a new name for C2.

---

# 15. Findings/short-paper remainder

There is a defensible lower-tier empirical remainder:

> quantify how much compression-induced free-generation failure is trajectory-mediated using a validated prefix-clamp instrument, across multiple perturbation families, with a monotonic dose response.

This could plausibly support a Findings / short diagnostic paper if there were a strategic reason to write it.

However:

- the project target was Main;
- the generic causal form overlaps prior exposure-bias diagnostics;
- RAC / AYOT already own important trajectory-aware compression phenomena and remedies;
- converting the project into a lower-tier paper solely to justify sunk compute is not itself a reason to continue.

**Default project policy:** no additional compute or writing investment for this remainder unless separately authorized for a concrete low-cost submission opportunity.

Do not let the existence of a Findings-sized remainder weaken the Main kill.

---

# 16. Final status matrix

| object | evidence | novelty | final action |
|---|---|---|---|
| protocol/readout sensitivity | strong | owned | archive |
| answer-depth confound | strong | useful audit, not paper | archive |
| intervention-locus selectivity | fails correct identification | insufficient | kill |
| depth slope dissociation | observationally strong | construct-confounded | motivation only |
| clean-prefix trajectory mediation | causally strong | substantially prior-owned | Findings-level remainder only |
| same-perturbation residual | not cleanly identified by synthetic controls | no Main claim | stop |
| selective state re-grounding | preregistered null | proposed novelty falsified | **kill** |
| UniComp / knowledge-bias consequence | potentially interesting | cannot carry paper alone | do not pivot |

---

# 17. FINAL DECISION

## **L08 — KILL FOR ACL / EMNLP / NAACL MAIN**

### Primary scientific reason

The only clean surviving causal effect is ordinary trajectory-mediated autoregressive error propagation under model perturbation; the additional state-carry / re-groundability mechanism required to distinguish the work from prior exposure-bias and reasoning-aware compression literature was directly tested and not supported.

### Secondary reasons

- core protocol effect already owned;
- previous capability-selectivity claim was depth-confounded;
- clean-prefix clamp itself is not a new inferential pattern;
- synthetic residual controls cannot cleanly isolate perturbation provenance from prefix quality across severities;
- C3 becomes evaluation/auditing commentary without a novel C2 mechanism.

### Reopen condition

**None under the current scientific parent.**

Only a genuinely new external discovery that changes the scientific question itself — not a new dataset, compressor, model, prompt, state definition, or intervention tweak — could justify discussing this family again. Such a future idea must be selected as a new candidate and must cite this archive as an anti-resurrection parent.

---

# 18. Short handoff for future agents

If you encounter L08 and wonder whether it was killed too aggressively, read these four numbers first:

- reference clamp rescue under quant 4-bit: **+0.2595 [0.191, 0.326]**;
- selective self-state refresh under quant 4-bit: **+0.0179 [−0.045, 0.080]**;
- preregistered treatment-specific refresh estimand: **0.0000 [−0.102, +0.102]**;
- readout-locus usable refresh trajectories at keep=0.75: **3/500**.

Then remember:

> **Replacing a bad trajectory with a good one works. Replaying the model's own already-correct load-bearing state does not. The proposed new mechanism is therefore not supported; the surviving effect is generic autoregressive error propagation.**

Stop there. Do not reconstruct L08 again.
