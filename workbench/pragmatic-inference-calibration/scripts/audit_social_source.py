"""E60 public original cache and human distributions; zero API calls."""
import csv
import hashlib
import itertools
import json
import math
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
import numpy as np
from run_followup_queue import ROOT

UP=ROOT/'upstream/llm-social-calibration'
sys.path.insert(0,str(UP))
from src import config
from src.parsing import parse_likert_response
from src.analysis import metrics
from prompts import build_prompts


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def json_safe(x):
    # Original DAS/ISS leave nonsignificant effects undefined, never score zero.
    if isinstance(x,dict):return {k:json_safe(v) for k,v in x.items()}
    if isinstance(x,list):return [json_safe(v) for v in x]
    if isinstance(x,float) and not math.isfinite(x):return None
    return x


def main():
    output=Path(__file__).resolve().parents[1]/'results/E60-social-source-audit.json';assert not output.exists()
    files={str(p.relative_to(UP)):sha(p) for p in UP.rglob('*') if p.is_file() and '.git' not in p.parts and '__pycache__' not in p.parts}
    human={};frames={}
    for i,n in [(1,362),(2,390)]:
        p=ROOT/'data'/f'E60-experiment{i}.csv';raw=list(csv.DictReader(p.open()))
        assert len(raw)==n and len({r['participant_id'] for r in raw})==n
        assert {r['knowledge'] for r in raw}==({'unknown'} if i==1 else {'knowl'})
        assert all(1<=int(r[k.replace('-','_')])<=7 for r in raw for k in config.ATTRIBUTES)
        cells=Counter((r['scenario'],r['context'],r['form']) for r in raw);assert len(cells)==24
        df=metrics.load_human_data(p);assert len(df)==n*6 and not df.isna().any().any();frames[i]=df
        means=metrics.mean_by(df,['scenario','context','utterance','attribute']);assert len(means)==144
        human[str(i)]={'n_participants':n,'n_scenarios':6,'n_condition_cells':24,'n_ratings':n*6,
                      'cell_counts':{'/'.join(k):v for k,v in cells.items()},'sha256':sha(p),
                      'condition_means':means.to_dict('records'),
                      'motivation_binary_fields':[k for k in raw[0] if k.startswith(('t2_','t3_')) and k!='t2_response']}
    cached={};paths=[]
    for condition in ('MIN','ALT','KMA','COM'):
        p=UP/'data/llm_ratings'/f'results_{condition}.json';raw=json.loads(p.read_text())
        keys=[(r['model'],r['scenario'],r['context'],r['utterance'],r['attribute'],r['sample_id']) for r in raw]
        expected=set(itertools.product(config.MODELS,config.SCENARIOS,config.CONTEXTS,config.UTTERANCES,config.ATTRIBUTES,range(10)))
        assert len(raw)==len(set(keys))==4320 and set(keys)==expected
        assert all(parse_likert_response(r['raw_response'])==(r['likert'],r['valid']) for r in raw)
        df=metrics.load_llm_data(p);models={}
        for model in config.MODELS:
            d=df[df.model==model];h=frames[1]
            x=metrics.compute_comprehensive_alignment_metrics(h,d)
            esr=metrics.compute_esr(h,d);inter=metrics.compute_esr_interaction(h,d)
            main=[abs(v['esr']-1) for v in esr.values() if v['esr'] is not None]
            interaction=[abs(v['esr_interaction']-1) for v in inter.values() if v['esr_interaction'] is not None]
            cds=(np.mean(main)+np.mean(interaction))/2
            assert len(main)==len(interaction)==5
            models[model]={'alignment':x,'main_esr':esr,'interaction_esr':inter,
                'CDS_combined':float(cds),'DAS':metrics.compute_das(h,d),'ISS':metrics.compute_iss(h,d)}
        cached[condition]={'n':len(raw),'valid':len(df),'strict_only_number_n':sum(bool(re.fullmatch(r'\s*[1-7]\s*',r['raw_response'])) for r in raw),
                           'models':models,'sha256':sha(p)};paths.append((condition,str(p)))
    # Independent ten-effect arithmetic vs the author's public CDS function.
    author=metrics.compute_CDS_data(paths,frames[1]);parity=[]
    for r in author.to_dict('records'):
        independent=cached[r['prompt']]['models'][r['model']]['CDS_combined']
        d=abs(independent-(r['CDS_main']+r['CDS_interaction'])/2);assert d<1e-12
        parity.append({'condition':r['prompt'],'model':r['model'],'absolute_delta':d})
    prompts=[]
    for name,s in config.SCENARIOS.items():
        for c,u,k in itertools.product(config.CONTEXTS,config.UTTERANCES,config.ATTRIBUTES):
            t=build_prompts.build_minimal_prompt(s,c,u,k)
            assert t.count(f'how {k} does')==1 and 'how confident does' not in t
            prompts.append({'scenario':name,'context':c,'utterance':u,'attribute':k,'prompt':t})
    assert len(prompts)==144
    source=ROOT/'data/E60-original-social-prompts.json'
    serialized=json.dumps(prompts,ensure_ascii=False,indent=2)+'\n'
    if source.exists():assert source.read_text()==serialized
    else:source.write_text(serialized)
    result={'experiment':'E60','upstream_revision':subprocess.check_output(['git','-C',str(UP),'rev-parse','HEAD'],text=True).strip(),
        'upstream_file_sha256':files,'human':human,'cache':cached,'author_function_arithmetic_parity':parity,
        'original_prompt_asset':str(source),'original_prompt_sha256':sha(source),'n_min_prompts':144,
        'source_code_uses_competent_not_confident':True,'historical_query_prompts_not_stored':True,
        'script_sha256':sha(Path(__file__)),'undefined_author_measures_stored_as_null':True,'limits':[
            'Archive contains 362/390 retained participants; original recruitment counts differ.',
            'Six scenarios, not 752 independent dialogue scenes; all participant and scene counts retained.',
            'Current code builds competent; raw response archives contain no full historical prompt for verification.',
            'No original Experiment 2 established-knowledge sentences in this LLM repository; human raw is not a stimulus file.',
            'Python entry point has stale function signatures; original public metric functions called without changing upstream.',
            'These measurements concern attributed social properties, not IQAP uncertainty about intended Yes/No.',
            'No API/model predictions collected; no inferred licensing labels.']}
    output.write_text(json.dumps(json_safe(result),indent=2,allow_nan=False)+'\n')
    print(json.dumps({c:{m:round(v['CDS_combined'],3) for m,v in d['models'].items()} for c,d in cached.items()}))


if __name__=='__main__':main()
