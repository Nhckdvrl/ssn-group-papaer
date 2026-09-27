# openslime python (torch 2.9.1+cu129, fla 0.4.0) + transformers 5.12.1 vendored from fgvd (has olmo3, olmo_hybrid).
export SHAPE=/home/xiang/ssn-group-papaer/explorations/shape_olmo
mkdir -p $SHAPE/vendor && ln -sfn /home/xiang/miniconda3/envs/fgvd/lib/python3.12/site-packages/transformers $SHAPE/vendor/transformers
export PYTHONPATH=$SHAPE/vendor:$SHAPE/src
export PY=/home/xiang/miniconda3/envs/openslime/bin/python
export HF_HUB_OFFLINE=1
export T7=/home/xiang/.cache/huggingface/hub/models--allenai--Olmo-3-1025-7B/snapshots/a81bae42db3975be1671e27b9c9a56da1a9f980f/   # main (pinned)
export H7=/home/xiang/.cache/huggingface/hub/models--allenai--Olmo-Hybrid-7B/snapshots/4f1cc566f9fdf3ce68da2ab6a788a83d89896dcf/   # main (pinned)
