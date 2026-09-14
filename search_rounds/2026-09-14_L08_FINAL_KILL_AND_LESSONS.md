# 2026-09-14 — L08 FINAL KILL / SEARCH-LEVEL ANTI-RESURRECTION

**Canonical detailed archive:** `candidates/L08_READOUT_DIMENSION/FINAL_ARCHIVE_2026-09-14.md`  
**Status:** **KILL FOR ACL / EMNLP / NAACL MAIN — DO NOT RECONSTRUCT**

This short file exists so future open-ended search agents encounter the kill even if they never open the L08 candidate directory.

---

## What finally killed L08

L08 repeatedly changed identity after an earlier claim became owned, confounded, or non-identifying:

1. representation/readout-dimension selectivity;
2. protocol-dependent capability damage;
3. intervention-locus selectivity after protocol matching;
4. `prompt-recoverable vs trajectory-carried` depth sensitivity;
5. trajectory mediation under persistent compression;
6. selective state re-grounding / state carry.

The last route was the first one with a genuinely discriminating Main-level gate.

### Stage-1 trajectory mediation was strongly positive

Keeping the model perturbation active on every forward pass while replacing part of the appended prefix with a reference trajectory produced large rescue:

- readout:first: `+0.3053 [0.247, 0.361]` at `f=.5`;
- prune 40%: `+0.1043 [0.061, 0.148]`;
- quant 4-bit: `+0.2595 [0.193, 0.326]`;
- readout clamp dose response: `0.094 -> 0.221 -> 0.400 -> 0.725 -> 0.972` for `f=0,.25,.5,.75,1`.

This establishes that perturbed generated context mediates a large share of failure.

### But the Main-level residual mechanism failed

The load-bearing prediction was that compression makes an already-computed, downstream-relevant intermediate state fail to remain effectively usable; replaying that state should selectively rescue the compressed trajectory.

Pre-registered estimand:

`Delta_refresh = [Y_T(state)-Y_T(placebo)] - [Y_0(state)-Y_0(placebo)]`

Final result after fixing the refresh position and rerunning:

`Delta_refresh = +0.0000 [-0.102, +0.102]`.

Under quant 4-bit:

- full reference-prefix clamp rescue: `+0.2595 [0.191, 0.326]`;
- replay of the model's own already-correct load-bearing state: `+0.0179 [-0.045, 0.080]`.

The proposed state-carry / external-re-grounding mechanism therefore does not explain the large clamp effect.

The surviving simple account is ordinary autoregressive error propagation:

> perturbation changes local generation -> the model writes a worse trajectory -> later predictions condition on that worse trajectory -> replacing enough of the bad trajectory with a good one helps.

That scientific shape is already substantially owned by exposure-bias / self-recovery diagnostics, while RAC / AYOT own the modern observation that reasoning/decode trajectories matter for compression and provide trajectory-aware remedies.

No Main-level novelty remains.

---

## Earlier claims that are also dead

### Generic protocol effect

Owned. Recognition/ranking vs free generation under pruning/compression cannot be claimed as L08 novelty.

### Intervention-locus boundary

Killed by answer-depth confounding. The historical `controlled` comparison matched nominal CoT/long generation but not answer-bearing trajectory depth. After correct depth matching, the mild-pruning severity control became null and the clean family boundary disappeared.

### `prompt-recoverable vs trajectory-carried`

Retired construct. MMLU's correct-candidate identity is not present in the prompt, while GSM8K can in principle re-read/re-solve from the original prompt.

### capability × provenance 2×2

Non-identifying. Supplying a GSM8K solution changes solve -> verify; forcing MMLU to derive a missing intermediate adds sequential computation. A crossover is explainable without provenance.

### corrupted-prefix residual

Do not keep rebuilding controls. Severe and mild interventions require incompatible corruption severity; quality matching and error-rate matching trade against statistical power and realism.

---

## Four permanent implementation / identification lessons

1. **Answer depth is not raw output length or `has CoT`.** Match the actual causal quantity.
2. **Item identity must be stable and asserted.** An `n`-dependent ID bug caused some control trajectories to attach to the wrong question; contaminated runs were isolated.
3. **An intervention must occur before the causal decision.** The first refresh point was after the relevant state/answer computation and had to be corrected and rerun.
4. **Do not freeze downstream outcomes as instrument invariants.** Clamp-release arms may diverge in length; the actual invariant is intervention coverage on every model forward pass.

---

## Permanent forbidden-rescue list

Do not reopen L08 Main by:

- adding more models/compressors to the protocol effect;
- returning to MC vs generation;
- returning to intervention-locus no-crossing counts;
- using the old pre-depth-matching severity control;
- renaming trajectory mediation as `external re-groundability`, `prefix contamination`, `state carry`, or `autoregressive amplification`;
- reviving `prompt-recoverable vs trajectory-carried`;
- rebuilding the superseded capability × provenance factorial;
- inventing more synthetic corrupted-prefix controls;
- claiming a possible `<10pp` state-refresh effect after the preregistered Main mechanism predicted a clamp-scale effect;
- model/task shopping for an estimable readout refresh arm;
- pivoting to UniComp / knowledge-bias auditing as the Main paper;
- treating the monotonic reference-clamp dose response as sufficient novelty.

A Findings/short empirical remainder may exist, but sunk compute is not a reason to write it and it must never weaken the Main kill.

---

# Search-process lesson: Residual-Mechanism Gate

L08 should become the canonical negative example for a new selection rule:

> **If the mother phenomenon is large but the broad mechanism is already owned, and Main novelty depends on a narrower residual mechanism, do not infer that the residual is promising from the size of the mother effect. Before substantial compute, require one selective intervention on which the owned account and new mechanism make different predictions, with a preregistered null that kills the Main route.**

The intervention must not simultaneously change task difficulty, sequential-computation burden, answer information, evaluator construct, or a similarly load-bearing alternative quantity.

If no such operation can be written cleanly, kill at Selection.

---

## Search-level final status

**L08 scientific parent is CLOSED.**

Reuse instrumentation if useful. Reuse methodological lessons aggressively. Do not reuse the paper question.
