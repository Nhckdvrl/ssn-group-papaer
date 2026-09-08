"""Audit completed inference provenance and sample identity across both formats."""
from pathlib import Path
import datetime,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
if __name__=='__main__':
    out=ROOT/'runs/verification_models_20260908.json'
    if out.exists():raise FileExistsError(out)
    records=[];sample_hashes=set();total=0
    for experiment,script,expected in [('E001a','run_interpretation_probe.py',168),('E001b','run_native_label_validation.py',84)]:
        for model in ('qwen32b','mistral24b'):
            run=ROOT/'runs'/f'{experiment}_{model}_v1'
            meta=json.loads((run/'completion.json').read_text());proto=json.loads((run/'protocol.json').read_text())
            assert sha(run/'protocol.json')==meta['protocol_sha256']
            assert sha(run/script)==meta['script_sha256']
            assert sha(run/'predictions.jsonl')==meta['output_sha256']
            for n,h in proto['artifact_hashes'].items():assert sha(run/n)==h
            samples=[json.loads(l) for l in (run/'samples.jsonl').read_text().splitlines()]
            ps=[json.loads(l) for l in (run/'predictions.jsonl').read_text().splitlines()]
            jobs=[json.loads(l) for l in (run/'jobs.jsonl').read_text().splitlines()]
            assert len(ps)==len(jobs)==len({p['job_id'] for p in ps})==expected
            assert {p['job_id'] for p in ps}=={j['job_id'] for j in jobs}
            assert len(samples)==42 and len({s['id'] for s in samples})==42
            assert {p['sample_id'] for p in ps}=={s['id'] for s in samples}
            sample_hashes.add(sha(run/'samples.jsonl'));total+=len(ps)
            files=['protocol.json','samples.jsonl','jobs.jsonl','rendered_prompts.jsonl','predictions.jsonl',script,'environment.json','completion.json']
            records.append({'run':run.name,'prediction_records':len(ps),'files_sha256':{n:sha(run/n) for n in files}})
    assert len(sample_hashes)==1 and total==504
    a=[json.loads(l) for l in (ROOT/'experiments/E001a_interpretation/jobs.jsonl').read_text().splitlines()]
    b=[json.loads(l) for l in (ROOT/'experiments/E001b_native_labels/jobs.jsonl').read_text().splitlines()]
    index={(j['sample_id'],j['condition']):j for j in a if j['order']=='DNI_INI'}
    for j in b:assert j['prompt']==index[j['sample_id'],j['condition']]['prompt'].rsplit('Options:',1)[0]+'Return exactly DNI or INI, without explanation.'
    result={'verified_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'prediction_records':total,
            'unique_natural_samples':42,'same_samples_all_runs':True,'E001b_preserves_context_roles_definitions':True,
            'runs':records,'scope':'Software/provenance integrity only; not semantic-gold validity, independent test performance or paper novelty.'}
    out.write_text(json.dumps(result,indent=2)+'\n');print('Verified 504 records, 42 identical natural samples, four complete runs.')
