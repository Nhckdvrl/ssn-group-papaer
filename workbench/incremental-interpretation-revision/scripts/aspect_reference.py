"""E15 paired decomposition of immutable E14 and new fixed-aspect rows."""
import argparse
import json
from pathlib import Path
import numpy as np
from analyze import estimate
from data import sha
from event_identity import digest


def read_run(path):
    cfg = json.loads((path / 'config.json').read_text())
    assert cfg['scores_sha256'] == sha(path / 'scores.jsonl')
    rows = [json.loads(x) for x in (path / 'scores.jsonl').read_text().splitlines()]
    assert len(rows) == cfg['task_count'] == len({r['item_id'] for r in rows})
    return cfg, rows


def analyze(old, new, cache):
    c0, r0 = read_run(old)
    c1, r1 = read_run(new)
    assert (len(r0), len(r1)) == (528, 176)
    for k in ('model_manifest', 'dtype', 'tf32', 'attention', 'seed', 'torch', 'transformers', 'batch_size', 'frozen'):
        assert c0[k] == c1[k], k
    data0 = cache / 'E14-material-preparation-v1/audited-v1.jsonl'
    data1 = cache / 'E15-material-preparation-v1/audited-v1.jsonl'
    assert sha(data0) == c0['data_sha256'] and sha(data1) == c1['data_sha256']
    material0 = {r['item_id']: r for r in map(json.loads, data0.read_text().splitlines())}
    material1 = {r['item_id']: r for r in map(json.loads, data1.read_text().splitlines())}
    score0 = {r['item_id']: r for r in r0}
    for r in r1:
        parent = r['parent_E14_item_id']
        a, b = material0[parent], material1[r['item_id']]
        before = a['sentence'][:a['authored_followup_start_word']]  # no semantic inference from future text
        # The bridge is located between exact S1 and authored S2; verify the
        # complete strings differ by just the preregistered lexical change.
        start = len(a['sentence'].split('. ', 1)[0]) + 2
        bridge_end = a['sentence'].index('. ', start) + 1
        bridge = a['sentence'][start:bridge_end]
        assert ' began a separate ' in bridge
        expected = a['sentence'][:start] + bridge.replace(' began a separate ', ' continued a separate ', 1) + a['sentence'][bridge_end:]
        assert b['sentence'] == expected
        for k in ('pair_id', 'source_np_option', 'condition', 'target_kind', 'target_phrase_sha256',
                  'eligible', 'episodic_reference', 'source_block'):
            assert r[k] == score0[parent][k], k
        assert digest(b['sentence']) == r['sentence_sha256']
    result = dict(experiment='E15', primary='Decompose E14 same/separate interaction into fixed-continued reference contrast A and fixed-separate aspect/presupposition contrast B.',
        units='bits: R = source-NP total target surprisal minus authored-reference total target surprisal; D = R_GP minus R_comma.',
        formulas={'A': 'D_continued_same - D_continued_separate', 'B': 'D_continued_separate - D_began_separate', 'original_I': 'A + B'},
        interpretation='Conditional language preference, not accuracy. B includes accommodation of a previously ongoing separate activity, not pure grammatical aspect. Fixed alternatives cancel their lengths in paired contrasts.',
        physical_new_tasks=176, reused_E14_tasks=528, cells={}, gp_minus_comma={}, components={}, per_source={},
        scores_sha256={'E14': c0['scores_sha256'], 'E15': c1['scores_sha256']},
        model_configs_verified_equal=True, material_single_word_change_verified=176,
        bootstrap_draws=10000, bootstrap_seed=20261005, analysis_code_sha256=sha(Path(__file__)))
    rows = [dict(r, anchor={'none':'none', 'same':'continued_same', 'separate':'began_separate'}[r['episode_anchor']]) for r in r0]
    rows += [dict(r, anchor='continued_separate') for r in r1]
    def stat(v):
        out = estimate([v[k] for k in sorted(v)]) if len(v) > 1 else dict(estimate=next(iter(v.values()), None), ci95=None, n_sets=len(v))
        return dict(out, pair_ids=sorted(v))
    def diff(a, b):
        return {k: a[k]-b[k] for k in a.keys() & b.keys()}
    for stratum in ('eligible', 'clear_reference', 'episodic_reference'):
        for block in ('all22', 'first12', 'last12'):
            rr = [r for r in rows if r[stratum] and (block == 'all22' or r['source_block'] == block)]
            index = {(r['pair_id'], r['source_np_option'], r['condition'], r['anchor'], r['target_kind']): r for r in rr}
            assert len(index) == len(rr)
            for option in (0, 1, 'both'):
                prefix = f'{stratum}/{block}/option{option}'
                ds = {}
                for anchor in ('none', 'continued_same', 'continued_separate', 'began_separate'):
                    vs = {}
                    for c in ('gp', 'explicit_cue'):
                        vals = {}
                        for sid in sorted({r['pair_id'] for r in rr}):
                            options = (0, 1) if option == 'both' else (option,)
                            values = []
                            for o in options:
                                a = index.get((sid, o, c, anchor, 'source_reference'))
                                b = index.get((sid, o, c, anchor, 'source_np'))
                                if a is None or b is None:
                                    break
                                assert a['target_context_sha256'] == b['target_context_sha256']
                                values.append(b['target_total_bits'] - a['target_total_bits'])
                            if len(values) == len(options):
                                vals[sid] = float(np.mean(values))
                        vs[c] = vals
                        result['cells'][f'{prefix}/{anchor}/{c}'] = stat(vals)
                    ds[anchor] = diff(vs['gp'], vs['explicit_cue'])
                    result['gp_minus_comma'][f'{prefix}/{anchor}'] = stat(ds[anchor])
                common = ds['continued_same'].keys() & ds['continued_separate'].keys() & ds['began_separate'].keys()
                A = {k: ds['continued_same'][k]-ds['continued_separate'][k] for k in common}
                B = {k: ds['continued_separate'][k]-ds['began_separate'][k] for k in common}
                I = {k: ds['continued_same'][k]-ds['began_separate'][k] for k in common}
                assert all(abs(A[k]+B[k]-I[k]) < 1e-10 for k in common)
                for name, v in (('A', A), ('B', B), ('original_I', I)):
                    result['components'][f'{prefix}/{name}'] = stat(v)
                result['per_source'][prefix] = [{ 'pair_id': k, 'A': A[k], 'B': B[k], 'original_I': I[k],
                    **{f'D_{a}': ds[a][k] for a in ds if k in ds[a]}} for k in sorted(common)]
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--old', type=Path, required=True)
    p.add_argument('--new', type=Path, required=True)
    p.add_argument('--cache', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    a.out.write_text(json.dumps(analyze(a.old, a.new, a.cache), indent=2) + '\n')
