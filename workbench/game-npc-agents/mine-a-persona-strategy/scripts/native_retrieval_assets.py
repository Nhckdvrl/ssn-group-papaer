#!/usr/bin/env python3
"""E75 resource accounting and static figures from completed, fixed experiments."""
import argparse
from collections import Counter
import json
from pathlib import Path


def cost(root,out,experiment='E75'):
    prefix=experiment.lower();is_fixed=experiment=='E76';profile_size=6 if is_fixed else 24
    jobs=[]
    for model in ['gemma','32b']:
        for suffix in ['profile_launch','launch']:
            metadata=json.loads((root/f'{prefix}_{model}_{suffix}.json').read_text())
            for job in metadata if isinstance(metadata,list) else [metadata]:
                folder=Path(job['cmd'][job['cmd'].index('--out')+1]);rt=json.loads((folder/'runtime.json').read_text())
                counts=Counter()
                for r in map(json.loads,(folder/'model_calls.jsonl').open()):
                    counts.update(calls=1,parse_errors=int(bool(r['parse_error'])),prompt_tokens=r['prompt_tokens'],
                                  completion_tokens=r['completion_tokens']);counts['stage_'+r['stage']]+=1
                assert counts['calls']==rt['calls'] and rt['new_cloud_calls']==0
                end=max((folder/'runtime.json').stat().st_mtime,folder.with_suffix('.log').stat().st_mtime)
                jobs.append({'folder':str(folder),'model':model,'profile':suffix.startswith('profile'),
                             'gpu':job['gpu'],'pid':job['pid'],'host':job['host'],**dict(counts),
                             'reused_calls':rt['reused_calls'],
                             'load_and_inference_gpu_hours':(rt['wall_seconds']+rt['model_load_seconds'])/3600,
                             'observed_slot_hours':(end-job['start_epoch'])/3600})
        original=list(map(json.loads,(root/f'{prefix}_{model}_profile/episodes.jsonl').open()))
        full_folder=root/(f'{prefix}_{model}' if is_fixed else f'{prefix}_{model}_s0')
        full={tuple(r[k] for k in ['case_id','seed','persona','condition']):r
              for r in map(json.loads,(full_folder/'episodes.jsonl').open())}
        assert len(original)==profile_size
        for r in original:assert full[tuple(r[k] for k in ['case_id','seed','persona','condition'])]==r
    keys=['calls','parse_errors','prompt_tokens','completion_tokens','stage_conv','stage_exec','reused_calls',
          'load_and_inference_gpu_hours','observed_slot_hours']
    totals={k:sum(j.get(k,0) for j in jobs) for k in keys}
    result={'status':'COMPLETE','experiment':experiment,'source_worlds':102,
            'unique_execution_branches':1224 if is_fixed else 4896,
            'profile_exactly_reused_branches':profile_size*2,'jobs':jobs,'totals':totals,
            'peak_gpus':2 if is_fixed else 4,'new_cloud_calls':0,
            'scope':['Profile actual calls counted once; full-shard logical reuse is not extra independent evidence.',
                     'Observed slot includes CPU imports, model load, inference and logged teardown.',
                     'Owned-container and retrieval eligibility/input controls used no model/GPU.']}
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(totals))


def figure(results,out):
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from native_request_precondition_figures import save
    plt.rcParams.update({'font.size':10,'pdf.fonttype':42,'svg.fonttype':'none','svg.hashsalt':'game-npc-E75'})
    fig,axes=plt.subplots(2,2,figsize=(12,7.5),layout='constrained')
    conditions=['ready_baseline','retrieval_baseline','ready_paths','retrieval_paths']
    metrics=[('goal','Authored task event','#4477AA'),('request','Give to requester','#EE7733'),
             ('other_source_give','Other source-item Give','#AA3377'),('no_decisive_event','No decisive event','#BBBBBB')]
    for i,(model,label) in enumerate([('gemma','Gemma 3 12B'),('32b','Qwen3 32B')]):
        result=json.loads((results/f'E75_{model}_complete.json').read_text())
        for j,(group,name) in enumerate([('source_give','Give tasks'),('source_use','Wear / Eat / Drink tasks')]):
            d=result['groups'][group];ax=axes[i,j]
            order=[p+'/'+c for c in conditions for p in ['firm','agreeable']]
            x=np.array([3*k+n for k in range(4) for n in range(2)]);bottom=np.zeros(8)
            for field,title,color in metrics:
                values=np.array([d['cells'][k][field]['mean'] for k in order])*100
                ax.bar(x,values,bottom=bottom,width=.85,color=color,label=title);bottom+=values
            assert np.allclose(bottom,100)
            vv=[d['cells'][k]['goal'] for k in order];mean=np.array([v['mean'] for v in vv])*100
            lo=np.array([v['graph_bootstrap_95'][0] for v in vv])*100
            hi=np.array([v['graph_bootstrap_95'][1] for v in vv])*100
            ax.errorbar(x,mean,yerr=[mean-lo,hi-mean],color='#222222',fmt='none',capsize=2,lw=1)
            ax.set_xticks(x,['F','A']*4)
            for k,text in enumerate(['Ready\nbaseline','Needs Get\nbaseline','Ready\nboth paths','Needs Get\nboth paths']):
                ax.text(3*k+.5,-.10,text,ha='center',va='top',transform=ax.get_xaxis_transform())
            ax.set_title(label+' / '+name+f' (N={d["worlds"]})');ax.set_ylim(0,103)
            ax.set_ylabel('Actual first decisive outcome (%)');ax.grid(axis='y',alpha=.15)
            ax.spines[['top','right']].set_visible(False)
    handles,labels=axes[0,0].get_legend_handles_labels()
    fig.legend(handles,labels,loc='outside upper center',ncol=4,frameon=False)
    fig.supxlabel('F = Firm; A = Agreeable. Original retrieval states; ready is a native-Get counterfactual.\nThree seeds per source graph. Whiskers: pointwise graph-cluster 95% intervals for the authored-task outcome.',fontsize=10)
    out.mkdir(parents=True,exist_ok=True);save(fig,out,'E75_task_request_joint_outcomes')


def fixed_figure(results,out):
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from native_request_precondition_figures import save
    plt.rcParams.update({'font.size':10,'pdf.fonttype':42,'svg.fonttype':'none','svg.hashsalt':'game-npc-E76'})
    fig,axes=plt.subplots(2,2,figsize=(12,7.2),layout='constrained',sharey='row')
    conditions=['retrieval_baseline','ready_frozen_dialogue','ready_baseline']
    labels=['Dialogue: floor\nExecution: floor','Same dialogue\nExecution: inventory','Dialogue: inventory\nExecution: inventory']
    for j,(model,title) in enumerate([('gemma','Gemma 3 12B'),('32b','Qwen3 32B')]):
        result=json.loads((results/f'E76_{model}_complete.json').read_text())
        for i,(group,subtitle) in enumerate([('all','All tasks'),('source_use','Wear / Eat / Drink')]):
            d=result['groups'][group];ax=axes[i,j]
            for metric,name,color,offset in [('goal','Authored task','#4477AA',-.08),('request','Give to requester','#EE7733',.08)]:
                vv=[d['contrasts']['A_minus_F/'+c][metric] for c in conditions]
                y=np.array([v['mean'] for v in vv])*100
                lo=np.array([v['graph_bootstrap_95'][0] for v in vv])*100
                hi=np.array([v['graph_bootstrap_95'][1] for v in vv])*100
                ax.errorbar(np.arange(3)+offset,y,yerr=[y-lo,hi-y],fmt='o',color=color,capsize=3,label=name)
            ax.set_xticks(np.arange(3),labels,fontsize=9);ax.axhline(0,color='#444444',lw=1)
            ax.set_ylabel('Agreeable − Firm (pp)');ax.set_title(title+' / '+subtitle+f' (N={d["worlds"]})')
            ax.grid(axis='y',alpha=.2);ax.spines[['top','right']].set_visible(False)
    handles,legend=axes[0,0].get_legend_handles_labels();fig.legend(handles,legend,loc='outside upper center',ncol=2,frameon=False)
    fig.supxlabel('Middle condition reuses the exact dialogue from the floor state; only native execution start changes.\nThree seeds per source graph; pointwise graph-cluster 95% intervals. This is one added counterfactual cell.',fontsize=10)
    out.mkdir(parents=True,exist_ok=True);save(fig,out,'E76_fixed_dialogue_access_effects')


def main():
    ap=argparse.ArgumentParser();sub=ap.add_subparsers(dest='mode',required=True)
    p=sub.add_parser('cost');p.add_argument('--runs-root',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p.add_argument('--experiment',choices=['E75','E76'],default='E75')
    p=sub.add_parser('figure');p.add_argument('--results',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    p=sub.add_parser('fixed-figure');p.add_argument('--results',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    if a.mode=='cost':cost(a.runs_root,a.out,a.experiment)
    elif a.mode=='fixed-figure':fixed_figure(a.results,a.out)
    else:figure(a.results,a.out)


if __name__=='__main__':main()
