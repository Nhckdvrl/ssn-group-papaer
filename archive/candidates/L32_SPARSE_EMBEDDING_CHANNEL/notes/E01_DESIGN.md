# L32 E01 — Design, frozen before any tuned arm was evaluated

**Date:** 2026-09-13. Authorization: `search_rounds/2026-09-13_SPARSE_EMBEDDING_CHANNEL_SELECTION.md`
(`PILOT-AUTHORIZED — E01 ONLY`).

Written after the base-model audit below and **before** any arm using a trained
delta was scored. Nothing here may be changed once a tuned arm has been run.

---

## 1. Estimand

Unchanged from Selection. For a **single** trained sparse update (the 18 en→ca
KS-Lottery rows), and metric `M`:

`Δ_c = M(channel c) − M(BASE)`, `R_c = Δ_c / Δ_ALL`

where the channel only decides **at which positions the already-learned tuned row
is read instead of the frozen base row**. Same model, same delta, same examples,
same decoding. Arms: `BASE, ALL, INSTRUCTION, SOURCE, PREFILL, TARGET`.

LLaMA-1 has `tie_word_embeddings=False`, so the update cannot reach the output
head directly. Any effect must arise from reading those rows as *input*.

## 2. Instrument audit performed BEFORE the pilot (and why it changes the report)

KS-Lottery reports LLaMA-7B en→ca at **5.7 spBLEU** untuned and **37.7** after
tuning 18 rows. The paper publishes neither its prompt template nor its output
post-processing. Both were audited on the untuned model, 200 Flores devtest
sentences, greedy (`results/prompt_probe.json`):

| template | first line only | whole continuation | mean chars | hit 256-token cap |
|---|---|---|---|---|
| explicit (frozen for E01) | **33.78** | **6.39** | 852 | 0.875 |
| alpaca | 6.40 | 1.96 | 909 | 1.00 |
| bare_pair | 26.51 | 9.98 | 427 | 0.31 |

The untuned base model's score on this task spans **1.96 – 33.78 spBLEU** as a
function of prompt and post-processing alone. The parent's 5.7 is reproducible
only when the whole continuation is scored: the base model *already produces the
Catalan translation* and then keeps generating.

Consequence for E01: **spBLEU must be reported under two scorings for every
arm**, and neither may be chosen after seeing results.

- `raw` — the full continuation to EOS. **This is the parent-comparable scoring
  and the one the frozen first-stage gate is evaluated on.**
- `trunc` — first line only. Termination is neutralised; what remains is
  translation quality.

Also recorded per arm: `frac_stopped` (EOS emitted before the cap) and
`mean_raw_chars`.

## 3. Frozen first-stage gate

From Selection, unmodified:

> `spBLEU(ALL) − spBLEU(BASE) ≥ +15` on en→ca Flores devtest, same sign in all 3
> training seeds. If this fails: **STOP E01, no mechanism interpretation.**

Evaluated on `raw` (§2). Pre-declared readings:

- **gate passes on `raw` AND `trunc` shows a comparable gain** → the parent
  effect is a translation-quality effect; proceed to the channel decomposition as
  written in Selection.
- **gate passes on `raw` but `trunc` gain is small** → the parent effect is
  mostly a termination/format policy. The channel question is still well posed
  and still worth answering (how does an update to *untied input rows* install an
  *output-side* stopping policy?), but the paper identity has moved. That is a
  claim mutation: report it, write a Claim Novelty Delta, and **do not** treat
  E01 as authorising the follow-ups in Selection §8.
- **gate fails on `raw`** → STOP; diagnose replication only.

## 4. Deviations from the parent, and why each is safe for the estimand

| # | parent | here | effect on the estimand |
|---|---|---|---|
| 1 | Lego-MT 10k en→ca | OPUS-100 ca-en, 10k sampled | none: the channel contrast reuses **one** trained model. Affects only the replication gate. The public `Lego-MT/Parallel_Dataset` release is a per-language mixed-direction 10k sample (`ca.jsonl` holds 935 en→ca pairs), so it cannot supply a bilingual 10k set. |
| 2 | — | pool filtered to 60–400 chars both sides | matches Flores sentence length (train mean 40.0 target tokens vs devtest 47.3); an unfiltered OPUS sample is subtitle-short (16.7) and trains a length policy that does not transfer. Frozen before training. |
| 3 | beam size 4 | greedy | applied identically to every arm; the contrast is between arms. |
| 4 | unpublished prompt | `explicit` template, frozen in `src/common.py` | identical for every arm and seed. §2 documents the sensitivity. |
| 5 | fp16/unspecified | bf16 backbone, fp32 delta | LR 1e-2 on an 18×4096 delta needs fp32 accumulation. |

Kept from the parent: LLaMA-7B (`huggyllama/llama-7b`, 32k vocab — the published
token ids are only meaningful in this vocabulary), the 18 en→ca ids from Table 5,
LR 1e-2, 5 epochs, Flores-101 devtest (1012 sentences, original tarball), spBLEU
via `sacrebleu` `tokenize="flores101"`.

## 5. Support audit (pre-registered, blocking)

Before any SOURCE-vs-TARGET interpretation, count Flores devtest sentences with
≥1 selected-token occurrence in the instruction span, the source span, and the
reference-target span. Require **≥250 sentences on each of source and target**.
If a channel has no opportunity, its null is uninterpretable → HOLD, not "that
channel does not matter".

## 6. Uncertainty

Arms are evaluated on the **same** 1012 sentences, so all contrasts are paired.
Sentence-level bootstrap (10,000 draws) on the paired differences, plus training
seed as a second resampling level once 3 seeds exist. Report both.

## 7. Instrument checks

- trainable parameter count must equal `18 × 4096 = 73,728` and the backbone must
  report **zero** trainable parameters (the L30 lesson: a silently trainable
  embedding matrix turns this into full fine-tuning).
- `BASE` arm with a trained delta loaded must score identically to the untuned
  model — if not, the gate is leaking.
- `ALL` arm must equal writing the delta into the embedding matrix directly.
- prompt/source segment boundaries are derived from prefix tokenizations and
  asserted, never guessed.

## 8. What E01 does not authorise

Unchanged from Selection: no multilingual sweep, no model zoo, no new PEFT
method, no "high frequency is causal" claim, no C2/C3.
