# L08 — Experiment Registry

Format per `RESEARCH_EXECUTION.md` §6. No experiment is listed here unless it can
distinguish live accounts, move a load-bearing claim, or force GO/RECONSTRUCT/KILL.

---

## E00 — Intervention correctness audit  `DONE`

**Question.** Does our hook implement the parent's operation exactly, and nothing else?
**Why necessary.** Every later claim is an intervention claim; if the intervention is
not exactly `W_U[:, S] h[S]`, nothing downstream identifies anything.

**Command.**
```
/home/xiang/miniconda3/envs/verl-clean/bin/python scripts/validate_intervention.py
```
**Model.** Qwen2.5-0.5B-Instruct, fp32 (so numerical identity is meaningful).

**Result (2026-09-10).**
| Check | Outcome |
|---|---|
| hook logits vs explicit `W_U[:,S] h[S]` | max abs diff 1.14e-05 (fp32) |
| `lm_head` weights unchanged | True |
| last hidden state unchanged | True |
| baseline restored after hook removal | max abs diff 0.0 |
| `mask="full"` identical to no hook | True |
| truncation changes the argmax | yes (12095 → 220) |

**Interpretation.** The intervention is the parent's, is confined to the readout, and
is exactly reversible. Note recorded during the audit: HuggingFace returns
`hidden_states[-1]` **after** the final RMSNorm, i.e. it is already the vector
projected to the vocabulary; a reference implementation that applies the norm again
double-normalises (this was caught and fixed).

### E00b — Batched rank scorer audit  `DONE`

`run_rank` left-pads, batches, and requests only the tail logits (`logits_to_keep`,
added after the first pass OOMed materialising 128k-wide logits for a whole batch).
Any of those three can silently score the wrong position and would corrupt every
ranking number in the paper.

```
CUDA_VISIBLE_DEVICES=0 python scripts/validate_rank_scoring.py
```

Checked against an unbatched, unwindowed, full-logit reference, with a batch size
deliberately not dividing the item count:

| check | result |
|---|---|
| max abs continuation log-prob difference | 3.815e-05 (fp32) |
| arg max agreement over candidates | True |

---

## E01 — Reproduction and artifact-free re-measurement  `RUNNING`

**Linked claims.** P0.1 (substrate), **C1.1**.
**Question.** Does the parent's asymmetry reproduce locally, and does SQuAD-v2 still
"survive" once measured without the `best_exact` no-answer floor?
**Why necessary.** C1.1 is currently an inference from a published table. It is
load-bearing (it deletes one of two survivor data points) and cheap to measure.

**Design.** Models × cells × masks, greedy decoding, identical token budgets across
masks.
- Models: `NousResearch/Meta-Llama-3.1-8B-Instruct`, `Qwen/Qwen2.5-7B-Instruct`
  (instruction-tuned; base checkpoints matching the parent are downloading, see E01b).
- Masks: `full`, `first` (keep first d/2), `last` (keep last d/2).
- Cells: `mmlu_rank` (n=1000), `squad_gen` (n=1000), `gsm8k_gen_cot` (n=500).

**Metrics.** MMLU accuracy; GSM8K strict `#### N` match **and** flexible last-number
match (so that a formatting collapse cannot masquerade as a reasoning collapse — the
same failure mode as C1.1); SQuAD-v2 `HasAns_exact`, `NoAns_acc`, `exact`, and the
`best_exact` floor.

**Informative outcomes.**
- `HasAns_exact` collapses while `best_exact` stays ≈50 → **C1.1 supported**.
- `HasAns_exact` survives → C1.1 rejected, SQuAD really is a survivor, and Account A
  gains a genuine reading-comprehension data point.
- GSM8K strict collapses but flexible does not → the parent's headline is partly a
  format effect; report and re-centre on the flexible metric.

---

## E01b — Parent-checkpoint fidelity  `QUEUED`

Same as E01 on `meta-llama/Llama-3.1-8B` and `Qwen/Qwen2.5-7B` (base, not instruct),
matching the parent exactly. Run only to confirm that instruction tuning is not
carrying the effect; not a separate claim.

---

## E02 — Protocol × depth × content factorial  `RUNNING`

**Linked claims.** **C1.2**, **C1.3**. This is the decisive experiment of C1.
**Question.** The parent's two tasks differ on three axes at once. Which axis does the
collapse track?

**Design.** Cross content against protocol/depth on the parent's own datasets, so no
new task is invented:

| cell | protocol | depth | content |
|---|---|---|---|
| `mmlu_rank` | rank K=4 | single | knowledge |
| `mmlu_gen_letter` | arg max over V | short | knowledge |
| `mmlu_gen_cot` | arg max over V | long | knowledge |
| `gsm8k_gen_direct` | arg max over V | short | reasoning |
| `gsm8k_gen_cot` | arg max over V | long | reasoning |
| `squad_gen` | arg max over V | short | reading |

The **decisive cell is `mmlu_gen_cot`**: identical knowledge content to `mmlu_rank`,
identical protocol and comparable depth to `gsm8k_gen_cot`.

**Informative outcomes.**
- `mmlu_gen_cot` collapses like `gsm8k_gen_cot` → **content is not the axis**;
  C1.2 supported; Account A weakened.
- `mmlu_gen_cot` survives at GSM8K-matched output length → **Account A supported**;
  a genuine reasoning-specific readout requirement, now properly controlled. The
  paper reconstructs around localising it (this is a win, not a kill).
- Short generative cells sit between rank and long-CoT → C1.3 supported, depth is a
  separable factor.

### E02 analysis plan (pre-registered 2026-09-10, before any E02 cell was scored)

The factorial contains three **matched** contrasts. Only these are read as
identifying a factor; every other cell pair is descriptive context.

| contrast | cells | matched on | varies |
|---|---|---|---|
| **PROTOCOL** | `mmlu_rank` vs `mmlu_gen_letter` | same items, same 5-shot prompt string, same single decision, same content | rank K=4 vs arg max over V |
| **DEPTH** | `gsm8k_gen_direct` vs `gsm8k_gen_cot` | same items, same 5-shot prompt family, same protocol, same content | ~5 vs ~10^2 generated decisions |
| **CONTENT** | `mmlu_gen_letter` vs `gsm8k_gen_direct`; `mmlu_gen_cot` vs `gsm8k_gen_cot` | protocol and (approximately) depth | knowledge vs reasoning |

The PROTOCOL contrast is exact: `build_mmlu` emits the identical prompt for both
cells, so the two conditions differ **only** in how the same forward pass is turned
into an answer. This is the confound-free core of C1.2.

Read-out rule, fixed in advance:
- relative performance `acc(mask)/acc(full)`, per model, per mask, since cells differ
  in absolute difficulty;
- a factor is called **carrying** if its matched contrast shows a relative-performance
  gap of at least 0.15 in the same direction for **both** models and **both** masks;
- if two factors both qualify, both are reported as carrying; the paper does not need
  a single winner.
- `mmlu_gen_cot` vs `gsm8k_gen_cot` is read as a content contrast **only if** their
  mean output lengths at full readout are within a factor of two; otherwise it is
  reported as a depth-confounded comparison and the CONTENT verdict rests on the
  short-generation pair alone.

**Known confound to handle at analysis time.** Cells differ in full-model accuracy, so
comparisons are on **relative** performance, and E03 supplies the margin-matched
version. `mmlu_gen_cot` output length must be reported next to `gsm8k_gen_cot`
length; if they differ greatly the depth axis is not matched and the cell is read
against C1.3 instead.

### Metric-strictness policy (added 2026-09-10 after the first E02 cells)

`C1.1` was about one metric hiding a collapse. The first E02 cells show the mirror
failure, and it is the same class of problem, so the policy is stated once and applied
everywhere:

- `gsm8k_gen_direct` under the `first` mask scores **0.000** strict (`#### N`) but
  **0.104** flexible (last number in the output) against a full-readout **0.160** —
  i.e. `0.00` vs `0.65` relative depending only on how strictly the answer string is
  matched. Here the permissive metric is the honest one: the model produces the right
  number and not the required decoration.
- `mmlu_gen_cot` under truncation has `parse_rate` 0.068 vs 0.927 — but its outputs
  are repetition loops, so there the permissive reading agrees with the strict one:
  the collapse is real.

**Policy.** Every generative cell reports strict and permissive scoring side by side.
A collapse is only called real when it survives the *most permissive* defensible
metric. A survival is only called real when it survives the *least* floored metric
(hence `HasAns_exact`, not `best_exact`).

**Consequence for the paper.** Scoring strictness joins protocol and depth as a
*measurement* factor that the parent's comparison confounds with capability. This is
not a nuisance to be controlled away — it is part of C3: what the field has been
measuring when it reports representational redundancy.

---

## E03 — Information loss or installed prior?  `SPECIFIED 2026-09-10, NOT YET RUN`

**Specified after E02's qualitative signature, before any E03 measurement.**

**The observation that forces this experiment.** Under truncation, long free
generation does not drift into subtly wrong reasoning. It degenerates into
repetition loops (`results/e01/llama31_8b_instruct/mmlu_gen_cot__first.jsonl`:
`" 1.  1.  2.  1.   1.   1.   1. ..."`). That is not the signature of accumulating
small per-step errors; it is the signature of an absorbing state.

**The hypothesis this suggests.** Truncation perturbs the logits by exactly

```
r_t = W_U[:, S^c] h_t[S^c]
```

Suppose `r_t` is largely **context-invariant** — i.e. `r_t ≈ b` for a fixed vocabulary
vector `b`. Then halving the readout does not primarily *destroy information*; it
*installs a fixed prior over the vocabulary*. That is mechanistically plausible:
LLM final representations are known to contain a few massive, roughly
context-constant outlier coordinates, and removing half the coordinates removes some
of them, leaving `−b = −W_U[:, S^c] h[S^c]` as an approximately constant logit shift.

A fixed vocabulary bias predicts **exactly** the pattern E02 is showing:
- **bounded ranking survives** — over four candidates as similar as " A"/" B"/" C"/" D",
  a fixed bias is close to common-mode and the arg max among them is preserved;
- **unconstrained arg max does not** — over ~150k tokens, `b` promotes whichever
  tokens it happens to favour, regardless of context;
- **long generation collapses hardest** — once a `b`-favoured token is emitted, the
  context reinforces it and the sequence is captured;
- **SQuAD-v2 floors at 50.07** — the model emits nothing usable, and the metric
  reports its no-answer baseline.

### E03a — Is the perturbation a fixed vector? (measurement)  `DONE 2026-09-10`

```
CUDA_VISIBLE_DEVICES=0 python scripts/run_e03a_perturbation.py \
    --model <ckpt> --mask first --n-prompts 96 --max-pos 24 \
    --out results/e03/perturbation_<tag>.json --bias-out results/e03/bias_<tag>.pt
```
96 prompts per cell for the fit split and 96 disjoint prompts for the held-out split,
24 token positions each (2304 positions per split).

| model / mask | cell | fixed energy fraction | mean pairwise cos | RMS of `r~` | RMS of `b̄` | `b̄` cross-split cos |
|---|---|---|---|---|---|---|
| Llama first | gsm8k_gen_cot | 0.196 | 0.242 | 508 | 225 | 0.999 |
| Llama first | mmlu_gen_letter | 0.250 | 0.229 | 565 | 282 | 0.940 |
| Llama last | gsm8k_gen_cot | 0.349 | 0.352 | 560 | 330 | 1.000 |
| Llama last | mmlu_gen_letter | 0.281 | 0.301 | 550 | 292 | 0.956 |
| Qwen first | gsm8k_gen_cot | 0.094 | 0.092 | 695 | 214 | 0.996 |
| Qwen first | mmlu_gen_letter | 0.100 | 0.141 | 705 | 223 | 0.877 |
| Qwen last | gsm8k_gen_cot | 0.162 | 0.149 | 774 | 312 | 0.998 |
| Qwen last | mmlu_gen_letter | 0.435 | 0.395 | 1096 | 723 | 0.969 |

**Result, stated against the pre-registered kill condition.** The pre-registration
said: *"If E03a shows the perturbation is dominated by its context-varying part, the
attractor hypothesis is wrong at the first step."* The fixed component carries
**9-44%** of the vocabulary-centred perturbation energy. It is therefore **not
dominant**, and the strong form of the hypothesis — "truncation is essentially the
installation of a fixed vocabulary prior" — is **not supported**.

**What is nevertheless established, and why E03b still runs.**
1. There is a large, **highly reproducible** fixed component: `b̄` estimated on two
   disjoint prompt sets agrees at cosine 0.88-0.9996. This is a real property of the
   removed subspace, not sampling noise.
2. Its absolute size is enormous in the units that decide behaviour. RMS 214-723
   *logit units*, where the margins that decide an arg max are O(1-10).
3. Energy fraction is a statement about vectors, not about decisions. A minority
   component concentrated on a few thousand tokens can dominate an arg max over 128k
   while a majority component spread thinly across the vocabulary does not.

So E03a moves the claim from "the damage *is* a fixed prior" to "a large stable fixed
prior is present alongside a larger context-varying part", and leaves the behavioural
question genuinely open. That is what E03b measures causally. Recording this here so
that the weakening of the original hypothesis is on the record rather than absorbed
silently.

### E03b — Mean-bias correction (the decisive causal test)
Re-run the collapsed generative cells with truncated readout **plus** a rank-one
correction that adds back only the estimated constant `b̄` — no per-context
information, one vector estimated on held-out contexts, zero extra parameters that
depend on the input.

| outcome | conclusion |
|---|---|
| accuracy largely **recovers** | The readout was not information-limited. Halving it installs a vocabulary prior. "50% of dimensions are redundant" is then true in a stronger sense than anyone claimed, and the reasoning interpretation of the parent's result is wrong. |
| accuracy **does not recover** | Real per-context information is lost in the removed half; Account A/C are live and E03c localises where. |
| partial recovery | Quantify the split between installed prior and lost information; this is the paper's central number. |

Both directions are publishable, which is why this is the experiment worth running.

**Identification controls (needed for the claim, not for a reviewer).** "Adding a
vector to the logits helps" is not the same claim as "the damage *is* that vector",
so E03b runs with:

| condition | purpose |
|---|---|
| truncated + `b̄` estimated on held-out contexts of the **same** cell | the effect |
| truncated + a **random** vector matched in norm to `b̄` | rules out "any large logit nudge revives generation" |
| truncated + `b̄` estimated on a **different task's** contexts | if it still recovers, the installed prior is context- and task-independent — a much stronger version of the claim |
| truncated + the **per-context** `r_t` added back | upper bound: this is by construction the full model, and confirms the decomposition is complete |

Without the norm-matched random control the result does not identify anything.

### E03c — Teacher-forced per-step degradation
Per-token top-1 agreement, correct-token log-prob and margin on gold continuations
under the same mask, for reasoning **and** non-reasoning long generation.
Separates "each step is damaged" (Account A) from "steps are fine but the trajectory
is captured" (attractor account) and gives the accumulation curve for Account C.

**Ordering.** E03a and E03b first: if the perturbation is a fixed vector and adding it
back recovers the task, the accumulation question is downstream of a much simpler
fact and E03c becomes a boundary measurement rather than the main mechanism test.

**What would make us drop this line.** If E03a shows the perturbation is dominated by
its context-varying part, the attractor hypothesis is wrong at the first step and we
return to the accumulation/geometry accounts with E03c as the main test. Recorded
here so that the negative result is on the record.


---

## E03b — Mean-bias correction  `DONE 2026-09-10`  ->  hypothesis REJECTED

```
CUDA_VISIBLE_DEVICES=<g> python scripts/run_e03b_bias.py --model <ckpt> \
    --tag <tag> --mask first --cells <cell> --n <n>
```
Machinery audited first (`scripts/validate_bias_hook.py`): `full + b == baseline + b`
exactly, and `truncated + r_t == baseline` to 1.1e-05, so the fixed/residual split of
`r_t` is exact and the hook adds what it claims.

Accuracy (permissive scoring), mask `first`, relative to full readout:

| model | cell | greedy (E02) | **+`b̄`** | +random, norm-matched | +cross-task `b̄` |
|---|---|---|---|---|---|
| Llama | gsm8k_gen_cot | 0.109 | **0.043** | 0.094 | — |
| Llama | mmlu_gen_cot | 0.030 | **0.015** | 0.011 | 0.000 |
| Qwen | gsm8k_gen_cot | 0.138 | **0.045** | 0.143 | — |
| Qwen | mmlu_gen_cot | 0.146 | **0.247** | 0.180 | 0.071 |

**Verdict: rejected.** Adding back the estimated fixed component does not recover the
task; in three of four cells it is *worse* than the uncorrected run, and it never
beats the norm-matched random control by a margin the design can call an effect
(Llama gsm8k 0.043 vs 0.094; Qwen gsm8k 0.045 vs 0.143; Llama mmlu 0.015 vs 0.011;
Qwen mmlu 0.247 vs 0.180). The random control is what makes this readable: without it,
the single Qwen/MMLU cell would have looked like a recovery.

Per the pre-registered table, this puts the mechanism on "real per-context information
is lost", not "a prior is installed".

---

## E04 — Does damage scale with the size of the decision set?  `DONE 2026-09-10`  ->  hypothesis REJECTED

Motivated by the E02 finding that ranking survives and unconstrained arg max does
not: the natural account is that beating 3 named competitors is easy and beating
~150k is hard (an extreme-value problem). Survival of the full model's own arg max
over the top-K full-model competitors, measured at natural text positions:

| K | 1 | 2 | 4 | 8 | 16 | 64 | 256 | 4096 | 65536 | \|V\| |
|---|---|---|---|---|---|---|---|---|---|---|
| Llama first | 1.000 | .788 | .710 | .643 | .625 | .621 | .618 | .618 | .618 | **.618** |
| Qwen first | 1.000 | .929 | .917 | .912 | .911 | .908 | .905 | .901 | .901 | **.901** |
| Qwen last | 1.000 | .958 | .950 | .948 | .937 | .931 | .926 | .923 | .921 | **.921** |

**Verdict: rejected, and informatively.** The curve is flat beyond K ~ 8. Essentially
all of the damage is a reshuffling of the top few candidates; the remaining ~150k
tokens contribute almost nothing. Vocabulary size is not the relevant quantity, and
the extreme-value account is wrong.

Two facts to carry forward: per-step top-1 agreement is **0.62-0.92**, i.e. the
next-token distribution is largely intact; and the damage is *local in rank*, so
whatever breaks long generation is not the promotion of implausible tokens.

---

## E05 — Is the collapse a decoding-dynamics failure?  `DONE 2026-09-10`  ->  hypothesis REJECTED

First, the observation that motivated it (`scripts/analyze_degeneration.py`, on the
E02 generations): truncation raises the fraction of outputs captured by a repetition
loop from 0.00-0.07 to **0.36-0.87**, with the loop starting in the first 8-17% of the
text. That is a large, real effect.

Then the causal test: `no_repeat_ngram_size=6` blocks the attractor without restoring
a single readout dimension.

| model | cell | greedy rel | looping | **+norep6 rel** | looping | x greedy |
|---|---|---|---|---|---|---|
| Llama | gsm8k_gen_cot | 0.109 | 0.872 | **0.089** | 0.006 | **0.81** |
| Qwen | gsm8k_gen_cot | 0.138 | 0.610 | **0.126** | 0.010 | **0.91** |
| Llama | mmlu_gen_cot | 0.030 | 0.412 | **0.041** | 0.003 | 1.38 |
| Qwen | mmlu_gen_cot | 0.146 | 0.632 | **0.258** | 0.007 | 1.77 |
| Qwen | mmlu_gen_cot | — | — | +sample 0.184 | 0.470 | 1.26 |

**Verdict: rejected as the mechanism.** On GSM8K, eliminating degeneration almost
entirely (0.872 -> 0.006 and 0.610 -> 0.010) leaves accuracy **unchanged or slightly
worse**. On MMLU-CoT it buys 1.4-1.8x against a 7-30x loss. Degeneration is a
conspicuous symptom, not the cause.

This is worth stating carefully because prior work on layer pruning has *asserted*
that degeneration does not fully explain generative-reasoning failure
(arXiv 2602.01997). Here it is shown causally, for an intervention that touches no
transformer weight and no layer of computation.

---

## E06 — Is survival a single function of the decision margin?  `DONE 2026-09-10`  ->  PARTIAL

Three mechanism hypotheses are now dead. What they have in common is that each posited
a *structure* to the damage (a fixed direction, a large-K competition, an attractor).
E04's flat-in-K curve says the damage is local in rank, which points at the least
structured possibility available:

> a decision survives iff the truncation-induced perturbation differential is smaller
> than the margin the full model had.

That predicts one curve `s(m)` per (model, mask) and predicts **every cell** from
`s(m)` plus the margin distribution of the decisions that cell requires — with **no
free parameters**. Content, protocol and length enter only through which margins a
task samples.

`scripts/run_e06_margin_law.py` measures `s(m)` on 160 running-text prompts x 24
positions, then measures the decision-point margin distribution for each of the five
E02 cells and emits the parameter-free prediction next to the observed first-step
survival.

**Informative outcomes.**
- The law predicts all cells across both models and masks -> C2: readout redundancy is
  a function of the margin distribution of the decisions being made, and ranking
  benchmarks sample only its high-margin tail. This is the quantitative form of C1.
- The law predicts ranking but under-predicts generation -> something beyond margin is
  at work; the residual is then the object to explain, and E04's first/last asymmetry
  (below) says that something is geometric.
- The law fails everywhere -> margin is not the quantity and the project has exhausted
  its mechanism candidates; see the stop rule in `README.md`.

---

## Cross-cutting finding: the parent's third conclusion is also protocol-bound

Free from the E02 data, no extra compute. Ratio of the better to the worse structured
mask, `max(rel_first, rel_last) / min(...)`:

| cell | Llama | Qwen |
|---|---|---|
| `mmlu_rank` | **1.0x** | **1.0x** |
| `mmlu_gen_letter` | 1.3x | 1.2x |
| `squad_gen` | 1.5x | 3.3x |
| `gsm8k_gen_cot` | 2.2x | 1.8x |
| `gsm8k_gen_direct` | 5.2x | 1.2x |
| `mmlu_gen_cot` | 5.4x | **13.0x** |

The parent writes that "how to reduce representations (removing first or last) does
not have an impact, **indicating the presence of inefficient representation space
usage by LLMs**". Under the ranking protocol we reproduce that exactly (1.0x). Under
generation, which half is removed matters by up to **13x**. The representational
conclusion is an artefact of the measurement protocol, like the other two.


### E06 result

`s(m)` is real and consistent: survival rises monotonically with the full model's
top1-vs-top2 margin in **all four** model x mask conditions, from ~0.2 below m = 1 to
~1.0 above m = 12. That much needs no structure and is the honest core of the damage.

As a **parameter-free predictor** of each cell's decision-point survival it is only
approximate, and it fails in one systematic place:

| model / mask | cell | margin (median) | predicted | observed | error |
|---|---|---|---|---|---|
| Llama first | mmlu_rank / gen_letter | 1.69 | 0.529 | 0.670 | +0.141 |
| Llama first | **gsm8k_gen_direct** | **4.88** | **0.759** | **0.097** | **−0.662** |
| Llama first | gsm8k_gen_cot | 0.88 | 0.362 | 0.033 | −0.328 |
| Qwen first | mmlu_rank / gen_letter | 5.31 | 0.744 | 0.830 | +0.086 |
| Qwen first | gsm8k_gen_direct | 10.88 | 0.976 | 1.000 | +0.024 |
| Qwen first | gsm8k_gen_cot | 1.12 | 0.416 | 0.553 | +0.137 |
| Qwen last | squad_gen | 2.25 | 0.701 | 0.337 | −0.364 |

The largest residual is the step at which Llama must emit the GSM8K answer marker: a
comfortable margin, a predicted survival of 0.759, an observed survival of 0.097. That
observation is what E08 and E09 were built to chase.

**Verdict: partial.** Margin governs most of the variation and is a genuine finding,
but it is not a law and it does not close the mechanism question.

---

## E08 — Computation or emission?  `DONE 2026-09-10`  ->  PARTIAL

GSM8K, mask `first`, the answer marker appended to the model's **own** truncated chain:

| model | free (must emit `####` itself) | forced | forced, chain capped | rel. to full |
|---|---|---|---|---|
| Llama | **0.0000** | **0.1780** | 0.1860 | 0.240 / 0.251 |
| Qwen | 0.1060 | **0.2040** | 0.1740 | 0.251 / 0.214 |

Handing the model the decision to stop and answer turns a literal zero into 0.178.
Emission failure is therefore a real and large component. But two thirds of the gap to
full readout (rel 1.0) remains, so the chains are damaged as well.

**Verdict: partial.** Real, quantified, insufficient as *the* mechanism.

---

## E09 — Are structural tokens selectively demoted?  `DONE 2026-09-10`  ->  REJECTED

Survival by token class, stratified within margin bins so the comparison is not just
restating that the classes have different margins:

| model / mask | class | n | margin (median) | survival |
|---|---|---|---|---|
| Llama first | structural marker | 200 | 0.69 | **0.000** |
| Llama first | word | 31836 | 1.62 | 0.510 |
| Llama first | number | 13826 | 3.75 | 0.523 |
| **Qwen first** | **structural marker** | 200 | **9.88** | **1.000** |
| Qwen first | word | 31921 | 9.62 | 0.882 |
| Qwen first | number | 24661 | 16.25 | 0.974 |

**Verdict: rejected.** Llama's markers die and Qwen's survive perfectly, and the
difference tracks their margins (0.69 vs 9.88), not their class. There is no
model-independent structural-token effect. The Llama `####` failure is the margin law
operating on a decision that happens to be a near-tie for that model.

---

## E10 — Does the protocol confound reproduce across compression families?  `PARTIAL 2026-09-10`

**Linked claim.** The reconstructed mainline in `MAINLINE.md`.
**Why necessary.** C1 is a claim about how the field measures. It is worth a paper only
if it holds beyond the single parent intervention. Readout truncation leaves the
model's computation untouched; magnitude pruning and weight quantization do not. If
the confound appears for all three, it is a property of the evaluation rather than of
the intervention.

`src/interventions.py` implements all three as reversible context managers;
`scripts/validate_interventions.py` verifies each one changes the logits and restores
them exactly (max abs diff 0.0 on exit for all three).

**Calibration** (Llama, GSM8K CoT, permissive scoring, relative to full):

| intervention | rel | `format_rate` | mean output chars |
|---|---|---|---|
| full | 1.000 | 0.946 | 235 |
| readout, first half | 0.109 | 0.000 | 461 |
| **magnitude prune 40%** | 0.053 | **0.000** | **2289** |
| magnitude prune 50% | 0.013 | 0.000 | 1280 |
| RTN quantize 3-bit | 0.000 | 0.000 | 1295 |

Pruning at 40% gives damage comparable to the parent's readout intervention and shows
the *same* signature — the answer marker is never emitted and the output length
inflates by an order of magnitude. 3-bit quantization is past the floor; 4-bit is being
calibrated.

**First cells of the factorial** (relative performance, same model at full precision):

| model | intervention | rank/know | gen-short/know |
|---|---|---|---|
| Llama | prune 40% | 0.723 | **0.485** |
| Qwen | prune 40% | 0.848 | **0.512** |

The protocol effect reproduces under a parameter intervention. The decisive
long-generation knowledge cell is still running.


### E10 result so far — the confound reproduces, and a boundary appears

Full six-cell factorial, magnitude pruning at 40% and RTN 4-bit quantization, both
models, alongside the readout intervention.

**The controlled test of capability-selective damage.** Two contrasts on the same
data. The first is how the literature establishes selectivity (rank-scored knowledge
vs generation-scored long reasoning); the second holds protocol and output length
fixed (long-generation knowledge vs long-generation reasoning). Ratios of relative
performance, paired bootstrap over items, B = 10000.

| model | intervention | uncontrolled | **controlled** | 95% CI | share removed |
|---|---|---|---|---|---|
| Llama 3.1 8B | prune 25% | 1.34 | **1.34** | [1.20, 1.51] | 0.3% |
| Llama 3.1 8B | prune 40% | 13.54 | **3.15** | [1.94, 5.58] | 82.8% |
| Llama 3.1 8B | quant 4-bit | 1.97 | **1.49** | [1.26, 1.77] | 49.7% |
| Llama 3.1 8B | readout, first | 8.12 | **0.27** | [0.10, 0.53] | 110.2% |
| Llama 3.1 8B | readout, last | 3.86 | **0.68** | [0.47, 0.94] | 111.2% |
| Qwen 2.5 7B | prune 40% | 71.24 | 2.52 | [0.77, 11.33] | 97.8% |
| Qwen 2.5 7B | quant 4-bit | 5.86 | **4.42** | [3.47, 5.79] | 29.5% |
| Qwen 2.5 7B | readout, first | 7.26 | 1.06 | [0.70, 1.55] | 99.1% |
| Qwen 2.5 7B | readout, last | 12.83 | **0.15** | [0.00, 0.37] | 107.2% |

**Two findings.**

1. Holding protocol and length fixed removes **49.7% to 111%** of the apparent
   capability-selectivity in every condition but one (prune 25%, which has no
   protocol inflation to remove because it is mild).
2. The families separate by **direction**, once the later conditions (OLMo-3 prune,
   Phi-4 quant) are included:

| intervention touches | significantly < 1 | null | significantly > 1 |
|---|---|---|---|
| **only the readout channel** (computation intact) | **5 of 6** | 1 | **0** |
| **the parameters** (computation damaged) | **0** | 2 | **5 of 7** |

Thirteen estimable conditions, four model families, three intervention families, and
not one crosses in the wrong direction. (An earlier numeric "no overlap" statement was
withdrawn when OLMo-3 pruning returned 1.01 and Phi-4 quantization 1.06.)

**Severity control.** The objection that pruning simply hits harder does not hold. A
deliberately mild prune (25%) has an uncontrolled ratio of 1.34 — no inflation at all
— and still shows genuine selectivity (1.34, CI [1.20, 1.51]), while a severe readout
truncation with an uncontrolled ratio of 8.12 shows none (0.27).

### E10 model-family extension  `RUNNING`

The readout factorial on additional families. Baselines that are themselves degenerate
are excluded by an explicit guard in `scripts/analyze_selectivity.py` (a ratio is
computed only when the full-precision baseline exceeds 0.05).

Early rows sharpen the protocol finding rather than weakening it — the effect is
*larger* outside the two original models:

| model | mask | `mmlu_rank` | `mmlu_gen_letter` | protocol gap |
|---|---|---|---|---|
| Llama 3.1 8B It | first | 0.889 | 0.837 | 1.1x |
| Qwen 2.5 7B It | first | 1.003 | 0.989 | 1.0x |
| **OLMo-3 7B (base)** | first | **0.966** | **0.411** | **2.4x** |
| **Phi-4-mini It** | last | **0.541** | **0.001** | **540x** |

Same items, same prompt string, same single decision; only the rule for reading the
answer out of the model differs.

Phi-4-mini also shows that the parent's "ranking survives" premise is itself
model-dependent: its `mmlu_rank` relative performance is 0.501 / 0.541, far below the
0.889-1.003 of Llama and Qwen.

---

## Invalid runs

`results/_invalid/` holds the `allenai/Olmo-3-7B-Instruct-DPO` factorial, excluded
from every analysis. At **full** readout that checkpoint emits zero characters on both
GSM8K cells under the harness's raw few-shot prompts, so its baselines are broken and
no ratio computed from them is interpretable. This is a prompt-format failure of the
harness on a chat-tuned checkpoint, not a result. The additional families use
checkpoints that accept raw few-shot prompting, which also matches the parent's
lm-eval-harness setup. See `results/_invalid/README.md`.

---

## Written but not run

Two runners exist in `scripts/` that no result in this registry depends on. They are
kept because the questions they ask are the natural next ones if the project returns
to the mechanism, and deleted code cannot be audited:

- `run_e03c_teacher_forcing.py` — replay the full model's own trajectory under
  truncation with the prefix forced, to get per-step top-1 agreement and the
  first-divergence distribution on generated (rather than prompt) text. Superseded for
  the current mainline by E04, which answered the per-step question more cheaply.
- `run_e07_temporal.py` — switch the mask on and off *during* a single generation, to
  turn the depth finding from a cross-cell comparison into a within-item causal one.
  Still worth running; listed in `PILOT_REPORT.md` §5.

`run_e04_logit_geometry.py` (a superseded draft of E04) and `queue_runs.py` (superseded
by `launch.py`, which loads each checkpoint once per worker instead of once per job)
were removed.
