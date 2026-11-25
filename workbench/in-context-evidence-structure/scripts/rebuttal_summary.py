"""Collect E134-E136 analyses into compact per-model tables (results/rebuttal_summary.json + printed markdown)."""
import json
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[1] / 'results'
MODELS = [('qwen3', 'Qwen3-8B'), ('qwen14', 'Qwen3-14B'), ('mistral', 'Mistral-7B'), ('llama', 'Llama-3.1-8B'),
          ('gemma2', 'Gemma-2-2B'), ('gemma9', 'Gemma-2-9B')]


def f(x, pct=False, ci=True):
    k = 100 if pct else 1
    s = f"{x['mean'] * k:.1f}" if pct else f"{x['mean']:.2f}"
    if ci:
        lo, hi = x['ci95']
        s += f" ({lo * k:.1f}–{hi * k:.1f})" if pct else f" ({lo:.2f}–{hi:.2f})"
    return s


def e134():
    out = {}
    print('\n## E134 controls (SST-5, 32 confirmation prompts)')
    print('| model | removed mass ans/count/mass (%) | ΔA-only: normal / sel / count / mass / norenorm | acc both: normal / sel / count / mass / norenorm |')
    for key, name in MODELS:
        p = R / 'e134' / f'{key}_confirmation' / 'analysis.json'
        if not p.exists():
            continue
        a = json.loads(p.read_text())
        out[name] = a
        rm = a['removed_mass']
        d = [a['delta'][f'shared_{k}_gate']['signed'] for k in ['normal', 'answer_cross_off', 'matched_count', 'matched_mass', 'answer_norenorm']]
        acc = [a['accuracy'][f'shared_{k}_native']['both'] for k in ['normal', 'answer_cross_off', 'matched_count', 'matched_mass', 'answer_norenorm']]
        print(f"| {name} | {rm['answer_cross_off']['mean']*100:.1f}/{rm['matched_count']['mean']*100:.1f}/{rm['matched_mass']['mean']*100:.1f} | "
              + ' / '.join(f(x, ci=False) for x in d) + ' | ' + ' / '.join(f(x, True, False) for x in acc) + ' |')
    print('\n| model | conflict acc (shared, native): iso / +names / iso_cl / +names_cl / iso_cf / +names_cf | far full-vocab both: iso / +names / iso_cl / +names_cl / iso_cf / +names_cf |')
    for name, a in out.items():
        sh = [a['accuracy'][f'shared_{k}_native']['opposite'] for k in ['all_cross_off', 'iso_names', 'all_cross_off_cl', 'iso_names_cl', 'all_cross_off_cf', 'iso_names_cf']]
        fa = [a['accuracy'][f'far_{k}_native']['both'] for k in ['all_cross_off', 'iso_names', 'all_cross_off_cl', 'iso_names_cl', 'all_cross_off_cf', 'iso_names_cf']]
        print(f'| {name} | ' + ' / '.join(f(x, True, False) for x in sh) + ' | ' + ' / '.join(f(x, True, False) for x in fa) + ' |')
    print('\n| model | grouped: ΔA-only AB / BA / interleaved | acc both native: AB / BA / interleaved | conflict acc native AB / BA / inter | AB+sel / BA+sel acc | far grouped acc AB / BA |')
    for name, a in out.items():
        d = [a['delta'][f'shared_{k}_gate']['signed'] for k in ['AB:normal', 'BA:normal', 'normal']]
        acc = [a['accuracy'][f'shared_{k}_native']['both'] for k in ['AB:normal', 'BA:normal', 'normal']]
        opp = [a['accuracy'][f'shared_{k}_native']['opposite'] for k in ['AB:normal', 'BA:normal', 'normal']]
        sel = [a['accuracy'][f'shared_{k}_native']['both'] for k in ['AB:answer_cross_off', 'BA:answer_cross_off']]
        far = [a['accuracy'][f'far_{k}_native']['both'] for k in ['AB:normal', 'BA:normal']]
        print(f'| {name} | ' + ' / '.join(f(x, ci=False) for x in d) + ' | ' + ' / '.join(f(x, True, False) for x in acc)
              + ' | ' + ' / '.join(f(x, True, False) for x in opp) + ' | ' + ' / '.join(f(x, True, False) for x in sel)
              + ' | ' + ' / '.join(f(x, True, False) for x in far) + ' |')
    print('\n| model | attention to B answer word (x1e-3): sameword-sameclass / sameword-diffclass / diffword-sameclass / diffword-diffclass | word effect | class effect |')
    for name, a in out.items():
        t = a['attention_2x2']
        print(f'| {name} | ' + ' / '.join(f"{t[c]['mean']*1e3:.2f}" for c in ['sameword_sameclass', 'sameword_diffclass', 'diffword_sameclass', 'diffword_diffclass'])
              + f" | {t['word_effect']['mean']*1e3:.2f} ({t['word_effect']['ci95'][0]*1e3:.2f}–{t['word_effect']['ci95'][1]*1e3:.2f})"
              + f" | {t['class_effect']['mean']*1e3:.2f} ({t['class_effect']['ci95'][0]*1e3:.2f}–{t['class_effect']['ci95'][1]*1e3:.2f}) |")
    print('\nkey contrasts (CI):')
    for name, a in out.items():
        C = a['contrasts']
        print(name, 'sel−count both', f(C['shared_answer_cross_off_minus_matched_count_native_both'], True),
              '| sel−mass both', f(C['shared_answer_cross_off_minus_matched_mass_native_both'], True),
              '| sel−norenorm', f(C['shared_answer_cross_off_minus_answer_norenorm_native_both'], True),
              '| Δred sel−mass', f(C['shared_answer_cross_off_minus_matched_mass_delta_reduction']),
              '| names gain opp', f(C['shared_names_gain_native_opposite'], True), 'cl', f(C['shared_names_gain_cl_native_opposite'], True),
              'cf', f(C['shared_names_gain_cf_native_opposite'], True))
    return out


def e136():
    out = {}
    print('\n## E136 three sources')
    print('| model | ΔB on A, A-only: shared / far / shared+sel | acc all native: normal / sel / iso / +names | A–B conflict acc: normal / sel |')
    for key, name in MODELS:
        p = R / 'e136' / f'{key}_confirmation' / 'analysis.json'
        if not p.exists():
            continue
        a = json.loads(p.read_text())
        out[name] = a
        d = [a['delta'][k] for k in ['shared_normal_gate', 'far_normal_gate', 'shared_answer_cross_off_gate']]
        acc = [a['accuracy'][f'shared_{k}_native']['all'] for k in ['normal', 'answer_cross_off', 'all_cross_off', 'iso_names']]
        opp = [a['accuracy'][f'shared_{k}_native']['AB_conflict'] for k in ['normal', 'answer_cross_off']]
        print(f'| {name} | ' + ' / '.join(f(x) for x in d) + ' | ' + ' / '.join(f(x, True, False) for x in acc) + ' | '
              + ' / '.join(f(x, True, False) for x in opp) + ' |')
        print('   sel−normal all', f(a['contrasts']['shared_answer_cross_off_minus_normal_native_all'], True),
              ' names gain', f(a['contrasts']['names_gain_native_all'], True))
    return out


def e135(tag):
    out = {}
    print(f'\n## E135 real annotator pairs ({tag})')
    names = ['shared_single_normal_native', 'shared_mix_normal_native', 'shared_mix_normal_gate', 'shared_mix_answer_cross_off_native',
             'shared_mix_answer_cross_off_gate', 'shared_mix_all_cross_off_native', 'far_mix_normal_native', 'shared_grouped_normal_native']
    print('| model | n | separation: ' + ' / '.join(n.replace('shared_', '').replace('_native', '') for n in names) + ' |')
    for key, name in MODELS:
        p = R / 'e135' / f'{key}_{tag}' / 'analysis.json'
        if not p.exists():
            continue
        a = json.loads(p.read_text())
        out[name] = a
        print(f"| {name} | {a['n_pairs']} | " + ' / '.join(f(a['conditions'][n]['separation'], ci=False) for n in names) + ' |')
        print('   disagree acc: ' + ' / '.join(f(a['conditions'][n]['disagree_acc'], True, False) for n in names))
        print('   agree acc: ' + ' / '.join(f(a['conditions'][n]['agree_acc'], True, False) for n in names))
        for n in names[2:]:
            print('   ', n, 'minus mixed normal sep', f(a['contrasts'][f'{n}_minus_mixed_normal_separation']))
        print('    mixed minus single sep', f(a['contrasts']['shared_mix_normal_native_minus_single_separation']))
    return out


if __name__ == '__main__':
    res = {'e134': e134(), 'e136': e136()}
    for tag in sys.argv[1:] or ['conf_contrast']:
        res['e135_' + tag] = e135(tag)
    (R / 'rebuttal_summary.json').write_text(json.dumps(res, indent=1))
