# L32 E04 — Preregistration: does it survive modern models and a different tokenizer?

**Written 2026-09-13, BEFORE any E04 run.** Locked. Deviations get a dated
section at the bottom, not an edit.

Authorized by the user after `search_rounds/2026-09-13_L32_MAIN_SELECTION.md`,
whose verdict was **PASS to Main candidate CONDITIONAL on this experiment**.
E04 is that condition. A null here returns L32 to the Findings paper E02 earned.

---

## 1. The gap E04 must close

Every L32 number so far comes from LLaMA-1 7B, a 2023 base model, because that
is what the parent used and because its published token ids are only meaningful
in its 32k SentencePiece vocabulary. Two questions follow, and neither is
answerable from what we have:

1. Does the termination confound and the one-row sufficiency survive on a
   **modern** base model?
2. Is "one structural row" an artifact of **SentencePiece**, where `\n` is a
   standalone token, or does it survive a **byte-BPE** vocabulary where newline
   merges into neighbouring tokens?

## 2. Models — three families, all untied

`tie_word_embeddings=False` is load-bearing: the tuned input row must not be
able to change output logits directly. Verified for all three before locking.

| model | vocab | tokenizer | tie | BOS |
|---|---|---|---|---|
| `huggyllama/llama-7b` | 32,000 | SentencePiece | False | 1 |
| `NousResearch/Meta-Llama-3.1-8B` | 128,256 | byte-BPE | False | 128000 |
| `Qwen/Qwen2.5-7B` | 152,064 | byte-BPE | False | **none** |

All three are already in the local HF cache.

## 3. Tokenization fact recorded before running

Under the frozen `P1_explicit` template, both modern tokenizers merge the
head newline into `'.\n'` (llama3 `627`, qwen `624`) but keep a **standalone
newline in the tail**, immediately before generation:

| model | `\n` row | `:` row | occurrences of `\n` in the prompt |
|---|---|---|---|
| llama1-7b | **13** | 29901 | 2 (head + tail) |
| llama3.1-8b | **198** | 25 | 1 (tail) |
| qwen2.5-7b | **198** | 25 | 1 (tail) |

BOS is **not** tested in E04 because Qwen2.5 has none, so it is not comparable
across families. The two rows tested are `\n` and `:`, both present in every
template under every tokenizer.

## 4. Denominator change, and why

E03 measured sufficiency against an 18-row ticket *we* selected. E04 uses
**full embedding tuning** as the denominator instead, because it is the parent's
own reference model — Theorem 2 certifies agreement with Embed Tuning, not with
translation. The claim becomes directly interpretable:

> **one row out of V recovers X% of tuning all V rows.**

LLaMA-1 is re-measured on this same denominator so all three models are
comparable. E03's numbers are not carried over.

## 5. Conditions

Per model × language (`ca`, `es`), identical pipeline, data filter, template,
LR 1e-2 (single-row) / 2e-5 (full embedding, the parent's Embed Tuning LR),
5 / 3 epochs respectively, 10k OPUS-100 pairs:

| condition | rows tuned | seeds |
|---|---|---|
| `FULL_EMBED` | all V | 1 |
| `ROW_NL` | `\n` only | 2 |
| `ROW_COLON` | `:` only | 1 |
| `ROW_RAND` | one random row, count-matched to `\n`, not in the template | 1 |

3 models × 2 languages × 5 runs = **30 runs**.

`ROW_RAND` is the null: if any single frequently-occurring row works, the result
is about row count, not about structural interface rows.

## 6. Measurement — unchanged and locked

The three E02 extraction rules (`R1_raw`, `R2_firstline`, `R3_prompt_restart`)
and both metrics (spBLEU `flores101`, chrF2) are computed for every arm, always.
Plus EOS rate and mean characters. Flores-101 devtest, 1012 sentences, greedy.

## 7. Primary quantities

- **sufficiency** `= Δ_R1(one row) / Δ_R1(FULL_EMBED)`
- **collapse** `= 1 − Δ_R2(FULL_EMBED) / Δ_R1(FULL_EMBED)` — the termination share
- **specificity** `= Δ_R1(ROW_NL) / Δ_R1(ROW_RAND)`

## 8. Pre-declared gate

**PASS (E04 clears the Main condition)** requires all three:

1. `collapse ≥ 0.5` in **≥2 of 3** models, averaged over languages;
2. `sufficiency ≥ 0.5` for `\n` in **≥2 of 3** models, averaged over languages
   and seeds;
3. `sufficiency(\n) > sufficiency(ROW_RAND)` in **≥2 of 3** models — otherwise
   the effect is "one row, any row", not "one structural row".

**KILL (return to Findings, close L32)** if on **both modern models** either
`collapse < 0.3` or `sufficiency(\n) < 0.3`. That would make the LLaMA-1 result
model-specific, and the Main case in the Selection document fails on its own
stated condition.

**Partial** outcomes between these are reported as graded, and the Main case is
argued only if gate (1)–(3) is met as written. I will not renegotiate the
thresholds after seeing numbers.

## 9. What E04 does not do

No new mechanism claim, no further model expansion, no new selection algorithm.
The Selection document's second Main ingredient — establishing the
one-row-plus-truncation reporting standard — is a *writing* task built on these
numbers, not an additional experiment.
