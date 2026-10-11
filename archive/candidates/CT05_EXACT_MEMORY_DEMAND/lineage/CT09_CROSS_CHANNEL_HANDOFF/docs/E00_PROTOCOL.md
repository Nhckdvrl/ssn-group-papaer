# CT09 E00 — Post-retrieval handoff (frozen 2026-09-27, before any contrast was computed)

## Model and data

- Qwen3.5-4B (discovery). Falcon-H1-3B replication is **not** part of E00 (not cached; needs its
  own authorization only if E00 passes).
- 400 items (`src/prep.py`, seed 20260927). Plain text, no chat template:
  `INTRO + 40 lines "KEY: VAL\n"`, N ≈ 300 tokens. Target line at index 2–37.
  Contexts A / B / 0 differ only in the target value (vA, vB, donor v0; random 4-letter
  pseudo-words of equal token length). `X_recent` moves the target line to the end.
- Query (late cut, primary): `\nQuestion: What is the secret value of KEY?\nAnswer:`.
  The chunk ends at the position whose next token would be the answer, so the lookup has been
  performed. **No value token is generated or teacher-forced before the cut.**
- Probe (identical in every condition): ` The secret value of KEY is` + teacher-forced value.
- Early cut (descriptive): query ends at `?\n`, probe `Answer:`.

## Conditions (all rows of one item in one batch; X ∈ {A, B}; each scored for vA and vB)

| code | KV during query | GDN state before query | KV at probe |
|---|---|---|---|
| FULL_SWAP | context X | donor 0 | kept |
| **POST** (primary) | context X | donor 0 | **all dropped** (context + query-local) |
| NOREAD | context X, but the query asks for another key | donor 0 | dropped |
| PRE | hidden | donor 0 | dropped (A/B identical by construction; Δ must be 0) |
| RECENT | hidden | native X_recent (value written as text ~20 tokens earlier) | dropped |
| FULL_NAT, POST_NAT, RECONLY | as above but native GDN state | | descriptive |
| E_FULL_SWAP, E_POST | early cut | donor 0 | kept / dropped |

"Dropped" hides columns [4, t) in every full-attention layer; the first 4 columns are identical
template tokens in all contexts.

## Estimand

`m_c(X) = log P(vA | ·) − log P(vB | ·)` (summed over value tokens);
`Δ_c = ½ [m_c(A) − m_c(B)]` per item.

**H = (Δ_POST − Δ_NOREAD) / (Δ_FULL_SWAP − Δ_NOREAD)**, ratio of item means, 95% item bootstrap
(10k). Also reported: pairwise accuracy (both m signs correct), H_nat, Δ_POST / Δ_RECENT,
early-cut ratio, split by target position.

## Gates (mechanical)

1. Instrument validity: Δ_FULL_SWAP ≥ 5 nats with accuracy ≥ 0.9, **and**
   Δ_RECENT / Δ_FULL_SWAP ≥ 0.3 (the probe can read a value out of the recurrent state when
   text put it there). PRE must give Δ = 0 exactly (else a bug). If validity fails → KILL as
   uninterpretable; the probe is not repaired.
2. **PASS** iff H ≥ 0.20 and the CI lower bound ≥ 0.10. Then stop and report; E01
   (Falcon-H1 replication + a natural recall→state-tracking task) needs explicit authorization.
3. Anything else → **KILL**, including a partial 0.05 ≤ H < 0.20. No second probe wording, no
   9B, no Falcon, no training "to teach handoff" (that is CT06 again).

## Disclosure

Before freezing, `src/smoke.py` was run on items 0–3: cached-chunk log P(vA) matched a plain
forward within 0.04 nats, and the model greedily answers correctly (FULL). The smoke also printed
the POST_NAT-style row for vA only (≈ −13 to −17 nats, vs ≈ −1 with KV). vB was not scored, so no
contrast was seen, but this is a hint towards a small H and is recorded here.
