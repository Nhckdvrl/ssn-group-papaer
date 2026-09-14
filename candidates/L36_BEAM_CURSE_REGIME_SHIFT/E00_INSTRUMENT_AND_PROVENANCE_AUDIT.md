# L36 E00 — Instrument and Provenance Audit

**Status:** **RUN 2026-09-14 — see [`results/e00/E00_VERDICT.md`](results/e00/E00_VERDICT.md); verdict HOLD**

This file is the union of two authorings that happened in parallel on 2026-09-14 and were merged
afterwards:

- **Part A — the authored gate** (commits `b56b030`, `bc31492`): why E00 is mandatory, what E01 is
  not allowed to become, the eligibility rules, and the requirement that the null be identified
  rather than merely non-significant.
- **Part B — the executed protocol** (commit `ab76807`, committed before any model was run): the
  same gate with concrete thresholds, decision rules and freeze requirements, plus the amendments
  forced during execution.

Part B governs what was actually run. Part A is kept because it carries the framing constraints and
two warnings that Part B does not state as sharply.

---

# Part A — the authored gate

**Date:** 2026-09-14  
**Status:** **MANDATORY PRE-E01 GATE — NO E01 RUN UNTIL PASS**  
**Purpose:** prevent a false modern-regime result caused by evaluation-set exposure, unmatched decoding semantics, or an unidentified null.

## 1. Why E00 is now mandatory

L36 remains the preferred next bounded candidate because its first scientific gate can be stated on externally defined quantities:

- intrinsic uncertainty is fixed from independently authored human references;
- beam width is the treatment;
- translation quality is the outcome;
- a classic encoder–decoder can serve as a positive-control regime.

However, the originally suggested modern checkpoint, `Unbabel/TowerInstruct-7B-v0.2`, is **not eligible** for the decisive WMT19 experiment. TowerBlocks-v0.2 publicly lists **WMT14 through WMT21** among its general-translation training sources. Therefore WMT19 evaluation material is within the model's known supervised-data lineage. A stable large-beam curve on the WMT19 substrate could then reflect direct task/test exposure rather than a changed LLM distributional regime.

This is exactly the kind of construct contamination L36 must rule out before compute.

A second correction concerns the TACL-2025 mother evidence. The public LLM4MT repository currently advertises released `de2en-10k` and `zh2en-10k` checkpoints, whereas the strongest paper curves use larger SFT conditions as well. The public code is useful for auditing HuggingFace generation semantics, but E01 must not claim an exact checkpoint reproduction unless the exact checkpoint used for the beam-width result is actually obtainable.

## 2. Frozen scientific object

The E01 law-break question remains:

> Holding human-defined intrinsic translation ambiguity fixed, does a modern decoder-only translation-capable LM still exhibit the classic uncertainty-conditioned deterioration as beam width grows?

E00 is not allowed to change this into:

- a TowerInstruct paper;
- a decoding-configuration paper;
- a benchmark-contamination paper;
- a generic `LLMs translate better` comparison.

## 3. Exact uncertainty substrate

The decisive substrate must reuse the ACL-2022 quantity as faithfully as possible:

- WMT19 English→German source items;
- independently authored human references used by Stahlberg, Kulikov & Kumar (2022), including the additional human reference lineage from Freitag et al. (2020);
- sentence-level intrinsic uncertainty computed **before any model generation**, using the published normalized pairwise-reference disagreement definition.

No token entropy, model entropy, LLM judge disagreement, or new ambiguity proxy may replace the human-reference quantity in E01.

## 4. Classic positive-control model

Use an open classic encoder–decoder on the same EN→DE substrate, with exact revision frozen before generation. `facebook/wmt19-en-de` is a suitable first candidate because it is a public WMT19 encoder–decoder submission and exposes explicit beam / length settings.

The classic model is an **instrument positive control**, not a competitor in a leaderboard.

Before interpreting a modern `no curse` result, the frozen pipeline must recover a material adverse large-beam pattern in the classic regime, especially in the high-intrinsic-uncertainty stratum. If it cannot, the instrument has failed and L36 stops; do not interpret a modern flat curve.

## 5. Modern-model eligibility gate

A modern EN→DE checkpoint may enter confirmatory E01 only if all of the following are satisfied **before looking at its beam-width outcome on WMT19**:

1. **Direction:** it can perform English→German generation without an ad-hoc task-specific finetune created for this project.
2. **Public frozen checkpoint:** exact revision / weights / prompt contract are available.
3. **Known-supervision audit:** no known supervised / instruction-tuning source directly includes WMT19 test/evaluation material. Any model whose documented training data explicitly includes WMT14–WMT21 evaluation sets is ineligible.
4. **No outcome-driven model choice:** candidate model(s) and eligibility evidence are frozen before the WMT19 beam sweep. Do not try several models and keep the one that gives the desired reversal.
5. **Translation competence:** independent published evidence or a predeclared no-claim competence check must show the model is a functioning EN→DE translator. The competence gate cannot depend on the eventual beam-width sign.
6. **Residual pretraining-contamination limitation:** if web-pretraining exclusion of WMT19 cannot be proven, state that limitation explicitly. Unknown web exposure is not equivalent to known direct supervised inclusion, but it must not be described as contamination-free.

### Immediate ruling

`Unbabel/TowerInstruct-7B-v0.2`: **INELIGIBLE for decisive WMT19 E01** due to known WMT14–WMT21 general-translation training lineage.

If no modern model passes the eligibility gate with defensible translation competence, set L36 to **HOLD / MODEL-PROVENANCE BLOCKER**. Do not relax the gate to obtain a runnable experiment.

## 6. Decoding-semantics audit

Before quality analysis, freeze for every model:

- beam widths (target set: `1, 4, 8, 16, 32`);
- deterministic decoding, no sampling in the primary path;
- EOS and PAD handling;
- maximum generated-token budget;
- length penalty / score normalization;
- early-stopping semantics;
- prompt and output extraction;
- whether beam hypotheses are selected by the model's native generation score or by an explicitly defined rescoring rule.

Do **not** compare an encoder–decoder's raw cumulative score with a decoder-only model's HuggingFace normalized score and call the difference a model-regime effect.

The public LLM4MT implementation is useful here because it exposes standard HuggingFace `GenerationConfig` beam decoding; it is a semantics reference, not necessarily the decisive modern checkpoint.

## 7. The null must be identified, not merely nonsignificant

A central L34 lesson is that a pretty interaction or a failed significance test is not an identified scientific result.

Therefore E01 must predeclare a **material-effect / equivalence criterion** for the modern high-uncertainty beam curve.

A valid law-break gate must establish both:

1. **positive control:** classic high-uncertainty items show a material deterioration as beam grows under the frozen pipeline;
2. **modern attenuation:** the corresponding modern deterioration is demonstrably much smaller, under a predeclared equivalence / relative-attenuation margin — not merely `p > .05`.

The exact margin will be frozen only after a no-claim resolution audit on the classic positive control and before looking at the modern WMT19 outcome.

No post-hoc threshold may be chosen from the modern curve.

## 8. Candidate confirmatory quantity

Let `Q_m(b, U)` be translation quality for model regime `m`, beam width `b`, and a predeclared uncertainty stratum `U`.

One interpretable family of quantities is:

```text
D_m(U) = Q_m(large_beam, U) - Q_m(reference_beam, U)
CURSE_m = D_m(high_U) - D_m(low_U)
REGIME_BREAK = CURSE_modern - CURSE_classic
```

The final exact metric / beam contrast / uncertainty stratification must be frozen in the E01 preregistration. E00 only requires that the modern law break be judged against a reproduced classic positive control and a material attenuation criterion.

## 9. E00 pass / fail

### PASS → write E01 preregistration

Pass only when:

- the WMT19 human-uncertainty data and calculation are frozen;
- the classic EN→DE positive-control checkpoint is frozen;
- one modern EN→DE checkpoint passes the provenance + competence gate;
- decoding semantics are explicitly matched/audited;
- a classic-effect resolution estimate supports a predeclared modern attenuation/equivalence margin.

### FAIL / HOLD

- no eligible modern checkpoint with adequate EN→DE competence → **HOLD / MODEL-PROVENANCE**;
- classic positive control does not reproduce a material uncertainty-conditioned curse → **KILL / INSTRUMENT FAILURE**;
- exact old uncertainty substrate cannot be reconstructed → **HOLD / SAME-QUANTITY FAILURE**;
- only a change in scoring/stopping convention explains the published modern reversal → **KILL MAIN ROUTE**.

No GPU mechanism experiment is authorized by E00.

## 10. Why L36 is currently preferred over the other live candidates

L36's first gate does not require a learned latent direction, a state transplant whose semantic identity must be assumed, a synthetic training curriculum, or a small second-order training difference. If E00 passes, E01 can make a direct go/no-go statement about an old published law on externally defined inputs.

This is why L36 is the preferred next candidate **only after E00 passes**.

---

# Part B — the executed protocol

**Status:** **MANDATORY PRE-E01 GATE — NO E01 RUN UNTIL PASS**
**Date frozen:** 2026-09-14
**Authorization:** this document supersedes `SELECTION.md` §7 for execution order.
`SELECTION.md` authorizes E01; **E01 may not run until every gate below passes.**
**Compute:** local `verl-clean` env (`/home/xiang/miniconda3/envs/verl-clean/bin/python`);
local GPUs on `fvcrc21` (4× RTX PRO 6000, 97 GB); no new environments, no package installs.

---

## 0. Why this gate exists

L34 died after a full training campaign because the experimental quantities could not be mapped
onto the theoretical claim *after* the numbers existed. L36's advertised advantage is that its
first-stage quantities are externally fixed (human-reference disagreement, beam width, translation
quality). That advantage is only real if three things are true **before** any beam curve is looked at:

1. we actually reconstructed *the old quantity*, not a look-alike;
2. our decoding/scoring pipeline is capable of exhibiting the classic pathology at all;
3. the modern model is not disqualified by evaluation-lineage exposure, and was frozen before
   anyone saw its beam curve.

E00 tests exactly those three things, plus a fourth bookkeeping item (§5) that prevents the
"not significant ⇒ law broken" failure mode.

E00 does **not** run any modern beam sweep. The modern beam curve is E01 and is not to be
produced, inspected, or summarized while this gate is open.

---

## 1. Gate A — SAME-QUANTITY substrate reconstruction

### A.1 What must be rebuilt

Stahlberg, Kulikov & Kumar (ACL 2022), eq. (1):

For an `n`-way annotated sentence with references `y_1 ... y_n`,

```
      (1 / C(n,2)) * sum_{i<j} d_edit(y_i, y_j)
u := ------------------------------------------
              (1 / n) * sum_i |y_i|
```

with `d_edit` the Levenshtein distance. Their MT-ende substrate is the **official WMT19
English→German test set** (`newstest2019`, 1997 segments) paired with the **additional
human-authored "AR" reference** of Freitag et al. (2020) — i.e. `n = 2`, so

```
u = d_edit(y_wmt, y_ar) / ((|y_wmt| + |y_ar|) / 2).
```

Sources:
- paper: https://aclanthology.org/2022.acl-long.591/ (§2, eq. 1, footnote 2)
- AR reference: https://github.com/google/wmt19-paraphrased-references (`wmt19/ende/wmt19-ende-ar.ref`)
- WMT19 test set: https://data.statmt.org/wmt19/translation-task/test.tgz

### A.2 Forbidden substitutions

`u` **must** come from human-reference disagreement. Prohibited for the load-bearing quantity:
model token entropy, ensemble disagreement, LLM-judge ambiguity ratings, paraphrase-model
distance, sentence length alone, any model-derived score.

The paraphrase references (`ARP`, `WMTP`, `HQ*`) are **not** used for `u`: only `AR` is an
independently written translation (Freitag et al. 2020; ACL-2022 footnote 2). Using a
paraphrase-of-the-reference would measure paraphrasing instructions, not task ambiguity.

### A.3 Underdetermined detail — declared, not hidden

The ACL-2022 paper does not state the **unit** of the Levenshtein distance (character vs. word).
Both are computed. **Primary:** character-level. Secondary/robustness: word-level.

Character level is primary because it is the reading under which our reconstruction reproduces the
paper's Figure 1 for MT-ende (mean `u` in the 0.3–0.45 band, increasing monotonically with
reference length); the word-level reading lands near 0.6, above the plotted range.

**AMENDED 2026-09-14 → A.3′ (see `results/e00/gateA_unit_resolution.md`).** The original A.3
threshold below failed (`rho = 0.904` passes, same-quartile `0.692 < 0.80`). Per A.3's own
instruction the unit was resolved against the authors' material *before any generation existed*:
the paper's Figure 1 levels turn out not to be reproducible under eq. (1) at all, while its Figure 6
binning (`u ∈ [0,0.33]/(0.33,0.66]/(0.66,1]`) is consistent with the character-level reading
(0.05% of segments above 1, vs 3.3% word-level). Character level is primary, and the gate is
**tightened**: every stratified result in Gate B and E01 must hold under **both** readings, computed
from the same generations. A claim that holds under only one reading does not count.

**Pass requirement A.3 (original, superseded):** the two readings must induce essentially the same stratification —
Spearman `rho >= 0.90` between character- and word-level `u`, and `>= 80%` of segments must land in
the same quartile under both. If they do not agree, the unit choice becomes a real researcher
degree of freedom and must be resolved against the authors' released numbers before E01.

### A.4 Freeze requirement

`u`, the quartile boundaries, and the segment ordering are computed and hashed **before any model
is loaded**. `results/e00/substrate_manifest.json` records sha256 of every input file, the `u`
table, and the quartile cut points. No later stage may recompute or re-bin `u`.

### A.5 Gate A pass/fail

- **PASS:** 1997 aligned segments; `u` computed per eq. (1); Figure-1-consistent profile;
  A.3 agreement satisfied; manifest hashed and committed.
- **FAIL:** any misalignment, any substitution of the quantity, or A.3 disagreement → **HOLD L36**.

---

## 2. Gate B — classic positive control (instrument capability)

### B.1 Claim under test

> Our decoding + evaluation pipeline, on this exact substrate, can exhibit the classic
> beam-search curse where the old law says it must: in the **high-uncertainty** stratum of
> `newstest2019` English→German, under classical (unnormalized) beam scoring.

This is a test of **our instrument**, not of any modern model. It runs first because it is cheap
and because failing it invalidates every downstream interpretation.

### B.2 Systems (declared in advance, in priority order)

1. **Primary classic system:** `facebook/wmt19-en-de` — the released FAIR WMT19 English→German
   Transformer (encoder–decoder), i.e. a system from the same era and shared task as the substrate.
   Revision pinned in the manifest.
2. **Secondary classic system (robustness, declared now):** `Helsinki-NLP/opus-mt-en-de` (Marian).

The gate is decided on the **primary** system. The secondary is reported in all cases and may
*not* be swapped into the primary role after the fact.

### B.3 Decoding semantics (the part TACL leaves implicit)

Every run reports its full generation contract. Two scoring semantics are run:

| tag | beam score | `length_penalty` (HF) | notes |
|---|---|---|---|
| `RAW` | `sum_t log p(y_t)` | `0.0` | the classic MAP objective; the regime in which the curse was originally reported |
| `NORM` | `sum_t log p(y_t) / |y|` | `1.0` | length-normalized, the modern default family |

Fixed across all cells: same source text, `num_return_sequences=1`, `early_stopping=False`,
`no_repeat_ngram_size=0`, `min_new_tokens=0`, no repetition penalty, identical
`max_new_tokens` budget, explicit BOS/EOS/PAD ids, deterministic (`do_sample=False`), fp32/bf16
recorded. Beam grid:

```
b ∈ {1, 4, 8, 16, 32, 64},  b_ref = 4,  b_large = 64  (b_large = 32 reported as sensitivity)
```

`b_ref = 4` is the classic peak reported by ACL-2022 (their MT BLEU peaks at beam 4).

### B.4 Quality measurement

- **Primary `Q`:** corpus BLEU against **both** references (WMT + AR), computed per stratum,
  sacrebleu-equivalent (`13a` tokenizer, case-sensitive, exp smoothing, closest-reference length
  for the brevity penalty).
- **Secondary:** single-reference (WMT) BLEU; corpus chrF2.
- **Diagnostics (not the target):** mean hypothesis/reference length ratio, empty-output rate,
  truncation (hit `max_new_tokens`) rate, mean beam score of the selected hypothesis.

BLEU and chrF2 are implemented in `src/mt_metrics.py` because `sacrebleu` is not present in the
frozen environment and the compute policy forbids installing packages. The implementation is
**validated against the upstream `sacrebleu` source run from a scratch checkout (no install)** on
the actual system outputs; the agreement check is recorded in `results/e00/metric_validation.json`.
Tolerance: `|ΔBLEU| <= 0.05`, `|ΔchrF2| <= 0.05`. Failing tolerance blocks the gate.

### B.5 Estimands

For system `m`, stratum `U`:

```
D_m(U)     = Q_m(b_large, U) − Q_m(b_ref, U)        # beam-widening effect
CURSE_m    = D_m(U_high) − D_m(U_low)               # uncertainty-conditioning of that effect
```

`U_high` = top quartile of frozen `u`; `U_low` = bottom quartile. Uncertainty is **frozen before
generation** (Gate A). Confidence intervals: paired bootstrap over segments, 1000 resamples,
seed fixed at 20260914, percentile intervals.

### B.6 Gate B decision rule (predeclared)

Under `RAW` semantics on the primary classic system:

- **PASS** requires both
  - **B.6.1 visible curse where the law predicts it:** `D_classic(U_high) <= −2.0` BLEU
    with bootstrap 95% CI upper bound `< −1.0`; and
  - **B.6.2 uncertainty conditioning:** `CURSE_classic <= −1.0` BLEU with bootstrap 95% CI
    upper bound `< 0`.
- **CONDITIONAL PASS:** B.6.1 holds but B.6.2 does not. E01 may proceed, but L36 may then
  **never claim** that it reproduced the *sentence-level uncertainty-conditioned* law with its own
  instrument; only the system-level curse is ours, and the conditional law remains a citation.
  This restriction must be carried verbatim into any E01 write-up.
- **FAIL:** B.6.1 does not hold → **INSTRUMENT FAILURE**. L36 is put on HOLD. It is explicitly
  forbidden to run the modern model and report a flat beam curve as "the law is broken", because
  a pipeline that cannot produce the curse on a 2019 encoder–decoder cannot license that claim.

### B.7 Anti-rescue clause

If the curse appears only under `NORM` and not under `RAW`, or only on the secondary system, the
result is recorded as-is and the gate is decided by B.6 as written. No post-hoc search over
`length_penalty`, stopping rules, `max_new_tokens`, prompts, or systems is permitted to manufacture
a passing control. The grid above is the whole grid.

---

## 3. Gate C — modern model provenance and eligibility

### C.1 Hard exclusion — disclosed WMT-evaluation lineage

A modern checkpoint is **ineligible** if its public documentation discloses supervised training on
WMT general-translation test/dev sets covering 2019.

Excluded by this rule, with citation:

| checkpoint | disclosed exposure | verdict |
|---|---|---|
| `Unbabel/TowerInstruct-*` (TowerBlocks v0.2) | dataset card lists **"WMT14 to WMT21 — General Translation"** in the supervised mix | **BANNED** |
| `haoranxu/ALMA-*` | ALMA paper §3.2: *"we collect human-written test datasets from WMT'17 to WMT'20"* as the parallel fine-tuning data | **BANNED** |

Sources: https://huggingface.co/datasets/Unbabel/TowerBlocks-v0.2 ; https://arxiv.org/pdf/2309.11674 (§3.2, App. Table 5).

This exclusion is the whole point of the gate: a model whose supervised data lineage contains the
WMT19 general-translation set cannot be used to argue that *this* test set's ambiguity no longer
produces search pathology. A flat beam curve there is uninterpretable, exactly the way L34's
primary estimand became uninterpretable.

The TACL-2025 LLM-SFT checkpoints are also not used as the modern arm: they are Llama2-7B models
supervised on WMT23 bilingual data and evaluated on `generaltest2023` German→English, i.e. a
different direction and substrate; reproducing them would additionally require training, which
`SELECTION.md` does not authorize.

### C.2 Eligible pool

Open-weight, decoder-only, instruction-tuned general LLMs with usable English→German ability and
**no disclosed WMT test-set supervision**, already present in the local HF cache:

- `meta-llama/Llama-3.1-8B-Instruct`
- `Qwen/Qwen2.5-7B-Instruct`, `Qwen/Qwen2.5-14B-Instruct`
- `google/gemma-3-12b-it`

### C.3 Substrate-blind capability screen

The modern model is selected on **`newstest2018` English→German**, a different year, disjoint from
the frozen substrate, using greedy decoding only (`num_beams=1`), on a fixed 300-segment subset
(first 300 segments, no selection). Selection rule, in order:

1. eligible under C.1;
2. highest `newstest2018` greedy chrF2 among the pool;
3. ties (`< 0.5` chrF2) broken by smaller parameter count.

**No beam sweep is run during selection**, on any substrate. The selected checkpoint, its
revision hash, prompt template, and generation contract are written to
`results/e00/modern_model_freeze.json` and committed **before** E01 generates anything.

A model that cannot produce well-formed German at all (greedy chrF2 `< 40` on newstest2018, or
`> 5%` malformed/empty outputs under the frozen prompt) is dropped from the pool. If no eligible
model clears the bar, **HOLD L36** — do not fall back to a banned checkpoint.

### C.4 Memorization probe (bounded, and honestly labelled)

Closed-data pretraining means C.1 can only exclude *disclosed* supervision. As a partial check,
on the frozen substrate the selected model is scored teacher-forced given the source:

- `NLL_wmt` = mean per-token NLL of the official WMT19 reference;
- `NLL_ar` = mean per-token NLL of the AR reference;
- `prefix-continuation exact-match rate`: feed source + first 50% of the WMT reference tokens,
  greedy-continue, measure exact match of the remainder.

Predeclared flags: exact-match rate `> 5%`, or `NLL_wmt` lower than `NLL_ar` by more than 0.5 nats
per token. Either flag ⇒ record a **CONTAMINATION WARNING** in the freeze file; E01 may still run,
but any law-break claim must report the probe and must additionally hold on a stratification that
excludes flagged segments. This probe cannot prove absence of contamination and will not be
described as if it could.

### C.5 Gate C pass/fail

- **PASS:** an eligible, non-banned checkpoint clears C.3 and is frozen with its contract.
- **FAIL:** no eligible model clears the bar → **HOLD L36**. Model-zoo search for a checkpoint that
  yields the desired flat curve is prohibited.

---

## 4. Gate D — power / resolution

Before E01, on the classic control's observed variance, report the paired-bootstrap MDE for
`D(U_high)` at the frozen substrate size (1997 segments; ~499 per quartile).

- **PASS:** MDE `<= 1.0` BLEU, i.e. the design can resolve the equivalence margin of §5.
- **FAIL:** MDE `> 1.0` BLEU → **HOLD**. Do not expand the substrate or pool models post hoc;
  the ACL-2022 multi-reference substrate is the whole substrate.

---

## 5. Predeclared law-break criteria for E01 (frozen here, before any modern curve)

This section exists so that "`Δ = −0.3`, `p = 0.28`" can never be reported as a broken law.

With `D_m(U)` and `CURSE_m` as defined in B.5, and the same beam grid, semantics, metric and
bootstrap:

```
REGIME_BREAK = CURSE_modern − CURSE_classic
ATT          = D_modern(U_high) − D_classic(U_high)      # attenuation of the high-u curse
```

E01 may claim the old law breaks **only if all three hold**:

1. **Equivalence, not silence.** `D_modern(U_high)` is statistically equivalent to no material
   deterioration: bootstrap 95% CI for `D_modern(U_high)` lies entirely above `−1.0` BLEU.
   A wide CI containing both `0` and `−3` is **not** a law break; it is an underpowered null.
2. **Material attenuation.** `ATT > 0` with bootstrap 95% CI lower bound `> +1.0` BLEU,
   i.e. the modern high-`u` curse is smaller than the classic one by more than the margin.
3. **Semantics-robust.** (1) and (2) hold under `RAW` semantics — the regime in which the classic
   curse exists. A flat curve that appears only under `NORM` is Outcome B of `SELECTION.md` §10
   (scoring-convention artifact) and **kills the Main route**.

Secondary, reported always, never load-bearing: the relative form
`D_m(U_high) / Q_m(b_ref, U_high)`, to address the objection that BLEU deltas are not comparable
across systems of different strength.

**Declared limitation, written now:** classic and modern are different systems at different quality
levels, so `ATT` mixes "regime" with "system". E01 alone therefore cannot attribute the attenuation
to the LLM regime *per se*; that attribution is the job of the later mechanism stage
(`SELECTION.md` §11, C2–C3). E01's job is only to establish that there is an attenuation worth
explaining.

---

## 6. Execution order (binding)

```
A  substrate build + freeze            (no model loaded)
B  classic positive control            (primary: facebook/wmt19-en-de)
C  modern eligibility + blind screen   (newstest2018 only)
D  power report from B's variance
--- gate decision written to results/e00/E00_VERDICT.md ---
E01 only if A,B,C,D pass or conditionally pass
```

Any gate that fails stops L36 at HOLD, cheaply, with no modern beam sweep run and no claim made.
