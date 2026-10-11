"""Render the frozen E124 primary and complete controls after all six runs.

This reporting script does not run a model or select scientific conditions.
"""
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FROZEN = 'ea65caf59d2b69ef5c14803fd1edbd7b227ad3813d2b4fa261c001faaaaea727'
FAMILIES = {'qwen3': 'Qwen3-8B', 'mistral': 'Mistral-7B-v0.3', 'llama': 'Llama-3.1-8B'}
PHASES = ['discovery', 'confirmation']


def fmt(v, scale=100):
    return f"{scale*v['mean']:.2f} [{scale*v['ci95'][0]:.2f}, {scale*v['ci95'][1]:.2f}]"


def main():
    assert hashlib.sha256((ROOT/'scripts/e124_source_identity_coordination.py').read_bytes()).hexdigest() == FROZEN
    all_runs = {}
    for family in FAMILIES:
        for phase in PHASES:
            d = ROOT/'results/e124'/f'{family}_{phase}'
            run, analysis = [json.loads((d/name).read_text()) for name in ['run.json', 'analysis.json']]
            n = 16 if phase == 'discovery' else 32
            assert run['script_sha256'] == FROZEN and analysis['n_contexts'] == n
            assert run['args']['n'] == n and run['args']['seed'] == (124001 if n == 16 else 124101)
            assert run['args']['materials'] == ('discovery' if n == 16 else 'validation')
            raw = [json.loads(x) for x in (d/'behavior.jsonl').read_text().splitlines()]
            contexts = (d/'contexts.jsonl').read_bytes()
            assert len(raw) == n and all(len(r['conditions']) == 47 for r in raw)
            assert all(len(v['z']) == 8 for r in raw for v in r['conditions'].values())
            assert run['contexts_sha256'] == hashlib.sha256(contexts).hexdigest()
            preflight_contexts = (ROOT/'results/e124'/f'{family}_{phase}_preflight'/'contexts.jsonl').read_bytes()
            assert contexts == preflight_contexts
            assert len(run['all_layer_consumption']) == 17 and len(run['query_layer_consumption']) == 47
            for consumption in [run['all_layer_consumption'], run['query_layer_consumption']]:
                assert all(set(map(int, counts)) == set(range(run['num_layers'])) and set(counts.values()) == {n}
                           for counts in consumption.values())
            assert all(run[k] <= .001 for k in ['numeric_max_error', 'cache_no_op_max_error',
                        'inert_roster_max_error', 'graph_zero_max_error'])
            all_runs[f'{family}_{phase}'] = {'run': run, 'analysis': analysis}
    total = {'runs': 6, 'contexts': sum(x['analysis']['n_contexts'] for x in all_runs.values()),
             'scores': sum(x['analysis']['n_contexts']*47*8 for x in all_runs.values()),
             'gpu_hours': sum(x['run']['gpu_hours'] for x in all_runs.values())}
    summary = {'scientific_script_sha256': FROZEN, 'primary': 'full-vocabulary next-token accuracy',
               'unit': 'context; equal weights over origin/cross, A/B, eight queries',
               'totals': total, 'runs': all_runs}
    dest = ROOT/'results/e124'
    (dest/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    md = ['# E124：公共身份信息在形成期与读取期的作用', '',
          '三checkpoint全部固定16探索→32确认；无按方向筛模型。主读数为完整词表，候选空间只是辅助。', '',
          f"6批/{total['contexts']}contexts/{total['scores']}评分，记录{total['gpu_hours']:.6f}GPU·时。科学源`{FROZEN}`。", '',
          '形成F控制demo对无标签名单的读取，R控制整个query的直接读取；所有私人Source监督始终互不可达。true和unrelated仅名单内容不同、token数/位置相同。F0R0缓存/输出的数值零确认名单无绕路；F1R0影响只能经形成后的demo状态。', '',
          '## 冻结主对比：身份特异的阶段增益', '',
          '每项为true阶段增益减unrelated同阶段增益，单位pp、context-bootstrap 95%CI。不是名单条件减无名单。', '',
          '| Model | 确认形成-only | 确认读取-only | 探索形成-only | 探索读取-only |',
          '|---|---:|---:|---:|---:|']
    for family, label in FAMILIES.items():
        dc = [all_runs[f'{family}_{p}']['analysis']['contrasts'] for p in ['confirmation','discovery']]
        md.append('| '+label+' | '+' | '.join(fmt(c[k]['both']) for c in dc
            for k in ['formation_true_minus_unrelated_gain','reading_true_minus_unrelated_gain'])+' |')
    for phase in ['confirmation','discovery']:
        md += ['', f'## {phase}：全部阶段条件与Actor', '',
               '| Model | roster/F/R | 完整词表 | own-space候选 | own词率 | A full | B full |',
               '|---|---|---:|---:|---:|---:|---:|']
        for family, label in FAMILIES.items():
            a = all_runs[f'{family}_{phase}']['analysis']
            for key, v in a['phase_accuracy'].items():
                md.append('| '+label+' | '+key+' | '+' | '.join(fmt(v[k]) for k in
                    ['both','candidate','source_word','A','B'])+' |')
        md += ['', '### 功能参照（不同prefix长度，不作名单F/R纯因果对比）', '',
               '| Model | condition | 完整词表 | own-space候选 | 另一Source词率 |',
               '|---|---|---:|---:|---:|']
        for family, label in FAMILIES.items():
            a = all_runs[f'{family}_{phase}']['analysis']
            for key, v in a['conditions'].items():
                if '_f' not in key:
                    md.append('| '+label+' | '+key+' | '+' | '.join(fmt(v[k]) for k in
                        ['full_accuracy','candidate_accuracy','other_word_rate'])+' |')
        md += ['', '### B约定对A的signed/absolute功能作用', '',
               '| Model | condition | signed nats | absolute nats |', '|---|---|---:|---:|']
        for family, label in FAMILIES.items():
            for key,v in all_runs[f'{family}_{phase}']['analysis']['B_code_response'].items():
                md.append(f"| {label} | {key} | {fmt(v['signed'],1)} | {fmt(v['absolute'],1)} |")
    md += ['', '## 保留范围', '',
           '名单无label/criterion/private约定。它检验names-only共同上下文的充分性，不能据负结果否定Feng完整实体-属性绑定或所有协调机制。遮罩改变attention质量并使后继状态活演化，因果解释是指定可达图，不是固定向量比例。确认更换Source姓名和官方query split，不构成新benchmark；与旧实验查询池可能重用。', '',
           '所有47条件、私人方向、同/反约定、F×R交互、margin与完整读数在各analysis.json和summary.json保留；图只展示确认阶段。raw JSONL不进git，独立校对另附。']
    (dest/'report.md').write_text('\n'.join(md)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.7), sharey=True)
    for ax, (family, label) in zip(axes, FAMILIES.items()):
        a = all_runs[f'{family}_confirmation']['analysis']['phase_accuracy']
        for offset, roster, color in [(-.075,'true','#1768ac'),(.075,'unrelated','#b86b26')]:
            vals = [a[f'{roster}_f{f}r{r}'] for f,r in [(0,0),(1,0),(0,1),(1,1)]]
            y = np.array([v['both']['mean'] for v in vals])*100
            err = np.array([[v['both']['mean']-v['both']['ci95'][0] for v in vals],
                            [v['both']['ci95'][1]-v['both']['mean'] for v in vals]])*100
            ax.errorbar(np.arange(4)+offset,y,yerr=err,marker='o',color=color,lw=1.4,capsize=3,label=roster+' full output')
            ax.plot(np.arange(4)+offset,[v['candidate']['mean']*100 for v in vals],marker='x',ls='--',color=color,alpha=.65,label=roster+' own candidates')
        ax.set_xticks(range(4),['Neither','Formation','Reading','Both'])
        ax.set_title(label)
        ax.set_xlabel('Public-roster access')
        ax.grid(axis='y',alpha=.2)
        ax.set_ylim(0,101)
    axes[0].set_ylabel('Accuracy (%)')
    axes[-1].legend(fontsize=7,loc='lower right')
    fig.suptitle('Unlabeled shared identities with independent private supervision (n=32)',fontsize=11)
    fig.tight_layout()
    for extension in ['png','pdf']:
        fig.savefig(ROOT/'results/figs'/f'fig_source_identity_coordination.{extension}',dpi=180)
    plt.close(fig)
    print(json.dumps(total))


if __name__ == '__main__':
    main()
