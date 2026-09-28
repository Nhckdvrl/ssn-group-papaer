#!/bin/bash
cd /home/xiang/ssn-group-papaer/explorations/shape_olmo
: > logs/jobs_ctx.txt
for m in "ssm state-spaces/transformerpp-2.7b PPT" "ssm state-spaces/mamba2attn-2.7b PPH" "ssm state-spaces/mamba2-2.7b PPR" "hf EleutherAI/pythia-1.4b PY14" "hf EleutherAI/pythia-2.8b PY28" "ssm state-spaces/mamba2-1.3b M2_13"; do
  set -- $m
  printf 'CX_%s\tHF_HUB_OFFLINE=1 SHAPE_PACK=neox2k_ PYTHONPATH=vendor/mamba:vendor/stubs:src /home/xiang/miniconda3/envs/openslime/bin/python src/ctx_ablation.py %s %s %s\n' "$3" "$1" "$2" "$3" >> logs/jobs_ctx.txt
done
cut -f1 logs/jobs_ctx.txt | tr '\n' ' '; echo
