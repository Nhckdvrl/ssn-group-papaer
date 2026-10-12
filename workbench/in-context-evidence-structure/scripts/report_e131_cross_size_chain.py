"""Report the fixed E131 chain and fresh context-paired size comparisons.

Reads completed stages only; does not change scores or inherited analyses.
"""
import hashlib,json
from pathlib import Path
import numpy as np
from e123_wave_report import output_metrics
from e118_criterion_code_feature_crossing import interval

ROOT=Path(__file__).resolve().parents[1]
MODELS={'qwen3':'Qwen3-8B','qwen32':'Qwen3-32B',
        'llama':'Llama-3.1-8B','llama70':'Llama-3.1-70B'}
STAGES={'mechanism':43,'native':64,'function':85}
def fmt(x,scale=1):
    return f"{x['mean']*scale:.4f} [{x['ci95'][0]*scale:.4f},{x['ci95'][1]*scale:.4f}]"
def pairs(stage,raw):
    """The predeclared core readouts, in context order, without model fitting."""
    z={k:np.asarray([r['conditions'][k]['z'] for r in raw]) for k in raw[0]['conditions']}
    result={}
    if stage in ['mechanism','native']:
        gold=np.asarray([r['gold'] for r in raw])
        if stage=='mechanism':
            d={s:((z['cross_'+s]-z['origin_'+s])*gold).mean(1)
               for s in ['f0r0','f1r0','f0r1','label_r0','edge_k_r0','edge_kv_r0']}
            for name,left,right in [('A_formation','f0r0','f1r0'),('B_reading','f0r0','f0r1'),
                    ('label_interface','f0r0','label_r0'),('answer_K','f0r0','edge_k_r0')]:
                result[name+'_signed']=d[left]-d[right]
                result[name+'_absolute']=abs(d[left])-abs(d[right])
            base=z['origin_f0r0']
            effects={s:((z[s]-base)*gold).mean(1) for s in [
                'relation_answer_cross_kv_native','relation_answer_within_kv_native']}
            result['answer_relation_signed']=effects['relation_answer_cross_kv_native']-effects['relation_answer_within_kv_native']
            result['answer_relation_absolute']=abs(effects['relation_answer_cross_kv_native'])-abs(effects['relation_answer_within_kv_native'])
        else:
            for scope in ['native','gate']:
                d={op:((z[f'cross_shared_{op}_{scope}']-z[f'origin_shared_{op}_{scope}'])*gold).mean(1)
                   for op in ['native','cross_answer_off','all_B_off','answer_only_restore']}
                for name,l,r in [('answer_removal','native','cross_answer_off'),
                        ('restricted_restore','answer_only_restore','all_B_off')]:
                    result[scope+'_'+name+'_signed']=d[l]-d[r]
                    result[scope+'_'+name+'_absolute']=abs(d[l])-abs(d[r])
    else:
        for readout in ['candidate','full']:
            aggregate={}
            for policy in ['normal','answer_cross_off','all_cross_off']:
                for scope in ['native','gate']:
                    def correct(r,w,owner):
                        c=r['conditions'][f'{w}_shared_{policy}_{scope}_{owner}']
                        return c['argmax_correct'] if readout=='full' else (np.asarray(c['z'])>0)==(np.asarray(c['gold'])>0)
                    v=np.asarray([[[correct(r,w,o) for o in [0,1]] for w in ['origin','cross']] for r in raw],float)
                    aggregate[policy,scope]=v.mean((1,2,3))
                    result[f'{readout}_{policy}_{scope}_both']=aggregate[policy,scope]
            for name,l,r in [('targeted_gain',('answer_cross_off','native'),('normal','native')),
                    ('targeted_minus_all',('answer_cross_off','native'),('all_cross_off','native')),
                    ('query_isolation',('normal','gate'),('normal','native'))]:
                result[readout+'_'+name]=aggregate[l]-aggregate[r]
    return result

def main():
    dest=ROOT/'results/e131';manifest=json.loads((dest/'engine_parent_manifest.json').read_text())
    planned=[f'{f}_{p}_{s}' for f in MODELS for p in (['confirmation'] if f in ['qwen3','llama'] else ['discovery','confirmation']) for s in STAGES]
    runs={};raws={}
    for name in planned:
        d=dest/name
        if not (d/'run.json').exists() or not (d/'analysis.json').exists():continue
        run=json.loads((d/'run.json').read_text())
        if 'matmul_allow_tf32' not in run:continue # protocol has not finalized this stage
        stage=run['stage'];n=run['args']['n'];raw=[json.loads(x) for x in (d/'behavior.jsonl').read_text().splitlines()]
        assert len(raw)==n and all(len(r['conditions'])==STAGES[stage] for r in raw)
        assert run['script_sha256']==manifest[stage]['engine_sha256']
        assert run['matmul_allow_tf32'] is False and run['dtype']=='float32'
        assert (d/'contexts.jsonl').read_bytes()==(dest/('preflight_'+name)/'contexts.jsonl').read_bytes()
        assert hashlib.sha256((d/'contexts.jsonl').read_bytes()).hexdigest()==run['contexts_sha256']
        assert run['numeric_max_error']<=.001
        analysis=json.loads((d/'analysis.json').read_text());assert analysis['n_contexts']==n
        item={'run':run,'analysis':analysis,'raw_sha256':hashlib.sha256((d/'behavior.jsonl').read_bytes()).hexdigest(),
              'scores':n*STAGES[stage]*8}
        if stage=='function':
            full=output_metrics(raw,json.loads((d/'preflight.json').read_text()))
            (d/'full_output_summary.json').write_text(json.dumps(full,indent=2)+'\n');item['full_output']=full
        runs[name]=item;raws[name]=raw
    paired={}
    for small,large in [('qwen3','qwen32'),('llama','llama70')]:
        for stage in STAGES:
            names=[f'{f}_confirmation_{stage}' for f in [small,large]]
            if not all(n in runs for n in names):continue
            assert all(runs[n]['run']['args']['n']==32 for n in names)
            assert (dest/names[0]/'contexts.jsonl').read_bytes()==(dest/names[1]/'contexts.jsonl').read_bytes()
            a,b=[pairs(stage,raws[n]) for n in names];assert a.keys()==b.keys()
            paired[large+'_'+stage]={k:interval(b[k]-a[k]) for k in a}
    workers=[json.loads(p.read_text()) for p in dest.glob('worker_*.json')]
    summary={'status':'COMPLETE' if len(runs)==18 else 'PARTIAL','planned_stages':18,
        'completed_stages':len(runs),'missing_stages':[n for n in planned if n not in runs],
        'scores':sum(r['scores'] for r in runs.values()),'contexts_by_stage':sum(r['run']['args']['n'] for r in runs.values()),
        'stage_device_hours':sum(r['run']['gpu_hours'] for r in runs.values()),
        'worker_resident_device_hours_so_far':sum(w['resident_device_hours_so_far'] for w in workers),
        'resource_scope':'worker cumulative snapshots at each last_observed_at, counted once per worker; currently running stages add residency at their next write; failed TF32 attempts remain separate',
        'paired_scope':'fresh confirmation contexts only, large minus small, paired context bootstrap 910; recipes differ, not a causal scaling law',
        'paired_confirmation':paired,'runs':runs}
    (dest/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    md=['# E131：大小模型上的同一形成、操作和Source功能链','',
        f"{summary['status']}：{len(runs)}/18个预定stage完成。发现n16与新确认n32分别展示；大小配对只用逐字相同的新32材料。未完成的stage不作结论。所有继承分析、条件与三通道保留，报告不拟合模型。",'',
        '## 形成与固定系数反事实','',
        '| Model / phase / n | A形成signed nats | A形成absolute nats | B读取signed nats | stage signed交互 | label B0 KV raw r | RMSE / zero | rule双差r | 固定word答案关联absolute |',
        '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for name,item in runs.items():
        if item['run']['stage']!='mechanism':continue
        a=item['analysis'];r=a['reconstruction']['label_interface_B0_kv'];c=a['contrasts']
        md.append('| '+name+f" / {a['n_contexts']} | "+' | '.join([
            fmt(c['A_formation_B_shared']['signed_rule_effect']),fmt(c['A_formation_B_shared']['absolute_rule_effect']),
            fmt(c['B_reading_A_shared']['signed_rule_effect']),fmt(c['stage_interaction']['signed_rule_effect']),
            f"{r['raw']['correlation']:.5f}",f"{r['raw']['rmse']:.5f} / {r['raw']['zero_rmse']:.5f}",
            f"{r['rule_double_contrast']['correlation']:.5f}",fmt(a['relation']['answer_native']['absolute_effect'])])+' |')
    md+=['','## 原生操作：相同路径在不同读取环境','',
        '| Model / phase / n | Full-source答案移除signed | Full-source受限恢复signed | A-only受限恢复signed |','|---|---:|---:|---:|']
    for name,item in runs.items():
        if item['run']['stage']!='native':continue
        a=item['analysis'];md.append('| '+name+f" / {a['n_contexts']} | "+' | '.join(fmt(a['contrasts'][k]['rule_signed']) for k in [
            'shared_native_cross_answer_removal','shared_native_answer_path_restoration','shared_gate_answer_path_restoration'])+' |')
    md+=['','## 真实文本两Source函数：shared词表、两Actor平均candidate/full','',
        '| Model / phase / n | Native candidate/full % | Targeted candidate/full % | targeted−native full pp | targeted−all full pp | query-only−native full pp |','|---|---:|---:|---:|---:|---:|']
    for name,item in runs.items():
        if item['run']['stage']!='function':continue
        a=item['analysis'];full=item['full_output']
        md.append('| '+name+f" / {a['n_contexts']} | "+' | '.join([
            fmt(a['policy_accuracy']['shared_normal_native']['both'],100)+' / '+fmt(full['policy_accuracy']['shared_normal_native']['both'],100),
            fmt(a['policy_accuracy']['shared_answer_cross_off_native']['both'],100)+' / '+fmt(full['policy_accuracy']['shared_answer_cross_off_native']['both'],100),
            *[fmt(full['contrasts'][k]['both'],100) for k in ['shared_answer_cross_off_minus_normal_native','shared_answer_minus_all_native','shared_query_isolation_normal']]])+' |')
    md+=['','## 新32材料的大小配对差','',
        '| Family / stage | Fixed readout | Large−small [95% paired context CI] |','|---|---|---:|']
    for name,values in paired.items():
        for key,v in values.items():md.append('| '+name+' | '+key+' | '+fmt(v,100 if name.endswith('function') else 1)+' |')
    if not paired:md.append('| — | 等待固定大模型新32确认；pilot不与不同材料的小模型作配对 | — |')
    md+=['','## 完整性与解释对象','',
        '上述表显示同一计算操作的核心读数；每stage完整43/64/85条件、全部K/KV/V及两重建目标、读数背景、私人方向和单函数/一句指令控制，保留在各analysis.json与独立raw审计。没有根据效果换模型、头、层、系数或材料。',
        '相同解释可以有不同的幅度、通道权重和层位置；形成与读取应分别看。准确率接近满分不意味着形成关系消失，某个交互CI跨零也不等于其他已测操作失效。尚未完成的确认与70B不提前结论。']
    (dest/'report.md').write_text('\n'.join(md)+'\n')
    print(json.dumps({k:summary[k] for k in ['status','completed_stages','scores','stage_device_hours']}))
if __name__=='__main__':main()
