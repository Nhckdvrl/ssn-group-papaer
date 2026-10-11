cd /home/xiang/ssn-group-papaer/candidates/CT08_INFORMATION_HIDING_COMPOSITIONALITY/src
SUBS=http://fvcrc10:8102/v1,http://fvcrc10:8103/v1,http://fvcrc12:8111/v1
LIMIT=4 /home/xiang/miniconda3/envs/verl-clean/bin/python e00_run.py B /tmp/ct08_smoke_b.jsonl http://fvcrc10:8101/v1 qwen3-8b $SUBS qwen3-8b 4 2>&1 | tail -8
python3 - <<'PY'
import json,sys
sys.path.insert(0,'/home/xiang/ssn-group-papaer/candidates/CT08_INFORMATION_HIDING_COMPOSITIONALITY/src')
for l in open('/tmp/ct08_smoke_b.jsonl'):
    r=json.loads(l); print(r['iid'], r.get('error'), round(r['sec']), 'iters', len(r.get('iters',[])), 'final:', str(r['final'])[:120])
    for it in r.get('iters',[])[:2]:
        for b in it['blocks'][:2]: print('   CODE:', b['code'][:200].replace('\n',' | '), ' -> calls', b['n_llm_calls'])
PY
