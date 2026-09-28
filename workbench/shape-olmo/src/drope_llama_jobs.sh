#!/bin/bash
cd /home/xiang/ssn-group-papaer/explorations/shape_olmo
/home/xiang/miniconda3/envs/verl-clean/bin/python -c "
from huggingface_hub import snapshot_download
for m in ['NousResearch/Llama-2-7b-hf','SakanaAI/Llama-2-7b-hf-DroPE']:
    print(m, snapshot_download(m, allow_patterns=['*.json','*.safetensors','*.py','*.model']), flush=True)
" > logs/dl_llama.log 2>&1
R=$(grep '^NousResearch' logs/dl_llama.log | awk '{print $2}'); D=$(grep '^SakanaAI' logs/dl_llama.log | awk '{print $2}')
{
printf 'PO_L2rope\tHF_HUB_OFFLINE=1 PROBE_GAPS=4,32 PROBE_TRC=0 /home/xiang/miniconda3/envs/verl-clean/bin/python src/probe_order.py %s/ L2rope\n' "$R"
printf 'PO_L2drope\tHF_HUB_OFFLINE=1 PROBE_GAPS=4,32 PROBE_TRC=1 /home/xiang/miniconda3/envs/verl-clean/bin/python src/probe_order.py %s/ L2drope\n' "$D"
} > logs/jobs_llama.txt
exec src/chain_queue.sh logs/jobs_llama.txt "probe_order Llama-2-7B RoPE vs DroPE (transformer DroPE control)"
