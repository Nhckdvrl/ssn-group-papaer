#!/bin/bash
# finish the 1-2 remaining models of E31/E32/E33/E34 on one GPU
cd "$(dirname "$0")"; g=$1
for r in run_e31.sh run_e32.sh run_e33.sh run_e34.sh; do bash $r $g; done
