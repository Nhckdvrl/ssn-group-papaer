"""Report every frozen E129 condition; no model calls or outcome selection."""
import hashlib,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
FROZEN='a177434cf425889df1fcc8b3607e6d5057a26080ad467e7999d002e6504b00bd'
FAMILIES={'llama':'Llama-3.1-8B','qwen14':'Qwen3-14B'}
RECIPIENTS=['origin','food_positive']
SCOPES=['own','joint']
def fmt(v,scale=1):
    if scale==1 and 0<max(abs(v['mean']),*(abs(x) for x in v['ci95']))<.0001:
        return f"{v['mean']:.3e} [{v['ci95'][0]:.3e}, {v['ci95'][1]:.3e}]"
    precision=5 if scale==1 else 2
    return f"{scale*v['mean']:.{precision}f} [{scale*v['ci95'][0]:.{precision}f}, {scale*v['ci95'][1]:.{precision}f}]"
def main():
    assert hashlib.sha256((ROOT/'scripts/e129_source_cue_task_information.py').read_bytes()).hexdigest()==FROZEN
    runs={}
    for f in FAMILIES:
        for phase,n,seed,material in [('discovery',16,129001,'discovery'),('confirmation',32,129101,'validation')]:
            d=ROOT/'results/e129'/f'{f}_{phase}'
            run,analysis=[json.loads((d/name).read_text()) for name in ['run.json','analysis.json']]
            assert run['script_sha256']==FROZEN and analysis['n_contexts']==n
            assert run['args']['n']==n and run['args']['seed']==seed and run['args']['materials']==material
            assert (d/'contexts.jsonl').read_bytes()==(ROOT/'results/e129'/f'{f}_{phase}_preflight'/'contexts.jsonl').read_bytes()
            assert hashlib.sha256((d/'contexts.jsonl').read_bytes()).hexdigest()==run['contexts_sha256']
            rows=[json.loads(s) for s in (d/'behavior.jsonl').read_text().splitlines()]
            assert len(rows)==n and all(len(r['conditions'])==64 for r in rows)
            assert all(len(v['z'])==8 and len(v['label_logits'])==8 for r in rows for v in r['conditions'].values())
            assert len(run['all_layer_consumption'])==17 and len(run['cue_layer_consumption'])==8 and len(run['query_layer_consumption'])==64
            for name in ['all_layer_consumption','cue_layer_consumption','query_layer_consumption']:
                assert all(set(map(int,v))==set(range(run['num_layers'])) and set(v.values())=={n} for v in run[name].values())
            assert all(run[k]<=.001 for k in ['numeric_max_error','cache_no_op_max_error','composition_max_error','graph_zero_max_error'])
            runs[f+'_'+phase]={'run':run,'analysis':analysis}
    total={'runs':4,'contexts':sum(r['analysis']['n_contexts'] for r in runs.values()),
           'scores':sum(r['analysis']['n_contexts']*64*8 for r in runs.values()),
           'gpu_hours':sum(r['run']['gpu_hours'] for r in runs.values()),
           'timer_scope':'completed scientific run timers including model loads; excludes CPU preflight and numeric-floor wait before entry'}
    dest=ROOT/'results/e129'
    (dest/'summary.json').write_text(json.dumps({'scientific_script_sha256':FROZEN,'primary':
        'within-context mean of two recipient determinants: CueB and CueB-minus-CueA; own body scope',
        'unit':'context; determinant computed before averaging recipient cases','totals':total,'runs':runs},indent=2)+'\n')
    md=['# E129：新输入之前的Source状态具有何种功能？','',
        'donor名字与B labelstream/输入多重集/位置固定，criterion×code四世界。Source Cue在测试输入前读取两组隔离形成的私人示例；仅整多层Cue K/V交换，recipient所有demo缓存保留。own主图body仅可读recipient B＋Cue＋HEAD；joint辅助可读两组。CueA/B在同recipient B位置/body图比较，identity×world非线性交互仍可发生。',
        f"\n4批/{total['contexts']}ctx/{total['scores']}评分，完整run计时{total['gpu_hours']:.6f}GPU·时；科学SHA {FROZEN}。",'',
        '两个co-primary均先对每recipient/context算signed det，再两个recipient等权平均，10000 context bootstrap。det是输出功能方向量，不等于latent rank；两行匹配选择性/实际donor函数必须共同看。两rank-one矩阵的差也可有正det，所以CueB本身co-primary不可省。','',
        '| Model / phase | CueB det, nats² | Source-specific det, nats² | Private False CueB / delta | Private True CueB / delta |','|---|---:|---:|---:|---:|']
    for phase in ['discovery','confirmation']:
        for f,label in FAMILIES.items():
            a=runs[f+'_'+phase]['analysis']
            md.append('| '+label+' / '+phase+' | '+' | '.join([fmt(a['co_primary_results']['CueB']),fmt(a['co_primary_results']['Source_specific'])]+[' / '.join(fmt(a['co_primary_private_directions'][direction][k]) for k in ['CueB','Source_specific']) for direction in ['False','True']])+' |')
    for phase in ['confirmation','discovery']:
        md+=['',f'## {phase} 功能矩阵与两种recipient','',
             '| Model | Recipient / Cue / scope | Food→Food | Food→Service | Service→Food | Service→Service |','|---|---|---:|---:|---:|---:|']
        for f,label in FAMILIES.items():
            a=runs[f+'_'+phase]['analysis']
            for k,m in a['matrices'].items():
                md.append('| '+label+' | '+k+' | '+' | '.join(fmt(m[t][feature]) for t in ['food','service'] for feature in ['food','service'])+' |')
        md+=['','### 方向、匹配选择性与尺度','',
             '| Model | Recipient / Cue / scope | det | Rotation | Food selectivity | Service selectivity | J |','|---|---|---:|---:|---:|---:|---:|']
        for f,label in FAMILIES.items():
            for k,v in runs[f+'_'+phase]['analysis']['matrix_statistics'].items():
                md.append('| '+label+' | '+k+' | '+' | '.join(fmt(v[m]) for m in ['det','rotation','food_selectivity','service_selectivity','interaction'])+' |')
        md+=['','### 全64条件：recipient与donor规则正确率','',
            '| Model | Condition | Recipient full% | Recipient conflict% | Recipient candidate% | Recipient margin | Donor full% | Donor conflict% | Donor margin |','|---|---|---:|---:|---:|---:|---:|---:|---:|']
        for f,label in FAMILIES.items():
            for k,v in runs[f+'_'+phase]['analysis']['conditions'].items():
                fields=[fmt(v[m],100) for m in ['full_accuracy','discordant_full_accuracy','candidate_accuracy']]+[fmt(v['correct_margin'])]
                fields+=[fmt(v[m],100 if m!='donor_correct_margin' else 1) if m in v else '—' for m in ['donor_full_accuracy','donor_discordant_full_accuracy','donor_correct_margin']]
                md.append('| '+label+' | '+k+' | '+' | '.join(fields)+' |')
    md+=['','native early/late保持原生形成与全部query读取，是字段次序参照。independent early Cue读两Source/body own，independent late全query own，不能将差值称纯次序效果。instruction保持原生形成，为纯一句提示。single每criterion/code与冲突域功能完整；所有private方向/feature basis/实际logits在analysis/raw保留。','',
        '阳性排除固定任务无关Source地址/共同一条输出方向作为完整解释，仍容许criterion-conditioned retrieval、prototype/task-vector、预训练方面能力与固定方面位置。前输入运输与冲突recipient任务覆盖的一般版本已被Hendel/JIT拥有；完整多层Cue不是单task vector或新组件。阴性也不证明模型没有criterion表示。','']
    (dest/'report.md').write_text('\n'.join(md))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,2,figsize=(10,7),sharey=True)
    for col,(f,label) in enumerate(FAMILIES.items()):
        a=runs[f+'_confirmation']['analysis']
        for row,(r,rlabel) in enumerate(zip(RECIPIENTS,['Recipient Service+','Recipient Food+'])):
            ax=axes[row,col]
            for i,(key,color) in enumerate([('cue1','#1768ac'),('source_specific','#c15725')]):
                m=a['matrices'][f'{r}_{key}_own'];v=[m[t][feature] for t in ['food','service'] for feature in ['food','service']]
                y=np.array([x['mean'] for x in v]);err=np.array([[x['mean']-x['ci95'][0] for x in v],[x['ci95'][1]-x['mean'] for x in v]])
                ax.errorbar(np.arange(4)+(-.09 if i==0 else .09),y,yerr=err,fmt='o',color=color,capsize=3,label='CueB' if i==0 else 'CueB−CueA')
            ax.axhline(0,color='black',lw=.7);ax.set_xticks(range(4),['F→F','F→S','S→F','S→S']);ax.set_title(label+' / '+rlabel,fontsize=10);ax.grid(axis='y',alpha=.2)
    axes[0,0].set_ylabel('Functional response (nats)');axes[1,0].set_ylabel('Functional response (nats)');axes[0,1].legend(fontsize=9)
    fig.suptitle('Pre-input cue transport with recipient evidence retained (own body, n=32)',fontsize=12)
    fig.tight_layout()
    for ext in ['png','pdf']:fig.savefig(ROOT/'results/figs'/f'fig_source_cue_functional_information.{ext}',dpi=180)
    plt.close(fig);print(json.dumps(total))
if __name__=='__main__':main()
