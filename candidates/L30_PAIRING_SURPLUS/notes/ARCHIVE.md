# L30 — Archive record

**Verdict: `NO-GO / ARCHIVED`. 2026-09-13.**

Not a novelty kill on the original question, and not a "the result was
unfavourable" kill. E01 ran cleanly and produced a trustworthy answer. The route
stops for three independent reasons, any one of which would be sufficient.

---

## 1. The original estimand is not measurable, and the headroom is now known

`Delta_pair = P - D_mask = +1.85 pp [-1.79, +5.42]`. Of that 7.58 pp interval,
only ~1.6 pp is training-seed variance; ~6 pp is the 541-prompt IFEval sample.
More seeds cannot fix it.

The decisive number is the untuned baseline, measured last:

| | strict prompt | strict instruction |
|---|---|---|
| untuned Gemma-2-2B | 19.96 | 32.85 |
| P (correct pairing) | 23.29 | 33.93 |

**52k Alpaca pairs buy +3.3 pp prompt-level and +1.1 pp instruction-level over no
training at all.** A sub-effect of instruction tuning cannot be resolved inside a
positive control with ~1 pp of dynamic range. This is the L19 lesson, reached
from the evaluation side.

## 2. The instrument is confounded by termination, not just noisy

Per-constraint-family strict accuracy:

| family | n | base | P | D_mask | S |
|---|---|---|---|---|---|
| language | 31 | **0.0** | 64.5 | 51.6 | 0.0 |
| startend | 67 | **0.0** | 40.3 | 43.3 | 0.0 |
| punctuation | 66 | **50.0** | 21.2 | 43.9 | 10.6 |
| length_constraints | 143 | 33.6 | 30.1 | 30.8 | 30.8 |
| detectable_format | 157 | 35.7 | 36.3 | 34.4 | 0.0 |

Median response length: base 4018 chars, P 696, D_mask 441, S 241.

The base model's 32.85% is an artifact of never terminating: it scores **0.0%**
on exactly the families that require obeying and stopping (`language`,
`startend`) and beats the tuned model on families that verbose text satisfies
incidentally (`punctuation`). Aggregate IFEval at this scale mixes
instruction-following with response-length policy, and every arm-wise contrast
sits on top of that confound. S's 8.32 is partly "it emits 241-char canned
text", not purely "it cannot follow constraints".

A further consequence: the tuning gain is concentrated in termination and global
form (`language` 0→64.5, `startend` 0→40.3), which is precisely what Hewitt et
al.'s hand-written rule-based adapter already demonstrates — one of their three
rules is "slowly increase the probability of ending the sequence". That
inference is owned.

## 3. The proposed pivot does not clear the novelty bar

The pivot was: *post-training damage comes from contradicted supervision, not
missing supervision* (S collapses to 6-11 distinct responses in every seed;
D_mask, equally correspondence-free, keeps 537-539).

Honest reviewer compression, and it holds:

> In D_mask the model cannot see the instruction, so no gradient ever pushes it
> away from its pretrained conditional behaviour. In S the model is explicitly
> trained to make its prediction independent of a *visible* instruction. Of
> course one preserves prompt conditioning and the other destroys it. That is
> what the objective says.

The D_mask control makes the result **clean**; it does not make it
**surprising**. The inference is available a priori.

Both candidate conditional laws also land in occupied territory:

- damage scales with pretrained association → the MAIN / FedDQC intuition;
- a small fraction of decorrelated data causes disproportionate global collapse
  → the threshold effect the data-poisoning literature already owns.

Under `RESEARCH_TOPIC_SELECTION.md` this is **INSUFFICIENT CONTRIBUTION**, not
unresolved novelty. "The exact sentence has not appeared" is not the bar.

## 4. What was learned that is worth keeping

- **A budget-matched correspondence-free control is constructible and matters.**
  The two mother papers do not implement the same control — Hewitt et al. empty
  the instruction string but keep the `<|user|>` scaffolding, An et al. drop the
  user turn — so "RT" is not a well-defined condition. Against a
  position-and-budget-matched control, D_rt differs by +1.91 pp [-1.66, +5.42].
  Anyone quantifying an IT−RT gap should know serialisation is inside it.
- **IFEval aggregate scores for non-terminating base models are not comparable
  to those of tuned models.** The family-level table above is the evidence.
- **Prior "input-output mapping matters little" results are all about
  demonstrations**, never the supervised pair (verified from source: Kung & Peng
  corrupt in-prompt examples while the supervised instance stays correct; Hewitt
  and An have no mismatched-pair arm). That gap is real — it is just not worth a
  Main paper on its own.

## 5. Reusable assets

All under `candidates/L30_PAIRING_SURPLUS/`, all working and validated:

- `src/train.py` — matched P/S/D_mask/D_rt trainer, hand-rolled LoRA, custom 4D
  attention masking that passes a zero-leakage test.
- `src/test_masks.py` — the construct-validity suite, including two documented
  failed test designs that were reference artifacts rather than leaks.
- `src/evaluate.py` + `src/instruction_following_eval/` — greedy IFEval with the
  unmodified Google Research verifier.
- `src/summarize.py` — prompt-clustered, seed-resampled bootstrap.
- `src/eval_remote.sh`, `src/status.sh` — multi-node evaluation and health checks.
- `results/pool/` — the frozen 51,758-pair pool and the S derangement.
- `results/evals/` — 31 evaluation runs; `results/E01_summary_ep3.json`.

Adapters under `results/runs/` are regenerable and excluded from git.

## 6. What would justify reopening

New evidence that the wrong-vs-absent asymmetry is **not** predictable from the
objective — for example, a regime where decorrelated supervision *fails* to
destroy prompt conditioning, or where absent supervision destroys it. That would
turn a corollary of gradient descent into a real conditional law.

Reopening would also need an instruction-following measurement that is not
confounded by termination and that has enough dynamic range for instruction
tuning itself to move it by more than a few points at the model scale used.
