# Killed Research-Question Ledger — Continuation

This file continues `failed/KILLED_LEDGER.md` where the historical ledger on `main` is stale. It is still a cumulative anti-resurrection ledger, not a one-file-per-topic archive.

**Continuation date:** 2026-09-17  
**Authoritative continuation begins:** **K193**  

> A new model, seed, procedure pair, curriculum, causal-localization method, or renamed framing does not reopen a killed parent question. Reopening requires a new scientific object that survives a fresh Selection audit independently of the failed lineage.

---

# K193 — L45: Does Internalization Preserve Procedural History?

**Status:** `ARCHIVED / NO-GO — PILOT FAILED — NO MECHANISTIC RESULT`  
**Date:** 2026-09-17  
**Primary failure:** `OTHER — UNSTABLE_FULLY_INTERNALIZED_ENDPOINT / IDENTIFICATION_FAILURE`  
**Secondary:** `DECISIVENESS_FAILURE`, `WORKLOAD_PATH_FAILURE`

## Locked scientific question

> If two otherwise matched models learn the same function through different explicit algorithms, does fully internalizing the reasoning preserve the taught causal algorithmic identity, or erase/canonicalize procedural history?

The intended experiment held the function, architecture, examples, prompt, answer, optimizer, update budget, and final direct-answer objective fixed while changing only the explicit procedure used during training. A causal-abstraction / interchange-intervention analysis was planned only after both procedure arms produced stable, behaviorally comparable fully-internalized endpoints.

## Why the pilot stops before DAS

The behavioral gate was intentionally placed before any mechanistic measurement. Under the frozen unified recipe selected only on behavioral competence — `lr=5e-5`, `250 steps/token`, `4500 final steps` — the four independent forward-presentation seeds gave:

| seed | Algorithm A S5 held-out | Algorithm B S5 held-out |
|---|---:|---:|
| 0 | 1.000 | 1.000 |
| 1 | 1.000 | 0.006 |
| 2 | 1.000 | 0.330 |
| 3 | 0.922 | 1.000 |
| **passes at >=0.95** | **3/4** | **2/4** |

The pre-declared rule was that `B <= 2/4` eliminates the procedure pair. It fired.

The failure is not adequately described as "Algorithm B is hard." Both arms can fail, and every run remains healthy until the final transition from `28/29` removed reasoning tokens to `29/29`: the point at which the last external scratchpad token disappears and the computation must become fully internal. B is more fragile and can collapse catastrophically, but A also missed the functional threshold on one seed.

A presentation-reversal diagnostic did **not** support the earlier positional explanation as the main behavioral cause: at seed 0, reverse-presentation S5 held-out accuracy was `A=0.969`, `B=1.000`. Thus the dominant obstacle is the instability of the fully-internalized endpoint under the current task × model × stepwise-internalization setup, not a simple first-two-vs-last-two operand position effect.

## Why successful-seed filtering is forbidden

A downstream causal-algorithm comparison would have to condition on which runs happened to survive the final internalization transition. That selection occurs **upstream of every DAS/control analysis** and is plausibly coupled to the optimization basin and therefore to the final internal algorithm itself.

Keeping only successful A/B endpoints would therefore compare a biased subset of training trajectories. No shuffled intervention, matched corruption, DAS capacity control, extra seed, or second localization method can repair that selection bias after the fact.

Accordingly:

> **No DAS was run. No S5 mechanistic IIA, causal-algorithm score, or procedural-inheritance effect was ever computed.**

This archive is a feasibility / identification failure. It is **not** evidence that procedural inheritance is absent.

## What was learned before the stop

1. The symmetric explicit procedures were learnable and generalized compositionally; the experimental construction itself was not a lookup-table trick.
2. In the explicit-CoT positive control, token-level interchange of the taught intermediate produced the exact counterfactual downstream answer with `IIA = 1.000`. This validated the basic counterfactual semantics of the task.
3. An earlier apparent A/B competence gap was partly a training-recipe artifact: `lr=1e-4` could destroy B, while a unified lower-LR/slower curriculum could bring both arms to `1.000` on some seeds. This repair was completed before any causal measurement.
4. Even after freezing that unified recipe, the final fully-internal transition remained seed-unstable. That instability is the decisive blocker.

## Lineage-level reason to stop rescuing

L45 arose only after the preceding L44 lineage had already consumed multiple increasingly specialized routes:

- **L44 / J-space:** abandoned because the intervention did not cleanly identify workspace dependence; J-direction ablation strongly damaged generic computation and was entangled with high-gain Jacobian transport.
- **L44 reconstruction / causal algorithm identity:** narrowed after a 2026 nearest-owner audit showed that the broad "does internalization preserve the explicit algorithm or learn a shortcut?" mother question was already too close to existing internalization work.
- **L45 / procedural history:** introduced a genuinely more independent matched question, but its fully-internalized endpoint failed the pre-mechanistic stability gate above.

Each individual stop was correct. Taken together, however, the repeated need to replace the instrument, sharpen the object, redesign the task, and repair the training endpoint is itself evidence that the current leverage is insufficient. Continuing by trying a third procedure pair, another internalization curriculum, another localization method, or another toy function would turn the programme into phenomenon hunting.

## Hard anti-resurrection rule

**Do not reopen L45 by:**

- filtering to successful seeds;
- adding more seeds until a clean subset appears;
- tuning the frozen curriculum or LR after the gate result;
- swapping in another A/B procedure pair on the same unstable endpoint and calling it the same pilot;
- replacing DAS with another causal-localization method;
- returning to J-space / workspace ablation;
- renaming the question as latent deliberation, algorithm preservation, algorithm migration, procedural inheritance, or automaticity while keeping the same experimental dependency.

A future project may revisit the broader scientific area only if it begins from an **independently stable internalization substrate** whose multi-seed fully-internal endpoint is established before the procedural-history hypothesis is introduced, and the resulting question passes a fresh owner/novelty audit as a new candidate.

## Reusable assets / lessons

Preserve rather than rerun:

- symmetric same-function / different-explicit-procedure task construction;
- treatment-fraction curriculum mapping;
- exact source→recipient counterfactual interchange harness;
- token-level positive control (`IIA=1.000`);
- the rule that endpoint competence/stability must be established across independent seeds **before** causal algorithm identity is measured;
- the lesson that competence-conditioned mechanistic analysis can create survivor bias when endpoint failure is treatment- or basin-dependent.

**Final disposition:** `K193 / ARCHIVED / DO NOT RESCUE WITH ANOTHER INSTRUMENT OR PROCEDURE PAIR`.
---

# K195 — S03: From Document End to Task Done (goal-relative assistant stopping)

**Status:** `ARCHIVED / NO-GO — OBJECT ABSORBED BY TRAINING RECIPE`
**Date:** 2026-09-19
**Primary failure:** `REAL_OBJECT_FAILURE` (the object has no low-dimensional,
recipe-invariant answer)
**Secondary:** `PAPER_SCALE_FAILURE`, `DECISIVENESS_FAILURE`
**Working directory preserved:** `candidates/S03_GOAL_RELATIVE_STOPPING/`

## Parent question (killed)

> How does post-training turn pretrained document/text-ending behaviour into
> goal-relative assistant stopping — i.e. what makes "the user's task is
> complete" a reason to emit the turn-end token?

Also killed in its reframed, stage-agnostic form: *what supervision teaches a
model to stop when the user's task is complete?*

## What was solid, and is not the reason for the kill

* **The phenomenon is real.** With a token-for-token identical assistant prefix
  and only the user goal changed, goal completion moves the turn-end decision in
  OLMo-3, Qwen2.5 and Llama-3.1.
* **It follows the turn-end token, not "EOS".** In Llama-3.1 Instruct the
  turn-end token moves *with* goal completion (`dz_stop` +6.63, 48/2) while the
  document-end token moves *against* it (−2.57, 8/42).
* **Pretrained bases already carry it**; post-training amplifies rather than
  creates it.
* **It is not output-row calibration.** With the entire LM head byte-frozen,
  internal-state adaptation improves `d_goal` in all three families
  (+11.27 / +8.73 / +2.95).

## Why it was killed

**The object kept being absorbed by the training recipe.** Every repair added a
dependency instead of removing one:

| dependency | what happened |
|---|---|
| training budget | one 750-step point produced *three* mutually inconsistent readings, each corrected by the same instrument at other budgets |
| model family | stop-readout adaptation is +6.03 (OLMo), −1.84 (Qwen), −1.31 (Llama) — the direction itself flips |
| measurement | two confounds: per-checkpoint stop-token drift, and tokenizer drift (post-training repurposed reserved `<|extra_id_*|>` slots, so base and Instruct encode the same system prompt to different ids). The second was caught only because a per-item input fingerprint assertion had been added |
| mechanism | three hypotheses for the family difference — initial-gradient alignment, boundary-direction geometry, and a generic-boundary-competence capacity trade-off — **all falsified by direct causal test**. The third failed because arm R's endpoint is initialization-invariant (13.53 / 13.68 / 13.77 from wildly different stop rows) |

Continuing meant enumerating `budget x LR x data x family x checkpoint x
serialization x stage`. Additionally, **there is no shared
`Pretrain -> SFT -> RL` recipe in 2026** (Qwen3 mode fusion, DeepSeek-R1's two
SFT and two RL rounds, Llama 4's SFT → online RL → DPO, OLMo-3's Think /
Instruct / RL-Zero flows), so the stage-indexed version of the question is
ill-posed: a reviewer can fairly ask *whose* stage.

## Final adjudication experiment (E04) — run, and it did not rescue

Reframed stage-agnostically and given one grid, no follow-ups. From
Think-SFT-final on the real `Dolci-Instruct-SFT` mixture, matched in pool,
order, steps, schedule, optimizer, batch and seed; only supervision varied.

```
condition                           D d_goal          95% CI   sign  bnd_auc  val_ce
full / correct      (ordinary SFT)     +6.70   [+5.56,+7.82]   48/2   0.9996   0.955
terminal / correct  (endpoint only)    +2.44   [+1.35,+3.52]  33/17   0.8427  17.207
content / correct   (no stop label)    +1.40   [+0.57,+2.23]  35/15   0.9922   1.001
full / shuffled     (goal decoupled)   -6.17   [-7.20,-5.11]   3/47   0.9992   1.122
terminal / shuffled (wrong goal)       -1.99   [-3.40,-0.67]  19/31   0.8818  16.206
```

* The **pairing** axis gave one clean fact: decoupling the goal from the
  response *destroys* goal-relative stopping while leaving generic boundary
  competence intact (`boundary_auc` 0.9992). This contradicts a purely
  "latent and merely elicited by response distribution" account.
* The **mask** axis did not resolve: `full` works, both decompositions are weak
  and near noise, and naming a carrier requires a content x endpoint
  interaction — one more conditional.
* Both `terminal` arms are **broken models** (objective saturated at step 100 —
  `train_loss` 0.0 — then 2,000+ further updates; val CE 17.2 / 16.2). Their
  numbers are uninterpretable. The LR/step sweep that might have rescued them
  was deliberately **not run**: it was a new experiment, and "the conclusion
  changes with LR" was already on the kill list.
* The one strong effect is **probably not specific to termination** — mispaired
  instruction data should degrade goal-conditioned behaviour generally.
  Specificity needs yet another control.

## Do not reopen S03 by

- adding a fourth/fifth model family, more seeds, or another budget point;
- rescuing the terminal-only arm with a shorter schedule, lower LR, or a
  token-count-matched objective;
- adding the specificity control for the shuffled-pairing effect and calling it
  a new question;
- hard-negative / premature-stopping-position curricula (the planned Phase 3,
  never reached — it was conditional on content supervision mattering, and it
  does not);
- SAE, neuron hunts, layer-wise probes, CKA, circuit tracing, or gradient
  geometry on the same phenomenon;
- renaming it as task-completion detection, termination control, response
  boundary learning, goal-conditioned EOS, or "knowing when to stop".

A future project may revisit this area only if it starts from a
**recipe-invariant** formulation whose answer does not depend on budget, family
or serialization, and passes a fresh owner/novelty audit as a new candidate.

## Reusable assets / lessons

Preserve rather than rerun:

- the exact-prefix matched-pair instrument (identical assistant prefix, only the
  user goal changed) and its lexical-matched control family;
- the raw-logit decomposition `d_goal = dz_stop − dz_cont`, and the reason
  `Δ log p(stop)` must never carry a parameter-locus claim (it contains a
  whole-vocabulary `Δ log Z` that flips signs);
- **the rule that a longitudinal curve must score one fixed termination token
  and assert byte-identical inputs per checkpoint.** Both defects occurred here;
  grafting a chat template is *not* sufficient, because the tokenizer changes
  too;
- the dissociation between generic boundary competence and goal-relative
  stopping (Qwen arm R: `boundary_auc` 0.965 → 0.999 while goal-relative reading
  *falls*);
- the methodological lesson that separately scheduled runs at 250/750/2250 steps
  are three optimization endpoints, not a trajectory;
- **the process lesson:** a healthy project gets simpler as it proceeds. Gaining
  a conditional at every repair is the kill signal, and it is cheaper to act on
  it than to fund one more rescue.

**Final disposition:** `K195 / ARCHIVED / DO NOT RESCUE WITH ANOTHER
SUPERVISION VARIANT, FAMILY, OR BUDGET`.
