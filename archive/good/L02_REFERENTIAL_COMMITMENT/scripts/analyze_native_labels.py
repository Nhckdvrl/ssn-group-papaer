"""Report all frozen native-label validation jobs, including invalid responses."""
import argparse,collections,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def analyze(run):
    meta=json.loads((run/'completion.json').read_text());proto=json.loads((run/'protocol.json').read_text())
    assert sha(run/'predictions.jsonl')==meta['output_sha256']
    assert sha(run/'protocol.json')==meta['protocol_sha256']
    for n,h in proto['artifact_hashes'].items():assert sha(run/n)==h
    samples={s['id']:s for s in map(json.loads,(run/'samples.jsonl').read_text().splitlines())}
    jobs={j['job_id']:j for j in map(json.loads,(run/'jobs.jsonl').read_text().splitlines())}
    ps=[json.loads(l) for l in (run/'predictions.jsonl').read_text().splitlines()]
    assert len(ps)==len(jobs)==len({p['job_id'] for p in ps})==84
    assert {p['job_id'] for p in ps}==set(jobs)
    decisions=[]
    for p in ps:
        for k in ('sample_id','condition'):assert p[k]==jobs[p['job_id']][k]
        raw=p['raw_response'].strip();pred=raw if raw in ('DNI','INI') else None;assert pred==p['prediction']
        s=samples[p['sample_id']]
        decisions.append({'sample_id':s['id'],'condition':p['condition'],'pair_id':s['pair_id'],
                          'gold':s['interpretation'],'prediction':pred,'raw_response':p['raw_response'],
                          'correct':pred==s['interpretation']})
    metrics={}
    for cond in ('sentence','full'):
        ds=[d for d in decisions if d['condition']==cond];pairs=collections.defaultdict(list)
        for d in ds:pairs[d['pair_id']].append(d['correct'])
        metrics[cond]={'n':len(ds),'correct':sum(d['correct'] for d in ds),'invalid':sum(d['prediction'] is None for d in ds),
                       'pair_n':len(pairs),'complete_pairs_correct':sum(all(v) for v in pairs.values()),
                       'confusion_gold_to_pred':dict(collections.Counter(d['gold']+'->'+str(d['prediction']) for d in ds))}
    by={(d['sample_id'],d['condition']):d for d in decisions}
    transitions=collections.Counter(str(by[sid,'sentence']['correct'])+'->'+str(by[sid,'full']['correct']) for sid in samples)
    return {'run':run.name,'model':meta['model'],'metrics':metrics,'sentence_to_full_correctness':dict(transitions),
            'source_prediction_sha256':sha(run/'predictions.jsonl'),'decisions':decisions,
            'scope':'Exploratory output-format validation on the same 42 development samples; not support/hallucination or method efficacy.'}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('run_ids',nargs='+');p.add_argument('--out',required=True);a=p.parse_args()
    out=ROOT/a.out
    if out.exists():raise FileExistsError(out)
    rs=[analyze(ROOT/'runs'/r) for r in a.run_ids]
    out.write_text(json.dumps({'analysis_script_sha256':sha(Path(__file__)),'runs':rs},indent=2)+'\n')
    for r in rs:print(json.dumps({k:v for k,v in r.items() if k!='decisions'},indent=2))
