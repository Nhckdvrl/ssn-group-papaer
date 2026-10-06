#!/usr/bin/env bash
# Source before network access: no proxy; Hugging Face assets use mirrors only.
unset HTTP_PROXY HTTPS_PROXY ALL_PROXY http_proxy https_proxy all_proxy
export NO_PROXY='*'
export no_proxy='*'
export HF_HUB_DISABLE_XET=1
export HF_ENDPOINT='https://hf-mirror.com'
export TOKENIZERS_PARALLELISM=false
export OMP_NUM_THREADS=8
export IIR_CACHE="${IIR_CACHE:-/data1/xiangding/work/incremental-interpretation-revision}"
export IIR_PYTHON="${IIR_PYTHON:-/data1/xiangding/env/pragmatic-inference-calibration/bin/python}"
