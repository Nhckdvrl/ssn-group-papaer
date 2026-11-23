#!/usr/bin/env bash
# E202: fetch the fla-hub 1.3B-100B zoo to node-local /tmp.
cd /tmp/xiang_hyb
for m in transformer delta_net mamba gla gsa hgrn hgrn2 retnet; do
  nohup bash /home/xiang/ssn-group-papaer/workbench/mechanism-population-dynamics/hybrid/scripts/dl_hf.sh fla-hub/$m-1.3B-100B main /tmp/xiang_hyb/models/fla_$m > dl_fla_$m.log 2>&1 &
done
