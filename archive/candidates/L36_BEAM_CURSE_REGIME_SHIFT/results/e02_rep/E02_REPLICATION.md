# L36 E02 — replication across seeds, model families and scale

**Why this exists.** The E02 result (`../e02/E02_RESULTS.md`) was one seed, one base
(`Qwen/Qwen2.5-3B`), one training set. The effect sizes were enormous (ratios of 1e5–1e9), and a
huge effect from a single run is exactly what a reviewer asks to see repeated. This is the tier-1
gap closed: **two additional seeds** (item 1) and **two additional bases chosen to separate family
from scale** (item 2).

- `unsloth/Llama-3.2-3B` — different family, **same** scale as the registered base → isolates family
- `Qwen/Qwen2.5-0.5B` — same family, **6× smaller** → isolates scale

Everything else is identical to the registered protocol: same 2998 `newstest2018` pairs, same
steps/batch/optimizer, same single shared boundary token, the only difference between conditions
being the surface format the boundary was taught in. On the Llama base the boundary symbol is
`<|reserved_special_token_0|>` rather than `<|quad_start|>` — in both cases an unused special token
with a near-zero prior, so the "one shared boundary symbol, no cardinality confound" design carries
over unchanged.

## 1. The boundary placement profile — 15/15 conditions as registered

`p(<END> | prefix)` at the position where the reference translation ends, final checkpoint:

| base | seed | condition | format A | format B | ratio | verdict |
|---|---|---|---|---|---|---|
| `Qwen2.5-3B` | 20260914 | `A_ONLY` | **0.966** | 0.000 | 5.2e8 | trained format only |
| `Qwen2.5-3B` | 20260915 | `A_ONLY` | **0.965** | 0.000 | 6.3e8 | trained format only |
| `Qwen2.5-3B` | 20260916 | `A_ONLY` | **0.966** | 0.000 | 6.3e8 | trained format only |
| `Qwen2.5-3B` | 20260914 | `B_ONLY` | 0.000 | **0.962** | 4.5e−9 | **reversed** |
| `Qwen2.5-3B` | 20260915 | `B_ONLY` | 0.000 | **0.960** | 5.0e−9 | **reversed** |
| `Qwen2.5-3B` | 20260916 | `B_ONLY` | 0.000 | **0.964** | 2.4e−9 | **reversed** |
| `Qwen2.5-3B` | ×3 seeds | `MIXED` | 0.961–0.962 | 0.960–0.963 | 1.0 | both |
| **`Llama-3.2-3B`** | 20260914 | `A_ONLY` | **0.952** | 0.000 | 2.0e4 | trained format only |
| **`Llama-3.2-3B`** | 20260914 | `B_ONLY` | 0.000 | **0.958** | 5.8e−7 | **reversed** |
| **`Llama-3.2-3B`** | 20260914 | `MIXED` | 0.947 | 0.946 | 1.0 | both |
| **`Qwen2.5-0.5B`** | 20260914 | `A_ONLY` | **0.902** | 0.000 | 2.9e6 | trained format only |
| **`Qwen2.5-0.5B`** | 20260914 | `B_ONLY` | 0.000 | **0.919** | 4.2e−7 | **reversed** |
| **`Qwen2.5-0.5B`** | 20260914 | `MIXED` | 0.877 | 0.878 | 1.0 | both |

**P1′ (sign reversal) and P2 (mixed rescues both) hold in all 15 conditions.** Across three seeds
the Qwen2.5-3B numbers agree to three decimals. Changing family at fixed scale, and changing scale
6× at fixed family, both leave the qualitative result untouched — only the ratio's magnitude moves
(1e4 to 1e9), which is the same "direction stable, magnitude lineage-specific" pattern the Tülu-3
replication found in off-the-shelf checkpoints.

## 2. The behavioural signature is run-on, not emptying — 15/15

Beam 64, RAW scoring, final checkpoint:

| base | condition | format A | format B |
|---|---|---|---|
| `Llama-3.2-3B` | `A_ONLY` | 0 % empty, lenR **0.96**, BLEU 41.3 | 0 % empty, lenR **3.81**, BLEU 7.6 |
| `Llama-3.2-3B` | `B_ONLY` | 0 % empty, lenR **3.97**, BLEU 2.9 | 0 % empty, lenR **0.96**, BLEU 42.3 |
| `Llama-3.2-3B` | `MIXED` | 0 %, lenR 0.98, BLEU 41.9 | 0 %, lenR 0.96, BLEU 41.9 |
| `Qwen2.5-0.5B` | `A_ONLY` | 0 %, lenR **0.92**, BLEU 20.9 | 0 %, lenR **3.36**, BLEU 1.7 |
| `Qwen2.5-0.5B` | `B_ONLY` | 0 %, lenR **4.70**, BLEU 1.3 | 0 %, lenR **0.92**, BLEU 21.2 |
| `Qwen2.5-0.5B` | `MIXED` | 0 %, lenR 0.93, BLEU 21.1 | 0 %, lenR 0.91, BLEU 21.5 |
| `Qwen2.5-3B` (×3 seeds) | `A_ONLY` | 0 %, lenR 0.95–0.96, BLEU 38.3–39.7 | 0 %, lenR **4.05**, BLEU 5.1–5.8 |
| `Qwen2.5-3B` (×3 seeds) | `B_ONLY` | 0 %, lenR **4.17–4.29**, BLEU 6.0–7.1 | 0 %, lenR 0.94–0.96, BLEU 35.3–39.4 |
| `Qwen2.5-3B` (×3 seeds) | `MIXED` | 0 %, lenR 0.96, BLEU 38.3–39.6 | 0 %, lenR 0.94–0.97, BLEU 34.3–37.5 |

Out of format these models do not stop — length ratio 3.4 to 4.7 — and the empty rate stays at
exactly 0 % everywhere. This is E02's amended P3 replicating on two more bases and two more seeds:
a model that never learned the boundary in a format fails there by **running on**, which is the
second damage channel, not the termination-collapse channel. `MIXED` removes the effect in both
formats at no cost in quality.

## 3. Caveats

- One seed each for the two new bases; the three-seed evidence is on the registered base only.
  What the new bases establish is family- and scale-invariance of the qualitative result, not a
  variance estimate for them.
- `Qwen2.5-0.5B` translates much worse in absolute terms (BLEU ~21 vs ~39). The boundary result is
  unaffected, but its quality numbers should not be compared across bases.
- The originally planned second base (`NousResearch/Llama-3.2-1B`) had only a config and tokenizer
  in the local cache and no weight files; all three of its runs failed to load. It was replaced by
  the two bases above, which is a strictly better design because it separates family from scale
  rather than varying both at once. No result from the failed runs exists or is reported.
