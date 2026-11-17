# E192: gather the small per-arm files (train log, run info, routers, held-out NLL, router-input dumps) into one node-local
# place for e192_analyze.py.  Run on fvcrc20.  Local arms are symlinked; fvcrc21 arms are rsynced node-to-node
# (resume.pt and full weights excluded).  A dump is complete when its meta.json exists (written last by e192_train.py).
# usage (on fvcrc20): bash e192_collect.sh
set -e
B=/tmp/xiang_e192; A=$B/analysis/arms; mkdir -p $A
for d in $B/arms/*/; do n=$(basename $d); [ -e $A/$n ] || ln -s $d $A/$n; done
for n in $(timeout 30 ssh -o BatchMode=yes 192.168.0.37 'ls /tmp/xiang_e192/arms'); do
  [ -L $A/$n ] && continue
  timeout 3600 nice -n 19 rsync -a --exclude 'resume*' --exclude 'full_*' --exclude stdout.log \
    192.168.0.37:/tmp/xiang_e192/arms/$n/ $A/$n/
done
# official checkpoints (router weights are read from the bf16 DCP tensors on CPU; dumps from e192_eval.py if present)
ls $A; ls $B/official 2>/dev/null || true
