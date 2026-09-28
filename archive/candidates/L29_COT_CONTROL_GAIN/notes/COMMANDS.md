# Executed commands and artifact locations

Repository sync: `git fetch origin main && git switch main && git merge --ff-only origin/main`
Starting main: `91fa4bb` (2026-09-12). No pre-existing uncommitted work.

All relative paths below are from `/home/xiang/ssn-group-papaer`.

Preparation:
```sh
python3 candidates/L29_COT_CONTROL_GAIN/src/prepare.py
```
The initial serial-per-file download was interrupted after preserving partial files;
resume/acceleration command:
```sh
python3 candidates/L29_COT_CONTROL_GAIN/src/download_ranges.py
```
Logs: `candidates/L29_COT_CONTROL_GAIN/results/{prepare,download_ranges}.log`.
Pinned weights: `/home/xiang/.cache/l29/step_{0100,1400,2800}` (outside git).
A `L29_DOWNLOAD_COMPLETE` marker is written only when the downloader has finished.

Natural-state jobs (each waits for download completion and then checks GPU availability):
```sh
ssh fvcrc13 '/home/xiang/ssn-group-papaer/candidates/L29_COT_CONTROL_GAIN/src/launch_when_ready.sh step_0100 0 natural'
ssh fvcrc13 '/home/xiang/ssn-group-papaer/candidates/L29_COT_CONTROL_GAIN/src/launch_when_ready.sh step_1400 2 natural'
ssh fvcrc13 '/home/xiang/ssn-group-papaer/candidates/L29_COT_CONTROL_GAIN/src/launch_when_ready.sh step_2800 3 natural'
```
Actual runs redirect stdout/stderr to candidate `results/logs/<step>_natural.log`.
Each job sets CUDA_VISIBLE_DEVICES to ONE named card, uses the existing
`/home/xiang/interesting/.venv-a100/bin/python`, and has a 1200-second process timeout.
Raw phase files: `candidates/L29_COT_CONTROL_GAIN/results/raw/<step>_<phase>.json`.
Each records software versions, code hashes, model revision, seeds, prompt tokens,
continuation tokens and intervention text. Partial outputs explicitly say complete=false.

Software checks:
```sh
python3 -m unittest discover -s candidates/L29_COT_CONTROL_GAIN/src -p 'test_*.py'
python3 -m py_compile candidates/L29_COT_CONTROL_GAIN/src/*.py
```
The instrument tests validate real boundary/eligibility bugs; they are not model evidence.
No score/rollout or substantive-pilot result is implied merely by these commands existing.

## Commands actually used for the completed audit

The shared filesystem proved unsuitable for model loading, so immutable checkpoints
were staged and hash-verified on node-local storage under
`/tmp/xiang-l29/checkpoints/<step>`. The existing local virtual environment was reused:
`/home/xiang/interesting/.venv-a100`. GPU jobs used fvcrc13 GPUs 0/1 and fvcrc15 GPU 3;
at most three cards ran concurrently.

Representative natural and score commands:

```sh
ssh fvcrc13 'cd /home/xiang/ssn-group-papaer && export CUDA_VISIBLE_DEVICES=0 L29_MODEL_ROOT=/tmp/xiang-l29/checkpoints HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=4; timeout 1200 /home/xiang/interesting/.venv-a100/bin/python -u candidates/L29_COT_CONTROL_GAIN/src/run_audit.py --step step_2800 --phase natural --batch-size 8'
ssh fvcrc13 'cd /home/xiang/ssn-group-papaer && export CUDA_VISIBLE_DEVICES=0 L29_MODEL_ROOT=/tmp/xiang-l29/checkpoints HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=4; timeout 1200 /home/xiang/interesting/.venv-a100/bin/python -u candidates/L29_COT_CONTROL_GAIN/src/run_audit.py --step step_0100 --phase score --batch-size 8'
```

Support admission and the primary two-arm rollout:

```sh
/home/xiang/interesting/.venv-a100/bin/python candidates/L29_COT_CONTROL_GAIN/src/summarize_audit.py --phase support
ssh fvcrc13 'cd /home/xiang/ssn-group-papaer && export CUDA_VISIBLE_DEVICES=0 L29_MODEL_ROOT=/tmp/xiang-l29/checkpoints HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=4; timeout 1200 /home/xiang/interesting/.venv-a100/bin/python -u candidates/L29_COT_CONTROL_GAIN/src/run_audit.py --step step_0100 --phase rollout --batch-size 8'
/home/xiang/interesting/.venv-a100/bin/python candidates/L29_COT_CONTROL_GAIN/src/summarize_audit.py --phase effects
```

The structural and anaphoric control audits used the same frozen states and seeds:

```sh
python candidates/L29_COT_CONTROL_GAIN/src/run_audit.py --step STEP --phase rollout --batch-size 8 --arms structural --output-tag structural
python candidates/L29_COT_CONTROL_GAIN/src/run_audit.py --step STEP --phase rollout --batch-size 8 --arms anaphoric_neutral anaphoric_active --output-tag anaphoric
python candidates/L29_COT_CONTROL_GAIN/src/summarize_factorial.py
python candidates/L29_COT_CONTROL_GAIN/src/summarize_anaphoric.py
```

All `python` commands above were executed with the same virtual-environment interpreter;
`STEP` was replaced by step 0100, 1400, or 2800 on the node holding that checkpoint.

## E01R final instrument audit

The split and pre-outcome gate were generated and frozen with:

```sh
/home/xiang/interesting/.venv-a100/bin/python candidates/L29_COT_CONTROL_GAIN/src/prepare_e01r.py --csv /tmp/l29_e01r_mmlu.csv
/home/xiang/interesting/.venv-a100/bin/python -m unittest discover -s candidates/L29_COT_CONTROL_GAIN/src -p 'test_*.py'
```

Only step 100 was authorized and run, on fvcrc13 GPU 0:

```sh
ssh fvcrc13 'cd /home/xiang/ssn-group-papaer && export CUDA_VISIBLE_DEVICES=0 L29_MODEL_ROOT=/tmp/xiang-l29/checkpoints HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=4; timeout 1200 /home/xiang/interesting/.venv-a100/bin/python -u candidates/L29_COT_CONTROL_GAIN/src/run_e01r.py --step step_0100 --phase natural --batch-size 8'
ssh fvcrc13 'cd /home/xiang/ssn-group-papaer && export CUDA_VISIBLE_DEVICES=0 L29_MODEL_ROOT=/tmp/xiang-l29/checkpoints HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=4; timeout 1200 /home/xiang/interesting/.venv-a100/bin/python -u candidates/L29_COT_CONTROL_GAIN/src/run_e01r.py --step step_0100 --phase rollout --batch-size 8'
/home/xiang/interesting/.venv-a100/bin/python candidates/L29_COT_CONTROL_GAIN/src/summarize_e01r_dev.py
```

The runner rejects any E01R step other than `step_0100`. Because the frozen gate failed,
no command was run for step 1400, step 2800, or the confirmatory split.
