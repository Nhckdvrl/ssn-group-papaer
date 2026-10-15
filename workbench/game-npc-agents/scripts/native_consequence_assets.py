#!/usr/bin/env python3
"""E74 measured resources, profile reuse verification and scientific exports."""
import argparse
from collections import Counter
import json
from pathlib import Path


def accounting(root, out):
    jobs = []
    for name in ['e74_profile_launch.json', 'e74_32b_profile_launch.json',
                 'e74_gemma_launch.json', 'e74_32b_launch.json']:
        metadata = json.loads((root/name).read_text())
        for job in metadata if isinstance(metadata, list) else [metadata]:
            folder = Path(job['cmd'][job['cmd'].index('--out')+1])
            runtime = json.loads((folder/'runtime.json').read_text())
            count = Counter()
            for r in map(json.loads, (folder/'model_calls.jsonl').open()):
                count.update(calls=1, parse_errors=int(bool(r['parse_error'])), prompt_tokens=r['prompt_tokens'],
                             completion_tokens=r['completion_tokens'])
                count['stage_'+r['stage']] += 1
            assert count['calls'] == runtime['calls'] and not runtime['new_cloud_calls']
            end = max((folder/'runtime.json').stat().st_mtime, folder.with_suffix('.log').stat().st_mtime)
            jobs.append({'folder':str(folder), 'host':job['host'], 'gpu':job['gpu'], 'pid':job['pid'],
                         'profile': 'profile' in folder.name, **dict(count),
                         'reused_calls':runtime['reused_calls'],
                         'model_load_and_inference_gpu_hours':(runtime['model_load_seconds']+runtime['wall_seconds'])/3600,
                         'observed_slot_hours':(end-job['start_epoch'])/3600})
    reuse = {}
    for model in ['gemma', '32b']:
        profile = root/f'e74_{model}_profile'; full = root/f'e74_{model}_s0'
        fields = {}
        for filename, keys in [('predictions.jsonl',['case_id','seed','persona','information']),
                               ('episodes.jsonl',['case_id','seed','persona','condition'])]:
            lookup = {tuple(r[k] for k in keys):r for r in map(json.loads,(full/filename).open())}
            original = list(map(json.loads,(profile/filename).open()))
            assert len(original) == 12
            for r in original: assert lookup[tuple(r[k] for k in keys)] == r
            fields[filename] = len(original)
        reuse[model] = fields
    totals = {k:sum(j.get(k,0) for j in jobs) for k in ['calls','parse_errors','prompt_tokens','completion_tokens',
             'stage_effects','stage_exec','reused_calls','model_load_and_inference_gpu_hours','observed_slot_hours']}
    result = {'status':'COMPLETE','experiment':'E74','source_worlds':117,
              'unique_prediction_contexts':2808,'unique_execution_branches':2808,'profile_exact_reuse':reuse,
              'jobs':jobs,'totals':totals,'new_cloud_calls':0,'peak_gpus':4,
              'scope':['Profile calls counted once, profile outputs not counted as additional independent cases.',
                       'Observed slot hours include CPU preparation, imports, load, inference and logged teardown.',
                       'One failed cache-preflight launch occurred before loading any model and made zero model calls.']}
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(totals))


def figures(results, out):
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from native_request_precondition_figures import save
    plt.rcParams.update({'font.size':10,'pdf.fonttype':42,'svg.fonttype':'none','svg.hashsalt':'game-npc-E74'})
    out.mkdir(exist_ok=True)
    fig, axes = plt.subplots(2,2,figsize=(12,7),layout='constrained')
    for i,(model,name) in enumerate([('gemma','Gemma 3 12B'),('32b','Qwen3 32B')]):
        d=json.loads((results/f'E74_{model}_complete.json').read_text())
        ax=axes[i,0]
        keys=['remove/exact','give_A/exact','remove_give_A/exact','remove_give_B/exact']
        for p,color,delta in [('firm','#4477AA',-.10),('agreeable','#AA3377',.10)]:
            vv=[d['prediction_cells'][p+'/divert_initial_feedback'][k] for k in keys]
            means=np.array([v['mean'] for v in vv])*100
            lo=np.array([v['graph_bootstrap_95'][0] for v in vv])*100
            hi=np.array([v['graph_bootstrap_95'][1] for v in vv])*100
            ax.errorbar(np.arange(len(keys))+delta,means,yerr=[means-lo,hi-means],fmt='o',color=color,capsize=3,label=p.capitalize())
        ax.set_xticks(np.arange(4),['Remove','Give A\nwhile equipped','Remove\nthen Give A','Remove\nthen Give B'])
        ax.set_ylabel('Exact physical prediction (%)');ax.set_title(name+' / initial mechanics information')
        ax=axes[i,1]
        conditions=['initial_feedback','self_forecast','native_forecast']
        for p,color,delta in [('firm','#4477AA',-.10),('agreeable','#AA3377',.10)]:
            vv=[d['execution_cells'][p+'/divert_'+c]['to_goal'] for c in conditions]
            means=np.array([v['mean'] for v in vv])*100
            lo=np.array([v['graph_bootstrap_95'][0] for v in vv])*100
            hi=np.array([v['graph_bootstrap_95'][1] for v in vv])*100
            ax.errorbar(np.arange(3)+delta,means,yerr=[means-lo,hi-means],fmt='o',color=color,capsize=3)
        ax.set_xticks(np.arange(3),['No table\n(E73)','Self-predicted\noutcome table','Native-true\noutcome table'])
        ax.set_ylabel('Executed Give to authored A (%)');ax.set_title(name+' / actual closed-loop execution')
    for ax in axes.flat:
        ax.set_ylim(0,104);ax.grid(axis='y',alpha=.2);ax.spines[['top','right']].set_visible(False)
    handles,labels=axes[0,0].get_legend_handles_labels();fig.legend(handles,labels,loc='outside upper center',ncol=2,frameon=False)
    fig.supxlabel('117 equipped worlds, diverting request B, three seeds; pointwise graph-cluster 95% intervals.\nElicited forecasts are task outputs, not direct hidden-belief measurements. Table comparisons preserve commands and format.',fontsize=10)
    save(fig,out,'E74_predictions_and_actual_actions')


def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True)
    a=sub.add_parser('cost');a.add_argument('--runs-root',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
    a=sub.add_parser('figures');a.add_argument('--results',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
    args=ap.parse_args()
    if args.mode=='cost':accounting(args.runs_root,args.out)
    else:figures(args.results,args.out)


if __name__=='__main__':main()
