"""All source rows, EOS, rotations and controls; no selection of successful items."""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
from transformers import AutoTokenizer, AutoConfig, GenerationConfig
from speaker_listener_data import prepare, inputs, parse, specs, tokenizer_path, WORDS, CODE
from aggregate import estimate


def metric_bounds(values, upper):
    """None is retained in a fixed-denominator bound, never deleted."""
    low = [0. if v is None else float(v) for v in values]
    high = [float(u) if v is None else float(v) for v,u in zip(values,upper)]
    result = {'n_source_items':len(values),'available_n':sum(v is not None for v in values),
              'all_item_mean_bounds':[float(np.mean(low)),float(np.mean(high))]}
    if all(v is not None for v in values): result['point_and_item_ci95'] = estimate(values)
    return result


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();assert not a.output.exists()
    rows,audit=prepare(a.root)
    pre=json.loads((Path(__file__).resolve().parents[1]/'results/E49-source-preflight.json').read_text())
    assert pre['source_audit']==audit and pre['gate_pass']
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    models={}
    for cp,mid,revision in specs(a.root):
        run=a.root/'runs'/('E49-speaker-listener-'+cp)
        config=json.loads((run/'config.json').read_text())
        assert config['complete'] and config['n']==1080 and config['source_audit']==audit and config['numerical_gate_pass']
        assert config['model']==mid and config['revision']==revision and config['dtype']=='float32'
        assert config['batch_size']==1 and config['max_new_tokens']==64 and not config['do_sample']
        script=config.get('runner_script','run_speaker_listener.py')
        assert script in ['run_speaker_listener.py','run_speaker_listener_qwen25.py']
        assert config['script_sha256']==sha(Path(__file__).with_name(script))
        assert config['helper_sha256']==sha(Path(__file__).with_name('speaker_listener_data.py'))==pre['helper_sha256']
        controls=json.loads((run/'numerical-control.json').read_text())
        assert len(controls)==4 and all(c['pass_gate'] and c['same_generated_ids'] and c['repeat_lp_delta']<.001 and c['independent_full_lp_delta']<.001 for c in controls)
        tok=AutoTokenizer.from_pretrained(tokenizer_path(a.root,cp),local_files_only=True)
        texts,ids,fp=inputs(tok,rows)
        assert fp==config['input_token_sha256']==pre['models'][cp]['input_token_sha256']
        try: generation=GenerationConfig.from_pretrained(a.root/'models'/cp,local_files_only=True)
        except OSError: generation=GenerationConfig.from_model_config(AutoConfig.from_pretrained(a.root/'models'/cp,local_files_only=True))
        if 'generation_config' in config: assert config['generation_config']==generation.to_dict()
        eos=generation.eos_token_id;eos=[eos] if isinstance(eos,int) else eos or []
        raw=[json.loads(l) for l in (run/'predictions.jsonl').read_text().splitlines()]
        assert len(raw)==len(rows)
        index={}
        for r,z,text in zip(rows,raw,texts):
            assert all(z[k]==v for k,v in r.items() if k not in ['prompt','human_norm'])
            assert z['prediction']==parse(z['raw_text'],r['task'])
            assert z['readout_prompt_sha256']==hashlib.sha256(text.encode()).hexdigest()
            assert z['n_output_tokens']==len(z['generated_ids'])==len(z['generated_token_logprobs'])
            assert z['terminated_by_eos']==bool(z['generated_ids'] and z['generated_ids'][-1] in eos)
            assert tok.decode(z['generated_ids'],skip_special_tokens=True)==z['raw_text']
            value=z['prediction'] if z['terminated_by_eos'] else None
            if r['task']=='listener' and value is not None:
                mapped=[0.]*3
                for v,k in zip(value,r['output_roles']):mapped[k]=v/100
            elif value is not None: mapped={word:v/100 for word,v in zip(r['word_order'],value)}
            else: mapped=None
            assert r['id'] not in index
            index[r['id']]={'row':r,'raw':z,'mapped':mapped}
        listener=defaultdict(list);speaker=defaultdict(list)
        by_item=defaultdict(list)
        for z in index.values():by_item[z['row']['item_id'],z['row']['identity']].append(z)
        joint=defaultdict(list)
        identity_items=defaultdict(dict)
        for (item,identity),zs in by_item.items():
            condition=zs[0]['row']['condition'];key=identity+'/'+condition
            l=[z for z in zs if z['row']['task']=='listener'];s=[z for z in zs if z['row']['task']=='speaker']
            assert len(l)==3 and len(s)==12
            lv=[z['mapped'] for z in l]
            full_l=all(v is not None for v in lv)
            mean_l=np.mean(lv,axis=0).tolist() if full_l else None
            target_low=np.mean([v[0] if v is not None else 0 for v in lv])
            target_high=np.mean([v[0] if v is not None else 1 for v in lv])
            norm={}
            for exp,h in l[0]['row']['human_norm'].items():
                q=np.array(h['mean'])/100
                norm[exp]={'target_mean':float(q[0]),'n_original_humans':h['n'],
                    'distribution_l1_bounds':[float(np.mean([np.abs(np.array(v)-q).sum() if v is not None else 0 for v in lv])),
                        float(np.mean([np.abs(np.array(v)-q).sum() if v is not None else 2*(1-min(q)) for v in lv]))]}
            correct=sum(v is not None and v[0]>max(v[1:]) for v in lv)
            listener[key].append({'item_id':item,'complete_n':sum(v is not None for v in lv),'complete_correct_n':correct,
                'target_mean_bounds':[float(target_low),float(target_high)],'all_three_rotations_mean':mean_l,'human':norm,
                'target_rotation_range':float(max(v[0] for v in lv)-min(v[0] for v in lv)) if full_l else None})
            identity_items[item,condition][identity]=(float(target_low),float(target_high))
            speaker[key].append({'item_id':item,'complete_n':sum(z['mapped'] is not None for z in s),
                'source_message':CODE[zs[0]['row']['source']['msg']],
                'four_order_role_predictions':[{'target_role':z['row']['target_role'],'order':z['row']['order'],
                    'prediction':z['mapped']} for z in s]})
            for order in range(4):
                ss=sorted([z for z in s if z['row']['order']==order],key=lambda z:z['row']['target_role'])
                msg=CODE[ss[0]['row']['source']['msg']]
                evidence=[z['mapped'][msg] for z in ss] if all(z['mapped'] is not None for z in ss) else None
                mass=sum(evidence) if evidence is not None else None
                posterior=[v/mass for v in evidence] if mass is not None and mass>0 else None
                distance=float(np.abs(np.array(mean_l)-posterior).sum()) if mean_l is not None and posterior is not None else None
                joint[key].append({'item_id':item,'word_order_rotation':order,'source_message_likelihood_sum':mass,
                    'bayes_prediction_uniform_object_prior':posterior,'listener_all_three_rotations':mean_l,
                    'distribution_l1_distance':distance,'undefined_due_zero_evidence_mass':mass==0})
        summaries={}
        for key,ls in listener.items():
            js=joint[key];peritem=defaultdict(list)
            for z in js:peritem[z['item_id']].append(z['distribution_l1_distance'])
            lo=[];hi=[];full=[]
            for vals in peritem.values():
                lo.append(float(np.mean([v if v is not None else 0 for v in vals])))
                hi.append(float(np.mean([v if v is not None else 2 for v in vals])))
                full.append(float(np.mean(vals)) if all(v is not None for v in vals) else None)
            point=estimate(full) if all(v is not None for v in full) else None
            ncontrol=len(ls)*3
            correct=sum(z['complete_correct_n'] for z in ls)
            summaries[key]={'source_item_n':len(ls),'listener_n':ncontrol,'listener_complete_n':sum(z['complete_n'] for z in ls),
                'listener_target_mean_bounds':[float(np.mean([z['target_mean_bounds'][0] for z in ls])),float(np.mean([z['target_mean_bounds'][1] for z in ls]))],
                'unambiguous_control':{'complete_unique_argmax_correct_n':correct,'n':ncontrol,'floor_pass':correct/ncontrol>=.95}
                    if key.endswith('/filler unambiguous') else None,
                'speaker_n':len(ls)*12,'speaker_complete_n':sum(z['complete_n'] for z in speaker[key]),
                'joint_all_item_l1_mean_bounds':[float(np.mean(lo)),float(np.mean(hi))],
                'joint_point_and_item_ci95_only_if_complete':point,'joint_item_records':js,
                'listener_item_records':ls,'speaker_item_records':speaker[key]}
        contrasts={}
        for condition in ['critical','filler unambiguous','filler ambiguous']:
            effects=[{'item_id':item,'bounds':[v['adult'][0]-v['child'][1],v['adult'][1]-v['child'][0]]}
                for (item,c),v in identity_items.items() if c==condition]
            assert len(effects)=={'critical':8,'filler unambiguous':12,'filler ambiguous':4}[condition]
            contrasts[condition]={'all_item_target_adult_minus_child_bounds':np.mean([z['bounds'] for z in effects],axis=0).tolist(),
                'point_and_item_ci95_only_if_complete':estimate([z['bounds'][0] for z in effects]) if all(z['bounds'][0]==z['bounds'][1] for z in effects) else None,
                'all_item_records':effects}
        models[cp]={'groups':summaries,'identity_contrasts':contrasts,'all_three_identity_control_floor_pass':all(
            summaries[i+'/filler unambiguous']['unambiguous_control']['floor_pass'] for i in ['unspecified','adult','child']),
            'run_fingerprints':{'config_sha256':sha(run/'config.json'),'raw_sha256':sha(run/'predictions.jsonl')},
            'numerical_controls':controls,'generation_policy_source':generation.to_dict(),'wall_seconds':config['wall_seconds']}
    out={'models':models,'n':8640,'source_audit':audit,'full_source_input_raw_score_gate_pass':True,
         'script_sha256':sha(Path(__file__)),'limits':[
            'Text migration lacks original photos, practice and history; not exact human identity-effect replication.',
            'Speaker task is a derived metalinguistic probability allocation with no source human speaker labels.',
            'Bayes consistency assumes a uniform object prior and combines separate task outputs; not an internal-process verifier.',
            'No incorrect/invalid model items removed. Zero evidence mass has undefined posterior and is retained.',
            'Item bootstrap averages all rotations; endpoint models are not training seeds. No causal RLHF or multiplicity-adjusted discovery.',
            'Greedy native generation defaults include Qwen2.5 repetition penalty; raw-logit parity is separate from this decoding policy.']}
    a.output.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps({cp:{'control_floor':v['all_three_identity_control_floor_pass'],
        'critical':v['identity_contrasts']['critical']} for cp,v in models.items()},indent=2))


if __name__=='__main__':main()
