# Runtime for this workbench (source on fvcrc hosts). Generation env: wam-va (torch 2.9 cu126, flash-attn 2.8.3).
export PY=/home/xiang/miniconda3/envs/wam-va/bin/python
export WB=/home/xiang/ssn-group-papaer/workbench/video-world-model-temporal-interfaces
export MG2=$WB/vendor/Matrix-Game/Matrix-Game-2
export PYTHONPATH=$WB/scripts:$MG2:$WB/vendor/pylib:$PYTHONPATH
export HF_HUB_OFFLINE=1
export TOKENIZERS_PARALLELISM=false
