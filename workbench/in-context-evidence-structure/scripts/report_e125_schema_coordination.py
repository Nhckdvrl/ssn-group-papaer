"""Render the frozen E125 primary and complete controls after all six runs.

This reporting script does not run a model or select scientific conditions.
"""
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
FROZEN = '75f7566582cbaf7cf80dd130b409b32436df281a262884d8db381991437612b9'
FAMILIES = {'qwen3': 'Qwen3-8B', 'mistral': 'Mistral-7B-v0.3', 'llama': 'Llama-3.1-8B'}
PHASES = ['discovery', 'confirmation']


def fmt(v, scale=100):
    return f"{scale*v['mean']:.2f} [{scale*v['ci95'][0]:.2f}, {scale*v['ci95'][1]:.2f}]"


def main():
    assert hashlib.sha256((ROOT/'scripts/e125_public_output_schema_coordination.py').read_bytes()).hexdigest() == FROZEN
    all_runs = {}
    for family in FAMILIES:
        for phase in PHASES:
            d = ROOT/'results/e125'/f'{family}_{phase}'
            run, analysis = [json.loads((d/name).read_text()) for name in ['run.json', 'analysis.json']]
            n = 16 if phase == 'discovery' else 32
            assert run['script_sha256'] == FROZEN and analysis['n_contexts'] == n
            assert run['args']['n'] == n and run['args']['seed'] == (125001 if n == 16 else 125101)
            assert run['args']['materials'] == ('discovery' if n == 16 else 'validation')
            raw = [json.loads(x) for x in (d/'behavior.jsonl').read_text().splitlines()]
            contexts = (d/'contexts.jsonl').read_bytes()
            assert len(raw) == n and all(len(r['conditions']) == 63 for r in raw)
            assert all(len(v['z']) == 8 for r in raw for v in r['conditions'].values())
            assert run['contexts_sha256'] == hashlib.sha256(contexts).hexdigest()
            preflight_contexts = (ROOT/'results/e125'/f'{family}_{phase}_preflight'/'contexts.jsonl').read_bytes()
            assert contexts == preflight_contexts
            assert len(run['all_layer_consumption']) == 21 and len(run['query_layer_consumption']) == 63
            for consumption in [run['all_layer_consumption'], run['query_layer_consumption']]:
                assert all(set(map(int, counts)) == set(range(run['num_layers'])) and set(counts.values()) == {n}
                           for counts in consumption.values())
            assert all(run[k] <= .001 for k in ['numeric_max_error', 'cache_no_op_max_error',
                        'inert_roster_max_error', 'graph_zero_max_error'])
            all_runs[f'{family}_{phase}'] = {'run': run, 'analysis': analysis}
    total = {'runs': 6, 'contexts': sum(x['analysis']['n_contexts'] for x in all_runs.values()),
             'scores': sum(x['analysis']['n_contexts']*63*8 for x in all_runs.values()),
             'gpu_hours': sum(x['run']['gpu_hours'] for x in all_runs.values())}
    summary = {'scientific_script_sha256': FROZEN, 'primary': 'full-vocabulary next-token accuracy',
               'unit': 'context; equal weights over origin/cross, A/B, eight queries',
               'totals': total, 'runs': all_runs}
    dest = ROOT/'results/e125'
    (dest/'summary.json').write_text(json.dumps(summary, indent=2)+'\n')
    md = ['# E125：公共Source–输出词关系在形成期与读取期的作用', '',
          '三checkpoint全部固定16探索→32确认；无按方向筛模型。主读数为完整词表，候选空间只是辅助。', '',
          f"6批/{total['contexts']}contexts/{total['scores']}评分，记录{total['gpu_hours']:.6f}GPU·时。科学源`{FROZEN}`。", '',
          '形成F控制demo对公共词空间表的读取，R控制整个query的直接读取；所有私人Source配对监督在历史形成中互不可达；联合query仍读取两缓存，公共表不提供任何评论对应哪个标签。true和unrelated公共表含相同输出词，名字绑定不同，token数/位置相同；swapped表保留真实名字/词多重集而交换对应关系。三表F0R0缓存/完整argmax零确认公共词表无绕路；F1R0影响只能经形成后的demo状态。', '',
          '## 冻结主对比：Source–词空间关系的阶段增益', '',
          '每项为true阶段增益减unrelated同阶段增益，单位pp、context-bootstrap 95%CI。不是有表减无表；true−swap需要另看swapped本身的另一Source词率才能讨论主动错误路由。', '',
          '| Model | 确认形成-only | 确认读取-only | 探索形成-only | 探索读取-only |',
          '|---|---:|---:|---:|---:|']
    for family, label in FAMILIES.items():
        dc = [all_runs[f'{family}_{p}']['analysis']['contrasts'] for p in ['confirmation','discovery']]
        md.append('| '+label+' | '+' | '.join(fmt(c[k]['both']) for c in dc
            for k in ['formation_true_minus_unrelated_gain','reading_true_minus_unrelated_gain'])+' |')
    md += ['', '## 固定名字/词集的关系交换对比', '',
           '| Model | 确认形成true−swapped | 确认读取true−swapped | 探索形成true−swapped | 探索读取true−swapped |',
           '|---|---:|---:|---:|---:|']
    for family,label in FAMILIES.items():
        contrasts = [all_runs[f'{family}_{p}']['analysis']['contrasts'] for p in ['confirmation','discovery']]
        md.append('| '+label+' | '+' | '.join(fmt(c[k]['both']) for c in contrasts
            for k in ['formation_true_minus_swapped_gain','reading_true_minus_swapped_gain'])+' |')
    for phase in ['confirmation','discovery']:
        md += ['', f'## {phase}：全部阶段条件与Actor', '',
               '| Model | roster/F/R | 完整词表 | own-space候选 | own词率 | other词率 | A full | B full |',
               '|---|---|---:|---:|---:|---:|---:|---:|']
        for family, label in FAMILIES.items():
            a = all_runs[f'{family}_{phase}']['analysis']
            for key, v in a['phase_accuracy'].items():
                md.append('| '+label+' | '+key+' | '+' | '.join(fmt(v[k]) for k in
                    ['both','candidate','source_word','other_word','A','B'])+' |')
        md += ['', '### 功能参照（不同prefix长度，不作表F/R纯因果对比）', '',
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
           '表提供Source对应的输出词集合，未提供任何私人input–label配对、criterion或code方向；它是显式schema的构造性检验，不自动识别天然绑定模块，失败也不否定所有协调机制。遮罩改变attention质量并使后继状态活演化，因果解释是指定可达图，不是固定向量比例。确认更换Source姓名和官方query split，不构成新benchmark；与旧实验查询池可能重用。', '',
           '所有63条件、私人方向、同/反约定、true−swapped/F×R交互、margin与完整读数在各analysis.json和summary.json保留；图只展示确认阶段。raw JSONL不进git，独立校对另附。']
    (dest/'report.md').write_text('\n'.join(md)+'\n')
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 3, figsize=(13, 3.7), sharey=True)
    for ax, (family, label) in zip(axes, FAMILIES.items()):
        a = all_runs[f'{family}_confirmation']['analysis']['phase_accuracy']
        for offset, roster, color in [(-.10,'true','#1768ac'),(0,'unrelated','#b86b26'),(.10,'swapped','#aa3453')]:
            vals = [a[f'{roster}_f{f}r{r}'] for f,r in [(0,0),(1,0),(0,1),(1,1)]]
            y = np.array([v['both']['mean'] for v in vals])*100
            err = np.array([[v['both']['mean']-v['both']['ci95'][0] for v in vals],
                            [v['both']['ci95'][1]-v['both']['mean'] for v in vals]])*100
            ax.errorbar(np.arange(4)+offset,y,yerr=err,marker='o',color=color,lw=1.4,capsize=3,label=roster+' full output')
            ax.plot(np.arange(4)+offset,[v['candidate']['mean']*100 for v in vals],marker='x',ls='--',color=color,alpha=.65,label=roster+' own candidates')
        ax.set_xticks(range(4),['Neither','Formation','Reading','Both'])
        ax.tick_params(axis='x', labelsize=9)
        ax.set_title(label)
        ax.set_xlabel('Public-schema access')
        ax.grid(axis='y',alpha=.2)
        ax.set_ylim(0,101)
    axes[0].set_ylabel('Accuracy (%)')
    axes[-1].legend(fontsize=7,loc='lower right')
    fig.suptitle('Public source–output schemas with independent private supervision (n=32)',fontsize=11)
    fig.tight_layout()
    for extension in ['png','pdf']:
        fig.savefig(ROOT/'results/figs'/f'fig_public_source_schema_coordination.{extension}',dpi=180)
    plt.close(fig)
    print(json.dumps(total))


if __name__ == '__main__':
    main()
