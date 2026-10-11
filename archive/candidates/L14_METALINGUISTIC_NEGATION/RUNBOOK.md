# L14 — Pilot Runbook

Run nothing until `data/pilot_items.jsonl` passes the human-audit contract.

## 1. Environment

The scorer requires:

```bash
python -c "import torch, transformers; print(torch.__version__, transformers.__version__)"
```

Use the existing local environment/model cache where possible. Do not download a model zoo for this pilot.

## 2. Freeze two model families

Choose two capable open instruction models from different families that are already locally available. Record exact local/HF revision, chat template, torch/transformers versions, and GPU environment in the result directory before inference.

Do not add a third family unless the two-family result is genuinely decision-ambiguous.

## 3. Validate data mechanically

The runner refuses any row without `human_validated: true` unless the explicit exploratory override is used.

Expected conditions per base:

```text
POS
DN
MN
PARAPHRASE
```

Check base completeness before inference.

## 4. Run E01 + E02 together

`run_pilot.py` scores both baseline and the frozen prior-work warning intervention in one run, using two A/B label mappings and averaging back into semantic YES/NO probabilities.

Example:

```bash
cd candidates/L14_METALINGUISTIC_NEGATION

python src/run_pilot.py \
  --model /path/to/model_family_1 \
  --data data/pilot_items.jsonl \
  --out results/e01_e02/model1.jsonl

python src/run_pilot.py \
  --model /path/to/model_family_2 \
  --data data/pilot_items.jsonl \
  --out results/e01_e02/model2.jsonl
```

For pipeline debugging only, before human validation:

```bash
python src/run_pilot.py ... --allow-unvalidated-exploratory
```

Such numbers are not evidence and must not be promoted into a claim.

## 5. Analyze

```bash
python scripts/analyze_pilot.py \
  results/e01_e02/model1.jsonl \
  results/e01_e02/model2.jsonl \
  --bootstrap 10000 \
  --out results/e01_e02/summary.json
```

The independent bootstrap unit is `base_id`.

Read these quantities first:

- baseline DN probability of the correct answer;
- baseline MN probability of the correct answer;
- `delta_dn` under the warning;
- `delta_mn` under the warning;
- the same results after removing `scalar_diagnostic` items.

The analysis conditions on passing baseline POS + PARAPHRASE controls before estimating the load-bearing DN/MN quantities.

## 6. Decision, before any new experiment

Apply `PILOT_CARD.md` literally.

Especially:

- **do not** respond to a null with layers/probes/new prompts;
- **do not** let scalar items carry the effect;
- **do not** expand from a positive result without re-running the ownership audit on the exact winning claim;
- **do not** run E03 unless E01/E02 leave a live target-selection question.

## 7. Result record

For each run preserve:

- exact command;
- model/revision;
- prompt template;
- data hash;
- environment versions;
- raw JSONL;
- analysis JSON;
- human-audit version/hash;
- current paper-identity / novelty decision.

A statistically clean result is not automatically a GO. The next state after a surviving E01/E02 is **RE-SELECTION**.
