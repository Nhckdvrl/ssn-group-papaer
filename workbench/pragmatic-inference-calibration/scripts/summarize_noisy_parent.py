"""E55 frozen primary and item-cluster intervals; validate every raw record first."""
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
from transformers import AutoTokenizer
from noisy_parent_data import ROOT,specs,prepare,fingerprint,tokenizer_path,sha


def interval(values,keys):
    grouped=defaultdict(list)
    for v,k in zip(values,keys):grouped[k].append(float(v))
    x=np.array([np.mean(v) for _,v in sorted(grouped.items())])
    rng=np.random.default_rng(20261003)
    boot=x[rng.integers(0,len(x),size=(5000,len(x)))].mean(axis=1)
    return {'mean':float(x.mean()),'item_cluster_ci95':np.quantile(boot,[.025,.975]).tolist(),
            'n_rows':len(values),'n_clusters':len(x),'bootstrap_seed':20261003,'bootstrap_replicates':5000}


def implausible(r):
    c=r['source']['Condition'];return c.startswith('implaus') or c.endswith('_implausible')


def group_key(r):
    return r['source']['source_file']+'/'+r['source']['Item']


def cells(rows):
    groups=defaultdict(list)
    for r in rows:
        groups[(r['interface'],r['instruction'],r['source']['source_file'],r['source']['Condition'])].append(r)
    out=[]
    for key,g in sorted(groups.items()):
        assert len(g)==20
        cell={'interface':key[0],'instruction':key[1],'source_file':key[2],'condition':key[3],
              'implausible':implausible(g[0])}
        for which in ('full','content'):
            cell[which]={'literal_probability':interval([r[which]['conditional_probs'][r['literal_index']] for r in g],list(map(group_key,g))),
                         'literal_argmax_rate':interval([r[which]['argmax']==r['literal_index'] for r in g],list(map(group_key,g))),
                         'candidate_mass_min_median':np.quantile([r[which]['candidate_mass'] for r in g],[0,.5]).tolist()}
        out.append(cell)
    return out


def main():
    out=Path(__file__).resolve().parents[1]/'results/E55-noisy-parent-summary.json';assert not out.exists()
    models={};raw_by_cp={};total=0
    pre=json.loads((out.parent/'E55-source-preflight.json').read_text());assert pre['gate_pass']
    for m in specs(ROOT):
        cp=m['id'].split('/')[-1];run=ROOT/'runs'/('E55-noisy-'+cp)
        config=json.loads((run/'config.json').read_text());assert config.get('complete') and config['numerical_gate_pass']
        assert config['model']==m['id'] and config['revision']==m['sha'] and config['n']==1600
        assert config['script_sha256']==sha(Path(__file__).with_name('run_noisy_parent.py'))
        assert config['helper_sha256']==sha(Path(__file__).with_name('noisy_parent_data.py'))==pre['helper_sha256']
        assert all(c['pass'] for c in json.loads((run/'numerical-control.json').read_text()))
        tok=AutoTokenizer.from_pretrained(tokenizer_path(ROOT,cp),local_files_only=True)
        expected,audit,nulls=prepare(ROOT,tok)
        assert audit==config['source_audit'] and fingerprint(expected,nulls)==config['input_sha256']==pre['audits'][cp]['input_sha256']
        raw=[json.loads(l) for l in (run/'predictions.jsonl').read_text().splitlines()]
        assert len(raw)==len({r['id'] for r in raw})==1600
        for x,y in zip(expected,raw):
            assert all(y[k]==v for k,v in x.items())
            for which in ('full','content'):
                q=y[which];lp=np.array(q['logprobs']);p=np.exp(lp-np.logaddexp.reduce(lp))
                assert np.isfinite(lp).all() and np.allclose(q['conditional_probs'],p,atol=1e-12,rtol=0)
                assert q['argmax']==int(lp.argmax()) and np.isclose(q['candidate_mass'],np.exp(lp).sum(),atol=1e-12,rtol=1e-10)
        total+=len(raw);raw_by_cp[cp]=raw
        controls=[];differences=[]
        lookup={(r['source']['source_file'],r['source']['Item'],r['source']['Condition'],r['interface'],r['instruction']):r for r in raw}
        for interface in ('bare','common-chat'):
            for instruction in ('default','literal'):
                g=[r for r in raw if r['interface']==interface and r['instruction']==instruction and not implausible(r)]
                assert len(g)==200
                controls.append({'interface':interface,'instruction':instruction,
                    'full_literal_argmax_rate':interval([r['full']['argmax']==r['literal_index'] for r in g],list(map(group_key,g))),
                    'full_literal_probability':interval([r['full']['conditional_probs'][r['literal_index']] for r in g],list(map(group_key,g))),
                    'full_mass_min_median':np.quantile([r['full']['candidate_mass'] for r in g],[0,.5]).tolist()})
            for file in sorted({r['source']['source_file'] for r in raw}):
                g=[r for r in raw if r['interface']==interface and r['instruction']=='default' and r['source']['source_file']==file]
                for is_implausible in (False,True):
                    h=[r for r in g if implausible(r)==is_implausible]
                    d={}
                    for which in ('full','content'):
                        values=[]
                        for r in h:
                            t=lookup[(file,r['source']['Item'],r['source']['Condition'],interface,'literal')]
                            i=r['literal_index'];values.append(t[which]['conditional_probs'][i]-r[which]['conditional_probs'][i])
                        d[which]=interval(values,list(map(group_key,h)))
                    differences.append({'interface':interface,'source_file':file,'implausible':is_implausible,'literal_minus_default':d})
        models[cp]={'model':m['id'],'revision':m['sha'],'n':len(raw),'all_raw_source_token_numeric_gates_pass':True,
                    'wall_seconds':config['wall_seconds'],'null_readout':config['null_readout'],'controls':controls,
                    'condition_cells':cells(raw),'instruction_differences':differences}
    stage=[]
    for base,instruct in [('Qwen2.5-14B','Qwen2.5-14B-Instruct'),('Mistral-7B-v0.3','Mistral-7B-Instruct-v0.3')]:
        a,b=raw_by_cp[base],raw_by_cp[instruct]
        assert all(x['id']==y['id'] and x['plan']==y['plan'] for x,y in zip(a,b))
        for interface in ('bare','common-chat'):
            for instruction in ('default','literal'):
                for file in sorted({r['source']['source_file'] for r in a}):
                    for is_implausible in (False,True):
                        g=[(x,y) for x,y in zip(a,b) if x['interface']==interface and x['instruction']==instruction
                           and x['source']['source_file']==file and implausible(x)==is_implausible]
                        stage.append({'base':base,'instruct':instruct,'interface':interface,'instruction':instruction,'source_file':file,
                            'implausible':is_implausible,'full_literal_probability_instruct_minus_base':interval(
                                [y['full']['conditional_probs'][y['literal_index']]-x['full']['conditional_probs'][x['literal_index']] for x,y in g],
                                [group_key(x) for x,y in g])})
    assert total==12800
    out.write_text(json.dumps({'n':total,'all_gates_pass':True,'primary':'full period continuation',
        'models':models,'matched_stage_differences':stage,'no_human_exact_parity_claim':True,
        'no_exposure_noise_or_world_prior_causal_claim':True,'no_fpr_dprime_or_ability_upgrade':True},indent=2)+'\n')
    print(json.dumps({'complete':True,'n':total,'output':str(out)}))


if __name__=='__main__':main()
