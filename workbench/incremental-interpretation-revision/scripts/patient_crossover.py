"""E16 author-NP crossover: separate patient-specific reuse from reference-form bias."""
import argparse
import collections
import json
from pathlib import Path
import re
import numpy as np
from analyze import estimate
from data import sha, write_jsonl
from event_identity import digest
from aspect_reference import read_run


def build(cache, out):
    assert not out.exists()
    parents = []
    for ex in ('E14', 'E15'):
        data = cache / f'{ex}-material-preparation-v1/audited-v1.jsonl'
        parents += [(ex, r) for r in map(json.loads, data.read_text().splitlines()) if r['target_kind'] == 'source_np']
    ix = {(ex, r['pair_id'], r['source_np_option'], r['condition'], r['episode_anchor']): r for ex, r in parents}
    built = []
    for ex, r in parents:
        b = ix[(ex, r['pair_id'], 1-r['source_np_option'], r['condition'], r['episode_anchor'])]
        phrase = b['sentence'][b['target_start_char']:b['target_stop_char']]
        text = r['sentence'][:r['target_start_char']] + phrase + r['sentence'][r['target_stop_char']:]
        stop = r['target_start_char']+len(phrase)
        words = list(re.finditer(r'\S+', text))
        span = [i for i, w in enumerate(words) if w.start() < stop and w.end() > r['target_start_char']]
        assert ' '.join(words[i].group() for i in span) == phrase
        new = dict(r, item_id='E16:'+r['item_id'], parent_experiment=ex, parent_item_id=r['item_id'],
            target_kind='other_source_np', sentence=text, context_reference_sentence=r['sentence'],
            target_stop_char=stop, target_span_word_indices=span, target_phrase_sha256=digest(phrase), sentence_sha256=digest(text),
            transformation='Only replace the S2 target core NP with the alternative core NP from the other authored S1 NP option. S1 and bridge remain unchanged; no semantic gold.')
        for k in list(new):
            if k.startswith('audit_'):
                del new[k]
        built.append(new)
    assert len(built) == 352
    write_jsonl(out, built)
    return dict(variants=len(built), candidate_sha256=sha(out))


def adopt(data, reviews, idmap_path, out):
    assert not out.exists()
    idmap = json.loads(idmap_path.read_text())
    annotations = {}
    for path in reviews:
        j = json.loads(path.read_text()); assert j['model'] == 'gpt-6-luna'
        for a in j['variant_reviews']:
            key = idmap[a['id']]; assert key not in annotations
            annotations[key] = (a, sha(path))
    rows = list(map(json.loads, data.read_text().splitlines()))
    assert set(annotations) == {r['item_id'] for r in rows}
    output = []
    for r in rows:
        a, h = annotations[r['item_id']]
        assert a['sentence_sha256'] == digest(r['sentence'])
        assert type(a['target_transformation_faithful']) is bool
        assert a['grammaticality'] in ('acceptable', 'marginal', 'unacceptable')
        assert a['reference_status'] in ('identifiable', 'requires_new_referent', 'uncertain')
        assert a['selectional_status'] in ('plausible', 'odd', 'uncertain')
        eligible = r['eligible'] and a['target_transformation_faithful'] and a['grammaticality'] != 'unacceptable'
        output.append(dict(r, eligible=eligible, acceptable=eligible and a['grammaticality']=='acceptable',
            audit_grammar=a['grammaticality'], audit_reference_status=a['reference_status'], audit_selectional_status=a['selectional_status'],
            audit_reason=a['reason'], audit_review_sha256=h, audit_provider='gpt-6-luna'))
    write_jsonl(out, output)
    report = dict(audited_sha256=sha(out), candidate_sha256=sha(data), variants=len(rows), source_items=22,
        eligible=sum(r['eligible'] for r in output), acceptable=sum(r['acceptable'] for r in output),
        grammar_counts=dict(collections.Counter(r['audit_grammar'] for r in output)),
        selectional_counts=dict(collections.Counter(r['audit_selectional_status'] for r in output)),
        reference_counts=dict(collections.Counter(r['audit_reference_status'] for r in output)),
        review_sha256=[sha(p) for p in reviews], semantic_gold_labels=0)
    out.with_suffix('.audit.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


def analyze(cache, new_path):
    configs, parents = {}, {}
    for ex in ('E14', 'E15'):
        configs[ex], rows = read_run(cache/'runs'/ex)
        parents.update({r['item_id']: r for r in rows})
    cn, rows = read_run(new_path)
    assert len(rows) == 352
    for ex, cfg in configs.items():
        for k in ('model_manifest','dtype','tf32','attention','seed','torch','transformers','batch_size','frozen'):
            assert cfg[k] == cn[k], k
    triples = []
    for r in rows:
        own = parents[r['parent_item_id']]
        ref = parents[r['parent_item_id'].replace(':source_np', ':source_reference')]
        for k in ('pair_id','source_np_option','condition','episode_anchor','target_context_sha256'):
            assert r[k] == own[k] == ref[k], k
        triples.append(dict(r, M=r['target_total_bits']-own['target_total_bits'],
            R_own=own['target_total_bits']-ref['target_total_bits'], R_other=r['target_total_bits']-ref['target_total_bits']))
    result = dict(experiment='E16', units='bits', primary='Excess preference for previously mentioned patient in GP versus comma, and its same/separate modulation at fixed continued.',
        formulas={'M':'bits(other_author_NP) - bits(own_author_NP)', 'D_M':'M_GP - M_comma',
                  'A_M':'D_M_continued_same - D_M_continued_separate',
                  'identity':'A_R_own = A_R_other - A_M'},
        interpretation='Patient-specific continuation preference; not semantic gold, parse accuracy, or proof of a stored event graph. Both NP choices averaged within source cancel base lexical frequency asymmetry; GP/comma retains identical mention counts.',
        physical_tasks=352, bootstrap_draws=10000, bootstrap_seed=20261005,
        scores_sha256={'E16':cn['scores_sha256'],**{ex:cfg['scores_sha256'] for ex,cfg in configs.items()}},
        analysis_code_sha256=sha(Path(__file__)), cells={}, gp_minus_comma={}, anchor_interactions={}, per_source={})
    def stat(v):
        s=estimate([v[k] for k in sorted(v)]) if len(v)>1 else dict(estimate=next(iter(v.values()),None),ci95=None,n_sets=len(v))
        return dict(s,pair_ids=sorted(v))
    def diff(a,b):return {k:a[k]-b[k] for k in a.keys() & b.keys()}
    for stratum in ('all', 'eligible', 'acceptable', 'episodic_reference'):
        for block in ('all22','first12','last12'):
            rr=[r for r in triples if (stratum=='all' or r[stratum]) and (block=='all22' or r['source_block']==block)]
            ix={(r['pair_id'],r['source_np_option'],r['condition'],r['episode_anchor']):r for r in rr}
            assert len(ix)==len(rr)
            for option in (0,1,'both'):
                prefix=f'{stratum}/{block}/option{option}'
                all_ds={}
                for measure in ('M','R_own','R_other'):
                    ds={}
                    for anchor in ('none','same','continued_separate','separate'):
                        vs={}
                        for condition in ('gp','explicit_cue'):
                            v={}
                            for sid in {r['pair_id'] for r in rr}:
                                choices=(0,1) if option=='both' else (option,)
                                observations=[ix.get((sid,o,condition,anchor)) for o in choices]
                                if all(observations):v[sid]=float(np.mean([r[measure] for r in observations]))
                            vs[condition]=v
                            result['cells'][f'{prefix}/{measure}/{anchor}/{condition}']=stat(v)
                        ds[anchor]=diff(vs['gp'],vs['explicit_cue'])
                        result['gp_minus_comma'][f'{prefix}/{measure}/{anchor}']=stat(ds[anchor])
                    interactions=diff(ds['same'],ds['continued_separate'])
                    result['anchor_interactions'][f'{prefix}/{measure}/same_minus_continued_separate']=stat(interactions)
                    all_ds[measure]=(ds,interactions)
                common=set.intersection(*(set(v[1]) for v in all_ds.values()))
                assert all(abs(all_ds['R_own'][1][k] - (all_ds['R_other'][1][k]-all_ds['M'][1][k]))<1e-10 for k in common)
                result['per_source'][prefix]=[dict(pair_id=k,**{f'A_{m}':v[1][k] for m,v in all_ds.items()},
                    **{f'D_M_{a}':all_ds['M'][0][a][k] for a in all_ds['M'][0] if k in all_ds['M'][0][a]}) for k in sorted(common)]
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True)
    b=s.add_parser('build');b.add_argument('--cache',type=Path,required=True);b.add_argument('--out',type=Path,required=True)
    a=s.add_parser('adopt');a.add_argument('--data',type=Path,required=True);a.add_argument('--reviews',type=Path,nargs='+',required=True);a.add_argument('--idmap',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
    n=s.add_parser('analyze');n.add_argument('--cache',type=Path,required=True);n.add_argument('--new',type=Path,required=True);n.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    if args.action=='build':print(json.dumps(build(args.cache,args.out),indent=2))
    elif args.action=='adopt':print(json.dumps(adopt(args.data,args.reviews,args.idmap,args.out),indent=2))
    else:args.out.write_text(json.dumps(analyze(args.cache,args.new),indent=2)+'\n')
