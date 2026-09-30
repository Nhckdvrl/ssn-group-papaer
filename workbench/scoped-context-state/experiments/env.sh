# fgvd env (torch cu130 + vllm 0.23) on Blackwell hosts without nvcc: no FlashInfer JIT sampler.
export HF_HUB_OFFLINE=1
export VLLM_USE_FLASHINFER_SAMPLER=0
export LD_LIBRARY_PATH=$HOME/miniconda3/envs/fgvd/lib/python3.12/site-packages/nvidia/cu13/lib:$LD_LIBRARY_PATH
export PY=$HOME/miniconda3/envs/fgvd/bin/python
