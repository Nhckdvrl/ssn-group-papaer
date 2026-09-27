source /home/xiang/ssn-group-papaer/candidates/CT07_MEMORY_QUERY_TIMING/src/env.sh
cd $CT07/src
rm -rf /tmp/ct07t; mkdir -p /tmp/ct07t
ONLY=120,124,0,4 CUDA_VISIBLE_DEVICES=0 $PY e00.py $Q35_9B /tmp/ct07t/t.jsonl 0 1 $CT05/data/checkpoints.jsonl "$CT05/results/e01/q35_9b.s*.jsonl" 2>&1 | grep -v 'Loading\|Warn\|fast path' | tail -15
python3 - <<'PY'
import json
for l in open('/tmp/ct07t/t.jsonl'):
    r=json.loads(l)
    if 'skip' in r: print(r); continue
    print(r['cid'],r['src'],r['N'],r['T'],r['n_value'],r['bnd'],round(r['sec']))
    print({k:round(v,2) for k,v in r['G'].items()})
    print({k:(round(v,2) if v is not None else None) for k,v in r['spearman_oracle'].items()})
PY
