# L36 E04 — is the rank → onset relation a HuggingFace artefact?

**Tier-1 gap 4.** Every beam curve in this candidate was produced by one library. The entry bound
`rank_stop ≤ 2b` is a property of *that* implementation's first step, so a reviewer is entitled to
ask whether `b*` describes models or describes `transformers`. This runs the same prompts and the
same beam widths through **vLLM 0.11.0**'s independently written beam search and compares.

**Answer: not an artefact.** 18 matched cells; the empty rate is *identical* in all 18, the length
ratio agrees to a mean of 0.029, and the damage-channel classification agrees 18/18. One systematic
discrepancy exists and is reported in §3.

## 0. Scope, and why these checkpoints

vLLM's `LLM.beam_search` terminates a hypothesis only on `tokenizer.eos_token_id`; it cannot express
the multi-token "a line break ends the translation" stop contract the few-shot cells use. The
comparison therefore runs on the **E02 checkpoints**, whose only boundary symbol is a single
dedicated token we trained in — the one setting where both libraries are expressing the same
stopping rule. `tokenizer.eos_token_id` is pointed at that token; prompts, segments (200 of
`newstest2019` En→De), widths, `length_penalty = 0` (RAW) and all post-processing are matched to
`src/e02_train.py:measure_behaviour`.

**A finding about the standard algorithm, not about one library:** vLLM's beam search also requests
`2 * beam_width` candidates per step (`vllm/entrypoints/llm.py`). The `2b` exposure bound is how
beam search is written in two independent implementations, not a HuggingFace quirk. That makes the
bound *more* general than the original framing, and still not a finding in itself (see
`STAGE_LINEAGE_FINDINGS.md` §0a) — the finding is the magnitude of the rank.

## 1. The comparison

`Qwen2.5-3B`, E02 final checkpoints, RAW scoring, 200 segments.

| condition / format | beam | vLLM empty / lenR / BLEU | HF empty / lenR / BLEU | Δ lenR | Δ BLEU |
|---|---|---|---|---|---|
| `A_ONLY` / A (in format) | 1 | 0.0 % / 0.979 / 35.53 | 0.0 % / 1.003 / 34.34 | −0.024 | +1.19 |
| | 16 | 0.0 % / 0.962 / 40.16 | 0.0 % / 0.959 / 39.90 | +0.003 | +0.27 |
| | 64 | 0.0 % / 0.954 / 39.18 | 0.0 % / 0.954 / 38.25 | **+0.000** | +0.92 |
| `A_ONLY` / B (**out of format**) | 1 | 0.0 % / **3.526** / 7.05 | 0.0 % / **3.505** / 6.99 | +0.021 | +0.05 |
| | 16 | 0.0 % / **3.833** / 7.64 | 0.0 % / **3.875** / 6.65 | −0.042 | +0.99 |
| | 64 | 0.0 % / **4.004** / 5.87 | 0.0 % / **4.049** / 5.06 | −0.045 | +0.80 |
| `B_ONLY` / A (**out of format**) | 1 | 0.0 % / **4.043** / 8.03 | 0.0 % / **4.002** / 7.95 | +0.041 | +0.08 |
| | 16 | 0.0 % / **4.087** / 8.08 | 0.0 % / **4.161** / 7.50 | −0.074 | +0.58 |
| | 64 | 0.0 % / **4.229** / 6.85 | 0.0 % / **4.288** / 5.98 | −0.060 | +0.87 |
| `B_ONLY` / B (in format) | 1 | 0.0 % / 0.991 / 35.77 | 0.0 % / 1.026 / 34.33 | −0.034 | +1.44 |
| | 16 | 0.0 % / 0.961 / 40.66 | 0.0 % / 0.977 / 37.73 | −0.016 | +2.92 |
| | 64 | 0.0 % / 0.958 / 39.46 | 0.0 % / 0.962 / 35.33 | −0.004 | +4.13 |
| `MIXED` / A | 1 | 0.0 % / 0.982 / 35.22 | 0.0 % / 1.062 / 32.81 | −0.080 | +2.41 |
| | 16 | 0.0 % / 0.967 / 40.26 | 0.0 % / 0.997 / 37.58 | −0.031 | +2.68 |
| | 64 | 0.0 % / 0.960 / 39.55 | 0.0 % / 0.959 / 38.25 | +0.001 | +1.29 |
| `MIXED` / B | 1 | 0.0 % / 0.991 / 35.10 | 0.0 % / 1.010 / 34.30 | −0.019 | +0.80 |
| | 16 | 0.0 % / 0.950 / 39.25 | 0.0 % / 0.963 / 38.24 | −0.013 | +1.01 |
| | 64 | 0.0 % / 0.952 / 37.32 | 0.0 % / 0.972 / 34.30 | −0.019 | +3.03 |

## 2. Summary

| quantity | agreement |
|---|---|
| empty rate | **identical in 18/18 cells** (max difference 0.00 pp) |
| length ratio | mean \|Δ\| = **0.029**, max 0.080 |
| damage-channel classification (run-on `lenR > 1.3` / collapse `empty ≥ 8 %`) | **18/18 agree** |
| BLEU | mean \|Δ\| = 1.41, max 4.13 — **see §3** |

The result the comparison exists to check reproduces exactly: **in format, length ratio ≈ 0.95–0.99;
out of format, length ratio ≈ 4.0**, in both libraries, at every width, with the empty rate pinned at
0 % throughout. E02's amended P3 — that a model which never learned the boundary in a format fails
there by running on rather than by collapsing — is not an artefact of `transformers`.

## 3. A systematic discrepancy, reported rather than buried

**vLLM's BLEU is higher than HuggingFace's in 18 of 18 cells** (mean +1.41, max +4.13). A consistent
sign across every cell is not sampling noise; the two implementations differ in something real —
most plausibly tie-breaking among equally scored hypotheses and/or floating-point ordering in the
top-`2b` selection, which at `length_penalty = 0` can change which of several equal-score
hypotheses is returned. We did not chase it further.

It does not affect this document's conclusion, which rests on the empty rate (identical) and the
length ratio (mean Δ 0.029) — but it does mean **absolute BLEU values in this project are
implementation-dependent at the ~1–4 point level**, and any future claim that compares BLEU across
decoding stacks has to account for it.

## 4. Harness bugs found and fixed before any comparison was drawn

Recorded because they are the reason a cross-implementation check is worth running at all — none of
them is visible from the HuggingFace side alone:

1. vLLM caps sample logprobs at 20, so every beam width above 10 raised `ValueError`. Fixed by
   declaring `max_logprobs = 2 * max_beam + 1`.
2. vLLM sets `BeamSearchSequence.text = decode(tokens)` where `tokens` **include the prompt**.
   Scoring `seq.text` scored the prompt's first line — constant across widths, BLEU 0.03. Fixed by
   passing prompts as token ids and decoding only the generated suffix.
3. The harness truncated hypotheses at the first newline and tokenized prompts with
   `add_special_tokens=True`; the HF side does neither. **This clipped exactly the run-on channel
   the comparison tests** — out-of-format cells read lenR 1.17–1.43 instead of ~4.0. Had it gone
   unnoticed it would have produced a fabricated "the two implementations disagree" result.

All outputs produced before these fixes are discarded and none are reported above.

## 5. Caveats

- One model (`Qwen2.5-3B` E02 checkpoints), one substrate, En→De, 200 segments, three widths.
- Because vLLM's beam search honours only a single EOS id, this check **cannot** be run on the
  few-shot cells whose stop set is ~2.2k line-break tokens — i.e. precisely the cells with the
  lowest ranks and the largest collapses. The cross-implementation evidence therefore covers the
  run-on channel and the in-format safe regime, **not** the termination-collapse channel directly.
  That is a real limit on §2's scope and is not papered over.
- vLLM's `beam_search` is a Python loop; at width 64 it is CPU-bound and roughly 30–45 min per cell,
  which is why the sweep stops at 64.
