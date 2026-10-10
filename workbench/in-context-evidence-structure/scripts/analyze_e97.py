"""Merge complete E97 batches before performing preference-invariance analysis."""
import argparse, hashlib, json
from pathlib import Path
from e97_goal_comparison import records,key,analyze


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--root',default='results/e97'); ap.add_argument('--source',default='results/e95/qwen35_discovery'); a=ap.parse_args()
    p=Path(a.root); expected={key(r):r for r in records(Path(a.source))}; rows=[]; batches=[]; runs=[]
    for i in range(3):
        q=p/f'qwen35_part{i}'; run=json.loads((q/'run.json').read_text()); runs.append(run)
        rr=[json.loads(s) for s in (q/'behavior.jsonl').read_text().splitlines()]
        assert len(rr)==run['n_rows']; rows+=rr; batches+=run['batch_indices']
    lut={key(r):r for r in rows}; assert len(lut)==len(rows)==160
    assert set(lut)==set(expected) and sorted(batches)==list(range(20))
    for k,r in lut.items():
        assert all(r[f]==expected[k][f] for f in ('gold','labels','kind','query','asked','self_criterion'))
    order={k:i for i,k in enumerate(expected)}; rows.sort(key=lambda r:order[key(r)])
    (p/'behavior_merged.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    (p/'analysis.json').write_text(json.dumps(analyze(rows),indent=2)+'\n')
    audit={'n_rows':len(rows),'unique_keys':len(lut),'all_frozen_records_retained':True,'all_batches_covered':True,
        'initial_censored':sum(r['score']['initial_censored'] for r in rows),'still_censored':sum(r['score']['still_censored'] for r in rows),
        'unresolved':sum(not r['score']['valid'] for r in rows),'gpu_hours':sum(r['gpu_hours'] for r in runs),
        'source_script_sha256':runs[0]['script_sha256'],'analyzer_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'audit_type':'executing-agent completeness check, not independent scientific review'}
    assert len({r['script_sha256'] for r in runs})==1
    (p/'completeness_audit.json').write_text(json.dumps(audit,indent=2)+'\n'); print(json.dumps(audit))


if __name__=='__main__': main()
