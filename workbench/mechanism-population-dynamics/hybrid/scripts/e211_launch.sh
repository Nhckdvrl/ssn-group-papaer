#!/usr/bin/env bash
# E211 on fvcrc13: GPU 0 = H noconv, GPU 1 = H nomem (capture, then Patchscopes with the unmodified H);
# GPU 2 = LL readout for H (none / noconv / nomem) and T (none) once the captures exist.
S=/home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts
B=/tmp/xiang_e194; O=$B/out211; mkdir -p $O
cd $B && cp $S/e211_capture.py $S/e211_lens.py $S/e194_capture.py $S/e196_causal.py $S/e194_patch.py .
export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 TOKENIZERS_PARALLELISM=false
filt() { grep -v "Warn\|warn\|falling\|Loading"; }
for spec in noconv:0 nomem:1; do
  c=${spec%%:*}; g=${spec##*:}
  ( CUDA_VISIBLE_DEVICES=$g ./env/bin/python -I e211_capture.py models/H work/items.json $O/H_$c $c 2>&1 | filt
    CUDA_VISIBLE_DEVICES=$g ./env/bin/python -I e194_patch.py models/H tok work/items.json $O/H_$c 2>&1 | filt
    echo E211_R2_DONE_$c ) > $O/$c.log 2>&1 &
done
( until [ -f $O/H_noconv/N.pt ] && [ -f $O/H_nomem/N.pt ]; do sleep 30; done
  CUDA_VISIBLE_DEVICES=2 ./env/bin/python -I e211_lens.py models/H work/items.json $O/lens_H.json none=out/H noconv=$O/H_noconv nomem=$O/H_nomem 2>&1 | filt
  CUDA_VISIBLE_DEVICES=2 ./env/bin/python -I e211_lens.py models/T work/items.json $O/lens_T.json none=out/T 2>&1 | filt
  echo E211_LENS_DONE ) > $O/lens.log 2>&1 &
wait
echo E211_DONE >> $O/lens.log
