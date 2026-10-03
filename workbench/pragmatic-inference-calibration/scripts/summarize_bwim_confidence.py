"""E45 bounded parent pilot: full history verification and task-floor before pragmatics."""
import argparse,collections,hashlib,json
from pathlib import Path
import numpy as np
from transformers import AutoTokenizer
from bwim_data import prepare,parse,SYSTEM,user_prompt,render,add_user
from commitment_data import common_model
from projection_budget_data import specs

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args();assert not a.output.exists();episodes,audit=prepare(a.root)
selected={'Qwen2.5-3B-Instruct','Qwen3-4B','Qwen3-8B','Qwen3-14B','Mistral-7B-Instruct-v0.3'};out={}
paths=[a.root/'runs'/('E45-bwim-'+cp+'-seeds'+suffix) for cp,_,_,_ in specs(a.root) if cp in selected for suffix in ['02','13']]
waiting=[p.name for p in paths if not (p/'config.json').exists() or not json.loads((p/'config.json').read_text()).get('complete')]
if waiting:raise RuntimeError('Cannot summarize before completion: '+','.join(waiting))
for cp,mid,revision,parent in specs(a.root):
    if cp not in selected:continue
    tok=AutoTokenizer.from_pretrained(common_model(a.root,cp),local_files_only=True);by_seed={};fingerprints=[]
    for seeds in [[0,2],[1,3]]:
        run=a.root/'runs'/('E45-bwim-'+cp+'-seeds'+''.join(map(str,seeds)));cfg=json.loads((run/'config.json').read_text())
        assert cfg['source_audit']==audit and cfg['numerical_gate_pass'] and cfg['seeds']==seeds and cfg['n']==80
        assert cfg['model']==mid and cfg['revision']==revision and cfg['max_new_tokens']==512 and cfg['dtype']=='float32'
        assert cfg['script_sha256']==hashlib.sha256(Path(__file__).with_name('run_bwim_confidence.py').read_bytes()).hexdigest()
        assert cfg['helper_sha256']==hashlib.sha256(Path(__file__).with_name('bwim_data.py').read_bytes()).hexdigest()
        assert all(z['pass'] for z in json.loads((run/'numerical-control.json').read_text()))
        raw=[json.loads(l) for l in (run/'predictions.jsonl').read_text().splitlines()];assert len(raw)==80
        fingerprints.append({'run':run.name,'config_sha256':hashlib.sha256((run/'config.json').read_bytes()).hexdigest(),
            'raw_sha256':hashlib.sha256((run/'predictions.jsonl').read_bytes()).hexdigest(),'wall_seconds':cfg['wall_seconds'],
            'peak_gpu_memory_bytes':cfg['peak_gpu_memory_bytes']})
        for seed in seeds:
            rr=[z for z in raw if z['seed']==seed];assert len(rr)==40
            messages=[{'role':'system','content':SYSTEM}]
            for i,(r,z) in enumerate(zip(episodes[seed],rr)):
                assert all(z[k]==json.loads(json.dumps(v)) for k,v in r.items())
                add_user(messages,user_prompt(r,i in [0,20]));assert messages==z['messages']
                text,ids=render(tok,messages)
                assert z['input_sha256']==hashlib.sha256(json.dumps(ids).encode()).hexdigest()
                assert z['prompt_sha256']==hashlib.sha256(text.encode()).hexdigest()
                assert len(ids)==z['n_input_tokens'] and len(ids)+512<=cfg['max_context_tokens']
                p=parse(z['raw_text']);assert z['parsed']==json.loads(json.dumps(p))
                assert z['available']==(p is not None and z['terminated_by_eos'])
                assert z['correct']==(p is not None and p['blocks']==r['gold_blocks'])
                assert z['pragmatic_choice']==(p is not None and p['blocks']==r['pragmatic_blocks'])
                messages.append({'role':'assistant','content':z['raw_text']})
                built=';'.join(','.join(map(str,b)) for b in p['blocks']) if p else 'unparseable response'
                add_user(messages,'FEEDBACK:'+str(z['correct'])+'; the structure you built = '+built+'; the correct structure = '+r['target_structure']+';')
            by_seed[seed]=rr
    all_raw=[z for rs in by_seed.values() for z in rs];groups={}
    for policy in ['pragmatic','literal']:
        for task in ['fully_spec','underspecified']:
            rr=[z for z in all_raw if z['speaker_policy']==policy and ((z['trial_type']=='fully_spec')==(task=='fully_spec'))]
            ratings=[z['parsed']['rating'] for z in rr if z['available']]
            groups[policy+'/'+task]={'n':len(rr),'available_n':len(ratings),
                'complete_correct_n':sum(z['available'] and z['correct'] for z in rr),
                'complete_other_structure_n':sum(z['available'] and not z['correct'] for z in rr),
                'invalid_or_truncated_n':sum(not z['available'] for z in rr),
                'pragmatic_structure_n':sum(z['available'] and z['pragmatic_choice'] for z in rr),
                'all_trial_confidence_mean_bounds':[(sum(ratings)+len(rr)-len(ratings))/len(rr),
                    (sum(ratings)+4*(len(rr)-len(ratings)))/len(rr)],
                'valid_only_confidence_diagnostic':float(np.mean(ratings)) if ratings else None,
                'quarters':{str(q):{'n':sum((z['round']-1)%20//5==q for z in rr),
                    'available_n':sum(z['available'] and (z['round']-1)%20//5==q for z in rr),
                    'rating_sum':sum(z['parsed']['rating'] for z in rr if z['available'] and (z['round']-1)%20//5==q)} for q in range(4)}}
    fully=[z for z in all_raw if z['trial_type']=='fully_spec'];ncorrect=sum(z['available'] and z['correct'] for z in fully)
    out[cp]={'groups':groups,'fully_controls_n':len(fully),'fully_complete_correct_n':ncorrect,
        'fully_floor_reference_ge95_percent':ncorrect/len(fully)>=.95,'max_actual_input_tokens':max(z['n_input_tokens'] for z in all_raw),
        'task_floor_limits_pragmatic_interpretation':ncorrect/len(fully)<.95,'run_fingerprints':fingerprints}
a.output.write_text(json.dumps({'models':out,'n':800,'source_audit':audit,'full_source_history_gate_pass':True,
    'limits':['Finite feasibility pilot, not original 30-sequence numerical reproduction.',
        'Coordinate task floor assessed before pragmatic interpretation; wrong spatial structure is not automatically pragmatic error.',
        'Literal-partner pragmatic preference is not FPR; source includes four pragmatically compatible critical targets.',
        'No trial-level human norm, no QA actions or API. Confidence rating is not internal uncertainty.',
        'Four source sequences, same source materials; not four independently trained models or new populations.']},indent=2)+'\n')
print(json.dumps({k:{'controls':(v['fully_complete_correct_n'],v['fully_controls_n']),
    'floor_pass':v['fully_floor_reference_ge95_percent'],'groups':v['groups']} for k,v in out.items()},indent=2))
