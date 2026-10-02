#!/usr/bin/env python3
"""Versioned raw reparsing, explicit validity and item/concept cluster summaries."""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy.stats import pearsonr
from scoring import parse_choice


def read(p):
    return [json.loads(s) for s in p.read_text().splitlines()]


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def estimate(values):
    x=np.asarray(values,dtype=float)
    assert len(x)>0
    rng=np.random.default_rng(0)
    boot=x[rng.integers(0,len(x),size=(2000,len(x)))].mean(axis=1)
    return {'mean':float(x.mean()),'ci95':np.quantile(boot,[.025,.975]).tolist(),'clusters':len(x)}


def cluster(rows,fn,unit=lambda r:r['item_id']):
    groups=defaultdict(list)
    for r in rows:groups[unit(r)].append(float(fn(r)))
    return estimate([np.mean(v) for v in groups.values()])


def choice_metrics(rows):
    out=cluster(rows,lambda r:r['prediction']==r['gold'])
    out.update(n_responses=len(rows),invalid=sum(r['prediction'] is None for r in rows),
        truncated=sum(r.get('truncated',False) for r in rows),
        accuracy_upper_if_all_invalid_correct=sum(r['prediction']==r['gold'] or r['prediction'] is None for r in rows)/len(rows),
        original_parser_accuracy=sum(r['original_prediction']==r['gold'] for r in rows)/len(rows),
        changed_parses=sum(r['prediction']!=r['original_prediction'] for r in rows))
    return out


def reparse(rows):
    return [r|{'original_prediction':r['prediction'],'prediction':parse_choice(r['response'],r['choices'])} for r in rows]


def splits(rows):
    return {k:choice_metrics(v) for k,v in {'all':rows,
        'maxims':[r for r in rows if r['phenomenon']!='literal'],
        'literal':[r for r in rows if r['phenomenon']=='literal']}.items()}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();runs=a.root/'runs'
    scorer_sha=sha(Path(__file__).with_name('scoring.py'))
    derived=runs/f'derived-parser-{scorer_sha[:12]}';derived.mkdir(exist_ok=True)
    out={'bootstrap':{'draws':2000,'seed':0,'method':'item clusters, three sampling/option orders averaged within item; Wavelength concept-pair clusters; percentile 95% CI',
        'limits':'fixed model and dataset, not model-population or causal stage uncertainty; descriptive comparisons, no multiplicity-adjusted discovery'},
        'scorer_sha256':scorer_sha,'script_sha256':sha(Path(__file__)),
        'multi':{},'paired_format_effect':{},'hu':{},'wavelength':{},'readout':{},'annotations':{},'incomplete_or_superseded':{},
        'recorded_gpu_hours':0.,'compute_note':'sum recorded completed runtimes incl repairs; interrupted jobs without wall time omitted; derived joins not double counted',
        'sdt_status':'NOT IDENTIFIED: no trustworthy warranted + option-level inference labels; literal accuracy is not false alarm rate'}
    multi_rows={}
    for run in sorted(runs.glob('E*')):
        if not run.is_dir() or not (run/'config.json').exists():continue
        cfg=json.loads((run/'config.json').read_text())
        if 'wall_seconds' in cfg:out['recorded_gpu_hours']+=cfg['wall_seconds']/3600
        if 'wall_seconds' not in cfg and not cfg.get('derived_complete'):
            out['incomplete_or_superseded'][run.name]={'status':'INCOMPLETE','files':{p.name:len(read(p)) for p in run.glob('*.jsonl')}};continue
        source={'config_sha256':sha(run/'config.json'),'result_hashes':{str(p):sha(p) for p in run.glob('*.jsonl')},
            'model':cfg.get('model',cfg.get('model_id')),'revision':cfg.get('revision')}
        if run.name.startswith(('E02-','E06-','E07-','E10-')) and cfg.get('n_per_seed')==300:
            if run.name.endswith('seed2-recovery'):
                out['incomplete_or_superseded'][run.name]={'status':'RECOVERY_SOURCE: evaluated only through verified three-seed join',**source};continue
            paths=sorted(run.glob('seed*.jsonl'))
            rows=[r for p in paths for r in read(p)]
            assert len(paths)==3 and len(rows)==900,(run.name,len(paths),len(rows))
            rr=reparse(rows);dest=derived/f'{run.name}.jsonl'
            if not dest.exists():dest.write_text(''.join(json.dumps(r|{'reparse_scorer_sha256':scorer_sha},ensure_ascii=False)+'\n' for r in rr))
            metrics=splits(rr);metrics.update(source,derived_path=str(dest),generation=cfg['generation'],
                format_only=bool(cfg.get('format_only_instruction')),seeds=cfg['seeds'])
            out['multi'][run.name]=metrics;multi_rows[run.name]=rr
        elif run.name=='E09-flan-multi':
            for condition in ['native','format']:
                rr=reparse([r for p in sorted(run.glob(condition+'-seed*.jsonl')) for r in read(p)])
                assert len(rr)==900
                name=run.name+'-'+condition;dest=derived/f'{name}.jsonl'
                if not dest.exists():dest.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rr))
                out['multi'][name]=splits(rr)|source|{'derived_path':str(dest),'format_only':condition=='format'};multi_rows[name]=rr
        elif cfg.get('task')=='hu':
            groups=defaultdict(list)
            for r in read(run/'predictions.jsonl'):groups[r['phenomenon']].append(r)
            out['hu'][run.name]={'source':source,'phenomena':{k:{'accuracy':cluster(v,lambda r:r['correct']),
                'prob_gold':cluster(v,lambda r:r['prob_true_answer']),'n_option_orders':len(v),
                'selected_labels':dict(__import__('collections').Counter(r['selected_label'] for r in v))} for k,v in groups.items()},
                'limits':'MCQ raw restricted intrinsic logits; no-story is ablation, not unlicensed control; Qwen2.5 default generation repetition policy differs from intrinsic logits'}
        elif cfg.get('task')=='wavelength':
            status='VALID_NUMERICAL_CONTROL' if run.name.endswith('fp32') or (cfg.get('dtype')=='float32' and cfg.get('numerical_gate_pass')) else 'SUPERSEDED_PRECISION_CONTROL'
            if run.name=='E15-wavelength-Qwen1.5-14B-Chat':
                cp=Path(__file__).resolve().parents[1]/'results/E15-numerical-controls.json'
                control=json.loads(cp.read_text())
                if cfg.get('dtype')=='float32' and all(q['batch_max_abs_logprob_delta']<.001 and q['argmax_same'] for q in control['wavelength']):status='VALID_NUMERICAL_CONTROL'
            if run.name=='E03-wavelength-qwen3-4b':status='VOID_THINKING_PROTOCOL'
            rows=read(run/'predictions.jsonl');assert len(rows)==cfg['n']
            metrics={k:cluster(rows,fn,lambda r:(r['source']['left'],r['source']['right'])) for k,fn in {
                'paper_mean_mae':lambda r:r['paper_absolute_error'],'parent_code_argmax_mae':lambda r:r['parent_code_argmax_error'],
                'wasserstein':lambda r:r['wasserstein'],'human_mae':lambda r:abs(r['human_mean']-float(r['source']['target']))}.items()}
            metrics.update(source,status=status,dtype=cfg.get('dtype'),
                pearson_human_mean=float(pearsonr([r['mean_prediction'] for r in rows],[r['human_mean'] for r in rows]).statistic))
            out['wavelength'][run.name]=metrics
        elif run.name.startswith('E08-') and (run/'predictions.jsonl').exists():
            rows=read(run/'predictions.jsonl');assert len(rows)==cfg['n']
            model_key='flan' if cfg['encoder_decoder'] else ('qwen3' if 'Qwen3-' in cfg['model'] else 'qwen25')
            control_name=f'E08-controls-{model_key}'+('-rightpad' if run.name.endswith('rightpad') else '')+'.json'
            cp=runs/control_name;control=json.loads(cp.read_text()) if cp.exists() else {}
            text_valid=(cfg.get('batch_parity_pass') is True) or (cfg['encoder_decoder'] and control.get('t5_text_batch_pass') is True)
            meta={'source':source,'dtype':cfg.get('dtype','float32' if cfg['encoder_decoder'] else 'bfloat16'),
                'dtype_provenance':'run config' if 'dtype' in cfg else 'legacy script policy; not retrospectively inserted into raw config',
                'letter_control_pass':control.get('letter_batch_pass'),
                'text_valid':text_valid,'text_batch_delta':cfg.get('batch_parity_max_abs_logprob_delta'),
                'controls_path':str(cp),'limits':'all readouts retain MCQ; copy/length/elicitation confounds; not direct knowledge or SDT','by_language':{}}
            for lang in sorted(set(r['language'] for r in rows)):
                rs=[r for r in rows if r['language']==lang]
                keys=['native_letter_prediction','format_letter_prediction','text_cumulative_prediction','text_per_token_prediction']
                meta['by_language'][lang]={p:{s:cluster(v,lambda r:r[p]==r['gold']) for s,v in {
                    'all':rs,'maxims':[r for r in rs if r['phenomenon']!='literal'],'literal':[r for r in rs if r['phenomenon']=='literal']}.items()} for p in keys}
            out['readout'][run.name]=meta
    # Predeclared paired item comparisons; preserve invalid as wrong + upper bound.
    for name,fmt in multi_rows.items():
        if not out['multi'][name]['format_only']:continue
        if name.startswith(('E06-','E10-')):native=name.replace('E06-','E02-').replace('E10-','E02-').removesuffix('-r1')
        elif name.startswith('E07-'):native=name.removesuffix('-format');native=native+'-joined' if native.endswith('korean') else native
        else:native=name.removesuffix('-format')+'-native'
        if native not in multi_rows:continue
        nr=multi_rows[native]
        for subset in ['all','maxims','literal']:
            get=lambda rs:[r for r in rs if subset=='all' or ((r['phenomenon']=='literal')==(subset=='literal'))]
            f=get(fmt);n=get(nr)
            groups=lambda rs:{i:np.mean([r['prediction']==r['gold'] for r in rs if r['item_id']==i]) for i in sorted(set(r['item_id'] for r in rs))}
            fg,ng=groups(f),groups(n);assert fg.keys()==ng.keys()
            out['paired_format_effect'].setdefault(name,{})[subset]=estimate([fg[i]-ng[i] for i in fg])|{'native_run':native,'format_run':name}
    ann=[]
    for run in sorted((a.root/'annotation').glob('E05-*')):
        if not (run/'annotations.jsonl').exists():continue
        cfg=json.loads((run/'config.json').read_text());rows=read(run/'annotations.jsonl');ann.append({r['item_id']:r['annotation'] for r in rows})
        out['recorded_gpu_hours']+=cfg.get('wall_seconds',0)/3600
        out['annotations'][run.name]={'n':len(rows),'schema_valid':sum(r['annotation'] is not None for r in rows)}
    if len(ann)==2:
        valid=[k for k in ann[0] if ann[0][k] and ann[1].get(k)]
        out['annotations']['agreement']={'joint_valid':len(valid),
            'licensing_disagreements':sum(ann[0][k]['inference_licensed']!=ann[1][k]['inference_licensed'] for k in valid),
            'option_class_disagreements':sum(ann[0][k]['option_classes'][c]!=ann[1][k]['option_classes'][c] for k in valid for c in 'ABCDE'),
            'ambiguous_either':sum(any(a[k]['inference_licensed']=='ambiguous' for a in ann) for k in valid),
            'status':'same-family drafts, not validated gold'}
    out['completed_primary_multi_responses']=sum(v['all']['n_responses'] for v in out['multi'].values())
    a.output.write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:len(out[k]) for k in ['multi','hu','wavelength','readout','annotations']}|{'responses':out['completed_primary_multi_responses']}))


if __name__=='__main__':main()
