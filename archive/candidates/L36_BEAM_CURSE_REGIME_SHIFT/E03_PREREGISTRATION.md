# L36 E03 — A held-out, out-of-sample test of the rank → onset rule

**Registered:** 2026-09-15, **after** the step-0 `rank_stop` of every held-out system was measured
and **before** any beam search was run on any of them. The measurement order is the point of this
protocol and is enforced by the commit history: the rank table and the predictions below are sealed
in one commit; the beam results arrive in a later one.

## 1. Why this experiment exists

Everything reported so far in this candidate — `STAGE_LINEAGE_FINDINGS.md`, `TULU3_REPLICATION.md`,
`DIRECTION_BREADTH.md` — establishes a **correlation**: across 22 measured systems,
Spearman(median `rank_stop`, empty rate @ beam 64) = −0.93. That number is worth very little on its
own, because in almost every one of those 22 cells the beam sweep was run *before or alongside* the
rank measurement. A correlation assembled that way cannot distinguish a law from a description.

Exactly one genuine out-of-sample prediction has been made so far (Olmo-3 base: `rank ≈ 532` ⇒
`b* ≈ 267`, predicted safe through beam 128 and exposed by beam 512; observed 0 % empty at 128,
8 % at 512, `RANK_ONSET_PREDICTION.md`). One success is an anecdote. This experiment turns the
correlation into a standing, falsifiable prediction on ten systems that have never been run through
a beam search in this project.

## 2. The rule being tested

For a system whose median step-0 stop rank is `r`:

- **Exposure threshold:** `b* = ceil(r / 2)`. HuggingFace beam search retains the top `2b`
  first-step candidates, so an immediate-stop hypothesis can enter the beam only when `b ≥ b*`.
  This half is algorithmic, not empirical, and is **not** what is under test.
- **What is under test** is that the *magnitude* of `r` — a quantity from one forward pass at
  position 0 — predicts the *behavioural* outcome of a search that has not been run, across systems
  differing in family, scale, tokenizer, stop-set cardinality and interface.

### 2.1 Calibration (fit on the 22 already-measured systems, not on the held-out set)

| stratum | predicted empty rate @ beam 64 | holds on calibration set |
|---|---|---|
| `r < 10` | **50 – 100 %** | 3/3 (observed 82.0 – 92.5 %) |
| `10 ≤ r < 128` | **5 – 60 %** | 7/7 (observed 6.0 – 41.5 %) |
| `r ≥ 128` | **0 – 8 %** | 12/12 (observed 0.0 – 6.0 %) |

These bands are declared now and are not adjustable after the held-out beams are run.

## 2.2 The held-out systems and their SEALED predictions

Measured with `src/stage_probe.py --beams ""` (step-0 only; no search was run). 400 segments,
frozen `newstest2019` En→De substrate, RAW scoring semantics throughout.

| # | system | interface | margin | median `rank_stop` | `b*` | **predicted empty @ b64** |
|---|---|---|---|---|---|---|
| 1 | `Qwen/Qwen2.5-7B-Instruct` | fewshot | +8.31 | **14** | 7 | **5 – 60 %** |
| 2 | `Qwen/Qwen2.5-7B` | fewshot | +6.76 | **24** | 12 | **5 – 60 %** |
| 3 | `mistralai/Mistral-7B-v0.3` | fewshot | +6.49 | **33** | 17 | **5 – 60 %** |
| 4 | `NousResearch/Meta-Llama-3.1-8B-Instruct` | fewshot | +8.20 | **43** | 22 | **5 – 60 %** |
| 5 | `microsoft/Phi-4-mini-instruct` | fewshot | +12.47 | **342** | 171 | **0 – 8 %** |
| 6 | `google/gemma-3-4b-it` | chat | +37.55 | **625** | 313 | **0 – 8 %** |
| 7 | `microsoft/Phi-4-mini-instruct` | chat | +16.73 | **1210** | 606 | **0 – 8 %** |
| 8 | `NousResearch/Meta-Llama-3.1-8B-Instruct` | chat | +20.00 | **23785** | 11893 | **0 – 8 %** |
| 9 | `Qwen/Qwen2.5-7B-Instruct` | chat | +25.87 | **46738** | 23369 | **0 – 8 %** |
| 10 | `Qwen/Qwen2.5-14B-Instruct` | chat | +35.74 | **54458** | 27229 | **0 – 8 %** |

Machine-readable copy: `results/heldout/E03_SEALED_PREDICTIONS.json`, sealed in the same commit.

**Set composition, recorded honestly.** The set was fixed as ten cells before measurement. One
(`HuggingFaceTB/SmolLM2-1.7B`, few-shot) failed to load — its cached tokenizer has no usable
sentencepiece vocabulary — and was replaced, **before any rank or beam was measured for either the
dropped or the replacing cell**, by `microsoft/Phi-4-mini-instruct` in the few-shot interface. That
substitution deliberately adds a third family to the in-format/out-of-format pairs tested by P3.
No further substitutions are permitted.

**Note on cell 5, which is the one that can hurt.** `Phi-4-mini-instruct` out of format has rank
342, i.e. the rule predicts it does **not** collapse. It is the only instruct checkpoint in this
project measured out of format that lands in the safe stratum, and it is therefore the cell most
likely to expose the rule as over-fit to the Olmo-3/Tülu-3 lineages. It is kept, and its prediction
is registered exactly as the rule assigns it.

## 3. Registered predictions

**P1 (primary, binary).** For each held-out system, the observed empty rate at beam 64 falls inside
the band its measured rank assigns it in §2.1. **Scored as 10 independent binary outcomes.**

**P2 (ordinal).** Spearman(measured rank, observed empty@64) over the ten held-out systems
`≤ −0.70`.

**P3 (the interesting cell).** The instruct checkpoints evaluated *out of format* (few-shot
interface) sit in a lower rank stratum than the same weights *in format* (chat), and collapse at
beam 64 while their chat cells do not. This is the Olmo-3/Tülu-3 format-keying claim, applied to
two model families that were not part of either lineage sweep.

**P4 (the second damage channel).** Among held-out systems with `r ≥ 128` that nonetheless lose
quality from beam 4 to beam 64, the loss is accompanied by a length ratio **> 1.3** (run-on), not by
empties — i.e. systems do not fail in a third, unpredicted way.

## 4. Falsifiers, declared in advance

- **P1 fails if 3 or more of the 10 systems** land outside their assigned band. Under the rule the
  bands are meant to be near-deterministic; 3 misses out of 10 means the bands are decoration.
  A single miss will be reported as a miss and the band's width revisited **in print**, not silently.
- **P2 fails if Spearman > −0.70.** The rule would then order systems no better than loosely.
- **P3 fails if any instruct model's few-shot cell has a *higher* rank than its chat cell**, which
  would make the format keying sign-unstable across families.
- **A directional failure that matters more than any of the above:** if a system with `r ≥ 128`
  shows ≥ 20 % empties at beam 64, the exposure argument itself is wrong, since such a system
  cannot admit an immediate-stop hypothesis into a width-64 beam at all. That outcome would
  indicate the instrument measures something other than what it claims, and would stop the
  candidate regardless of the other three predictions.

## 5. Stop rule

The beam sweep is run once, at beams 1, 16 and 64, 200 segments, RAW scoring (`length_penalty = 0`),
on the frozen `newstest2019` En→De substrate, with the same `src/stage_probe.py` used for every
other cell in this candidate. No system is added to or removed from the held-out set after this
document is committed. If a run fails for an infrastructural reason (OOM, missing weights) it is
reported as a failed cell, not replaced.

## 6. What a pass licenses, and what it does not

A pass licenses this sentence and no stronger one:

> The position-0 stop rank, measured before any search is run, predicts out of sample which systems
> lose outputs to beam search and roughly how many, across model families, scales and interfaces.

It does **not** license a claim about *why* a given checkpoint has the rank it has — that is what
`E02` addresses causally on trained-from-scratch conditions — nor about decoders other than
HuggingFace beam search. The latter is tested separately in E04 (vLLM cross-implementation check).
