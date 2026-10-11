# Reproducing L02 evidence

Run from this subproject directory. Do not overwrite historical runs. No command
below updates the outer repository or shared Python environments. Raw sources
and PDFs have URL/hash manifests; `data/SOURCE_ADJUDICATION.md` records rejected
payloads. A successful HTTP request alone does not admit a scientific dataset.

## Standard-library audits

Use `.venv/bin/python` (Python 3.12.3). Parser tests:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -v
```

Original SemEval extraction and E000 have their existing scripts and immutable
`runs/E000_20260908_v1` / `runs/E000_20260908_replay` snapshots. For the follow-up
audits, choose unused output directories:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/audit_ucca_resource.py --out runs/E000b_replay
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/audit_coreference.py --out runs/E000c_replay
```

UCCA expects the authors' repository under `data/raw/ucca_refined_2021`, checked
out at `432bac16527299b389a0f964e34abf040e000f7c`. E000b's report hashes every
data/XML file and E000c's report identifies the original SemEval XML hash.
Compare data artifacts byte-for-byte; run timestamps / execution-script hashes
can differ after adding a CLI output-directory option. The original executed
scripts remain with their original runs.

## E001a model diagnostic

Read its frozen `protocol.json`, `EXECUTION_NOTES.md` and `DECISION_CRITERIA.md`
first. The 42 sample IDs and 168 prompts per model are frozen and hash-checked.
Use the existing local `/home/xiang/miniconda3/envs/verl-clean/bin/python` with
torch 2.8.0+cu128, transformers 4.57.6, accelerate 1.13.0, tokenizers 0.22.2.
If recreating dependencies, create an environment **inside L02**. Do not install
into or repair a shared environment.

After checking current GPU occupancy, choose free devices and unique run IDs:

```sh
CUDA_VISIBLE_DEVICES=0 PYTHONDONTWRITEBYTECODE=1 /home/xiang/miniconda3/envs/verl-clean/bin/python -u scripts/run_interpretation_probe.py --model qwen32b --run-id E001a_qwen32b_replay --batch-size 2
CUDA_VISIBLE_DEVICES=2 PYTHONDONTWRITEBYTECODE=1 /home/xiang/miniconda3/envs/verl-clean/bin/python -u scripts/run_interpretation_probe.py --model mistral24b --run-id E001a_mistral24b_replay --batch-size 2
```

The script reads pinned local HF snapshots, redirects runtime caches into L02,
stores actual chat-template renderings, checks untruncated token lengths, and
writes raw A/B log probabilities plus environment/completion records. Both label
orders are averaged in DNI-versus-INI log-odds space. These scores are forced
label likelihoods, not calibrated probabilities or generated filler decisions.

Analyze only completed runs:

```sh
PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/analyze_interpretation_probe.py E001a_qwen32b_replay E001a_mistral24b_replay --out runs/E001a_replay_analysis.json
```

The analyzer rejects missing/duplicated jobs or changed frozen inputs. It reports
all items, pairs, label-order disagreements, context changes and non-A/B argmax
tokens. No sample-level confidence interval is presented as genre generalization.
Do not turn INI misclassification into a hallucination rate.

## E001b format validation

The same environment runs `scripts/run_native_label_validation.py` with `--model`
and `--run-id` arguments as above, after checking GPU occupancy. Its frozen
protocol is in `experiments/E001b_native_labels`. Do not rerun the preparation
script into the existing frozen directory. This exploratory check directly
generates DNI/INI with an eight-token ceiling and accepts only exact labels
apart from outer whitespace.

Analyze fresh completed runs with `scripts/analyze_native_labels.py RUN1 RUN2
--out runs/UNUSED_analysis.json`. Original four-run verification is retained in
`runs/verification_models_20260908.json`; its verifier refuses to overwrite it.
