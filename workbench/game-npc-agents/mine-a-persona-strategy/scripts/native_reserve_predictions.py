#!/usr/bin/env python3
"""Render the E68 preregistered predictions from complete graph-cluster reports."""
import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--results', type=Path, required=True)
    a = ap.parse_args()
    models = {m: json.loads((a.results / f'E68_{m}_cross_summary.json').read_text())
              for m in ['gemma', '32b']}
    assert all(r['status'] == 'COMPLETE' and r['episodes'] == 2814 for r in models.values())
    rows = []
    for model, report in models.items():
        for scope in ['all', 'wear_wield', 'give']:
            for persona in ['firm', 'agreeable']:
                stem = f'{scope}/{persona}/block_status/'
                specifications = [
                    ('P1', 'G−A', 'coherent_generic_priority_minus_asset_protection',
                     ['goal', 'first_step_goal']),
                    ('P2', 'B−G', 'coherent_negative_only_minus_generic_priority',
                     ['first_step_block', 'any_legal_block', 'transfer']),
                    ('P3', 'A−G', 'coherent_asset_protection_minus_generic_priority',
                     ['transfer', 'any_examine', 'any_speech']),
                ]
                if scope == 'wear_wield':
                    specifications += [
                        ('P4', 'Exec G−A | upstream A', 'exec_G_minus_A_given_asset_protection', ['goal']),
                        ('P4', 'Exec G−A | upstream G', 'exec_G_minus_A_given_generic_priority', ['goal']),
                    ]
                for prediction, contrast, key, fields in specifications:
                    for metric in fields:
                        rows.append(dict(prediction=prediction, model=model, scope=scope,
                                         persona=persona, contrast=contrast, metric=metric,
                                         **report['contrasts'][stem + key][metric]))
        for metric in ['transfer', 'both', 'goal']:
            rows.append(dict(prediction='P5', model=model, scope='other_item',
                             persona='agreeable−firm', contrast='A−F | generic', metric=metric,
                             **report['contrasts']['all/other_item/A_minus_F_generic'][metric]))
    result = {
        'status': 'COMPLETE',
        'interpretation': 'Prespecified directional estimates; no automatic scientific pass/fail threshold.',
        'scope': 'all=109 graphs; wear_wield=41; give=58; other_item=60. Seeds averaged within graph.',
        'intervals': 'Pointwise 95% paired graph bootstrap, not simultaneous intervals.',
        'negative_rule_scope': 'Give goals can conflict directly with B. The 41 equip worlds are the prior-declared comparable P2 stratum.',
        'estimates': rows,
    }
    (a.results / 'E68_prediction_readout.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    lines = ['# E68预注册预测读数', '', result['scope'], '',
             'G=generic_priority；A=asset_protection；B=negative_only。P5中的A−F专指Agreeable−Firm。', '',
             '下表均为百分点差与逐项95%图簇区间，不用区间作为自动科学判决。P2须同时区分首步block与全episode首次合法block。', '']
    for scope in ['all', 'wear_wield', 'give', 'other_item']:
        lines += [f'## {scope}', '', '| 预测 | 模型 | 人设 | 对照 | 读数 | 差值pp [95% CI] | 独立图 |',
                  '|---|---|---|---|---|---:|---:|']
        for r in rows:
            if r['scope'] != scope:
                continue
            lo, hi = r['graph_bootstrap_95']
            lines.append(f"| {r['prediction']} | {r['model']} | {r['persona']} | {r['contrast']} | {r['metric']} | "
                         f"{100*r['mean']:+.2f} [{100*lo:.2f}, {100*hi:.2f}] | {r['independent_graphs']} |")
        lines.append('')
    (a.results / 'E68_prediction_readout.md').write_text('\n'.join(lines) + '\n')
    print(json.dumps({'prespecified_estimates': len(rows), 'model_calls': 0}))


if __name__ == '__main__':
    main()
