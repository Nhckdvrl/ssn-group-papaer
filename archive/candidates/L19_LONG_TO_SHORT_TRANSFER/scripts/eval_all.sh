#!/usr/bin/env bash
# Evaluate checkpoints on the parent's short-context protocol, one model per GPU,
# up to 4 concurrently. vLLM backend; falls back to the HF backend if .venv-eval
# is not present.
#
# usage:  scripts/eval_all.sh results/sft/PC-UC-UC-n2000 results/sft/PC-UC-CHATQA2-n2000
set -uo pipefail
cd "$(dirname "$0")/.."
EVALPY=.venv-eval/bin/python
[ -x "$EVALPY" ] || EVALPY=.venv/bin/python
BACKEND=vllm
[ "$EVALPY" = ".venv/bin/python" ] && BACKEND=hf
# the venv is invoked by absolute path, so its bin/ is not on PATH; vLLM shells out to ninja
export PATH="$PWD/$(dirname "$EVALPY"):$PATH"
mkdir -p logs results/eval

one () {  # one <gpu> <ckpt>
  local gpu=$1 ckpt=$2 tag; tag=$(basename "$ckpt")
  for spec in "mmlu 0 -" "lambada_openai 0 -" "gsm8k_cot 4 -" "bbh_cot_fewshot 3 100"; do
    set -- $spec; local task=$1 shots=$2 lim=$3
    local outdir="results/eval/$tag/$task"
    [ -d "$outdir" ] && { echo "skip $tag/$task"; continue; }
    local args=(--model "$BACKEND" --tasks "$task" --num_fewshot "$shots"
                --output_path "$outdir" --seed 0)
    if [ "$BACKEND" = vllm ]; then
      args+=(--model_args "pretrained=$ckpt,dtype=bfloat16,gpu_memory_utilization=0.85,max_model_len=8192,tensor_parallel_size=1" --batch_size auto)
    else
      args+=(--model_args "pretrained=$ckpt,dtype=bfloat16,attn_implementation=sdpa" --batch_size 8)
    fi
    [ "$lim" != "-" ] && args+=(--limit "$lim")
    CUDA_VISIBLE_DEVICES=$gpu $EVALPY -m lm_eval "${args[@]}" \
      >> "logs/eval_$tag.log" 2>&1 || echo "FAILED $tag/$task (see logs/eval_$tag.log)"
  done
  echo "EVAL_DONE $tag"
}

i=${GPU0:-0}
for ckpt in "$@"; do
  one $((i % 4)) "$ckpt" &
  i=$((i+1))
done
wait
echo ALL_EVAL_DONE
