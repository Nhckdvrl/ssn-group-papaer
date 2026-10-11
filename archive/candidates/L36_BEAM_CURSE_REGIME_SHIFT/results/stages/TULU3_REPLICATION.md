# Second lineage: does the stage sweep replicate on Tülu-3?

**Status:** exploratory (E00-EXT breadth). **Substrate:** frozen `newstest2019` En→De, 400 segments
for step-0, 200 for the beam cells, RAW scoring. **Instrument:** `src/termination.py`, unchanged.

The Olmo-3 sweep (`STAGE_LINEAGE_FINDINGS.md`) made two claims that a second, independently built
lineage can break: *(a)* the termination regime jumps at SFT, and *(b)* the learned boundary is
keyed to the generation format. Tülu-3 (`allenai/Llama-3.1-Tulu-3-8B-{SFT,DPO}` + the RLVR final,
base `NousResearch/Meta-Llama-3.1-8B`) shares the recipe shape — base → SFT → DPO → RLVR — but a
different base model, different data and a different lab pipeline.

**One of the two claims replicated. The other did not, and the failure is informative.**

## 1. The Tülu-3 lineage

| tag | stage | interface | margin | median `rank_stop` | `b*` | BLEU@1 | BLEU@16 | BLEU@64 | empty@64 | lenR@64 |
|---|---|---|---|---|---|---|---|---|---|---|
| `tulu3-base` | base | few-shot | +6.94 | **45** | 23 | 43.8 | 38.8 | 19.3 | **26.5 %** | 0.63 |
| `tulu3-sft` | SFT | few-shot | +7.94 | **40** | 20 | 43.1 | 34.5 | 21.6 | **27.5 %** | 0.58 |
| `tulu3-dpo` | DPO | few-shot | +9.88 | **40** | 20 | 41.8 | 39.7 | 36.0 | 10.0 % | 0.82 |
| `tulu3-rlvr` | RLVR | few-shot | +10.51 | **48** | 24 | 42.3 | 41.9 | 40.0 | 6.0 % | 0.88 |
| `tulu3-sft` | SFT | chat | +8.73 | **134** | 67 | 42.3 | 39.9 | 25.8 | 6.0 % | 0.76 |
| `tulu3-dpo` | DPO | chat | +9.92 | **95** | 48 | 40.6 | 41.7 | 35.9 | 7.0 % | 0.84 |
| `tulu3-rlvr` | RLVR | chat | +12.21 | **340** | 170 | 41.0 | 40.7 | 31.6 | 1.0 % | 0.76 |

## 2. What replicated

**The format keying (claim b).** In every post-trained Tülu stage the stop rank is higher inside the
chat format than outside it — SFT 40 → 134, DPO 40 → 95, RLVR 48 → 340 — with the same sign as
Olmo-3, and the beam behaviour follows (SFT few-shot 27.5 % empty vs chat 6.0 %). So "the learned
termination boundary is conditional on the generation format" is not an Olmo-3 quirk.

**The magnitude is lineage-specific, and much smaller.** Olmo-3 SFT moves 3 → 1222 across formats
(~400×); Tülu-3 SFT moves 40 → 134 (3.4×). Any claim of the form "post-training makes the model
unable to stop out of format" must therefore be stated as a *direction with lineage-dependent
magnitude*, not as a constant of the post-training regime.

**RLVR pushes the boundary outward in both lineages.** RLVR holds the largest rank of any Tülu
stage in both formats (48 / 340) and is the most beam-robust cell (6 % / 1 % empty, BLEU 42.3 → 40.0
from beam 1 to 64). Olmo-3 RLVR chat does the same thing an order of magnitude harder (rank 41025,
0 % empty, BLEU rising 28.6 → 31.1). Two independent RLVR runs moving termination the same way is
the strongest cross-lineage regularity in this table.

## 3. What did NOT replicate — the SFT jump

`STAGE_LINEAGE_FINDINGS.md` §3(a) said: *"The jump is at SFT."* **On Tülu-3 there is no jump at
SFT.** In-format, base → SFT moves the rank 45 → 40, i.e. not at all. The reason is on the base
side: **Llama-3.1-8B base already sits at rank 45** (`b*` = 23) and already collapses under beam
search — 26.5 % empty at beam 64, length ratio 0.63 — whereas Olmo-3 base sits at rank 532 and is
untouched through beam 128. The two base models are in different termination regimes before any
post-training happens.

So the correct statement is not "SFT installs the collapse". It is:

> Checkpoints occupy very different termination regimes, spanning four orders of magnitude in stop
> rank; *which* training step moves a given lineage into or out of the dangerous regime is
> lineage-specific, but the map from the regime to the beam behaviour is not.

This is recorded as a correction to §3(a), not an addendum: the single-lineage version of that claim
was not supported once a second lineage was run.

## 4. The part that survives both lineages: rank → onset

Pooling every system measured in this candidate — 4 FAIR WMT19 encoder-decoders (four language
directions), the 6 Olmo-3 cells, the 7 Tülu-3 cells and the two Olmo-3 onset probes — 19 systems
spanning two architecture classes, three model families, four training stages, two interfaces and
four language directions:

**Spearman(median `rank_stop`, empty rate @ beam 64) = −0.932 (n = 19).**

The predeclared threshold `b* = ceil(rank/2)` separates the two groups cleanly at the 8 % level:

| group | n | median empty@64 | range |
|---|---|---|---|
| `b* < 64` (exposed at beam 64) | 10 | 27.5 % | 6.0 – 92.5 % |
| `b* ≥ 64` (not exposed) | 9 | **0.0 %** | 0.0 – 6.0 % |

Every system that loses more than 8 % of its outputs at beam 64 has `b* < 64`; no system with
`b* ≥ 64` exceeds 6 %. The quantity is measured from a **single forward pass at position 0**, before
any search is run.

## 5. Caveats

- `rank_stop` and the empty rate are not independent constructs in the trivial sense — the search
  algorithm enforces `rank ≤ 2b` for entry — but the pooled correlation is over *magnitude*, across
  systems that differ in architecture, tokenizer, stop-set cardinality and language, and exposure is
  necessary-not-sufficient (§1 of the findings file: 13–49 % of exposed segments actually collapse).
- The few-shot and chat stop sets differ in cardinality (~2.2k line-break tokens vs one end-of-turn
  id). Within-lineage format comparisons inherit that confound; `E02` removes it by construction
  with a single shared `<END>` token in both formats, and the E02 result stands independently.
- Seven Tülu cells, one substrate, one direction for the lineage work; the direction breadth comes
  from the classic side only (`results/directions/DIRECTION_BREADTH.md`). Modern-side direction
  probes are not yet run.
- `tulu3-base` at beam 1 scores BLEU 43.8 on a multi-reference En→De substrate; Llama-3.1-8B's
  WMT19 exposure is unknown and this number should not be read as a quality claim.
