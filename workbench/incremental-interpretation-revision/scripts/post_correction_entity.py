"""E22: ordinary entity mention after exactly the same exclusive role facts."""
import argparse
import json
import re
from pathlib import Path
import numpy as np
from analyze import estimate
from aspect_reference import read_run
from data import sha, write_jsonl
from event_identity import digest
from entity_accessibility import adopt_neutral


def build(cache, out):
    assert not out.exists()
    fields = {r['pair_id']: r for r in json.loads((cache/'E14-material-preparation-v1/fields-v3.json').read_text())['rows']}
    parents = []
    for ex, style, version in [('E20', 'named', 'v1'), ('E21', 'generic', 'v3')]:
        for r in map(json.loads, (cache/f'{ex}-material-preparation-v1/audited-{version}.jsonl').read_text().splitlines()):
            if r['target_kind'] == 'source_np' and r['episode_anchor'] == 'same' and (ex == 'E20' or r['exclusion_style'] == style):
                parents.append((ex, style, r))
    ix = {(ex, r['pair_id'], r['source_np_option'], r['condition'], r['role_evidence']): r for ex, _, r in parents}
    rows = []
    for ex, style, r in parents:
        words = list(re.finditer(r'\S+', r['sentence']))
        prefix = r['sentence'][:words[r['authored_followup_start_word']].start()]
        actor = fields[r['pair_id']]['S2_subject']
        for kind, option in [('source_np', r['source_np_option']), ('other_source_np', 1-r['source_np_option'])]:
            other = ix[(ex, r['pair_id'], option, r['condition'], r['role_evidence'])]
            phrase = other['sentence'][other['target_start_char']:other['target_stop_char']]
            pre = prefix + actor + ' later noticed '
            text = pre + phrase + ' for a moment.'
            start, stop = len(pre), len(pre)+len(phrase)
            nw = list(re.finditer(r'\S+', text))
            span = [i for i,w in enumerate(nw) if w.start()<stop and w.end()>start]
            assert ' '.join(nw[i].group() for i in span) == phrase
            nr = dict(r, item_id='E22:'+r['item_id']+':'+kind, parent_item_id=r['item_id'], parent_experiment=ex,
                      exclusion_style=style, readout_frame='neutral_entity', target_kind=kind, sentence=text,
                      target_start_char=start, target_stop_char=stop, target_span_word_indices=span,
                      target_phrase_sha256=digest(phrase), target_context_sha256=digest(pre), sentence_sha256=digest(text),
                      prior_facts_preserved=r['audit_facts_preserved'], prior_faithful_role=r['faithful_order'],
                      transformation='Exact source S1, exclusive-role statement and same-activity bridge retained; source actor later noticed own/other author NP. Notice imposes no original event-patient role.')
            for k in list(nr):
                if k.startswith('audit_'): del nr[k]
            rows.append(nr)
    assert len(rows) == 224
    write_jsonl(out, rows)
    return dict(variants=len(rows), candidate_sha256=sha(out))


def adopt(data, reviews, idmap, out):
    report = adopt_neutral(data, reviews, idmap, out)
    rows = list(map(json.loads, out.read_text().splitlines()))
    for r in rows:
        r['faithful_role_neutral'] = r['prior_faithful_role'] and r['neutral_role_clear']
    write_jsonl(out, rows)
    report.update(audited_sha256=sha(out), faithful_role_neutral=sum(r['faithful_role_neutral'] for r in rows),
                  note='Original GP readability was rated marginal by both reviewers. Acceptable-only GP/comma contrasts can be empty; neither grammar ratings nor old fact ratings are overridden. Other-author NP is a legitimate new-referent foil, not assumed previously mentioned.')
    out.with_suffix('.audit.json').write_text(json.dumps(report, indent=2)+'\n')
    return report


def analyze(cache, newpath):
    cn, neutral = read_run(newpath)
    assert len(neutral) == 224
    relation, configs = [], {}
    for ex, style in [('E20', 'named'), ('E21', 'generic')]:
        configs[ex], rs = read_run(cache/'runs'/ex)
        for k in ('model_manifest','dtype','tf32','attention','seed','torch','transformers','batch_size','frozen'):
            assert configs[ex][k] == cn[k], k
        relation += [dict(r, exclusion_style=style) for r in rs if r['episode_anchor']=='same' and r['target_kind']!='source_reference' and (ex=='E20' or r['exclusion_style']==style)]
    assert len(relation) == 224
    def key(r): return (r['pair_id'], r['source_np_option'], r['condition'], r['role_evidence'], r['exclusion_style'], r['target_kind'])
    relix = {key(r):r for r in relation}
    assert set(relix) == {key(r) for r in neutral}
    result = dict(experiment='E22', units='bits', physical_tasks=224, bootstrap_draws=10000, bootstrap_seed=20261005,
                  formulas={'M':'bits(other author NP) - bits(own author NP)', 'D':'M_GP - M_comma',
                            'style_change':'M_named - M_generic within each condition',
                            'role_specific_change':'style_change_relation - style_change_neutral'},
                  interpretation='Separates post-correction general entity accessibility from predicate-dependent own-patient preference. Neither likelihood contrast is semantic accuracy or proof of internal role bindings.',
                  scores_sha256={'E22':cn['scores_sha256'], **{ex:c['scores_sha256'] for ex,c in configs.items()}},
                  analysis_code_sha256=sha(Path(__file__)), cells={}, contrasts={}, per_source={})
    def stat(v):
        s = estimate([v[k] for k in sorted(v)]) if len(v)>1 else dict(estimate=next(iter(v.values()),None), ci95=None, n_sets=len(v))
        return dict(s, pair_ids=sorted(v))
    def diff(a,b): return {k:a[k]-b[k] for k in a.keys()&b.keys()}
    for stratum in ('all','eligible','acceptable','neutral_role_clear','faithful_role_neutral'):
        # Require both styles to qualify for the same exact variant. GP and
        # comma intersections occur when computing D; no marginal GP deletion
        # is concealed behind an acceptable-only aggregate.
        keep = set.intersection(*({(r['pair_id'],r['source_np_option'],r['condition'],r['role_evidence'],r['target_kind']) for r in neutral if r['exclusion_style']==s and (stratum=='all' or r[stratum])} for s in ('named','generic')))
        rr = [r for r in neutral if (r['pair_id'],r['source_np_option'],r['condition'],r['role_evidence'],r['target_kind']) in keep]
        ix = {key(r):r for r in rr}
        for option in (0,1,'both'):
            prefix=f'{stratum}/option{option}'; vectors={}; details={}
            for frame, rowsix in [('neutral',ix),('relation',relix)]:
                for style in ('named','generic'):
                    for evidence in ('reference_only','initial_patient_only'):
                        for condition in ('gp','explicit_cue'):
                            v={}
                            for sid in {r['pair_id'] for r in rr}:
                                choices=(0,1) if option=='both' else (option,); obs=[]
                                for o in choices:
                                    ko=(sid,o,condition,evidence,style,'source_np'); kf=(*ko[:-1],'other_source_np')
                                    if ko not in ix or kf not in ix: break
                                    own, other=rowsix[ko],rowsix[kf]
                                    assert own['target_context_sha256']==other['target_context_sha256']
                                    obs.append(other['target_total_bits']-own['target_total_bits'])
                                if len(obs)==len(choices): v[sid]=float(np.mean(obs))
                            vectors[(frame,style,evidence,condition)]=v
                            result['cells'][f'{prefix}/{frame}/{style}/{evidence}/{condition}']=stat(v)
                        d=diff(vectors[(frame,style,evidence,'gp')],vectors[(frame,style,evidence,'explicit_cue')])
                        result['contrasts'][f'{prefix}/D/{frame}/{style}/{evidence}']=stat(d)
                        details[f'D_{frame}_{style}_{evidence}']=d
            for evidence in ('reference_only','initial_patient_only'):
                for condition in ('gp','explicit_cue'):
                    changes={f:diff(vectors[(f,'named',evidence,condition)],vectors[(f,'generic',evidence,condition)]) for f in ('neutral','relation')}
                    for frame,v in changes.items():
                        result['contrasts'][f'{prefix}/named_minus_generic/{frame}/{evidence}/{condition}']=stat(v)
                        details[f'change_{frame}_{evidence}_{condition}']=v
                    interaction=diff(changes['relation'],changes['neutral'])
                    result['contrasts'][f'{prefix}/role_specific_change/{evidence}/{condition}']=stat(interaction)
                    details[f'role_specific_change_{evidence}_{condition}']=interaction
                ds={}
                for frame in ('neutral','relation'):
                    ds[frame]=diff(details[f'change_{frame}_{evidence}_gp'], details[f'change_{frame}_{evidence}_explicit_cue'])
                    result['contrasts'][f'{prefix}/history_style_change/{frame}/{evidence}']=stat(ds[frame])
                result['contrasts'][f'{prefix}/history_role_specific_change/{evidence}']=stat(diff(ds['relation'],ds['neutral']))
            common=set.intersection(*(set(v) for v in details.values()))
            result['per_source'][prefix]=[dict(pair_id=sid,**{k:v[sid] for k,v in details.items()}) for sid in sorted(common)]
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(); sub=p.add_subparsers(dest='action',required=True)
    b=sub.add_parser('build'); b.add_argument('--cache',type=Path,required=True); b.add_argument('--out',type=Path,required=True)
    a=sub.add_parser('adopt'); a.add_argument('--data',type=Path,required=True); a.add_argument('--reviews',type=Path,nargs='+',required=True); a.add_argument('--idmap',type=Path,required=True); a.add_argument('--out',type=Path,required=True)
    n=sub.add_parser('analyze'); n.add_argument('--cache',type=Path,required=True); n.add_argument('--new',type=Path,required=True); n.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    if args.action=='build': print(json.dumps(build(args.cache,args.out),indent=2))
    elif args.action=='adopt': print(json.dumps(adopt(args.data,args.reviews,args.idmap,args.out),indent=2))
    else: args.out.write_text(json.dumps(analyze(args.cache,args.new),indent=2)+'\n')
