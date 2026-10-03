"""Audit selected truncation diagnostics; never rank performance on this selected set."""
import argparse,collections,hashlib,json
from pathlib import Path
from projection_budget_data import specs,selected
from projection_data import parse_rating

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args();assert not a.output.exists();out={}
pre=json.loads(Path('workbench/pragmatic-inference-calibration/results/E42-selected-preflight.json').read_text())
for cp,mid,rev,parent in specs(a.root):
    src,audit=selected(a.root,cp);run=a.root/'runs'/('E42-budget-'+cp)
    config=json.loads((run/'config.json').read_text());assert config['complete'] and config['n']==len(src)
    assert config['selection_audit']==audit==pre[cp]['audit']
    assert config['input_token_sha256']==pre[cp]['selected_input_token_sha256']
    assert config['model']==mid and config['revision']==rev and config['max_new_tokens']==32 and config['dtype']=='float32'
    controls=json.loads((run/'numerical-control.json').read_text());assert all(z['pass'] for z in controls)
    raw=[json.loads(l) for l in (run/'predictions.jsonl').read_text().splitlines()];assert len(raw)==len(src)
    groups=collections.defaultdict(lambda:collections.Counter());examples=[];maxlp=0
    for z,s in zip(raw,src):
        old=s['original'];assert (z['id'],z['interface'],z['selection'])==(old['id'],old['interface'],s['selection'])
        assert z['readout_prompt_sha256']==old['readout_prompt_sha256']
        assert z['original_rating']==old['rating'] and z['original_generated_ids']==old['generated_ids']
        assert z['prefix_ids_match'] and z['generated_ids'][:len(old['generated_ids'])]==old['generated_ids']
        assert parse_rating(z['raw_text'])==z['rating']
        lp=max([abs(u-v) for u,v in zip(z['generated_token_logprobs'],old['generated_token_logprobs'])] or [0]);maxlp=max(maxlp,lp)
        assert lp<.001
        g=groups[(z['interface'],old['task'],z['selection'])];g['n']+=1
        g['eos_complete_n']+=int(z['terminated_by_eos']);g['numeric_valid_n']+=int(z['rating'] is not None)
        if z['rating'] is None:g['became_invalid_n']+=1
        elif z['rating']==old['rating']:g['same_rating_n']+=1
        else:g['changed_rating_n']+=1
        if z['selection']=='first_eos_stratum_sentinel':assert z['generated_ids']==old['generated_ids'] and z['rating']==old['rating']
        if (z['rating'] is None or z['rating']!=old['rating']) and len(examples)<4:
            examples.append({'id':z['id'],'interface':z['interface'],'original':old['raw_text'],'extended':z['raw_text']})
    out[cp]={'n':len(raw),'groups':{'/'.join(k):dict(v) for k,v in groups.items()},'max_prefix_lp_delta':maxlp,
        'source_config_sha256':hashlib.sha256((run/'config.json').read_bytes()).hexdigest(),
        'prefix_and_sentinels_pass':True,'examples_not_selected_as_evidence':examples}
a.output.write_text(json.dumps({'models':out,'gate_pass':True,'n':sum(z['n'] for z in out.values()),
    'limits':['Diagnostic selection is based on original completion status; not a performance sample.',
        'Whole-response strict parser unchanged; invalid is not a pragmatic error.',
        'Original five-token raw and summaries preserved. No further budget or prompt repair.']},indent=2)+'\n')
print(json.dumps({k:{'n':v['n'],'groups':v['groups']} for k,v in out.items()},indent=2))
