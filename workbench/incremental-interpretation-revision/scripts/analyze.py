"""Set-cluster paired bootstrap. Fixed prompt suite is averaged before sampling."""
import argparse
import collections
import json
from pathlib import Path
import numpy as np
from data import sha

def estimate(values):
    a=np.asarray(values,dtype=float)
    rng=np.random.default_rng(20261005)
    means=a[rng.integers(0,len(a),size=(10000,len(a)))].mean(axis=1)
    return {'estimate':float(a.mean()),'ci95':np.quantile(means,[.025,.975]).tolist(),'n_sets':len(a)}

def e00(rows):
    def group_stats(sub):
        sets=collections.defaultdict(lambda:collections.defaultdict(list))
        for r in sub:sets[r['pair_id']][(r['condition'],r['question_type'])].append(r)
        out={}
        for metric in ('correct','p_correct','choice_mass'):
            avg={sid:{k:float(np.mean([r[metric] for r in rr])) for k,rr in cells.items()} for sid,cells in sets.items()}
            if not avg:continue
            for c in ('gp','non_gp'):
                for q in ('simple','lingering'):
                    out[f'{metric}/{c}/{q}']=estimate([d[(c,q)] for d in avg.values()])
            for q in ('simple','lingering'):
                out[f'{metric}/nonGP_minus_GP/{q}']=estimate([d[('non_gp',q)]-d[('gp',q)] for d in avg.values()])
            out[f'{metric}/specificity_DiD']=estimate([d[('non_gp','lingering')]-d[('gp','lingering')]-d[('non_gp','simple')]+d[('gp','simple')] for d in avg.values()])
        return out
    suites={'upstream_16':[r for r in rows if r['prompt_id'].startswith('raw_') and not r['prompt_id'].endswith('repeat')],
            'native_chat':[r for r in rows if r['prompt_id'].startswith('chat_') and not r['prompt_id'].endswith('repair')],
            'native_chat_repair':[r for r in rows if r['prompt_id'].endswith('repair')]}
    out={'suites':{},'by_prompt':{},'subtypes':{},'repeat':{},'decision':'not evaluated'}
    for name,rr in suites.items():
        out['suites'][name]=group_stats(rr)
        out['subtypes'][name]={t:group_stats([r for r in rr if r['subtype']==t]) for t in sorted({r['subtype'] for r in rr})}
    for pid in sorted({r['prompt_id'] for r in rows}):out['by_prompt'][pid]=group_stats([r for r in rows if r['prompt_id']==pid])
    effects=[v['correct/nonGP_minus_GP/lingering']['estimate'] for pid,v in out['by_prompt'].items() if pid.startswith('raw_') and not pid.endswith('repeat')]
    out['prompt_effect_variation']={'min':min(effects),'max':max(effects),'sd':float(np.std(effects)),
                                    'range':max(effects)-min(effects)}
    original={r['item_id']:r for r in rows if r['prompt_id']=='raw_reg_0'}
    repeat={r['item_id']:r for r in rows if r['prompt_id']=='raw_reg_0_repeat'}
    out['repeat']={'max_probability_delta':max(abs(original[k]['p_yes']-repeat[k]['p_yes']) for k in original),
                   'accuracy_flips':sum(original[k]['correct']!=repeat[k]['correct'] for k in original)}
    for metric in ('correct','p_correct'):
        order_deltas=[]
        for pi in range(8):
            a=out['by_prompt'][f'raw_reg_{pi}'][f'{metric}/nonGP_minus_GP/lingering']['estimate']
            b=out['by_prompt'][f'raw_rev_{pi}'][f'{metric}/nonGP_minus_GP/lingering']['estimate']
            order_deltas.append(a-b)
        out[f'{metric}_order_effect_deltas']=order_deltas
    primary=out['suites']['upstream_16']['correct/nonGP_minus_GP/lingering']
    specificity=out['suites']['upstream_16']['correct/specificity_DiD']
    out['gate_inputs']={'primary':primary,'specificity':specificity,'prompt_variation':out['prompt_effect_variation'],
                        'all_prompt_effects_positive':min(effects)>0}
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('predictions',type=Path);ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--experiment',default='E00');args=ap.parse_args()
    rows=[json.loads(line) for line in args.predictions.read_text().splitlines()]
    config_path=args.predictions.parent/'config.json'
    if config_path.exists():
        config=json.loads(config_path.read_text())
        assert config.get('predictions_sha256')==sha(args.predictions),'Run is unfinished or predictions changed; wait for inference completion'
        assert len(rows)==config['task_count'],'incomplete task coverage'
    if args.experiment in ('E00','E04'):result=e00(rows)
    elif args.experiment=='E03':
        from order_audit import analyze_order
        result=analyze_order(rows)
    elif args.experiment=='E05':
        from response_audit import analyze_response
        result=analyze_response(rows)
    elif args.experiment=='E06':
        from attachment_audit import analyze_attachment
        result=analyze_attachment(rows)
    elif args.experiment=='E07':
        from native_audit import analyze_native
        result=analyze_native(rows)
    elif args.experiment=='E08':
        from focus_audit import analyze_focus
        result=analyze_focus(rows)
    elif args.experiment=='E09':
        from sap import analyze_sap
        result=analyze_sap(rows)
    elif args.experiment=='E10':
        from option_access import analyze_access
        result=analyze_access(rows)
    elif args.experiment=='E11':
        from role_reference import analyze_reference
        result=analyze_reference(rows)
    else:
        from revision_map import analyze_revision
        result=analyze_revision(rows)
    result.update(predictions_sha256=sha(args.predictions),row_count=len(rows),bootstrap_seed=20261005,bootstrap_draws=10000)
    result['analysis_code_sha256']={p.name:sha(p) for p in Path(__file__).parent.glob('*.py') if p.name in ('analyze.py','focus_audit.py','native_audit.py','revision_map.py','sap.py','option_access.py','role_reference.py')}
    args.out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result.get('gate_inputs',{}),indent=2))

if __name__=='__main__':main()
