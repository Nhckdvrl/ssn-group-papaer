# Same runtime as CT05 (openslime python + transformers 5.12.1 vendored from fgvd).
export CT09=/home/xiang/ssn-group-papaer/candidates/CT09_CROSS_CHANNEL_HANDOFF
mkdir -p $CT09/vendor && ln -sfn /home/xiang/miniconda3/envs/fgvd/lib/python3.12/site-packages/transformers $CT09/vendor/transformers
export PYTHONPATH=$CT09/vendor:$CT09/src
export PY=/home/xiang/miniconda3/envs/openslime/bin/python
export HF_HUB_OFFLINE=1
export Q35_4B=$(ls -d /home/xiang/.cache/huggingface/hub/models--Qwen--Qwen3.5-4B/snapshots/*/)
export Q35_9B=$(ls -d /home/xiang/.cache/huggingface/hub/models--Qwen--Qwen3.5-9B/snapshots/*/)
