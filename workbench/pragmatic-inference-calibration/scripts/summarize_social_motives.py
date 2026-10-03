"""E61 all-target source verification; scene CI and fixed-human uncertainty sensitivity."""
import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
import numpy as np
from transformers import AutoTokenizer
from aggregate import estimate
from social_motive_data import prepare,specs,common_path,sha,fingerprint,dependencies,SCENARIO_MAP


def describe(rows,values):
    grouped=defaultdict(list)
    for r,v in zip(rows,values):grouped[r['scene']].append(v)
    return {k:estimate([np.mean([v[k] for v in vs]) for vs in grouped.values()]) for k in values[0]}


def human_bootstrap(root):
    cells=defaultdict(list)
    for r in csv.DictReader((root/'data/E60-experiment1.csv').open()):
        cells[SCENARIO_MAP[r['scenario']],{'lowPr':'low','highPr':'high'}[r['context']],r['form']].append(r)
    out={};rng=np.random.default_rng(0)
    for cell,people in sorted(cells.items()):
        draws=rng.integers(len(people),size=(2000,len(people)))
        for field in people[0]:
            if field not in ['competent','knowledgeable','well_prepared','helpful','likeable','pedantic'] and not field.startswith('t3_'):continue
            x=np.array([int(r[field]) for r in people])[draws]
            out[cell+(field.replace('_','-') if not field.startswith('t3_') else field,)]=(np.array([(x==j).mean(1) for j in range(1,8)]).T if not field.startswith('t3_') else np.stack([x.mean(1),1-x.mean(1)],axis=1))
    return out


def measure(r,q,h=None):
    p=np.array(q['conditional_probs']);h=np.array(r['human_counts'])/r['human_n'] if h is None else h
    assert len(p)==len(h) and abs(h.sum()-1)<1e-12
    v={'human_distribution_brier':float(np.square(p-h).sum()),'candidate_mass':q['candidate_mass']}
    if r['kind']=='trait':
        levels=np.arange(1,8);pm=float(p@levels);hm=float(h@levels)
        v.update(model_mean_rating=pm,human_mean_rating=hm,mean_rating_absolute_error=abs(pm-hm))
    else:v.update(model_select_probability=float(p[0]),human_select_rate=float(h[0]),selection_absolute_error=float(abs(p[0]-h[0])))
    return v


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();assert not a.output.exists()
    pre=json.loads((Path(__file__).resolve().parents[1]/'results/E61-source-preflight.json').read_text())
    assert pre['gate_pass'] and pre['models']==specs(a.root)
    boot=human_bootstrap(a.root);prepared={};models={};vs={};rs={};bs={};families=defaultdict(list);total=0
    for m in specs(a.root):
        cp=m['id'].split('/')[-1];run=a.root/'runs'/('E61-social-motives-'+cp)
        if m['family'] not in prepared:
            tok=AutoTokenizer.from_pretrained(common_path(a.root,m),local_files_only=True);prepared[m['family']]=prepare(a.root,tok)
        rows,audit,nulls=prepared[m['family']];audit=json.loads(json.dumps(audit))
        cfg=json.loads((run/'config.json').read_text())
        assert cfg['complete'] and cfg['n']==len(rows)==1572 and cfg['model']==m['id'] and cfg['revision']==m['sha']
        assert cfg['source_audit']==audit==pre['audits'][cp]['source_audit'] and cfg['input_sha256']==fingerprint(rows,nulls)==pre['audits'][cp]['input_sha256']
        assert cfg['script_sha256']==sha(Path(__file__).with_name('run_social_motives.py'))
        assert cfg['helper_sha256']==sha(Path(__file__).with_name('social_motive_data.py'))==pre['helper_sha256']
        assert cfg['dependency_sha256']==dependencies()==pre['dependencies'] and cfg['numerical_gate_pass']
        assert cfg['dtype']=='float32' and cfg['batch_size']==1 and cfg['attention']=='eager' and not cfg['tf32']
        controls=json.loads((run/'numerical-control.json').read_text());assert len(controls)==32
        assert all(c['pass'] and c['repeat_lp_delta']<1e-6 and c['independent_full_lp_delta']<.001 and c['probability_delta']<.001 and c['argmax_agrees'] for c in controls)
        raw=[json.loads(l) for l in (run/'predictions.jsonl').read_text().splitlines()];assert len(raw)==1572
        values={};entry={};bvals={};groups=defaultdict(list);ent=defaultdict(list);copies=defaultdict(list);human_sensitivity=defaultdict(list);effects={}
        for r,z in zip(rows,raw):
            assert all(z[k]==v for k,v in r.items())
            for key in ('full_logprob','content_logprob'):
                q=z[key];lp=np.array([s[key] for s in z['choice_scores']]);assert np.isfinite(lp).all()
                norm=float(np.logaddexp.reduce(lp));assert np.allclose(q['conditional_probs'],np.exp(lp-norm),rtol=1e-10,atol=1e-12)
                assert q['argmax']==int(lp.argmax()) and 0<=q['candidate_mass']<=1.00001 and abs(q['candidate_mass']-math.exp(norm))<1e-12
                group='/'.join((r['alias'],r['interface'],key,r['kind']))
                if r['kind'].endswith('copy'):
                    copies[group].append({'correct':float(q['argmax']==r['expected_index']),'candidate_mass':q['candidate_mass'],'expected_probability':q['conditional_probs'][r['expected_index']]});continue
                v=measure(r,q);k=(r['id'],key);values[k]=v;entry[k]=r;groups[group].append(v);ent[group].append(r)
                h=boot[r['scene'],r['context'],r['utterance'],r['attribute']];pred=np.array(q['conditional_probs'])
                bv=np.square(pred-h).sum(1);bvals[k]=bv;human_sensitivity[group].append(bv)
                effect_group='/'.join((r['alias'],r['interface'],key,r['kind'],r['attribute']))
                effect_value=v['model_mean_rating'] if r['kind']=='trait' else v['model_select_probability']
                human_value=v['human_mean_rating'] if r['kind']=='trait' else v['human_select_rate']
                effects.setdefault(effect_group,{})[r['scene'],r['context'],r['utterance']]=(effect_value,human_value)
        interactions={}
        for g,ev in effects.items():
            per=[]
            for scene in sorted({k[0] for k in ev}):
                contrast=lambda j:ev[scene,'high','precise'][j]-ev[scene,'high','approx'][j]-ev[scene,'low','precise'][j]+ev[scene,'low','approx'][j]
                per.append({'scene':scene,'model_interaction':contrast(0),'human_interaction':contrast(1),'model_minus_human_interaction':contrast(0)-contrast(1)})
            assert len(per)==6
            interactions[g]={'scene_values':per,**{k:estimate([v[k] for v in per]) for k in per[0] if k!='scene'}}
        models[cp]={'model':m['id'],'revision':m['sha'],'family':m['family'],'stage':m['stage'],
            'descriptions':{g:describe(ent[g],v) for g,v in groups.items()},
            'fixed_model_human_sampling_brier_ci95':{g:np.quantile(np.mean(v,axis=0),[.025,.975]).tolist() for g,v in human_sensitivity.items()},
            'form_context_interactions':interactions,'copy_controls':{g:{k:estimate([v[k] for v in vv]) for k in vv[0]} for g,vv in copies.items()},
            'null_readout':cfg['null_readout'],'n':len(raw),'wall_seconds':cfg['wall_seconds'],
            'config_sha256':sha(run/'config.json'),'raw_sha256':sha(run/'predictions.jsonl'),'numerical_controls':controls}
        vs[cp]=values;rs[cp]=entry;bs[cp]=bvals;families[m['family']].append(cp);total+=len(raw)
    paired={}
    for family,names in families.items():
        for left,right in zip(names,names[1:]):
            assert vs[left].keys()==vs[right].keys();groups=defaultdict(list);ent=defaultdict(list);hbs=defaultdict(list)
            for k,x in vs[left].items():
                r=rs[left][k];g='/'.join((r['alias'],r['interface'],k[1],r['kind']))
                groups[g].append({j:vs[right][k][j]-v for j,v in x.items()});ent[g].append(r);hbs[g].append(bs[right][k]-bs[left][k])
            paired[left+' -> '+right]={'changes':{g:describe(ent[g],v) for g,v in groups.items()},
                'fixed_models_human_sampling_brier_delta_ci95':{g:np.quantile(np.mean(v,axis=0),[.025,.975]).tolist() for g,v in hbs.items()}}
    result={'experiment':'E61','n':total,'models':models,'paired_stage_changes':paired,'source_input_numerical_gate_pass':True,
        'script_sha256':sha(Path(__file__)),'limits':[
            'Six independent scenes; CI is coarse pilot evidence, not 12576 independent situations.',
            'Human bootstrap stratified within each condition preserves joint participant trait/checkbox correlations.',
            'Binary queries adapt the original joint-checkbox task; not a joint motive distribution or original task reproduction.',
            'Human norm distance is not factual truth, intrinsic uncertainty or causal mediation.',
            'Full candidate mass/copy controls do not alone establish natural comprehension.',
            'Null diagnostics cover two illustrative task frames only; not a target-matched correction for all sixteen attributes.',
            'All targets/interfaces/instruction conditions retained; no best-prompt selection or licensing/SDT label.',
            'Same family common terminal is controlled interface; algorithms/data/budgets covary across stages.']}
    a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({cp:{g:{k:round(v[k]['mean'],4) for k in v if k in ['human_distribution_brier','candidate_mass','mean_rating_absolute_error','selection_absolute_error']} for g,v in m['descriptions'].items() if 'original/common-chat/full' in g} for cp,m in models.items()},indent=2))


if __name__=='__main__':main()
