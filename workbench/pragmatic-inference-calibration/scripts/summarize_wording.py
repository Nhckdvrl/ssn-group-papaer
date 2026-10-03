"""E59 full-source verification, all wordings retained, paired stage interactions."""
import argparse
import json
import math
from collections import defaultdict
from pathlib import Path
import numpy as np
from transformers import AutoTokenizer
from wording_data import prepare,specs,common_path,sha,fingerprint,dependencies
from summarize_dense_natural import iqap_metrics,iqap_describe
from aggregate import estimate


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert not a.output.exists()
    pre=json.loads((Path(__file__).resolve().parents[1]/'results/E59-source-preflight.json').read_text())
    assert pre['gate_pass'] and pre['models']==specs(a.root)
    models={};values={};entries={};families=defaultdict(list);prepared={};total=0
    for m in specs(a.root):
        cp=m['id'].split('/')[-1];run=a.root/'runs'/('E59-wording-'+cp)
        if m['family'] not in prepared:
            tok=AutoTokenizer.from_pretrained(common_path(a.root,m),local_files_only=True)
            prepared[m['family']]=prepare(a.root,tok)
        rows,audit,nulls=prepared[m['family']];cfg=json.loads((run/'config.json').read_text())
        assert cfg['complete'] and cfg['n']==len(rows)==924 and cfg['model']==m['id'] and cfg['revision']==m['sha']
        assert cfg['family']==m['family'] and cfg['stage']==m['stage'] and cfg['source_audit']==audit
        assert cfg['input_sha256']==fingerprint(rows,nulls)==pre['audits'][cp]['input_sha256']
        assert cfg['helper_sha256']==sha(Path(__file__).with_name('wording_data.py'))==pre['helper_sha256']
        assert cfg['script_sha256']==sha(Path(__file__).with_name('run_wording.py'))
        assert cfg['dependency_sha256']==dependencies()==pre['dependencies']
        assert cfg['dtype']=='float32' and cfg['batch_size']==1 and cfg['attention']=='eager' and not cfg['tf32']
        controls=json.loads((run/'numerical-control.json').read_text());assert len(controls)==24
        assert cfg['numerical_gate_pass'] and all(c['pass'] and c['repeat_lp_delta']<1e-6 and c['independent_full_lp_delta']<.001 and c['probability_delta']<.001 and c['argmax_agrees'] for c in controls)
        raw=[json.loads(l) for l in (run/'predictions.jsonl').read_text().splitlines()];assert len(raw)==924
        groups=defaultdict(list);ent=defaultdict(list);copy=defaultdict(list);vmap={};emap={};parity=None
        old={}
        if m['family'] in ('OLMo2','Qwen2.5'):
            e='E51' if m['family']=='OLMo2' else 'E52'
            parent=a.root/'runs'/(e+'-iqap-'+cp)
            pcfg=json.loads((parent/'config.json').read_text())
            assert pcfg['complete'] and pcfg['model']==m['id'] and pcfg['revision']==m['sha'] and pcfg['dtype']==cfg['dtype']
            old={(z['interface'],z['source']['Item']):z for z in map(json.loads,(parent/'predictions.jsonl').read_text().splitlines())}
            assert len(old)==300
            parity={'parent':e,'n':0,'max_lp_delta':0.,'max_probability_delta':0.}
        for r,z in zip(rows,raw):
            assert all(z[k]==v for k,v in r.items())
            for key in ('full_logprob','content_logprob'):
                lp=np.array([s[key] for s in z['choice_scores']]);assert np.isfinite(lp).all()
                norm=float(np.logaddexp.reduce(lp));q=z[key]
                assert np.allclose(q['conditional_probs'],np.exp(lp-norm),rtol=1e-10,atol=1e-12)
                assert q['argmax']==int(lp.argmax()) and 0<=q['candidate_mass']<=1.00001
                assert abs(q['candidate_mass']-math.exp(norm))<1e-12
                group='/'.join((z['alias'],z['interface'],key))
                if z['kind']=='copy':
                    copy[group].append({'correct':float(q['argmax']==z['expected_index']),
                         'expected_probability':q['conditional_probs'][z['expected_index']],
                         'candidate_mass':q['candidate_mass']})
                else:
                    v=iqap_metrics(z['source'],q);groups[group].append(v);ent[group].append(z)
                    k=(z['alias'],z['interface'],key,z['source']['Item']);vmap[k]=v;emap[k]=z
            if old and z['kind']=='natural' and z['alias']=='W0':
                p=old[z['interface'],z['source']['Item']];assert p['source']==z['source'] and p['plan']==z['plan']
                parity['n']+=1
                for key in ('full_logprob','content_logprob'):
                    parity['max_lp_delta']=max(parity['max_lp_delta'],max(abs(u[key]-v[key]) for u,v in zip(p['choice_scores'],z['choice_scores'])))
                    parity['max_probability_delta']=max(parity['max_probability_delta'],max(abs(u-v) for u,v in zip(p[key]['conditional_probs'],z[key]['conditional_probs'])))
        if old:assert parity['n']==300 and parity['max_lp_delta']<.001 and parity['max_probability_delta']<.001
        models[cp]={'model':m['id'],'revision':m['sha'],'family':m['family'],'stage':m['stage'],
                    'descriptions':{g:iqap_describe(ent[g],vs) for g,vs in groups.items()},
                    'copy_controls':{g:{k:estimate([v[k] for v in vs]) for k in vs[0]} for g,vs in copy.items()},
                    'null_readout':cfg['null_readout'],'W0_parent_parity':parity,'n':len(raw),
                    'config_sha256':sha(run/'config.json'),'raw_sha256':sha(run/'predictions.jsonl'),
                    'wall_seconds':cfg['wall_seconds'],'numerical_controls':controls}
        assert len(vmap)==1800;values[cp]=vmap;entries[cp]=emap;families[m['family']].append(cp);total+=len(raw)
    paired={};interactions={}
    for family,names in families.items():
        for left,right in zip(names,names[1:]):
            lv,rv=values[left],values[right];assert lv.keys()==rv.keys()
            gs=defaultdict(list);es=defaultdict(list);igs=defaultdict(list);ies=defaultdict(list)
            for k,x in lv.items():
                g='/'.join(k[:3]);gs[g].append({j:rv[k][j]-v for j,v in x.items()});es[g].append(entries[left][k])
                if k[0]!='W0':
                    base=('W0',)+k[1:]
                    igs[g].append({j:(rv[k][j]-v)-(rv[base][j]-lv[base][j]) for j,v in x.items()})
                    ies[g].append(entries[left][k])
            name=left+' -> '+right
            paired[name]={g:iqap_describe(es[g],vs) for g,vs in gs.items()}
            interactions[name]={g:iqap_describe(ies[g],vs) for g,vs in igs.items()}
    result={'experiment':'E59','n':total,'models':models,'paired_stage_changes':paired,
            'alias_minus_W0_stage_change':interactions,'source_input_numerical_parent_gate_pass':True,
            'script_sha256':sha(Path(__file__)),'limits':[
                'Wordings retain categories but have no independently collected human semantic norms.',
                'Copy-reference controls check category mapping; not natural pragmatic comprehension.',
                'Common terminal is controlled interface, not native Base generation.',
                'Human ratings concern interpreting intent; not speaker epistemic certainty or intrinsic confidence.',
                'Stage data, algorithm and budgets co-vary; paired item CI is not training-seed CI.',
                'All wordings and interfaces retained; no licensing gold or SDT claim.']}
    a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({cp:{g:{k:v[k]['mean'] for k in ('polarity_correct','four_way_brier','candidate_mass')} for g,v in m['descriptions'].items() if 'common-chat/full' in g} for cp,m in models.items()},indent=2))


if __name__=='__main__':main()
