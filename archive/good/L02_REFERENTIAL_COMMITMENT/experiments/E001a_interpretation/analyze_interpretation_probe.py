"""Analyze complete E001a runs under frozen order-averaged likelihood rule."""
import argparse, collections, hashlib, json, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def analyze(run):
    complete=json.loads((run/'completion.json').read_text())
    assert sha(run/'predictions.jsonl')==complete['output_sha256']
    proto=json.loads((run/'protocol.json').read_text())
    assert sha(run/'protocol.json')==complete['protocol_sha256']
    for name,digest in proto['artifact_hashes'].items():assert sha(run/name)==digest
    samples={x['id']:x for x in map(json.loads,(run/'samples.jsonl').read_text().splitlines())}
    jobs={x['job_id']:x for x in map(json.loads,(run/'jobs.jsonl').read_text().splitlines())}
    preds=[json.loads(l) for l in (run/'predictions.jsonl').read_text().splitlines()]
    assert len(preds)==len(jobs)==len({x['job_id'] for x in preds})==168
    assert set(jobs)=={x['job_id'] for x in preds}
    groups=collections.defaultdict(list)
    for p in preds:
        for k in ('sample_id','condition','order','a_label','b_label'): assert p[k]==jobs[p['job_id']][k]
        assert all(math.isfinite(p[k]) for k in ('logp_A','logp_B'))
        groups[p['sample_id'],p['condition']].append(p)
    decisions=[]
    for (sid,cond),ps in sorted(groups.items()):
        assert len(ps)==2 and {p['order'] for p in ps}=={'DNI_INI','INI_DNI'}
        odds=[(p['logp_A']-p['logp_B'])*(1 if p['a_label']=='DNI' else -1) for p in ps]
        mean=sum(odds)/2; pred='DNI' if mean>=0 else 'INI';gold=samples[sid]['interpretation']
        decisions.append({'sample_id':sid,'pair_id':samples[sid]['pair_id'],'condition':cond,
                          'gold':gold,'prediction':pred,'correct':pred==gold,'mean_log_odds_DNI':mean,
                          'order_disagreement':(odds[0]>=0)!=(odds[1]>=0)})
    metrics={}
    for cond in ('sentence','full'):
        ds=[d for d in decisions if d['condition']==cond];pairs=collections.defaultdict(list)
        for d in ds:pairs[d['pair_id']].append(d['correct'])
        metrics[cond]={'n':len(ds),'correct':sum(d['correct'] for d in ds),
            'pair_n':len(pairs),'complete_pairs_correct':sum(all(v) for v in pairs.values()),
            'order_disagreements':sum(d['order_disagreement'] for d in ds),
            'confusion_gold_to_pred':dict(collections.Counter(d['gold']+'->'+d['prediction'] for d in ds)),
            'non_AB_argmax_jobs':sum(p['top_token'] not in ('A','B') for p in preds if p['condition']==cond),
            'input_tokens_min':min(p['input_tokens'] for p in preds if p['condition']==cond),
            'input_tokens_max':max(p['input_tokens'] for p in preds if p['condition']==cond)}
    indexed={(d['sample_id'],d['condition']):d for d in decisions}
    transitions=collections.Counter()
    for sid in samples:
        s,f=indexed[sid,'sentence'],indexed[sid,'full']
        transitions[str(s['correct'])+'->'+str(f['correct'])]+=1
    return {'run':run.name,'model':complete['model'],'metrics':metrics,'sentence_to_full_correctness':dict(transitions),
            'source_prediction_sha256':sha(run/'predictions.jsonl'),
            'interpretation':'42 gold-balanced challenge examples from one story; no population CI, no filler support or hallucination metric.',
            'decisions':decisions}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run_ids',nargs='+');p.add_argument('--out',required=True);a=p.parse_args()
    out=ROOT/a.out
    if out.exists():raise FileExistsError(out)
    results=[analyze(ROOT/'runs'/r) for r in a.run_ids]
    out.write_text(json.dumps({'analysis_script_sha256':sha(Path(__file__)),'runs':results},indent=2)+'\n')
    for r in results:print(json.dumps({k:v for k,v in r.items() if k!='decisions'},indent=2))
