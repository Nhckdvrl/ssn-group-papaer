"""Report all E126 cache compositions; does not select or run model conditions."""
import hashlib
import json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
FROZEN='ad2c6f7af7ab81966ea1253a80e7006747f3485b182fddd1453ffbb1ceb45975'
FAMILIES={'qwen3':'Qwen3-8B','mistral':'Mistral-7B-v0.3','llama':'Llama-3.1-8B'}
def fmt(v,scale=100):
    return f"{scale*v['mean']:.2f} [{scale*v['ci95'][0]:.2f}, {scale*v['ci95'][1]:.2f}]"
def main():
    assert hashlib.sha256((ROOT/'scripts/e126_equivalent_schema_cache_composition.py').read_bytes()).hexdigest()==FROZEN
    runs={}
    for family in FAMILIES:
        for phase,n,seed,mat in [('discovery',16,126001,'discovery'),('confirmation',32,126101,'validation')]:
            d=ROOT/'results/e126'/f'{family}_{phase}'
            run,analysis=[json.loads((d/name).read_text()) for name in ['run.json','analysis.json']]
            assert run['script_sha256']==FROZEN and analysis['n_contexts']==n
            assert run['args']['n']==n and run['args']['seed']==seed and run['args']['materials']==mat
            raw=[json.loads(x) for x in (d/'behavior.jsonl').read_text().splitlines()]
            assert len(raw)==n and all(len(r['conditions'])==43 for r in raw)
            assert all(len(v['z'])==8 for r in raw for v in r['conditions'].values())
            contexts=(d/'contexts.jsonl').read_bytes()
            assert contexts==(ROOT/'results/e126'/f'{family}_{phase}_preflight'/'contexts.jsonl').read_bytes()
            assert hashlib.sha256(contexts).hexdigest()==run['contexts_sha256']
            assert len(run['all_layer_consumption'])==11 and len(run['query_layer_consumption'])==43
            for consumption in [run['all_layer_consumption'],run['query_layer_consumption']]:
                assert all(set(map(int,v))==set(range(run['num_layers'])) and set(v.values())=={n} for v in consumption.values())
            assert all(run[k]<=.001 for k in ['numeric_max_error','cache_no_op_max_error','composition_max_error','graph_zero_max_error'])
            assert abs(analysis['contrasts']['own_coherent_minus_mixed']['both']['mean'])<1e-10
            runs[family+'_'+phase]={'run':run,'analysis':analysis}
    total={'runs':6,'contexts':sum(r['analysis']['n_contexts'] for r in runs.values()),
        'scores':sum(r['analysis']['n_contexts']*43*8 for r in runs.values()),
        'gpu_hours':sum(r['run']['gpu_hours'] for r in runs.values())}
    dest=ROOT/'results/e126'
    (dest/'summary.json').write_text(json.dumps({'scientific_script_sha256':FROZEN,'primary':'full-vocabulary next-token accuracy',
        'unit':'context; equal weights over worlds, sources and eight queries','totals':total,'runs':runs},indent=2)+'\n')
    md=['# E126：信息等价形成背景与私人规则记忆的组合','',
        '三checkpoint固定16探索→32确认。两公共表含完全相同Source–输出词事实，只反转行顺序；private tokens/位置/gold全不变。形成跨Source私人访问全部关闭，whole-query每层不读公共表。A/B全部private K/V合成00/11（coherent）与01/10（mixed），公共cache取0。','',
        f"6批/{total['contexts']}contexts/{total['scores']}评分，记录{total['gpu_hours']:.6f} GPU·时，科学SHA `{FROZEN}`。",'',
        '## 冻结主对比：coherent − mixed','',
        '.5[(00+11)−(01+10)]在同context/world/Actor/query配对，抵消单缓存加性的质量差；positive不自动识别bindingID，共同读取时范数/显著性/其它非加性解释仍可存在。own-only对比为设计恒等式与数值检查，不能当科研双分离。','',
        '| Model / phase | joint完整词表pp | joint候选pp | joint来源词率pp | joint正确margin nats | own-only完整词表pp |','|---|---:|---:|---:|---:|---:|']
    for phase in ['discovery','confirmation']:
        for family,label in FAMILIES.items():
            c=runs[family+'_'+phase]['analysis']['contrasts'];j=c['joint_coherent_minus_mixed']
            md.append('| '+label+' / '+phase+' | '+' | '.join([fmt(j['both']),fmt(j['candidate']),fmt(j['source_word']),fmt(j['margin'],1),fmt(c['own_coherent_minus_mixed']['both'])])+' |')
    for phase in ['confirmation','discovery']:
        md+=['',f'## {phase} 全部组合与Actor','',
             '| Model | cache/scope | 完整词表% | 候选% | 来源词率% | other词率% | A full% | B full% |','|---|---|---:|---:|---:|---:|---:|---:|']
        for family,label in FAMILIES.items():
            a=runs[family+'_'+phase]['analysis']
            for k,v in a['cache_accuracy'].items():
                md.append('| '+label+' | '+k+' | '+' | '.join(fmt(v[m]) for m in ['both','candidate','source_word','other_word','A','B'])+' |')
        md+=['','### 私人功能/native/一句指令参照','',
             '| Model | condition | full% | candidate% | other词率% |','|---|---|---:|---:|---:|']
        for family,label in FAMILIES.items():
            for k,v in runs[family+'_'+phase]['analysis']['conditions'].items():
                if 'cache' not in k:
                    md.append('| '+label+' | '+k+' | '+' | '.join(fmt(v[m]) for m in ['full_accuracy','candidate_accuracy','other_word_rate'])+' |')
    md+=['','所有same/opposite/私人方向、margin、B-code signed/absolute功能读数在analysis/summary保留，主读数未在看结果后更改。完整图、token/gold/actual每层mask与raw独立审计另附；未把private监督隔离称隐私保护，query仍共同读取两个Source。新上下文/名字不构成新benchmark。','']
    (dest/'report.md').write_text('\n'.join(md))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,3,figsize=(12.5,3.9),sharey=True)
    order=['00','01','10','11']
    for ax,(family,label) in zip(axes,FAMILIES.items()):
        a=runs[family+'_confirmation']['analysis']['cache_accuracy']
        for scope,color,marker in [('joint','#1768ac','o'),('own','#348243','s')]:
            vals=[a['cache'+pair+'_'+scope] for pair in order]
            y=np.array([v['both']['mean']*100 for v in vals])
            err=np.array([[100*(v['both']['mean']-v['both']['ci95'][0]) for v in vals],
                          [100*(v['both']['ci95'][1]-v['both']['mean']) for v in vals]])
            ax.errorbar(range(4),y,yerr=err,color=color,marker=marker,lw=1.5,capsize=3,label=scope+' full output')
            ax.plot(range(4),[v['candidate']['mean']*100 for v in vals],ls='--',marker='x',color=color,alpha=.6,label=scope+' own candidates')
        ax.set_xticks(range(4),['00\ncoherent','01\nmixed','10\nmixed','11\ncoherent'])
        ax.set_xlabel('Formation-order pair (A, B)');ax.set_title(label)
        ax.set_ylim(0,101);ax.grid(axis='y',alpha=.2)
    axes[0].set_ylabel('Accuracy (%)');axes[-1].legend(fontsize=8,loc='lower right')
    fig.suptitle('Equivalent public facts, separately formed private rules (n=32)',fontsize=11)
    fig.tight_layout()
    for ext in ['png','pdf']:fig.savefig(ROOT/'results/figs'/f'fig_equivalent_schema_cache_composition.{ext}',dpi=180)
    plt.close(fig);print(json.dumps(total))
if __name__=='__main__':main()
