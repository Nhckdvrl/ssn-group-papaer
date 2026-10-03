"""E46 preserves the frozen E43 semantic material and parser."""
import argparse, hashlib, json
from pathlib import Path
from transformers import AutoTokenizer
from commitment_data import prepare, inputs, parse

GROUPS=['literal','meaning','trust','binary']
def common_model(root,cp):
    assert cp in ['Qwen2.5-14B','Qwen2.5-14B-Instruct']
    return root/'models/Qwen2.5-14B-Instruct'

def selected(rows,group):
    assert group in GROUPS
    return [r for r in rows if (r['task'] in ['comprehension','fact-verifier'] if group=='binary'
        else r['task'] in ['commitment','trust'] and r['target']==group)]

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();assert not a.output.exists();rows,audit=prepare(a.root)
    prior=json.loads(Path('workbench/pragmatic-inference-calibration/results/E43-source-preflight.json').read_text())
    assert prior['gate_pass'] and prior['audit']==audit
    counts={g:len(selected(rows,g)) for g in GROUPS};assert list(counts.values())==[64,64,64,72]
    assert len({r['id'] for g in GROUPS for r in selected(rows,g)})==sum(counts.values())==len(rows)==264
    manifest=json.loads((a.root/'models/qwen25-14-stage-manifest.json').read_text());models={}
    for m in manifest:
        cp=m['id'].split('/')[-1];tok=AutoTokenizer.from_pretrained(common_model(a.root,cp),local_files_only=True)
        models[cp]={'full':{k:inputs(tok,rows,k,cp)[2] for k in ['bare','common-chat']},
            'groups':{g:{k:inputs(tok,selected(rows,g),k,cp)[2] for k in ['bare','common-chat']} for g in GROUPS}}
    assert len(models)==2 and len({json.dumps(x,sort_keys=True) for x in models.values()})==1
    a.output.write_text(json.dumps({'gate_pass':True,'audit':audit,'models':models,'counts':counts,
        'original_dependency_sha256':hashlib.sha256(Path(__file__).with_name('commitment_data.py').read_bytes()).hexdigest()},indent=2)+'\n')
    print(json.dumps({'gate_pass':True,'counts':counts,'n':1056}))
