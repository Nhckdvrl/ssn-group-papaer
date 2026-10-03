"""E41 complete paired endpoints; original Hu and ImplicatureX likelihoods."""
import argparse, hashlib, json
from collections import defaultdict
from pathlib import Path
import numpy as np
from transformers import AutoTokenizer
from qwen14_readout import prepare, fingerprint
from summarize_boundary_controls import describe

ap=argparse.ArgumentParser()
ap.add_argument('--root',type=Path,required=True)
ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args();assert not a.output.exists()
manifest=json.loads((a.root/'models/qwen25-14-stage-manifest.json').read_text())
tok=AutoTokenizer.from_pretrained(a.root/'models/Qwen2.5-14B-Instruct',local_files_only=True)
plans={t:prepare(a.root,tok,t) for t in ['hu-bare','hu-chat','implicaturex']}
models={};values={}
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for m in manifest:
    cp=m['id'].split('/')[-1];out={'configs':{},'hu':{},'implicaturex':{}};v={}
    for task,expected in plans.items():
        path=a.root/'runs'/('E41-'+task+'-'+cp)
        c=json.loads((path/'config.json').read_text())
        assert c['complete'] and c['numerical_gate_pass'] and c['input_token_hash']==fingerprint(expected)
        assert c['n']==len(expected) and c['dtype']=='float32' and c['batch_size']==1
        assert c['model']==m['id'] and c['revision']==m['sha']
        assert c['script_sha256']==sha(Path(__file__).with_name('run_qwen14_parent.py'))
        assert c['helper_sha256']==sha(Path(__file__).with_name('qwen14_readout.py'))
        controls=json.loads((path/'numerical-control.json').read_text())
        assert [z['index'] for z in controls]==[0,len(expected)-1] and all(z['pass'] for z in controls)
        raw=[json.loads(l) for l in (path/'predictions.jsonl').read_text().splitlines()]
        assert len(raw)==len(expected)
        out['configs'][task]={'run':path.name,'config_sha256':sha(path/'config.json'),
            'raw_sha256':sha(path/'predictions.jsonl'),'n':len(raw),'input_token_hash':fingerprint(expected),
            'numerical_controls':controls}
        for z,r in zip(raw,expected):
            p=r['plan'];s=r['source']
            assert z['full_choice_ids']==p['full_choice_ids'] and z['prompt_sha256']==p['prompt_sha256']
            assert z['generated_common_prefix_ids']==p['generated_common_prefix_ids']
            # Hu preserves the source original/no-story condition in the raw row.
            # The readout interface is identified by the run and exact prompt IDs.
            assert z['condition']==s.get('condition',r['condition'])
            assert all(z[k]==val for k,val in s.items() if k not in ['prompt','system_prompt'])
            assert abs(sum(z['numeric_choice_probs'].values())-1)<1e-5
            assert z['prediction']==max(z['numeric_choice_probs'],key=z['numeric_choice_probs'].get)
            assert 0<=z['support_mass']<=1 and 0<=z['conditional_candidate_mass']<=1
            assert np.allclose(np.exp(np.array(z['full_choice_content_logprobs'])-
                np.logaddexp.reduce(z['full_choice_content_logprobs'])),list(z['numeric_choice_probs'].values()),atol=1e-6)
            if task.startswith('hu'):
                assert z['correct']==(z['prediction']==s['gold']) and z['prob_true_answer']==z['numeric_choice_probs'][s['gold']]
            else:assert z['p_true']==z['numeric_choice_probs'][s['true_label']]
        groups=defaultdict(list)
        if task.startswith('hu'):
            itemrows=defaultdict(list)
            for z in raw:itemrows[z['phenomenon'],z['condition'],z['item_id']].append(z)
            collapsed={k:{metric:float(np.mean([z[metric] for z in rs])) for metric in
                ['correct','prob_true_answer','support_mass','conditional_candidate_mass']} for k,rs in itemrows.items()}
            for (ph,condition,item),d in collapsed.items():groups[ph+'/'+condition].append(d)
            out['hu'][task]={g:describe(ds) for g,ds in groups.items()};v[task]=collapsed
        else:
            idx={(z['condition'],z['item_id'],z['state'],z['true_label']):z for z in raw};assert len(idx)==len(raw)
            collapsed={}
            for cond in ['parent','format']:
                for item in sorted({z['item_id'] for z in raw}):
                    states={s:float(np.mean([idx[cond,item,s,o]['p_true'] for o in ['1','2']]))
                        for s in ['baseline','prior','cancel','irrelevant','negation','strengthen']}
                    rs=[idx[cond,item,s,o] for s in states for o in ['1','2']]
                    ph=rs[0]['phenomenon'];base=states['baseline'];delta=states['cancel']-base
                    d={**states,'recognition':float(base>.5),'cancellation_recognition':float(delta<0),
                        'joint_update':float(base>.5 and delta<0),'strengthen_recognition':float(states['strengthen']>base),
                        'irrelevant_argmax_preserved':float((states['irrelevant']>.5)==(base>.5)),
                        'cancel_delta':delta,'irrelevant_delta':states['irrelevant']-base,
                        'cancel_minus_irrelevant_delta':states['cancel']-states['irrelevant'],
                        'cancel_numerical_boundary':float(abs(delta)<=.001),
                        'mean_support_mass':float(np.mean([z['support_mass'] for z in rs])),
                        'mean_conditional_candidate_mass':float(np.mean([z['conditional_candidate_mass'] for z in rs])),
                        'max_order_ptrue_difference':max(abs(idx[cond,item,s,'1']['p_true']-idx[cond,item,s,'2']['p_true']) for s in states)}
                    collapsed[cond,ph,item]=d;groups[cond+'/'+ph].append(d)
            out['implicaturex']={g:describe(ds) for g,ds in groups.items()};v[task]=collapsed
    models[cp]=out;values[cp]=v
left,right=values.values();changes={}
for task,vs in left.items():
    assert vs.keys()==right[task].keys();groups=defaultdict(list)
    for key,d in vs.items():
        g='/'.join(key[:-1])
        groups[g].append({metric:right[task][key][metric]-value for metric,value in d.items()})
    changes[task]={g:describe(ds) for g,ds in groups.items()}
result={'models':models,'instruct_minus_base':changes,'full_source_input_and_score_gate_pass':True,
    'n':18468,'limits':['One matched checkpoint pair is not a population of training seeds or isolated RLHF intervention.',
        'Common complete official Instruct tokenizer controls the input; chat is not guaranteed native for Base.',
        'Conditional numeric likelihoods may hide weak candidate support; support mass and both answer encodings retained.',
        'Approx/irrelevant continuations have no complete human license norm; no FPR or unified SDT.',
        'Item bootstrap uncertainty is conditional on frozen source materials, not architecture or training population uncertainty.',
        'Projection lives in a separate EOS-aware E41 summary; no pooling of different judgment targets.']}
a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
for cp,v in models.items():
    print(cp,{metric:d['mean'] for metric,d in v['implicaturex']['parent/naturally_occurring_conversational'].items()
        if metric in ['baseline','recognition','cancel_minus_irrelevant_delta','mean_support_mass']})
print('natural stage delta',changes['implicaturex']['parent/naturally_occurring_conversational']['cancel_minus_irrelevant_delta'])
