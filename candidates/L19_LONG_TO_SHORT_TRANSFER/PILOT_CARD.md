# L19 / E01 — Preregistration (frozen 2026-09-11, before any training run)

## Locked question

> Holding the question, the gold answer, the answer-supporting evidence, the source
> document, the example set, the supervised target tokens, the base model, the optimizer
> schedule and the number of gradient steps fixed, does presenting that same supervision
> inside a long natural context causally change subsequent **short-context** capability?

## Design

Two SFT runs from `princeton-nlp/Llama-3-8B-ProLong-512k-Base` (the mother paper's base
model). Each run trains on the **same 20,000 examples in the same order**:

| block | both arms | differs? |
|---|---|---|
| 10,000 UltraChat-200k `train_sft` conversations | identical sample, identical order | no |
| 10,000 NQ examples | identical ids, questions, gold answers, targets | **context only** |

The NQ block is the treatment:

- `SHORT-SUPPORT`: prompt = question + human gold long-answer paragraph (median 106 tok)
- `LONG-FULL`: prompt = question + the whole Wikipedia page (median ~11k tok)

Two seeds per arm (data order and init noise), 4 runs total.

### Three design decisions that protect the inference

**1. Loss is masked to completion tokens only.** The two arms therefore have *byte-for-
byte identical loss-bearing tokens* and identical gradient-step count. The extra tokens
in `LONG-FULL` are forward-pass context, not extra supervision. This removes the
"long arm just got more training signal" reading before it can be raised. It does not
remove the FLOPs difference, which is stated as a surviving alternative below.

**2. Both arms carry the identical UltraChat backbone.** Deviation from the original
sketch, made deliberately. NQ-only SFT turns an 8B base model into a short-span
extractor; GSM8K and BBH would collapse toward the floor in *both* arms and
`Δ_transfer ≈ 0` would then be uninterpretable — a power failure dressed up as a null.
The backbone keeps both arms in the instruction-following regime where the mother paper
measured 53-58 macro, i.e. where the effect it reports is actually measurable. It also
places the design inside the mother's own hybrid-training axis (their Appendix Table 7
sweeps UltraChat:ChatQA2 ratios) with length as the only manipulated variable.
Token-wise the long arm is still ~95% long-context tokens, i.e. a real long-SFT mixture.

**3. A mother positive control is run in the same regime.** `ChatQA2` (10k examples) vs
`UltraChat` (10k examples), same base, same pilot budget. Purpose: establish that this
training stack can reproduce the *direction* of the published effect at pilot scale.
Without it, a matched null is not evidence about length — only about our power.

## Primary outcome

`Δ_transfer = ShortBench(LONG-FULL) − ShortBench(SHORT-SUPPORT)`, on the mother's own
short benchmarks with the mother's own protocol (Appendix B Table 3):

| benchmark | CoT | shots | metric |
|---|---|---|---|
| MMLU | no | 0 | accuracy |
| BBH | yes | 3 | exact match |
| LAMBADA | no | 0 | accuracy |
| GSM8K | yes | 4 | accuracy |

Preregistered primary statistic: the **macro mean over these four**, seeds pooled, with
a per-benchmark table always reported. NQ itself is **not** evaluated — in-domain QA
adaptation is not the question. Reporting only GSM8K is forbidden.

## Two sub-macros, split before the runs

`MOTHER_REANALYSIS.md` shows that the parent's residual effect — the part a
dataset-quality story does not explain — is concentrated in LAMBADA, which is the one
benchmark of the nine that is about *using the local context* rather than about general
capability. That distinction is preregistered here rather than discovered afterwards:

- **CAP** = macro over MMLU, BBH, GSM8K. General capability, no long input anywhere.
- **CTX** = LAMBADA, plus the context-reliance probe below.

The primary statistic remains the 4-benchmark macro. CAP/CTX is a fixed decomposition of
it, not a post-hoc subset search.

| CAP | CTX | world |
|---|---|---|
| up | up | **W1** — long-context exposure improves general capability |
| flat | up | **W3** — it does not make the model more capable, it makes it more context-reliant |
| flat | flat | **W2** — the published effect belongs to the datasets |

W3 is the outcome we are least able to reach by accident and the one that would most
change how the parent's headline is read: it would relocate their own "knowledge
preference bias" from a difference between two datasets to a genuine consequence of
input length.

## Secondary outcome: context-reliance probe (evaluation only, no extra training)

Built from **held-out** NQ pairs that appear in no training run. For each, the gold
answer in the support paragraph is replaced by a counterfactual entity of the same type;
the model is asked the question with that edited paragraph as context. We report the
rate at which it answers from the context rather than from parametric memory.

This is the behavioural core of the parent's knowledge-conflict analysis, measured under
matched supervision instead of across two datasets. It costs no training run.

It is **secondary**: it cannot overturn the primary macro, and a movement here with a
flat CAP is reported as W3, not as a capability claim.

## What each outcome means

| outcome | reading | next |
|---|---|---|
| **A.** positive control reproduces, matched `LONG > SHORT` | length exposure has a causal effect on cross-length transfer even with supervision held fixed | E02 may decompose it: position exposure vs information-selection pressure vs genuine long-range dependency |
| **B.** positive control reproduces, matched `LONG ≈ SHORT` | the published effect is not a length law; it is carried by what long datasets *teach*. Directly revises the mother's causal interpretation | E02 checks whether the mother's MHA/FFN/retrieval-head signatures also disappear under matched supervision |
| **C.** positive control reproduces, matched `LONG < SHORT` | length imposes a transfer *tax*; the observed positive transfer must come from dataset properties strong enough to overcome it | E02 asks which property |
| **D.** positive control does not reproduce, or seeds disagree by more than the condition gap | **no identification power. KILL / HOLD.** No mechanism analysis, no replication rescue, no extra seeds hunting for the effect | stop |

Outcome D is the one that ends the route. It is checked first.

## Kill conditions (checked in this order)

1. seed-to-seed spread within an arm ≥ the between-arm gap → D;
2. positive control gap ≤ 0 on the macro → D;
3. ~~either arm's macro falls below the base model's~~ — **withdrawn 2026-09-12, before
   any treatment run.** This criterion was mis-specified: the parent's own published
   UltraChat-SFT macro on these four benchmarks is 60.41, below our untrained base's
   64.45, so the rule would have condemned their published result as an instrument
   failure. SFT from an instruct-derived base costs a few points by construction.
   Replaced by: **a single benchmark collapsing while the others hold** (GSM8K 62→39
   with MMLU/BBH/LAMBADA within ±3.5) is the instrument-failure signature, because a
   real capability change does not land on one task alone. That signature is what
   correctly identified the learning-rate fault;
4. a `LONG > SHORT` result that vanishes when the 3 long-context-free benchmarks are
   considered separately from LAMBADA → report as W3, not as a general-capability claim.

## Surviving alternatives if A occurs (not fixable inside E01, stated in advance)

- the long arm consumed ~15x more forward FLOPs;
- far-position exposure (SkipAlign shows this is separable from real long text);
- distractor-selection pressure;
- document coherence / topical breadth of the surrounding page.

E01 is authorized to establish **that** matched-supervision length matters, not **why**.
Any attempt to answer "why" with E01 data alone is a claim-evidence mismatch.

## Reviewer compression, honestly stated

> "Zheng et al. with better length controls, plus SkipAlign/GATEAU."

This kills a paper whose only content is E01. E01 is therefore explicitly **not** a paper.
It is the gate that decides whether the identification programme is worth running.

## Explicit non-authorizations

Not authorized before E01 reports: attention-head analysis, FFN transplant, activation
patching, retrieval-score heatmaps, extra model families, extra benchmarks, QASPER,
the 1B-token budget, or any writing of a paper draft.

## Budget ladder — the positive control is bought first

Kill condition D ends the route, so it is paid for before the treatment is. The long arm
is the only expensive thing here (138.7M context tokens at the full pair set against
1.4M in the short arm), so the question "what is the smallest N at which this regime
reproduces the parent's direction at all?" is worth answering before spending anything
on `SHORT-SUPPORT` / `LONG-FULL`.

| stage | runs | N | on failure |
|---|---|---|---|
| 1 | `PC-UC-UC` vs `PC-UC-CHATQA2` | 2,000 | escalate to 5,000 **once** |
| 1b | same | 5,000 | **hard stop — outcome D, route halted** |
| 2 | `SHORT-SUPPORT` / `LONG-FULL`, 2 seeds | the N stage 1 licensed | — |

Three commitments that keep this a calibration rather than a tuning loop:

1. the ceiling is 5,000 and there is no third rung;
2. the treatment arms are never trained or evaluated during stage 1, so no treatment
   data informs the choice of N;
3. N is the same integer for both arms and both stages, and the pair set itself stays
   frozen — only its first N entries are used, in the frozen order.

Backbone size tracks N one-to-one (`--n_uc = --n_nq`) so the treatment is never diluted
below half the examples.

## Power, stated before the runs

This is a screening design, and the honest statement of its limits belongs here rather
than in the discussion of a null.

At 1B tokens with a full dataset swap, the parent's UltraChat→ChatQA2 gap on our four
benchmarks is: MMLU +1.30, BBH +2.79, LAMBADA +5.67, GSM8K +14.06, **macro +5.96**.
Our pilot spends roughly a tenth of that token budget and applies the treatment to half
the examples, so a real length effect should be expected to be *substantially* smaller
than +5.96 here. E01 cannot rule out a small positive effect.

Two consequences, fixed in advance:

1. **The null is read relatively, never absolutely.** The claim licensed by outcome B is
   "under matched supervision the effect is at most a fraction *f* of the dataset-swap
   effect measured in the same regime", where *f* is computed from the positive control
   actually obtained. It is not "there is no length effect".
2. **With two seeds per arm there is no run-level inference.** We report per-benchmark
   bootstrap CIs over evaluation items (which capture eval noise only) and the raw
   seed-to-seed range (which is the only handle on training noise). If the seed range
   swamps both the matched gap and the positive-control gap, that is outcome D, and the
   correct response is to stop, not to add seeds until a gap appears.

Adding seeds after seeing results is forbidden. If the measured throughput permits a
third seed, that decision is made and recorded **before** any evaluation is run.

## One conditional secondary run, declared now

The UltraChat backbone dilutes the treatment to half the examples. If the primary
contrast is null **and** the positive control reproduces (outcome B), one further pair is
authorized before that null is written down anywhere:

- **E01-e / E01-f**: NQ-only, no backbone, `SHORT-SUPPORT` vs `LONG-FULL`, seed 1 only.

This is the full-dose version of the same manipulation. It is confounded by format
collapse — 10k span-extraction examples turn a base model into a span extractor — and is
therefore **diagnostic of dilution only**. It can convert a primary null into "the null
may be a dose effect"; it can never convert a primary null into a positive result, and
its benchmark numbers do not enter the primary table.

It is not authorized under outcome A, C or D.

## Loss normalisation, recorded because it matters

Loss is the mean cross-entropy over the labelled tokens of one micro-batch, and
micro-batch size is 1, so every *example* contributes equally regardless of how many
completion tokens it has (NQ answers ~5 tokens, UltraChat turns ~500). This weighting is
byte-identical across arms, which is what the inference needs; it is recorded here
because it determines how much of the gradient the NQ block actually commands.
