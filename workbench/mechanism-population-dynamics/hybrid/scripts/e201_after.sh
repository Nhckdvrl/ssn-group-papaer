#!/usr/bin/env bash
# After each E201 training run finishes, run its pre-registered readout conditions on the same GPU.
# Usage: e201_after.sh "ARCH:GPU ..."
cd /tmp/xiang_e201
cp /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts/e201_train.py /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts/e201_readout.py .
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
declare -A CONDS=([hyb_conv]="none noconv nomem" [hyb_noconv]="none nomem" [gdn_conv]="none noconv nomem" [gdn_noconv]="none nomem" [tf]="none noattn" [tf_canon]="none nocanon noattn nocanon_noattn")
mkdir -p readout
for spec in $1; do
  a=${spec%%:*}; g=${spec##*:}
  ( until grep -q "TRAIN_DONE\|Traceback" runs/$a.log; do sleep 60; done
    for c in ${CONDS[$a]}; do
      CUDA_VISIBLE_DEVICES=$g /tmp/xiang_e201/env/bin/python -I e201_readout.py runs/$a /tmp/xiang_e194/work/items.json /tmp/xiang_e194/passages.json /tmp/xiang_e194/tok readout/${a}__$c.json $c >> readout/$a.log 2>&1
    done
    echo "READOUT_DONE $a" >> readout/$a.log ) &
done
wait
