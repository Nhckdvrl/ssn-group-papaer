# L19 — Ownership audit (verified 2026-09-11)

## Parent, verified from the PDF rather than the abstract

**Zheng, Li, Yu, Chen. "When Long Helps Short." EMNLP 2025 Main** (2025.emnlp-main.522;
arXiv 2509.18762).

Verified by reading the full paper (`data/mother_paper.txt`):

- Base model: `Llama-3-8B-ProLong-512k-Base`, following Gao et al. 2025.
- Budget unified at 1B tokens / 4M-token batch across all five runs. **The headline is
  not a token-count artifact** — an earlier suspicion of ours that the paper refutes.
- The "controlled experiments" of their §4 are **five different datasets**: UltraChat and
  Tulu-v2 as short; LongAlpaca, LongMIT, ChatQA2 as long (Appendix A Table 2).
- **There is no experiment anywhere in the paper that varies sequence length while
  holding data source and supervision fixed.** No truncation arm, no padding arm, no
  paired construction. Confirmed by full-text search for truncat*/length distribution.
- Their mechanism analyses (MHA replacement 54.7→67.8 on GSM8K, retrieval score
  16.94 vs 15.39, FFN replacement, attention entropy, knowledge-preference conflict,
  hybrid-ratio sweep) are all **UltraChat-SFT vs ChatQA2-SFT** — two datasets, one
  comparison. Every mechanism claim inherits the same confound as the headline.

So the paper's central causal variable is not identified. See `MOTHER_REANALYSIS.md`
for what its own Table 1 shows once dataset is treated as the unit.

## Nearest work, and what each actually owns

**SkipAlign** (arXiv 2405.03939). Synthesises long-range *positional* dependency by
position skipping, without real long text, and improves long-context ability. Owns:
position index manipulation is a substitute for length **for long-context ability**.
Does not measure short-task transfer. For us it is a future competing-account operation,
not a collision.

**GATEAU** (EMNLP 2025 Main, 2025.emnlp-main.375). Selects long SFT samples rich in
long-range dependency; better long-context alignment. Owns: *which* long samples help
**long** tasks. Dependent variable is long-context ability.

**EXACT** (arXiv 2605.10544, verified to exist). Shows nominal context window is the
wrong variable: under packed training most targets get a short *effective* context;
rebalancing toward long effective-context supervision gives +5 to +17 on NoLiMa/RULER
while standard short benchmarks stay roughly flat (~+0.24 macro). Owns: effective
context exposure ≠ nominal length, **for long-context ability**. Its short-benchmark
flatness is a nearby and important data point — it is, if anything, mild independent
evidence against a general length→short-capability law, obtained under a different
manipulation.

**"Longer Context, Deeper Thinking"** (arXiv 2505.17315). Newly surfaced in this audit
and the closest on the *dependent variable*: models with stronger long-context capacity
reach higher reasoning accuracy after SFT, with gains that persist on short inputs.
Crucially they vary the **base model's long-context capacity** with SFT data held fixed —
the mirror image of our manipulation, which varies **SFT input length** with base model
and supervision held fixed. Not a collision; it is a live competing account for the
mother phenomenon (long-SFT data may act by exercising a capacity that was already
there), and it raises the value of separating the two.

## Strongest compression, and the answer

> Prior A (mother: long-SFT datasets score higher on short benchmarks)
> + Prior B (SkipAlign/GATEAU/EXACT: what matters is dependency / effective context,
>   not nominal length)
> + Prior C (Longer-Context-Deeper-Thinking: long-context capacity aids reasoning)
> = our paper?

No, and the gap is specific. A, B and C between them assert that nominal length is the
wrong variable **for long-context ability**, and separately that long-SFT data correlates
with better short-task scores. **Nobody has manipulated input length with the
supervision content held fixed and measured short-task transfer.** The one published
result that touches it (EXACT's flat short benchmarks) points the opposite way from the
mother's headline, under a different intervention, and neither paper cites the tension.

Ownership verdict, unchanged from the pre-audit judgement but now verified against
primary sources:

- **Direct collision:** no.
- **Crowded ingredients:** yes.
- **Plausible independent contribution:** yes — the identification of the causal variable
  behind a published EMNLP Main headline.

## The fence

E01 alone compresses to "Zheng et al. with better controls". That is not a Main paper and
must not be written as one. The route earns a paper only if the identification programme
runs to: which variable actually drives transfer → does that variable predict which
long-SFT datasets help → do the mother's MHA/FFN/retrieval signatures track the real
variable rather than nominal length.

If, after E01, novelty can only be preserved by narrowing to an odd condition, kill.
