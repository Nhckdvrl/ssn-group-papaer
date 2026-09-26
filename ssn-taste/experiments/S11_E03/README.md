# S11 E03 — frozen interval-construction versus certification diagnostic

## Only question

Does the E01/E02 explicit-rule failure arise while deriving the compatible interval from a rounded report, or while certifying a threshold from an already given interval? This is a construct diagnostic, not a new S11 benchmark or an inequality-direction project. E01/E02 files stay untouched.

## Frozen generation and runtime

- Seed `110326`; sample **80** distinct one-decimal central values from `10..999` tenths after excluding every E01/E02 base value. `greater than` and `less than` alternate, 40 bases each.
- Every base has four items: evidence representation (`rounded_report`, `explicit_interval`) × precision (`coarse`, `fine`), for **320** prompts. Both representations use the same center, endpoint-derived interval, `x ± 0.02` threshold, inequality direction, and downstream sentence. Coarse analytic answer is No; fine answer is Yes.
- The rounded-report prompt is **byte-for-byte the E01/E02 explicit measurement prompt template**, with only new numbers. The interval prompt replaces the rounded-report evidence by an exact half-open interval. In both representations the downstream question is exactly: `Can this report alone certify that the true length is [greater/less] than [threshold] m?`
- All centers, reporting steps, intervals, thresholds, and labels are computed using `Decimal` and E01's frozen arithmetic helpers. Thresholds are strictly inside the coarse interval, outside the fine interval, and never on an endpoint. The interval is a direct mathematical consequence of the matching rounded report under the stated E01 rounding rule.
- Same cached model `Qwen/Qwen2.5-7B-Instruct`, bfloat16, greedy decoding, chat template, max four new tokens, exact E01 A/B parser; target runtime batch 16 with 2 GiB per-GPU model-placement cap. Record actual revision/settings. If runtime resource failure forces a change, archive partial output and rerun the full batch; do not pool versions.

Commit this README, generator/scorer, tests, and generated item pool before inference. Check disjointness, exact prompts, label derivation, balance, endpoints, pairing, parser, and manually inspect items. No natural condition, prompt sweep, CoT, second model, probe, or mechanism.

## Primary table and pair readout

For **each** representation, report exact correct/total separately for `greater` × `coarse`, `greater` × `fine`, `less` × `coarse`, and `less` × `fine`. For each representation × direction, count matched coarse/fine patterns `B/A` (correct No/Yes), `A/A`, `B/B`, `A/B` (reversed), and invalid. Never collapse directions into one accuracy. Also report parser invalids and exact item counts.

Descriptive high-competence gate: each direction × precision cell has at least **34/40** correct, and each direction has at least **30/40** correct `B/A` matched pairs. A direction that misses either criterion is not stable high performance. This is a construct-validity threshold, not a significance test.

## Interpretation frozen before outputs

- **A:** Explicit interval passes in both directions, while rounded report fails its matched-cell gate. Then downstream certification is feasible; the main failure is report → interval construction/use. S11 may continue only with a narrowed question about converting reported precision into constraints, without claiming selective invariance.
- **B:** Explicit interval fails, including the E01/E02 direction asymmetry or other broad errors. **KILL current S11 threshold route:** the readout cannot reliably measure measurement precision.
- **C:** Both representations pass. First audit exact wording and runtime against E01/E02; do not infer sudden precision understanding.
- **D:** Explicit interval passes only one direction. Treat as readout validity failure and **KILL current S11 threshold route**.

If neither A nor C cleanly applies, the validity result controls: interval failure in either direction stops this threshold route. Any new behavioral explanation requires a separate held-out experiment; E03 cannot both discover and validate it.
