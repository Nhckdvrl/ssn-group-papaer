# S03 — From Document End to Task Done

**Status:** PILOT — phenomenon and parameter locus established; acquisition
mechanism NOT yet found. Not paper-ready.
**Opened:** 2026-09-17 · **README last re-based on evidence:** 2026-09-19
**Topic authority:** `ssn-taste/S03_FROM_DOCUMENT_END_TO_TASK_DONE.md`, `ssn-taste/SELECTED_TOPICS.md`

## Frozen scientific object

> How does post-training turn pretrained document/text-ending behaviour into
> goal-relative assistant stopping?

Pretraining teaches *when this text ends*. An assistant must decide *whether
this user's task is done, so this turn should stop now*. Those are different
completion criteria. The object is the acquisition of

```
user-goal completion  ->  STOP vs task-relevant continuation
```

Not an EOS benchmark, not a stopping leaderboard, not instruction following,
not response length, not a circuit hunt.

## Instrument (E01)

Matched pair = two conditions with a **token-for-token identical assistant
prefix**; only the user goal changes, which flips whether the replayed prefix
already satisfies the request.

```
stop_margin = z(stop) - z(correct next missing token)
d_goal      = stop_margin(complete) - stop_margin(incomplete)
            = dz_stop - dz_cont
```

The raw-logit decomposition is canonical. `Δ log p(stop)` carries a
whole-vocabulary normalizer `Δ log Z` that differs by arm and has flipped the
apparent sign of an effect more than once in this project; it is never used for
a parameter-locus or architecture claim.

Stimuli (50 primary pairs + 12 lexical-matched controls), deliberately
non-isomorphic:

| family | goal form | cardinality stated? |
|---|---|---|
| `A_bounded_quantity` | "give the first N" | yes |
| `B_semantic_predicate` | set-membership predicate | **no** |
| `C_slot_requirement` | requested field set | implicitly |
| `D` (control) | C with the missing field named in **both** prompts | — |

`B` decides that the effect is not counting; `D` decides that the slot effect is
not lexical priming from the missing field's name.

Every run also emits the continuation-awareness control (rank and probability of
the correct missing continuation in the incomplete condition).

## What is established

1. **Goal completion controls assistant termination, at exact prefix identity.**
   Present in OLMo-3, Qwen2.5 and Llama-3.1.
2. **It follows the token that ends the assistant turn, not "EOS".** In
   Llama-3.1 Instruct the turn-end token moves *with* goal completion
   (`dz_stop` = +6.63, 48/2) while the document-end token moves *against* it
   (−2.57, 8/42). Textual completeness raising EOS does not explain this.
3. **Pretrained bases already have goal sensitivity**, and post-training
   amplifies it — `dz_stop` at base → instruct: +3.79 → +6.94 (Qwen),
   +2.47 → +6.63 (Llama). Post-training does **not** create this from zero.
4. **Pretrained families start from radically different termination geometry.**
   Base `dz_cont`: +0.67 (OLMo-3), −7.34 (Llama-3.1), −12.45 (Qwen2.5). This is
   a fact about pretraining and is currently **unexplained**.
5. **Goal-relative stopping is not output-row calibration.** With the entire LM
   head byte-frozen (arm `Sbody`, 2250 steps of ordinary instruction SFT),
   internal-state adaptation improves `d_goal` in all three families:
   **+11.27 / +8.73 / +2.95** (sign 49/1, 47/3, 37/13). Stop-readout adaptation
   (arm `R`, 4,097 trainable parameters) ranges from **+6.03 to −1.84** — it is
   model-dependent and can be actively harmful.
6. **Learning where responses usually end ≠ learning when this user's task is
   done.** Qwen arm R takes generic `boundary_auc` 0.965 → 0.999 while its
   goal-relative reading goes *down*.

## What has been retracted (do not revive)

Left in `docs/RESEARCH_LOG.md` with dated corrections rather than deleted.

* ~~"Reading and clearing are different problems with different parameter
  loci"~~ and ~~"goal-relative stopping requires two changes"~~ — falsified by
  Llama-3.1: `Sbody` moves `dz_stop` by only +0.29 (null) yet `d_goal` by +2.95
  through the continuation side alone. Either side can carry the effect.
* ~~"A stop readout structurally cannot clear the continuation"~~ as a
  *finding* — arm R holds every non-stop logit fixed **by construction**, so
  `Δdz_cont^R = 0` at every family, budget, seed and capacity. It is a
  decomposition constraint, not a result, and must not be a headline.
* ~~"Qwen/Llama bases are not clean document continuers"~~ — excuse-making for
  inconvenient data; both are official pretrained bases.
* Three proposed mechanisms for the cross-family difference in arm R, all
  **tested and rejected**: initial-gradient alignment `(−g)·v`; mean
  boundary-direction geometry `cos(b, v)`; and the generic-boundary-competence
  capacity trade-off (falsified by a within-OLMo causal test — R's endpoint is
  initialization-invariant, 13.53 / 13.68 / 13.77 from wildly different
  starting rows). The Llama held-out sign hit is downgraded to an
  **unexplained cross-family correlation**; it is not a validated prediction
  and does not belong in an abstract.
* The `250 / 750 / 2250`-step runs are **not a trajectory**. Each rebuilds its
  own cosine schedule, so they are three optimization endpoints, not
  checkpoints of one run. They license matched-endpoint robustness claims only,
  never acquisition dynamics.
* The old `Layer B` table in `docs/RESULTS.md` scored each checkpoint with its
  **own** generation-config stop set (base on `<|endoftext|>` alone, every
  post-trained stage on a two-token logsumexp), so the measured action changes
  along the curve. Marked CONFOUNDED; superseded by the fixed-token trajectory.

## What the project is missing

> **Which supervision in ordinary post-training teaches "the user's request is
> satisfied, so stop"?** There is no `task_complete=True` label anywhere in SFT.

Execution order: (1) a real natural acquisition trajectory over the *actual*
OLMo-3 post-training chain — Base → Think-SFT → Instruct-SFT → DPO → RLVR, with
Instruct-SFT warm-started from Think-SFT, measured on **one fixed stop token**
across every checkpoint; then (2) supervision-source decomposition (full SFT vs
content-only vs EOT-only vs instruction-decoupled) at whichever stage the
trajectory identifies; then, only if content supervision matters,
(3) hard-negative premature-stopping positions with a causal reweight; then
(4) held-out validation on a frozen E01-v2.

## Layout

```
src/        experiment code
stimuli/    E01 exact-prefix stimuli (instrument, NOT a benchmark)
results/    raw per-item measurements + logs (never overwritten)
docs/       RESULTS.md (generated) and RESEARCH_LOG.md (dated, append-only)
```

Numbers: `docs/RESULTS.md` (regenerate with `src/make_results.py`).
Reasoning, including every correction: `docs/RESEARCH_LOG.md`.
