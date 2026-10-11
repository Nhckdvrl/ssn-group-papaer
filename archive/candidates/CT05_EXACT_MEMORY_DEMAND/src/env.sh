# Runtime: openslime env (torch 2.9.1+cu129 works on driver 550 A100s) + transformers 5.12.1
# vendored from the fgvd env (tf 5.3 in openslime ignores cached GDN state for multi-token chunks).
export CT05=/home/xiang/ssn-group-papaer/candidates/CT05_EXACT_MEMORY_DEMAND
mkdir -p $CT05/vendor && ln -sfn /home/xiang/miniconda3/envs/fgvd/lib/python3.12/site-packages/transformers $CT05/vendor/transformers
export PYTHONPATH=$CT05/vendor:$CT05/src
export PY=/home/xiang/miniconda3/envs/openslime/bin/python
export HF_HUB_OFFLINE=1
export Q35_4B=$(ls -d /home/xiang/.cache/huggingface/hub/models--Qwen--Qwen3.5-4B/snapshots/*/)
export Q35_9B=$(ls -d /home/xiang/.cache/huggingface/hub/models--Qwen--Qwen3.5-9B/snapshots/*/)
export Q3_8B=$(ls -d /home/xiang/.cache/huggingface/hub/models--Qwen--Qwen3-8B/snapshots/*/)
export Q3_4B=$(ls -d /home/xiang/.cache/huggingface/hub/models--Qwen--Qwen3-4B/snapshots/*/)
