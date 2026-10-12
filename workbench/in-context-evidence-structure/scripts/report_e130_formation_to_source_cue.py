"""Complete report of the prospectively frozen E130 interface and formation policies."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
SHA='7ef59b3f853e1437dbffd11319ae1c1fe937ffa21723ac2b89bfe971e5a72973'
FAMILIES={'llama':'Llama-3.1-8B','qwen14':'Qwen3-14B'}
POLICIES=['independent','native','targeted']
def fmt(v,scale=1):
    high=max(abs(v['mean']),*(abs(x) for x in v['ci95']))
    if scale==1 and 0<high<.0001:return f"{v['mean']:.3e} [{v['ci95'][0]:.3e}, {v['ci95'][1]:.3e}]"
    d=5 if scale==1 else 2
    return f"{scale*v['mean']:.{d}f} [{scale*v['ci95'][0]:.{d}f}, {scale*v['ci95'][1]:.{d}f}]"
def main():
    assert hashlib.sha256((ROOT/'scripts/e130_formation_to_source_cue.py').read_bytes()).hexdigest()==SHA
    runs={}
    for f in FAMILIES:
        for phase,n,seed,material in [('discovery',16,130001,'discovery'),('confirmation',32,130101,'validation')]:
            d=ROOT/'results/e130'/f'{f}_{phase}'
            run,a=[json.loads((d/k).read_text()) for k in ['run.json','analysis.json']]
            assert run['script_sha256']==SHA and a['n_contexts']==n
            assert run['args']['seed']==seed and run['args']['materials']==material
            assert (d/'contexts.jsonl').read_bytes()==(ROOT/'results/e130'/f'preflight_{f}_{material}'/'contexts.jsonl').read_bytes()
            assert hashlib.sha256((d/'contexts.jsonl').read_bytes()).hexdigest()==run['contexts_sha256']
            raw=[json.loads(x) for x in (d/'behavior.jsonl').read_text().splitlines()]
            assert len(raw)==n and all(len(r['conditions'])==136 for r in raw)
            assert all(len(v['z'])==8 and len(v['label_logits'])==8 for r in raw for v in r['conditions'].values())
            for k,count in [('all_layer_consumption',21),('cue_layer_consumption',24),('query_layer_consumption',136)]:
                assert len(run[k])==count
                assert all(set(map(int,x))==set(range(run['num_layers'])) and set(x.values())=={n} for x in run[k].values())
            assert all(run[k]<=.001 for k in ['numeric_max_error','cache_no_op_max_error','composition_max_error','graph_zero_max_error'])
            runs[f+'_'+phase]={'run':run,'analysis':a}
    totals={'runs':4,'contexts':96,'scores':104448,'gpu_hours':sum(x['run']['gpu_hours'] for x in runs.values()),'timer_scope':'completed scientific single-GPU run timers, includes weights load, excludes import/floor wait'}
    dest=ROOT/'results/e130';summary={'source_sha256':SHA,'totals':totals,'co_primary_scope':'native donor policy, own-body, mean of per-recipient/context signed determinants','runs':runs}
    (dest/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    md=['# E130：历史共享如何准备Source条件的功能信号？','',
      '同一Source前输入Cue，从完整native、选择性answer→label阻断targeted、全部私人隔离independent三历史形成。全部移植到相同F0 recipient，Cue/body/token位置固定。两个co-primary只取native donor；三政策全部配对、来源与Code方向、两gold实际输出全部保留。','',
      f"4批/96ctx/104448评分，完整run{totals['gpu_hours']:.6f}GPU·时；源{SHA}；10000 context-bootstrap910。",'',
      '| Model / phase | native CueB det nats² | native Source-specific det nats² |','|---|---:|---:|']
    for phase in ['discovery','confirmation']:
        for f,label in FAMILIES.items():
            a=runs[f+'_'+phase]['analysis'];md.append('| '+label+' / '+phase+' | '+' | '.join(fmt(a['co_primary_results'][k]) for k in ['CueB','Source_specific'])+' |')
    for phase in ['confirmation','discovery']:
        md+=['',f'## {phase} 三种形成政策：两recipient/context先det后平均','',
          '| Model | policy / scope / Cue | det | Rotation | Food selectivity | Service selectivity | J |','|---|---|---:|---:|---:|---:|---:|']
        for f,label in FAMILIES.items():
            for k,v in runs[f+'_'+phase]['analysis']['contrasts'].items():md.append('| '+label+' | '+k+' | '+' | '.join(fmt(v[m]) for m in ['det','rotation','food_selectivity','service_selectivity','interaction'])+' |')
        md+=['','### 配对政策差（先context差，再CI）','',
         '| Model | paired policy / scope / Cue | det | Rotation | Food selectivity | Service selectivity | J |','|---|---|---:|---:|---:|---:|---:|']
        for f,label in FAMILIES.items():
            for k,v in runs[f+'_'+phase]['analysis']['formation_contrasts'].items():md.append('| '+label+' | '+k+' | '+' | '.join(fmt(v[m]) for m in ['det','rotation','food_selectivity','service_selectivity','interaction'])+' |')
        md+=['','### 完整功能矩阵','',
             '| Model | policy / recipient / Cue / scope | Food→Food | Food→Service | Service→Food | Service→Service |','|---|---|---:|---:|---:|---:|']
        for f,label in FAMILIES.items():
            for k,m in runs[f+'_'+phase]['analysis']['matrices'].items():md.append('| '+label+' | '+k+' | '+' | '.join(fmt(m[t][x]) for t in ['food','service'] for x in ['food','service'])+' |')
        md+=['','### 全136接口：recipient与donor实际函数','',
         '| Model | Condition | Recipient full% | Recipient conflict% | Recipient candidate% | Recipient margin | Donor full% | Donor conflict% | Donor candidate% | Donor margin |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
        for f,label in FAMILIES.items():
            for k,v in runs[f+'_'+phase]['analysis']['conditions'].items():
                fields=[fmt(v[m],100) for m in ['full_accuracy','discordant_full_accuracy','candidate_accuracy']]+[fmt(v['correct_margin'])]
                fields+=[fmt(v[m],1 if m=='donor_correct_margin' else 100) if m in v else '—' for m in ['donor_full_accuracy','donor_discordant_full_accuracy','donor_candidate_accuracy','donor_correct_margin']]
                md.append('| '+label+' | '+k+' | '+' | '.join(fields)+' |')
        md+=['','### 固定donor code的criterion-only方向','',
         '| Model | policy / recipient / Cue / scope / code | A-code Food−Service | donor-code Food−Service | Food | Service | Bias | FS |','|---|---|---:|---:|---:|---:|---:|---:|']
        for f,label in FAMILIES.items():
            for k,v in runs[f+'_'+phase]['analysis']['criterion_only'].items():md.append('| '+label+' | '+k+' | '+' | '.join(fmt(v['all'][m]) for m in ['A_code_Food_minus_Service_selectivity','donor_code_Food_minus_Service_selectivity','food','service','bias','food_service'])+' |')
        md+=['','### 全配对政策的recipient/donor函数差','',
         '| Model | paired policy / recipient / donor / Cue / scope | Recipient full pp | conflict pp | candidate pp | margin nats | Donor full pp | conflict pp | candidate pp | margin nats |','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
        for f,label in FAMILIES.items():
            for k,v in runs[f+'_'+phase]['analysis']['formation_performance_contrasts'].items():md.append('| '+label+' | '+k+' | '+' | '.join(fmt(v[m],1 if 'margin' in m else 100) for m in ['full_accuracy','discordant_full_accuracy','candidate_accuracy','correct_margin','donor_full_accuracy','donor_discordant_full_accuracy','donor_candidate_accuracy','donor_correct_margin'])+' |')
    md+=['','## 解释范围','',
      '两模型两个native确认co-primary均CI跨0，不确认完整criterion×code Cue运输；矩阵的匹配Food/Service方向与donor实际函数不可被差det替代。微小正、负与固定code方向保留，不能概括成没有标准信息或统一targeted修复。三形成政策的边数/质量不等，作用属于指定政策；whole-KV Cue不是单task vector或唯一程序。','',
      '单函数与native/targeted early/late全query功能逐接口保留；native/targeted的prepared-vs-whole forward数值控制实测经过，不拿0作假设。independent early/late还改变CueAll/bodyOwn与全queryOwn图。pure instruction保持native形成；actual full输出和candidate区别公开。','',
      'E129/130是有限输入前接口范围，不改变已确认关系形成/原生操作/函数政策的阳性。下一步E131跨大小模型检验原核心三环节，相同干预、同新材料小模型锚点，反映机制与使用的关系，不继续字段/头/强度搜索。','',
      '全部private方向、每recipient/Cue/scopes矩阵与配对政策CI在analysis.json；原raw/context不进git，路径与固定seed可重建。']
    (dest/'report.md').write_text('\n'.join(md)+'\n');print(json.dumps(totals))
if __name__=='__main__':main()
