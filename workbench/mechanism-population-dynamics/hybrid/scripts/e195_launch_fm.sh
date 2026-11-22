#!/usr/bin/env bash
# Launch Falcon-Mamba (FM) and its random-init copy (FM0) for E195 on fvcrc10, one item per forward (slow-path memory).
cd /tmp/xiang_e194
nohup bash e195_run.sh /tmp/xiang_hyb/models/FM /tmp/xiang_hyb/work_fm/items.json /tmp/xiang_hyb/out/FM 0 "--items_per_batch 1" > /tmp/xiang_hyb/run_FM.log 2>&1 &
nohup bash e195_run.sh /tmp/xiang_hyb/models/FM /tmp/xiang_hyb/work_fm/items.json /tmp/xiang_hyb/out/FM0 1 "--items_per_batch 1 --random 195" > /tmp/xiang_hyb/run_FM0.log 2>&1 &
