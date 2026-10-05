"""E19 explicit episode-local role evidence before same/separate bridges."""
import argparse
import json
from pathlib import Path
import re
import numpy as np
from data import sha, write_jsonl
from event_identity import digest
from aspect_reference import read_run
from analyze import estimate
from patient_crossover import adopt


def build(cache,fields_path,out,anchors=('same','continued_separate'),experiment='E19'):
    assert not out.exists()
    fields={(r['pair_id'],r['np_option']):r for r in json.loads(fields_path.read_text())['rows']}
    packets={r['pair_id']:r for r in json.loads((fields_path.parent/'role-evidence-packets.json').read_text())['packets']}
    parents=[]
    for ex in ('E14','E15'):
        parents += [(ex,r) for r in map(json.loads,(cache/f'{ex}-material-preparation-v1/audited-v1.jsonl').read_text().splitlines()) if r['target_kind']=='source_np' and r['episode_anchor'] in anchors and r['episodic_reference']]
    refs={}
    for ex in ('E14','E15'):
        refs.update({r['item_id']:r for r in map(json.loads,(cache/f'{ex}-material-preparation-v1/audited-v1.jsonl').read_text().splitlines())})
    ix={(ex,r['pair_id'],r['source_np_option'],r['condition'],r['episode_anchor']):r for ex,r in parents}
    output=[]
    for ex,r in parents:
        f=fields[(r['pair_id'],r['source_np_option'])]
        assert f['input_sha256']==packets[r['pair_id']]['input_sha256']
        first_end=r['sentence'].index('. ')+1
        for evidence in ('reference_only','initial_patient_only'):
            statement=f[evidence+'_sentence'];assert statement.startswith('In that ') and statement.endswith('.')
            for kind,o in [('source_np',r['source_np_option']),('other_source_np',1-r['source_np_option']),('source_reference',None)]:
                if o is None:
                    b=refs[r['item_id'].replace(':source_np',':source_reference')]
                else:b=ix[(ex,r['pair_id'],o,r['condition'],r['episode_anchor'])]
                phrase=b['sentence'][b['target_start_char']:b['target_stop_char']]
                suffix=r['sentence'][first_end:r['target_start_char']]+phrase+r['sentence'][r['target_stop_char']:]
                text=r['sentence'][:first_end]+' '+statement+suffix
                start=r['target_start_char']+len(statement)+1;stop=start+len(phrase)
                words=list(re.finditer(r'\S+',text));span=[i for i,w in enumerate(words) if w.start()<stop and w.end()>start]
                assert ' '.join(words[i].group() for i in span)==phrase
                nr=dict(r,item_id=f'{experiment}:{r["item_id"]}:{evidence}:{kind}',target_kind=kind,sentence=text,parent_item_id=r['item_id'],parent_experiment=ex,
                    role_evidence=evidence,target_start_char=start,target_stop_char=stop,target_span_word_indices=span,target_phrase_sha256=digest(phrase),target_context_sha256=digest(text[:start]),sentence_sha256=digest(text),
                    authored_followup_start_word=r['authored_followup_start_word']+len(statement.split()),role_fields_sha256=sha(fields_path),
                    transformation='Exact S1 and same/separate bridge retained. Independently constructed explicit role evidence limited to original episode inserted between S1 and bridge; author S2 target is reference/own/other NP.')
                for k in list(nr):
                    if k.startswith('audit_'):del nr[k]
                output.append(nr)
    assert len(output)==7*2*2*2*len(anchors)*3
    write_jsonl(out,output)
    return dict(variants=len(output),source_items=7,candidate_sha256=sha(out),fields_sha256=sha(fields_path))


def adopt_roles(data,reviews,idmap,out):
    report=adopt(data,reviews,idmap,out)
    mapping=json.loads(idmap.read_text());annotations={}
    for p in reviews:
        for a in json.loads(p.read_text())['variant_reviews']:
            assert a['event_scope'] in ('original_episode','new_episode','uncertain')
            assert a['role_exclusivity'] in ('clear','uncertain')
            assert a['target_episode_scope'] in ('original_episode','new_episode','uncertain')
            assert a['temporal_compatibility'] in ('clear','uncertain','conflict')
            annotations[mapping[a['id']]]=a
    rows=list(map(json.loads,out.read_text().splitlines()))
    for r in rows:
        a=annotations[r['item_id']]
        expected='original_episode' if r['episode_anchor']=='same' else 'new_episode'
        r.update(audit_target_episode_scope=a['target_episode_scope'],clear_episode_readout=r['eligible'] and a['target_episode_scope']==expected,audit_event_scope=a['event_scope'],audit_role_exclusivity=a['role_exclusivity'],audit_temporal_compatibility=a['temporal_compatibility'],
                 clear_role_evidence=r['eligible'] and a['event_scope']=='original_episode' and a['role_exclusivity']=='clear' and a['temporal_compatibility']=='clear' and a['target_episode_scope']==expected)
    write_jsonl(out,rows)
    report.update(audited_sha256=sha(out),clear_role_evidence=sum(r['clear_role_evidence'] for r in rows))
    out.with_suffix('.audit.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def analyze(cache,path):
    cfg,rows=read_run(path);assert len(rows)==336
    parent={};oldcfg={}
    for ex in ('E14','E15'):
        oldcfg[ex],rs=read_run(cache/'runs'/ex);parent.update({r['item_id']:r for r in rs})
    oldcfg['E16'],cross=read_run(cache/'runs/E16')
    for old in oldcfg.values():
        for k in ('model_manifest','dtype','tf32','attention','seed','torch','transformers','batch_size','frozen'):assert old[k]==cfg[k],k
    baseline=[]
    for r in cross:
        if r['episodic_reference'] and r['episode_anchor'] in ('same','continued_separate'):
            own=parent[r['parent_item_id']];ref=parent[r['parent_item_id'].replace(':source_np',':source_reference')]
            baseline.append(dict(r,role_evidence='none',R=own['target_total_bits']-ref['target_total_bits'],M=r['target_total_bits']-own['target_total_bits']))
    result=dict(experiment='E19',units='bits',primary='Does explicit exclusive role evidence reduce GP-minus-comma history dependence in the original versus a separate activity?',
        formulas={'R':'bits(own NP) - bits(source reference)','M':'bits(other NP) - bits(own NP)'},
        interpretation='Role-evidence dependence of continuations; separate episode unconstrained, so its NP preference has no semantic accuracy label. Evidence sentences are experimental narrative information, not author gold.',
        bootstrap_draws=10000,bootstrap_seed=20261005,physical_tasks=336,cells={},contrasts={},per_source={},scores_sha256={'E19':cfg['scores_sha256'],**{ex:c['scores_sha256'] for ex,c in oldcfg.items()}},analysis_code_sha256=sha(Path(__file__)))
    def stat(v):
        s=estimate([v[k] for k in sorted(v)]) if len(v)>1 else dict(estimate=next(iter(v.values()),None),ci95=None,n_sets=len(v))
        return dict(s,pair_ids=sorted(v))
    def diff(a,b):return {k:a[k]-b[k] for k in a.keys()&b.keys()}
    for stratum in ('all','eligible','acceptable','clear_episode_readout','clear_role_evidence'):
        rr=[r for r in rows if stratum=='all' or r[stratum]]
        ix={(r['pair_id'],r['source_np_option'],r['condition'],r['episode_anchor'],r['role_evidence'],r['target_kind']):r for r in rr}
        assert len(ix)==len(rr)
        for option in (0,1,'both'):
            prefix=f'{stratum}/option{option}';effects={}
            for measure in ('R','M'):
                ds={};vs={}
                for evidence in ('none','reference_only','initial_patient_only'):
                    for anchor in ('same','continued_separate'):
                        cells={}
                        for condition in ('gp','explicit_cue'):
                            v={}
                            for sid in {r['pair_id'] for r in rr}:
                                choices=(0,1) if option=='both' else (option,);observations=[]
                                for o in choices:
                                    if evidence=='none':
                                        b=next((b for b in baseline if b['pair_id']==sid and b['source_np_option']==o and b['condition']==condition and b['episode_anchor']==anchor),None)
                                        # Enforce the reviewed pair cohort also for baseline comparisons.
                                        have=all(ix.get((sid,o,condition,anchor,e,t)) for e in ('reference_only','initial_patient_only') for t in ('source_np','other_source_np','source_reference'))
                                        if b is None or not have:break
                                        observations.append(b[measure])
                                    else:
                                        own=ix.get((sid,o,condition,anchor,evidence,'source_np'));other=ix.get((sid,o,condition,anchor,evidence,'other_source_np'));ref=ix.get((sid,o,condition,anchor,evidence,'source_reference'))
                                        if any(r is None for r in (own,other,ref)):break
                                        assert own['target_context_sha256']==other['target_context_sha256']==ref['target_context_sha256']
                                        observations.append(own['target_total_bits']-ref['target_total_bits'] if measure=='R' else other['target_total_bits']-own['target_total_bits'])
                                if len(observations)==len(choices):v[sid]=float(np.mean(observations))
                            cells[condition]=v;result['cells'][f'{prefix}/{measure}/{evidence}/{anchor}/{condition}']=stat(v)
                        vs[(evidence,anchor)]=cells;ds[(evidence,anchor)]=diff(cells['gp'],cells['explicit_cue'])
                        result['contrasts'][f'{prefix}/{measure}/D/{evidence}/{anchor}']=stat(ds[(evidence,anchor)])
                for evidence in ('reference_only','initial_patient_only'):
                    for anchor in ('same','continued_separate'):
                        result['contrasts'][f'{prefix}/{measure}/history_change/{evidence}/{anchor}']=stat(diff(ds[(evidence,anchor)],ds[('none',anchor)]))
                for anchor in ('same','continued_separate'):
                    for condition in ('gp','explicit_cue'):
                        result['contrasts'][f'{prefix}/{measure}/role_evidence_effect/{anchor}/{condition}']=stat(diff(vs[('reference_only',anchor)][condition],vs[('initial_patient_only',anchor)][condition]))
                for evidence in ('none','reference_only','initial_patient_only'):
                    result['contrasts'][f'{prefix}/{measure}/scope_history/{evidence}']=stat(diff(ds[(evidence,'same')],ds[(evidence,'continued_separate')]))
                effects[measure]=ds
            common=set.intersection(*(set(d) for ds in effects.values() for d in ds.values()))
            result['per_source'][prefix]=[dict(pair_id=k,**{f'{m}_D_{e}_{a}':ds[(e,a)][k] for m,ds in effects.items() for e,a in ds}) for k in sorted(common)]
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True)
    b=s.add_parser('build');b.add_argument('--cache',type=Path,required=True);b.add_argument('--fields',type=Path,required=True);b.add_argument('--out',type=Path,required=True)
    a=s.add_parser('adopt');a.add_argument('--data',type=Path,required=True);a.add_argument('--reviews',type=Path,nargs='+',required=True);a.add_argument('--idmap',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
    n=s.add_parser('analyze');n.add_argument('--cache',type=Path,required=True);n.add_argument('--new',type=Path,required=True);n.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    if args.action=='build':print(json.dumps(build(args.cache,args.fields,args.out),indent=2))
    elif args.action=='adopt':print(json.dumps(adopt_roles(args.data,args.reviews,args.idmap,args.out),indent=2))
    else:args.out.write_text(json.dumps(analyze(args.cache,args.new),indent=2)+'\n')
