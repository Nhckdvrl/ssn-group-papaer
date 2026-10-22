#!/usr/bin/env python3
"""Aggregate complete D-E10 runs with book-level paired uncertainty, no new inference."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import statistics
from run_adaptation_pipeline import SYSTEMS,read
from score_adaptation_quality import DIMENSIONS


def aggregate_primary(primary,books,expected_count):
    """Equal questions within a role, roles within a book, then equal books."""
    byrole=defaultdict(lambda:defaultdict(list));good={}
    for r in primary:
        if r['valid']:
            value=r['result']['scores'];good[r['question_id']]=value
            for dim in DIMENSIONS:byrole[r['book_name'],r['episode_id']][dim].append(value[dim])
    bybook={b:{} for b in books}
    for b in books:
        rows=[v for (book,_),v in byrole.items() if book==b]
        for dim in DIMENSIONS:bybook[b][dim]=statistics.mean(statistics.mean(v[dim]) for v in rows) if rows else None
    complete=len(good)==expected_count
    metrics={dim:statistics.mean(bybook[b][dim] for b in books) for dim in DIMENSIONS} if complete else None
    return good,bybook,metrics


def main():
    import numpy as np
    p=argparse.ArgumentParser();p.add_argument('--asset-root',required=True);p.add_argument('--out',required=True)
    a=p.parse_args();root=Path(a.asset_root);runs=root/'runs/D-E10';out=Path(a.out);out.mkdir(exist_ok=True)
    selection=read(root/'data/evaluation_D-E10/episodes.jsonl');expected={q['question_id'] for e in selection for q in e['queries']}
    books=sorted({e['book'] for e in selection});rng=np.random.default_rng(173);bootstrap=rng.integers(0,len(books),(10000,len(books)))
    result=dict(experiment='D-E10',status='COMPLETE-AUTOMATED-AGGREGATION',n_books=len(books),n_episodes=len(selection),n_queries=len(expected),systems={},training={},
        interpretation='Exploratory five-dimension source-conditioned role judgments. Not validated growth accuracy, not autonomous long dialogue, not a mechanism claim. Single training seed. Descriptive case review remains separate.')
    book_values={}
    reference_states={r['episode_id']:r['update_target'] for r in read(root/'data/evaluation_D-E10/references.jsonl')}
    for system in SYSTEMS:
        path=runs/('system_'+system);meta=json.loads((path/'metadata.json').read_text())
        if not meta.get('complete'):raise ValueError('Incomplete system: '+system)
        responses=read(path/'outputs.jsonl')
        if {r['question_id'] for r in responses}!=expected:raise ValueError('Different output cohort')
        scores=read(runs/'judges'/system/'selected.jsonl');primary=[r for r in scores if not r['repeat']]
        if {r['question_id'] for r in primary}!=expected:raise ValueError('Different judge cohort')
        good,bybook,metrics=aggregate_primary(primary,books,len(expected))
        complete=len(good)==len(expected)
        if complete:
            book_values[system]=np.array([statistics.mean(bybook[b].values()) for b in books])
        repeated=[]
        for r in scores:
            if r['repeat'] and r['valid'] and r['question_id'] in good:
                repeated.append(statistics.mean(abs(r['result']['scores'][d]-good[r['question_id']][d]) for d in DIMENSIONS))
        result['systems'][system]=dict(n_outputs=len(responses),valid_outputs=sum(r['valid'] for r in responses),
            valid_states=meta['valid_states'],valid_motivations=meta['valid_motivations'],valid_primary_judgments=len(good),
            all_primary_judgments_complete=complete,macro_quality=statistics.mean(metrics.values()) if metrics else None,
            dimensions=metrics,by_book=bybook,repeat_pairs=len(repeated),mean_repeat_absolute_difference=statistics.mean(repeated) if repeated else None,
            n_primary_strict_json=sum(r['valid'] and r['result']['strict_json'] for r in primary),
            gpu_process_hours=meta['gpu_process_hours'],recorded_generation_attempts=meta['recorded_generation_attempts'])
        if system in ['base','update_sft','multitask_sft','strong32']:
            states=read(path/'states.jsonl')
            result['systems'][system]['native_change_flag_agreement']=dict(
                matched=sum(r['valid'] and r['state'].get('profile_updated') is reference_states[r['episode_id']]['profile_updated'] for r in states),
                denominator=len(selection),meaning='Agreement with published teacher flag, not psychological growth accuracy; invalid carries do not count as correct.')
    if 'base' in book_values:
        for name,values in book_values.items():
            delta=values-book_values['base'];distribution=delta[bootstrap].mean(1)
            result['systems'][name]['paired_macro_quality_vs_base']=dict(mean=float(delta.mean()),ci95=np.quantile(distribution,[.025,.975]).tolist(),independent_units='six books; equal role weight within each book')
    for mode in ['update','multitask']:
        path=runs/('train_'+mode+'_v2');m=json.loads((path/'metadata.json').read_text())
        if not m.get('complete'):raise ValueError('Training incomplete')
        validation=read(path/'validation.jsonl')
        result['training'][mode]={k:m[k] for k in ['planned_examples','planned_forward_tokens','planned_target_tokens','planned_steps','processed_tasks','wall_s','final_checkpoint']}
        result['training'][mode]['validation']=[{k:v[k] for k in ['label','step','mean_token_nll']} for v in validation]
    result['judge_gpu_hours']=sum(json.loads(p.read_text()).get('wall_s',0) for p in (runs/'judges').glob('*/*/metadata.json'))/3600
    result['judgment_attempts']=sum(len(read(p)) for p in (runs/'judges').glob('*/*/responses.jsonl'))
    likelihood_meta=json.loads((runs/'likelihood/metadata.json').read_text())
    if not likelihood_meta.get('complete'):raise ValueError('Fixed-consumer likelihood incomplete')
    likelihood=read(runs/'likelihood/scores.jsonl')
    if len(likelihood)!=len(SYSTEMS)*len(expected):raise ValueError('Incomplete fixed-consumer readout')
    result['likelihood_gpu_hours']=likelihood_meta['wall_s']/3600
    result['fixed_consumer_source_nll']={}
    for system in SYSTEMS:
        subset=[r for r in likelihood if r['condition']==system]
        perrole=defaultdict(list)
        for r in subset:perrole[r['book_name'],r['trajectory_id']].append(r['mean_target_nll'])
        means=[statistics.mean(statistics.mean(v) for (book,_),v in perrole.items() if book==b) for b in books]
        result['fixed_consumer_source_nll'][system]=dict(macro_mean=statistics.mean(means),by_book=dict(zip(books,means)),
            consumer='Unadapted Qwen3-8B for every system; evaluates supplied state/motivation/context, not the system actor weights')
    (out/'D-E10-summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    lines=['# D-E10：训练与后续互动的自动汇总','',
        '**执行已完成；本页是按运行前协议生成的数字汇总，完整案例的科研解读尚需单独审阅。未自动升级CLAIMS。**','',
        f"6作品、{len(selection)}角色经历、{len(expected)}后续原生上下文；每部作品等权、作品内人物等权。七系统完整同一cohort。",'',
        '| 系统 | 有效回复 | 有效动机 | 质量均分（1–5） | 对base配对差及95%区间 |','|---|---:|---:|---:|---|']
    for name in SYSTEMS:
        r=result['systems'][name];d=r.get('paired_macro_quality_vs_base');mean=r['macro_quality']
        quality=f'{mean:.3f}' if mean is not None else '评分缺失，不给全量均分'
        diff=f"{d['mean']:+.3f} [{d['ci95'][0]:+.3f}, {d['ci95'][1]:+.3f}]" if d else '未计算'
        lines.append(f"| {name} | {r['valid_outputs']}/{len(expected)} | {r['valid_motivations']}/{len(selection)} | {quality} | {diff} |")
    lines+=['','质量是本轮五维探索性评委读数，不是成长准确率；完整分项、严格JSON覆盖与重复评分波动见[D-E10-summary.json](D-E10-summary.json)。缺失不会按幸存子集伪装全量均分。','',
        '这些是发布顺序的角色过程和独立后续情境，未认证整部原著时间，也不是自由玩家长对话。公开场景、世界及局部历史可能帮助普通系统补偿状态错误；保留这种成功。训练单seed，跨评委/真人效度尚未在本轮建立。','',
        '## 实际训练','',
        '| 基线 | 训练样本曝光 | forward tokens | GPU进程小时 | 最后验证NLL |','|---|---:|---:|---:|---:|']
    for name,t in result['training'].items():
        lines.append(f"| {name} | {t['planned_examples']} | {t['planned_forward_tokens']} | {t['wall_s']/3600:.3f} | {t['validation'][-1]['mean_token_nll']:.4f} |")
    lines+=['','原生更新与多任务按总forward token预算比较，示范次数、目标token数及任务分布不同；见训练元数据。检查点、原始尝试、token IDs、实际新态和动机均在ASSETS登记的仓库外D-E10目录。','',
            '训练损失下降不能单独证明人物成长；需要结合上述后续行为、固定案例及普通强系统，判断下一步学习方法的增量。']
    lines+=['','## 共同消费者的辅助读数','','下表用同一个未适配Qwen3-8B消费每条路径产生的状态/动机/上下文，衡量原生后续句子的条件NLL。它不是心理真值或角色质量的替代；完整经历路径有更多输入。','',
            '| 状态/动机路径 | 原句NLL，作品宏平均 |','|---|---:|']
    for name,value in result['fixed_consumer_source_nll'].items():lines.append(f"| {name} | {value['macro_mean']:.4f} |")
    (out/'D-E10-RUN-REPORT.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v['macro_quality'] for k,v in result['systems'].items()},indent=2))


if __name__=='__main__':main()
