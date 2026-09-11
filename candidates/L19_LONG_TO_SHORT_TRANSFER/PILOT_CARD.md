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
3. either arm's macro falls below the base model's, i.e. SFT damaged rather than tuned
   the model, in a way that puts benchmarks at floor → D (power failure, not a result);
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
