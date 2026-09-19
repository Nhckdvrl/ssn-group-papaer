# S03 — From Document End to Task Done

**Status:** `KILLED / ARCHIVED — K195` (2026-09-19)
**Do not reopen this parent question with a new model, dataset, stage,
supervision variant, or name.** Read `docs/RESEARCH_LOG.md` bottom-up first;
the last three entries are the ones that matter.
**Opened:** 2026-09-17 · **Killed:** 2026-09-19
**Topic authority:** `ssn-taste/S03_FROM_DOCUMENT_END_TO_TASK_DONE.md`

## Why it was killed

The phenomenon is real and the instrument is sound. The project died because
the **scientific object kept being absorbed by the training recipe**: every
attempt to compress it into a mechanism added a dependency rather than removing
one — training budget, model family, stop-token/tokenizer/serialization drift,
and three mechanistic hypotheses for the cross-family difference, each
falsified by direct causal test. Continuing meant enumerating
`budget x LR x data x family x checkpoint x serialization x stage`: a forensic
investigation, not a paper. And because 2026 post-training is not a shared
`Pretrain -> SFT -> RL` pipeline, there was no universal developmental path to
recover in the first place.

The final adjudication experiment (E04) came back one layer short. Ordinary SFT
on correctly paired instruction data builds goal-relative stopping (+6.70,
48/2) and mispaired data destroys it (−6.17, 3/47) **without harming generic
boundary competence** (`boundary_auc` 0.9992, val CE 1.122) — a clean fact, but
the supervision *mask* axis did not resolve (`terminal` +2.44 at 33/17,
`content` +1.40 at 35/15, both far below `full`), both terminal-only arms
trained themselves into broken models on a saturated objective, and the one
strong effect is probably not specific to termination. Establishing specificity
needed another control, which is exactly the cost that was being stopped.

A good project gets simpler as it goes. This one gained a condition at every
repair.

**Reusable, and worth preserving rather than rerunning:** the exact-prefix
matched-pair instrument; the raw-logit decomposition
`d_goal = dz_stop − dz_cont` and the reason `Δ log p(stop)` must not be used for
locus claims; the rule that a longitudinal curve must score **one fixed
termination token** and assert **byte-identical inputs** per item (both
defects occurred here, and the second was caught only because the assertion
existed); and the observation that generic boundary competence and
goal-relative stopping dissociate.

## Frozen scientific object (as of the kill)

> **What supervision teaches a language model to stop when the user's task is
> complete?** Equivalently: how does post-training bind already-latent
> goal-completion information to the termination action?

Pretraining teaches *when this text ends*. An assistant must decide *whether
this user's task is done, so this turn should stop now*. Those are different
completion criteria, and nothing in ordinary training data carries a
`task_complete=True` label. The object is the acquisition of

```
user-goal completion  ->  STOP vs task-relevant continuation
```

**The object is a learning signal, not a training stage.** As of 2026 there is
no shared `Pretrain -> SFT -> RL` recipe to index: publicly described flows
differ substantially from one another (Qwen3's long-CoT cold start, reasoning
RL and thinking/non-thinking fusion; DeepSeek-R1's cold-start SFT, reasoning
RL, rejection-sampling SFT and a further general RL round; Llama 4's
lightweight SFT into online RL into lightweight DPO; OLMo-3's separate Think,
Instruct and RL-Zero flows). *(Each of these needs its citation checked against
the primary source before it is written into a paper.)* "Which stage teaches
goal-relative stopping?" therefore has no stage-independent answer — a reviewer
can fairly ask *whose* stage, and where Think-SFT or mode fusion is supposed to
sit. The supervision underneath those recipes — endpoint supervision,
continue-here supervision, instruction-response pairing, preference over
complete vs incomplete responses — is comparable across all of them, and that
is what this project factorises.

The heterogeneity of modern recipes is the **motivation**, not an obstacle:
*named stages are not comparable across modern model flows, so we ask the
lower-level question of what supervision is sufficient to turn goal completion
into a stopping action.*

Not an EOS benchmark, not a stopping leaderboard, not instruction following,
not response length, not a circuit hunt, and **not a developmental-stage
study**.

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

## The natural anchor (observational, deliberately demoted)

The OLMo-3 trajectory is a **case study in one fully open flow**, used only to
show that goal-relative stopping really does change a lot under real modern
post-training, and to locate a transition worth using as a laboratory. It is
**not** a universal developmental claim and its stage names carry no weight.

Measured with one frozen instrument, one fixed stop action (`<|endoftext|>`),
one serialization, and byte-identical inputs asserted per item:

| transition | Δd_goal | sign | Δdz_stop | Δdz_cont |
|---|---|---|---|---|
| base → Think-SFT | +2.76 | 38/12 | −3.25 | −6.01 |
| Think-SFT → Instruct-SFT | **+7.31** | 49/1 | **+7.26** | −0.04 |
| Instruct-SFT → DPO | +6.97 | 49/1 | +3.56 | −3.41 |
| DPO → RLVR | +3.26 | 49/1 | +2.20 | −1.06 |

The one sentence this licenses: *in this fully open flow, the largest clean
goal→STOP jump occurs across the Think-SFT → Instruct-SFT transition.* That
is why the causal experiment starts from Think-SFT final on Dolci-Instruct-SFT
data — a real incoming checkpoint and its real incoming data — and nothing
further is claimed about stages.

(Building a within-stage timeline was started and **stopped**: refining *when
inside a named stage* is exactly the stage-centric detail this project is not
about. Five stage endpoints plus one Think-SFT intermediate are kept.)

## The decisive experiment (E04) — RUN, and it adjudicated KILL

Same initialization, same example pool, same order, same step count, same
schedule, same optimizer, same batch, same seed. **Only the supervision
changes.**

| condition | what it supervises |
|---|---|
| `full/correct` | content tokens + the turn-end token (positive control) |
| `terminal/correct` | the turn-end token **only** — never told what to say |
| `content/correct` | content tokens only, terminator masked — **never told where to stop** |
| `full/shuffled` | the same responses, lengths and endpoints, attached to *another* user's goal |
| `terminal/shuffled` | endpoints without the goal that determines them |

The readings are stage-agnostic and transfer to any recipe: *endpoint
supervision is sufficient to bind an existing goal-completion signal to
termination*, or *it is insufficient and the binding comes from learning the
content states at which continuation remains appropriate*, or *the binding
requires the instruction-response pairing itself* (`correct` ≫ `shuffled`), or
*no binding is needed because the ability is latent and merely elicited by a
change in response distribution* (`shuffled` ≈ `correct`, the Hewitt et al.
account).

**Kill criterion, agreed in advance — and triggered.** The mask axis did not
separate: `full` +6.70 (48/2) against `terminal` +2.44 (33/17) and `content`
+1.40 (35/15), with no component nameable as the carrier without invoking a
content x endpoint interaction. Full table in `docs/RESULTS.md`; reasoning in
the final `docs/RESEARCH_LOG.md` entry.

## Layout

```
src/        experiment code
stimuli/    E01 exact-prefix stimuli (instrument, NOT a benchmark)
results/    raw per-item measurements + logs (never overwritten)
docs/       RESULTS.md (generated) and RESEARCH_LOG.md (dated, append-only)
```

Numbers: `docs/RESULTS.md` (regenerate with `src/make_results.py`).
Reasoning, including every correction: `docs/RESEARCH_LOG.md`.
