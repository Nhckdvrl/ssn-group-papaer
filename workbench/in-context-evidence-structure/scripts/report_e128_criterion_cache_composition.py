"""Report the complete frozen E128 matrix; no model scoring or outcome selection."""
import hashlib,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
FROZEN='f0a0146708e193e017eb33a1caf955d8e4d4bf22d91d73abb403b500be92265a'
FAMILIES={'qwen3':'Qwen3-8B','mistral':'Mistral-7B-v0.3','llama':'Llama-3.1-8B','qwen14':'Qwen3-14B'}
WORLDS=['origin','service_negative','food_positive','food_negative']
def fmt(v,scale=100):return f"{scale*v['mean']:.2f} [{scale*v['ci95'][0]:.2f}, {scale*v['ci95'][1]:.2f}]"
def main():
    assert hashlib.sha256((ROOT/'scripts/e128_criterion_cache_composition.py').read_bytes()).hexdigest()==FROZEN
    runs={}
    for f in FAMILIES:
        for phase,n,seed,material in [('discovery',16,128001,'discovery'),('confirmation',32,128101,'validation')]:
            d=ROOT/'results/e128'/f'{f}_{phase}'
            run,analysis=[json.loads((d/name).read_text()) for name in ['run.json','analysis.json']]
            assert run['script_sha256']==FROZEN and analysis['n_contexts']==n
            assert run['args']['n']==n and run['args']['seed']==seed and run['args']['materials']==material
            assert (d/'contexts.jsonl').read_bytes()==(ROOT/'results/e128'/f'{f}_{phase}_preflight'/'contexts.jsonl').read_bytes()
            assert hashlib.sha256((d/'contexts.jsonl').read_bytes()).hexdigest()==run['contexts_sha256']
            rows=[json.loads(s) for s in (d/'behavior.jsonl').read_text().splitlines()]
            assert len(rows)==n and all(len(r['conditions'])==85 for r in rows)
            assert all(len(v['z'])==8 and len(v['label_logits'])==8 for r in rows for v in r['conditions'].values())
            assert len(run['all_layer_consumption'])==21 and len(run['query_layer_consumption'])==85
            for consumption in [run['all_layer_consumption'],run['query_layer_consumption']]:
                assert all(set(map(int,v))==set(range(run['num_layers'])) and set(v.values())=={n} for v in consumption.values())
            assert all(run[k]<=.001 for k in ['numeric_max_error','cache_no_op_max_error','composition_max_error','graph_zero_max_error'])
            assert abs(analysis['contrasts']['own_coherent_minus_mixed']['primary_scope']['mean'])<1e-10
            runs[f+'_'+phase]={'run':run,'analysis':analysis}
    total={'runs':8,'contexts':sum(r['analysis']['n_contexts'] for r in runs.values()),
           'scores':sum(r['analysis']['n_contexts']*85*8 for r in runs.values()),
           'gpu_hours':sum(r['run']['gpu_hours'] for r in runs.values()),
           'timer_scope':'completed scientific run timers including model loads; excludes CPU preflight, numeric-floor wait before entry and operational model transfer'}
    dest=ROOT/'results/e128'
    (dest/'summary.json').write_text(json.dumps({'scientific_script_sha256':FROZEN,
        'primary':'origin/different input criteria/same private code/discordant queries; joint coherent-minus-mixed full argmax',
        'unit':'context; equal sources; four discordant queries in primary','totals':total,'runs':runs},indent=2)+'\n')
    md=['# E128：同输出同code时的输入标准选择','',
        '两Source共享no/yes，A Food、B criterion×code四world；私人历史形成隔离、whole-query不直读公共schema。公共表仅改信息等价的行顺序，私人global位置不变；00/11共同形成背景与01/10混合背景全Source缓存组合。',
        f"\n8批/{total['contexts']}ctx/{total['scores']}评分，完整run计时{total['gpu_hours']:.6f}GPU·时；科学SHA {FROZEN}。",'',
        'primary origin：A Food/B Service、相同private code，4/8方面discordant query×两个Source；context配对coherent−mixed完整词表准确率。T为同一primary gold-margin的等价投影，非独立机制/输入过滤证据。', '',
        '| Model / phase | Primary, pp | T, nats | A primary, pp | B primary, pp | Private False / True primary, pp |',
        '|---|---:|---:|---:|---:|---:|']
    for phase in ['discovery','confirmation']:
        for f,label in FAMILIES.items():
            a=runs[f+'_'+phase]['analysis'];c=a['contrasts']['joint_coherent_minus_mixed'];t=a['functional_source_readout_contrasts']['joint_coherent_minus_mixed']['criterion_selectivity']
            md.append('| '+label+' / '+phase+' | '+' | '.join([fmt(a['primary_result']),fmt(t,1),fmt(c['primary_A']),fmt(c['primary_B']),fmt(a['primary_private_directions']['False'])+' / '+fmt(a['primary_private_directions']['True'])])+' |')
    for phase in ['confirmation','discovery']:
        md+=['',f'## {phase} 全缓存与函数能力','',
             '| Model | Cache/scope | Primary full% | All worlds full% | A full% | B full% | Candidate all% | In-label% | Margin all, nats |',
             '|---|---|---:|---:|---:|---:|---:|---:|']
        for f,label in FAMILIES.items():
            a=runs[f+'_'+phase]['analysis']
            for k,v in a['cache_accuracy'].items():
                md.append('| '+label+' | '+k+' | '+' | '.join([fmt(v[m]) for m in ['primary_scope','both','A','B','candidate','in_word_set']]+[fmt(v['margin'],1)])+' |')
        md+=['','### 四world全query secondary','',
            '| Model | Contrast | Service / same code (origin) | Service / opposite | Food / same | Food / opposite |','|---|---|---:|---:|---:|---:|']
        for f,label in FAMILIES.items():
            a=runs[f+'_'+phase]['analysis']
            for key in ['joint_coherent_minus_mixed','own_coherent_minus_mixed','joint_order11_minus_00','own_order11_minus_00']:
                md.append('| '+label+' | '+key+' | '+' | '.join(fmt(a['contrasts'][key][w]) for w in WORLDS)+' |')
        md+=['','### Origin函数响应与共同项','',
             '| Model | Cache/scope | T | A criterion selectivity | B criterion selectivity | common Food | common Service | abs common |','|---|---|---:|---:|---:|---:|---:|---:|']
        for f,label in FAMILIES.items():
            a=runs[f+'_'+phase]['analysis']
            for k,v in a['functional_source_readout'].items():
                md.append('| '+label+' | '+k+' | '+' | '.join(fmt(v[m],1) for m in ['criterion_selectivity','A_criterion_selectivity','B_criterion_selectivity','common_food','common_service','common_absolute'])+' |')
            for k,v in a['functional_source_readout_contrasts'].items():
                md.append('| '+label+' | delta '+k+' | '+' | '.join(fmt(v[m],1) for m in ['criterion_selectivity','A_criterion_selectivity','B_criterion_selectivity','common_food','common_service','common_absolute'])+' |')
        md+=['','### Native、纯一句指令与single功能','',
             '| Model | Condition | Full% | Candidate% | In-label% | Correct margin |','|---|---|---:|---:|---:|---:|']
        for f,label in FAMILIES.items():
            for k,v in runs[f+'_'+phase]['analysis']['conditions'].items():
                if 'cache' not in k:
                    md.append('| '+label+' | '+k+' | '+' | '.join([fmt(v[m]) for m in ['full_accuracy','candidate_accuracy','in_requested_word_set']]+[fmt(v['correct_margin'],1)])+' |')
    md+=['','各condition的完整Food/Service/bias/product与private方向、所有query logits保留在analysis/raw，不按结果删。own0为平衡设计恒等；whole-cache变化不识别新的ID/输入过滤。输入标准语义与固定方面位置尚未分离；标准相关输出变化仍允许已有binding/竞争检索。','']
    (dest/'report.md').write_text('\n'.join(md))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(1,4,figsize=(15.5,3.8),sharey=True)
    pairs=['00','01','10','11']
    for ax,(f,label) in zip(axes,FAMILIES.items()):
        a=runs[f+'_confirmation']['analysis']['cache_accuracy']
        for scope,color,marker in [('joint','#1768ac','o'),('own','#348243','s')]:
            v=[a['shared_cache'+p+'_'+scope]['primary_scope'] for p in pairs]
            y=np.array([100*x['mean'] for x in v]);err=np.array([[100*(x['mean']-x['ci95'][0]) for x in v],[100*(x['ci95'][1]-x['mean']) for x in v]])
            ax.errorbar(range(4),y,yerr=err,fmt=marker+'-',color=color,capsize=3,label=scope)
        ax.set_title(label);ax.set_xticks(range(4),['00\ncoherent','01\nmixed','10\nmixed','11\ncoherent']);ax.set_ylim(0,101);ax.grid(axis='y',alpha=.2)
    axes[0].set_ylabel('Criterion-conflict full accuracy (%)');axes[-1].legend(loc='lower right',fontsize=9)
    fig.suptitle('Same words and codes, different inferred input criteria (n=32)',fontsize=12);fig.tight_layout()
    for ext in ['png','pdf']:fig.savefig(ROOT/'results/figs'/f'fig_criterion_cache_compatibility.{ext}',dpi=180)
    plt.close(fig);print(json.dumps(total))
if __name__=='__main__':main()
