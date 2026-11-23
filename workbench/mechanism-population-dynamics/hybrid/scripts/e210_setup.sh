#!/usr/bin/env bash
# E210 setup on fvcrc11: copy the E194 env from fvcrc13 (node to node), download RWKV-4-Pile and Pythia (4 sizes each).
S=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts
mkdir -p /tmp/xiang_e194/uv /tmp/xiang_hyb/models /tmp/xiang_hyb/work_neox
if [ ! -x /tmp/xiang_e194/env/bin/python ]; then
  ssh -o BatchMode=yes -o LogLevel=ERROR fvcrc13 "tar -C /tmp/xiang_e194 -cf - env uv/python passages.json" | tar -C /tmp/xiang_e194 -xf -
fi
/tmp/xiang_e194/env/bin/python -c "import torch, transformers; print('ENV', torch.__version__, transformers.__version__, torch.cuda.is_available())"
for s in 169m 430m 1b5 3b; do bash $S/dl_hf.sh RWKV/rwkv-4-$s-pile main /tmp/xiang_hyb/models/rwkv4_$s bin > /tmp/xiang_hyb/dl_rwkv4_$s.log 2>&1 & done
for s in 160m 410m 1.4b 2.8b; do bash $S/dl_hf.sh EleutherAI/pythia-$s main /tmp/xiang_hyb/models/pythia_$s > /tmp/xiang_hyb/dl_pythia_$s.log 2>&1 & done
wait
grep -h "MISMATCH" /tmp/xiang_hyb/dl_rwkv4_*.log /tmp/xiang_hyb/dl_pythia_*.log
grep -h DL_DONE /tmp/xiang_hyb/dl_rwkv4_*.log /tmp/xiang_hyb/dl_pythia_*.log | wc -l
echo E210_SETUP_DONE
