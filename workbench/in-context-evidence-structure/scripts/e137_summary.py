"""Print E137 readouts per model and variant (results/e137/<model>_<variant>/analysis.json)."""
import json
from pathlib import Path

R = Path(__file__).resolve().parents[1] / 'results' / 'e137'
MODELS = ['qwen3', 'qwen14', 'mistral', 'llama', 'gemma2', 'gemma9']


def f(x, scale=1):
    lo, hi = x['ci95']
    ex = '' if lo > 0 or hi < 0 else '~'
    return f"{x['mean'] * scale:+.2f}[{lo * scale:+.2f},{hi * scale:+.2f}]{ex}"


for var in ['k3', 'alt', 'k6']:
    print(f'== {var}')
    for m in MODELS:
        p = R / f'{m}_{var}' / 'analysis.json'
        if not p.exists():
            continue
        a = json.loads(p.read_text())
        d, c, acc = a['delta'], a['contrasts'], a['accuracy']
        print(f"{m:8s} D_gate {f(d['shared_normal_gate'])} far {f(d['far_normal_gate'])} sel {f(d['shared_answer_cross_off_gate'])} | "
              f"acc native {acc['shared_normal_native']['all']['mean']*100:.1f} conflict {acc['shared_normal_native']['AB_conflict']['mean']*100:.1f} "
              f"farnat {acc['far_normal_native']['all']['mean']*100:.1f} | sel-normal {f(c['shared_answer_cross_off_minus_normal_native_all'], 100)} "
              f"iso {acc['shared_all_cross_off_native']['all']['mean']*100:.1f} names {f(c['names_gain_native_all'], 100)}")
