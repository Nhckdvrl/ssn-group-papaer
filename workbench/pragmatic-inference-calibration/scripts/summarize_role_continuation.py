"""E50 all lexical spans and source roles, paired with complete E49 when available."""
import argparse,hashlib,json,math
from pathlib import Path
from collections import defaultdict
import numpy as np
from transformers import AutoTokenizer
from role_continuation_data import prepare,fingerprint,specs,tokenizer_path,WORDS,CODE
from aggregate import estimate


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();assert not a.output.exists()
    pre=json.loads((Path(__file__).resolve().parents[1]/'results/E50-source-preflight.json').read_text());assert pre['gate_pass']
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    e49path=Path(__file__).resolve().parents[1]/'results/E49-joint-speaker-listener-summary.json'
    e49=json.loads(e49path.read_text()) if e49path.exists() else None
    if e49 is not None:assert e49['full_source_input_raw_score_gate_pass'] and e49['source_audit']==pre['source_audit']
    models={}
    for cp,mid,revision in specs(a.root):
        run=a.root/'runs'/('E50-role-continuation-'+cp);cfg=json.loads((run/'config.json').read_text())
        assert cfg['complete'] and cfg['n']==864 and cfg['numerical_gate_pass'] and cfg['source_audit']==pre['source_audit']
        assert cfg['model']==mid and cfg['revision']==revision and cfg['dtype']=='float32' and cfg['candidate_batch_size']==4
        assert cfg['script_sha256']==sha(Path(__file__).with_name('run_role_continuation.py'))
        assert cfg['helper_sha256']==sha(Path(__file__).with_name('role_continuation_data.py'))==pre['helper_sha256']
        assert cfg['original_dependency_sha256']==sha(Path(__file__).with_name('speaker_listener_data.py'))==pre['original_dependency_sha256']
        controls=json.loads((run/'numerical-control.json').read_text());assert len(controls)==8
        assert all(z['pass'] and z['repeat_delta']<1e-6 and z['independent_single_full_lp_delta']<.001 and z['probability_delta']<.001 and z['argmax_agrees'] for z in controls)
        tok=AutoTokenizer.from_pretrained(tokenizer_path(a.root,cp),local_files_only=True);plans,audit=prepare(a.root,tok)
        assert cfg['input_token_sha256']==fingerprint(plans)==pre['models'][cp]['input_token_sha256']
        raw=[json.loads(l) for l in (run/'predictions.jsonl').read_text().splitlines()];assert len(raw)==len(plans)
        cells=defaultdict(list)
        for z,r in zip(raw,plans):
            assert z['plan']==r['plan'] and z['interface']==r['interface']
            assert all(z[k]==v for k,v in r['row'].items() if k not in ['prompt','human_norm'])
            for which in ['full','content']:
                q=z[which];lp=np.array(q['logprobs'],dtype=float)
                assert len(lp)==len(r['plan'][which+'_ids']) and np.isfinite(lp).all()
                expected=np.exp(lp-np.logaddexp.reduce(lp))
                assert np.allclose(expected,q['conditional_probs'],atol=1e-12,rtol=1e-10)
                assert q['argmax']==int(lp.argmax()) and abs(q['candidate_mass']-sum(math.exp(x) for x in lp))<1e-12
                assert 0<=q['candidate_mass']<=1.00001
                if z['task']=='listener':
                    value=np.zeros(3)
                    for prob,role in zip(q['conditional_probs'],z['output_roles']):value[role]=prob
                    mapped=value.tolist()
                else:mapped=dict(zip(WORDS,q['conditional_probs']))
                cells[z['interface'],which,z['identity'],z['condition'],z['item_id']].append({'row':r['row'],'value':mapped,
                    'candidate_mass':q['candidate_mass']})
        groups=defaultdict(list)
        for (interface,which,identity,condition,item),zs in cells.items():
            listener=[z for z in zs if z['row']['task']=='listener']
            speaker=sorted([z for z in zs if z['row']['task']=='speaker'],key=lambda z:z['row']['target_role'])
            assert len(listener)==len(speaker)==3
            lv=[z['value'] for z in listener];mean=np.mean(lv,axis=0)
            msg=CODE[speaker[0]['row']['source']['msg']];likelihood=np.array([z['value'][msg] for z in speaker])
            mass=float(likelihood.sum());posterior=(likelihood/mass).tolist() if mass>0 else None
            distance=float(np.abs(mean-posterior).sum()) if posterior is not None else None
            norm={exp:{'human_mean':(np.array(h['mean'])/100).tolist(),'n_humans':h['n'],
                'model_distribution_l1':float(np.abs(mean-np.array(h['mean'])/100).sum())}
                for exp,h in listener[0]['row']['human_norm'].items()}
            pair=None
            if e49 is not None:
                oldgroup=e49['models'][cp]['groups'][identity+'/'+condition]
                old=next(z for z in oldgroup['listener_item_records'] if z['item_id']==item)
                old_joint=[z for z in oldgroup['joint_item_records'] if z['item_id']==item]
                pair={'e49_listener_all_three_rotations':old['all_three_rotations_mean'],
                    'e49_listener_l1_vs_e50':float(np.abs(mean-old['all_three_rotations_mean']).sum()) if old['all_three_rotations_mean'] is not None else None,
                    'e49_four_order_joint_l1': [z['distribution_l1_distance'] for z in old_joint],
                    'e49_all_four_available':all(z['distribution_l1_distance'] is not None for z in old_joint)}
            groups[interface+'/'+which+'/'+identity+'/'+condition].append({'item_id':item,
                'listener_mean':mean.tolist(),'listener_rotation_target_range':float(np.ptp([v[0] for v in lv])),
                'listener_complete_unique_argmax_correct_n':sum(v[0]>max(v[1:]) for v in lv),
                'listener_candidate_masses':[z['candidate_mass'] for z in listener],
                'speaker_candidate_masses':[z['candidate_mass'] for z in speaker],
                'speaker_source_word_conditional_probabilities':likelihood.tolist(),'source_word_likelihood_sum':mass,
                'bayes_uniform_prior_posterior':posterior,'joint_l1':distance,'human':norm,'e49_comparison':pair})
        summaries={}
        for key,zs in groups.items():
            ds=[z['joint_l1'] for z in zs]
            summaries[key]={'source_item_n':len(zs),'listener_target_mean':estimate([z['listener_mean'][0] for z in zs]),
                'listener_candidate_mass':estimate([np.mean(z['listener_candidate_masses']) for z in zs]),
                'speaker_candidate_mass':estimate([np.mean(z['speaker_candidate_masses']) for z in zs]),
                'joint_all_item_l1_bounds':[float(np.mean([v if v is not None else 0 for v in ds])),float(np.mean([v if v is not None else 2 for v in ds]))],
                'joint_point_and_item_ci95_only_if_complete':estimate(ds) if all(v is not None for v in ds) else None,
                'all_item_records':zs}
            if key.endswith('/filler unambiguous'):
                correct=sum(z['listener_complete_unique_argmax_correct_n'] for z in zs);n=3*len(zs)
                summaries[key]['unambiguous_control']={'correct_n':correct,'n':n,'floor_pass':correct/n>=.95}
        contrasts={}
        for interface in ['bare','common-chat']:
            for which in ['full','content']:
                for condition in ['critical','filler unambiguous','filler ambiguous']:
                    adult={z['item_id']:z for z in groups[interface+'/'+which+'/adult/'+condition]}
                    child={z['item_id']:z for z in groups[interface+'/'+which+'/child/'+condition]}
                    assert adult.keys()==child.keys()
                    contrasts[interface+'/'+which+'/'+condition]=estimate([adult[k]['listener_mean'][0]-child[k]['listener_mean'][0] for k in adult])
        models[cp]={'groups':summaries,'adult_minus_child_target_probability':contrasts,'numerical_controls':controls,
            'config_sha256':sha(run/'config.json'),'raw_sha256':sha(run/'predictions.jsonl'),'wall_seconds':cfg['wall_seconds']}
    result={'models':models,'n':6912,'full_source_input_score_gate_pass':True,'source_audit':pre['source_audit'],
        'e49_comparison_included':e49 is not None,'e49_summary_sha256':sha(e49path) if e49 is not None else None,
        'script_sha256':sha(Path(__file__)),'limits':[
            'Period-completed likelihood is primary; content-only is the declared secondary, no outcome-based substitution.',
            'Forced continuation prefixes and finite candidate normalization are not transparent language knowledge.',
            'Candidate probability mass, all source items and rotations retained; zero source evidence posterior is undefined.',
            'Original photographs/practice/history are absent; no exact human identity-effect replication.',
            'Separate speaker task and uniform-prior Bayes comparison cannot identify an internal mechanism.',
            'Item-cluster bootstrap, endpoint models not training seeds, no causal RLHF or adjusted confirmatory discovery.']}
    a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({cp:{k:g.get('unambiguous_control') for k,g in m['groups'].items() if k.endswith('/filler unambiguous')}
        for cp,m in models.items()},indent=2))


if __name__=='__main__':main()
