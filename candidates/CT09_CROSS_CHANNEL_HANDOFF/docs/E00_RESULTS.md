# CT09 E00 — Results and Verdict (2026-09-27)

Protocol: `E00_PROTOCOL.md`, frozen and committed (`214e3c4`) before the run.
Raw: `results/e00/s{0,1,2}.jsonl` (400 items, Qwen3.5-4B). Readout: `results/e00_summary.txt`
(`src/analyze_e00.py`). Launch: `logs/E00_LAUNCH.md`.

## Verdict: **KILL** (by the frozen gates)

| condition | mean Δ (nats) | 95% CI | both signs correct |
|---|---|---|---|
| FULL_SWAP (KV kept, donor state) | 16.36 | [16.17, 16.56] | 1.00 |
| **POST** (KV read during query, then all KV dropped) | **1.79** | [1.73, 1.86] | 0.47 |
| NOREAD (other key queried, then dropped) | 0.03 | [0.02, 0.04] | 0.02 |
| RECENT (value written as text ~20 tokens before, no KV) | 0.02 | [0.00, 0.03] | 0.02 |
| RECONLY (native state, no KV; 2609.04434 rec-only) | 0.05 | [0.04, 0.06] | 0.02 |
| PRE (donor state, no KV) | 0 exactly | | |
| E_POST (cut before `Answer:`) / E_FULL_SWAP | 0.66 / 15.88 | | 0.20 / 1.00 |

- **H = 0.108 [0.104, 0.112]** (native-state version 0.112). Stable across target position
  (0.098 / 0.109 / 0.117 by third of the list). Early cut: 0.041.
- Gate 1 (instrument validity) **fails as written**: RECENT / FULL_SWAP = 0.001 < 0.3.
- Gate 2 **fails**: H < 0.20. The frozen rule sends the partial band 0.05 ≤ H < 0.20 to KILL.

## Reading (no new runs)

1. The Gate-1 premise was wrong, and this is recorded rather than used as an escape. The gate
   assumed that "the probe can read recurrence" would show up as RECENT > 0. It did not, yet POST
   is read at 1.8 nats, 60× NOREAD. The instrument does read the recurrent channel. What it cannot
   read is a value that recurrence took in *as text*. The verdict rests on Gate 2, which fails
   on its own.
2. The effect is real and retrieval-specific, but partial. After one lookup, the recurrent channel
   holds about a tenth of attention's log-odds for the retrieved value, and it gets both A/B signs
   right in 47% of items. The same value presented as text ~20 tokens earlier leaves ≈ 0. An
   unrelated read leaves ≈ 0. Most of the transfer happens at the answer position
   (early cut 0.04 vs late 0.11).
3. Unresolved, and counting against the topic under the stop-loss rule: the carrier could be the
   GDN short-conv window (kernel 4, which holds the last three query positions' layer inputs,
   including the answer-position hidden state) rather than the matrix state. Only the matrix state
   would count as "recurrence remembers". Separating the two needs a new run, which is not taken.
   Nor is any of the following: another probe wording, Qwen3.5-9B, Falcon-H1, longer
   probe-to-query gaps.
