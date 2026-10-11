"""Report all E127 cache compositions; does not select or run model conditions."""
import hashlib
import json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
FROZEN='cef7952d4ef556abad45c9c2e6d6f351e3b0a1b3fffa9232b9eb728806c943de'
FAMILIES={'qwen3':'Qwen3-8B','mistral':'Mistral-7B-v0.3','llama':'Llama-3.1-8B','qwen14':'Qwen3-14B'}
def fmt(v,scale=100):
    return f"{scale*v['mean']:.2f} [{scale*v['ci95'][0]:.2f}, {scale*v['ci95'][1]:.2f}]"
def main():
    assert hashlib.sha256((ROOT/'scripts/e127_shared_output_cache_composition.py').read_bytes()).hexdigest()==FROZEN
    runs={}
    for family in FAMILIES:
        for phase,n,seed,mat in [('discovery',16,127001,'discovery'),('confirmation',32,127101,'validation')]:
            d=ROOT/'results/e127'/f'{family}_{phase}'
            run,analysis=[json.loads((d/name).read_text()) for name in ['run.json','analysis.json']]
            assert run['script_sha256']==FROZEN and analysis['n_contexts']==n
            assert run['args']['n']==n and run['args']['seed']==seed and run['args']['materials']==mat
            raw=[json.loads(x) for x in (d/'behavior.jsonl').read_text().splitlines()]
            assert len(raw)==n and all(len(r['conditions'])==86 for r in raw)
            assert all(len(v['z'])==8 for r in raw for v in r['conditions'].values())
            contexts=(d/'contexts.jsonl').read_bytes()
            assert contexts==(ROOT/'results/e127'/f'{family}_{phase}_preflight'/'contexts.jsonl').read_bytes()
            assert hashlib.sha256(contexts).hexdigest()==run['contexts_sha256']
            assert len(run['all_layer_consumption'])==22 and len(run['query_layer_consumption'])==86
            for consumption in [run['all_layer_consumption'],run['query_layer_consumption']]:
                assert all(set(map(int,v))==set(range(run['num_layers'])) and set(v.values())=={n} for v in consumption.values())
            assert all(run[k]<=.001 for k in ['numeric_max_error','cache_no_op_max_error','composition_max_error','graph_zero_max_error'])
            assert abs(analysis['contrasts']['shared_own_coherent_minus_mixed']['both']['mean'])<1e-10
            runs[family+'_'+phase]={'run':run,'analysis':analysis}
    total={'runs':8,'contexts':sum(r['analysis']['n_contexts'] for r in runs.values()),
        'scores':sum(r['analysis']['n_contexts']*86*8 for r in runs.values()),
        'gpu_hours':sum(r['run']['gpu_hours'] for r in runs.values()),
        'timer_scope':'completed scientific run timers; excludes preserved A100 partial run, zero-score load failure, startup reservation and cache transfer'}
    dest=ROOT/'results/e127'
    (dest/'summary.json').write_text(json.dumps({'scientific_script_sha256':FROZEN,
        'primary':'shared/opposite world joint coherent-minus-mixed full-vocabulary accuracy',
        'unit':'context; equal sources and eight queries', 'totals':total,'runs':runs},indent=2)+'\n')
    md=['# E127：共享输出下的私人规则缓存组合','',
        '四checkpoint固定16探索→32确认。shared与far使用同评论、私人code、Source名字与query；两个等价公共表行顺序形成00/11共同背景与01/10混合背景的全Source私人K/V。全历史private跨Source隔离，whole-query不直读表，保持原global位置。','',
        f"8批/{total['contexts']}contexts/{total['scores']}评分，完整run计时{total['gpu_hours']:.6f} GPU·时（不含保留的A100 partial、0-score加载失败/占位与模型暂存），科学SHA `{FROZEN}`。",'',
        '## 冻结primary与namespace参照','',
        'shared/opposite的完整输出为primary，其他world与far为冻结secondary。shared词本身不能辨Source；in-word-set不是来源选择证据。own-only平衡coherence0是设计恒等，逐Source/order实际功能另报。namespace改变词先验/集合区分度，不把ns差当纯identity机制。','',
        '| Model / phase | shared/opposite primary, pp | shared/all, pp | far/all, pp | shared/same, pp | shared minus far all interaction, pp |','|---|---:|---:|---:|---:|---:|']
    for phase in ['discovery','confirmation']:
        for family,label in FAMILIES.items():
            a=runs[family+'_'+phase]['analysis']; c=a['contrasts']
            md.append('| '+label+' / '+phase+' | '+' | '.join(fmt(v) for v in [a['primary_result'],
                c['shared_joint_coherent_minus_mixed']['both'],c['far_joint_coherent_minus_mixed']['both'],
                c['shared_joint_coherent_minus_mixed']['same'],c['shared_minus_far_joint_coherence']['both']])+' |')
    md+=['','## 预评分来源特异响应与共同偏移','',
        'far使用两词集合相对logsumexp的跨Source请求差/均值；shared只用opposite世界的goldA导向code logit差/均值。绝对共同项先逐query取abs再平均，避免正负抵消。两种读数定义不同，不跨namespace当同一指标相减。shared特异项是既有两Actor gold-margin的等价投影，非独立机制证据；均不识别binding ID。','',
        '| Model / phase | Namespace / scope | coherent-minus-mixed source-specific, logits | common signed | mean absolute common |','|---|---|---:|---:|---:|']
    for phase in ['confirmation','discovery']:
        for family,label in FAMILIES.items():
            a=runs[family+'_'+phase]['analysis']
            for ns in ['shared','far']:
                for scope in ['joint','own']:
                    v=a['functional_source_readout_contrasts'][ns+'_'+scope+'_coherent_minus_mixed']
                    md.append('| '+label+' / '+phase+' | '+ns+' / '+scope+' | '+' | '.join(fmt(v[m],1) for m in ['source_specific','source_common','source_common_absolute'])+' |')
        md+=['',f'## {phase} 全部缓存、请求来源与world','',
            '| Model | Namespace/cache/scope | full% | candidate% | in-word-set% | identifiable other-source word% | A full% | B full% | opposite% | same% |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
        for family,label in FAMILIES.items():
            a=runs[family+'_'+phase]['analysis']
            for k,v in a['cache_accuracy'].items():
                md.append('| '+label+' | '+k+' | '+' | '.join([fmt(v[m]) for m in ['both','candidate','in_word_set']]+[fmt(v['other_word']) if k.startswith('far_') else '不可识别']+[fmt(v[m]) for m in ['A','B','opposite','same']])+' |')
        md+=['','### Native、指令与私人single能力','',
             '| Model | condition | full% | candidate% | in-word-set% |','|---|---|---:|---:|---:|']
        for family,label in FAMILIES.items():
            for k,v in runs[family+'_'+phase]['analysis']['conditions'].items():
                if 'cache' not in k:
                    md.append('| '+label+' | '+k+' | '+' | '.join(fmt(v[m]) for m in ['full_accuracy','candidate_accuracy','in_requested_word_set'])+' |')
    md+=['','全部私人方向、B-code响应、每接口margin与source-common观测在analysis/summary保留。未按模型科学方向选择确认；实际每层mask/数值/gold与完整raw独立核对另附。whole-cache互换不分解latent；accuracy非线性也可产生配对效应。','']
    (dest/'report.md').write_text('\n'.join(md))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,4,figsize=(15.5,7.5),sharey=True)
    order=['00','01','10','11']
    for column,(family,label) in enumerate(FAMILIES.items()):
        a=runs[family+'_confirmation']['analysis']['cache_accuracy']
        for row,ns in enumerate(['shared','far']):
            ax=axes[row,column]
            for scope,color,marker in [('joint','#1768ac','o'),('own','#348243','s')]:
                vals=[a[ns+'_cache'+pair+'_'+scope] for pair in order]
                metric='opposite' if ns=='shared' else 'both'
                y=np.array([v[metric]['mean']*100 for v in vals])
                err=np.array([[100*(v[metric]['mean']-v[metric]['ci95'][0]) for v in vals],
                              [100*(v[metric]['ci95'][1]-v[metric]['mean']) for v in vals]])
                ax.errorbar(range(4),y,yerr=err,color=color,marker=marker,lw=1.5,capsize=3,label=scope+' full output')
                if ns=='far':ax.plot(range(4),[v['candidate']['mean']*100 for v in vals],ls='--',marker='x',color=color,alpha=.6,label=scope+' own candidates')
            ax.set_xticks(range(4),['00\ncoherent','01\nmixed','10\nmixed','11\ncoherent'])
            ax.set_title(label+' / '+('shared, opposite' if ns=='shared' else 'far, both worlds'));ax.set_ylim(0,101);ax.grid(axis='y',alpha=.2)
            if row==1:ax.set_xlabel('Formation-order pair (A, B)')
    axes[0,0].set_ylabel('Accuracy (%)');axes[1,0].set_ylabel('Accuracy (%)')
    axes[1,-1].legend(fontsize=8,loc='lower right')
    fig.suptitle('Private rule composition with shared and separate outputs (n=32)',fontsize=12)
    fig.tight_layout()
    for ext in ['png','pdf']:fig.savefig(ROOT/'results/figs'/f'fig_shared_output_cache_composition.{ext}',dpi=180)
    plt.close(fig)
    fig,axes=plt.subplots(1,2,figsize=(9.8,3.7),sharey=True)
    labels=list(FAMILIES.values())
    for ax,namespace,metric in [(axes[0],'shared','opposite'),(axes[1],'far','both')]:
        values=[runs[f+'_confirmation']['analysis']['contrasts'][namespace+'_joint_coherent_minus_mixed'][metric] for f in FAMILIES]
        means=np.array([v['mean']*100 for v in values]);err=np.array([[100*(v['mean']-v['ci95'][0]) for v in values],[100*(v['ci95'][1]-v['mean']) for v in values]])
        ax.errorbar(range(4),means,yerr=err,fmt='o',color='#1768ac',capsize=4)
        ax.axhline(0,color='#555555',lw=.8);ax.set_xticks(range(4),['Qwen\n8B','Mistral\n7B','Llama\n8B','Qwen\n14B'])
        ax.set_title('Shared words / opposite rules' if namespace=='shared' else 'Separate words / both rule worlds')
        ax.grid(axis='y',alpha=.2)
    axes[0].set_ylabel('Coherent minus mixed accuracy (pp)')
    fig.suptitle('Equivalent public facts, different private-cache compatibility (n=32)',fontsize=11)
    fig.tight_layout()
    for ext in ['png','pdf']:fig.savefig(ROOT/'results/figs'/f'fig_rule_and_wordspace_cache_compatibility.{ext}',dpi=180)
    plt.close(fig);print(json.dumps(total))
if __name__=='__main__':main()
