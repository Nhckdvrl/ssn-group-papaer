# L16 — Experiment Ledger

**Status:** no model output has been inspected for L16 at registration time.  
**Authorization:** E01 + conditional E02 only; see `PILOT_CARD.md`.

---

## Frozen setup — 2026-09-11

### Models

- Qwen3-32B
- Mistral-Small-24B

### Primary inference

- normal reasoning / CoT allowed
- greedy
- seed 0
- max_tokens 1024

### Primary data

- 48 base scenarios
- 4 domains × 12 bases
- 9 mutually exclusive/exhaustive atomic outcomes per base
- target H1 fixed
- conditions: FLAT / M2 / M3a / M3b / M9
- E01 total = 240 cells/model = 480 cells across two models

### Primary contrast

`Delta29 = P(H1|M2) - P(H1|M9)`

### Primary E01 survival gate

Both model families must satisfy:

- mean `Delta29 >= .05`
- scenario-bootstrap 95% CI lower bound > 0
- `Delta29 > 0` in >= .65 of scenarios
- positive mean `Delta29` in >= 3/4 domains
- parse rate >= .95

See `PILOT_CARD.md` for mechanism diagnostics and E02 gates.

---

## Smoke record

**Not yet run.**

When run, record:

- date/time;
- commit SHA of code/data;
- exact model checkpoint/revision;
- serving stack/version;
- GPU assignment;
- number of cells;
- parser/truncation failures;
- any pipeline-only change made before full E01.

No scientific threshold or metric may be changed in response to smoke outputs.

---

## E01 record

**Not yet run.**

Required artifacts:

- immutable stimulus JSONL/CSV with scenario IDs and partition maps;
- validation report proving atom identity/order and non-partition hash equality;
- raw generations;
- parsed probabilities;
- scenario-level summary table;
- bootstrap output;
- `summary.md` or `PILOT_REPORT.md` containing the kill/survive decision.

---

## E02 record

**Not yet run; conditional on E01 gate.**

If E01 fails, record `NOT RUN — prerequisite failed` and archive the route. Do not run E02 to search for a rescue.

---

# Mutation log

None at registration.

Any material change to RQ, estimand, central claim, mechanism, reviewer one-line takeaway, gold, or primary operation must be recorded here **before further compute** and requires return to selection / fresh ownership audit.
