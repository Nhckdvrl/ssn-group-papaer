"""E17 neutral entity mention versus original activity-dependent patient use."""
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


def build(cache,out):
    assert not out.exists()
    fields={r['pair_id']:r for r in json.loads((cache/'E14-material-preparation-v1/fields-v3.json').read_text())['rows']}
    parents=[]
    for ex in ('E14','E15'):
        parents += [(ex,r) for r in map(json.loads,(cache/f'{ex}-material-preparation-v1/audited-v1.jsonl').read_text().splitlines()) if r['target_kind']=='source_np' and r['episode_anchor']!='separate']
    ix={(ex,r['pair_id'],r['source_np_option'],r['condition'],r['episode_anchor']):r for ex,r in parents}
    output=[]
    for ex,r in parents:
        words=list(re.finditer(r'\S+',r['sentence']));prefix=r['sentence'][:words[r['authored_followup_start_word']].start()]
        actor=fields[r['pair_id']]['S2_subject']
        for kind,o in [('source_np',r['source_np_option']),('other_source_np',1-r['source_np_option'])]:
            other=ix[(ex,r['pair_id'],o,r['condition'],r['episode_anchor'])]
            phrase=other['sentence'][other['target_start_char']:other['target_stop_char']]
            text=prefix+actor+' later noticed '+phrase+' for a moment.'
            start=len(prefix+actor+' later noticed ');stop=start+len(phrase)
            nw=list(re.finditer(r'\S+',text));span=[i for i,w in enumerate(nw) if w.start()<stop and w.end()>start]
            assert ' '.join(nw[i].group() for i in span)==phrase
            nr=dict(r,item_id='E17:'+r['item_id']+':'+kind,target_kind=kind,sentence=text,parent_item_id=r['item_id'],parent_experiment=ex,
                target_start_char=start,target_stop_char=stop,target_span_word_indices=span,target_phrase_sha256=digest(phrase),target_context_sha256=digest(text[:start]),
                sentence_sha256=digest(text),neutral_actor=actor,source_followup_sha256=digest(r['sentence'][len(prefix):]),
                transformation='Exact S1 and bridge retained; independently annotated source actor later noticed own or other author-provided NP. No original event-role predicate in the new continuation.')
            for k in list(nr):
                if k.startswith('audit_'):del nr[k]
            output.append(nr)
    assert len(output)==528
    write_jsonl(out,output)
    return dict(variants=528,candidate_sha256=sha(out))


def adopt_neutral(data,reviews,idmap,out):
    # Generic independent grammar/reference adoption, plus this contrast's
    # predeclared neutral-role requirement, never inferred from model scores.
    report=adopt(data,reviews,idmap,out)
    mapping=json.loads(idmap.read_text());annotations={}
    for p in reviews:
        for a in json.loads(p.read_text())['variant_reviews']:
            assert a['original_event_role_required'] in (True,False,None)
            annotations[mapping[a['id']]]=a['original_event_role_required']
    rows=list(map(json.loads,out.read_text().splitlines()))
    for r in rows:
        r['audit_original_event_role_required']=annotations[r['item_id']]
        r['neutral_role_clear']=r['eligible'] and annotations[r['item_id']] is False
    write_jsonl(out,rows)
    report.update(audited_sha256=sha(out),neutral_role_clear=sum(r['neutral_role_clear'] for r in rows))
    out.with_suffix('.audit.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


def analyze(cache,newpath):
    parents={};configs={}
    for ex in ('E14','E15'):
        configs[ex],rs=read_run(cache/'runs'/ex);parents.update({r['item_id']:r for r in rs})
    configs['E16'],relation=read_run(cache/'runs/E16')
    cn,neutral=read_run(newpath);assert len(neutral)==528
    for cfg in configs.values():
        for k in ('model_manifest','dtype','tf32','attention','seed','torch','transformers','batch_size','frozen'):assert cfg[k]==cn[k],k
    rel={}
    for r in relation:
        own=parents[r['parent_item_id']]
        rel[(r['pair_id'],r['source_np_option'],r['condition'],r['episode_anchor'])]=r['target_total_bits']-own['target_total_bits']
    result=dict(experiment='E17',units='bits',primary='K = (GP-minus-comma mentioned-NP preference in activity-dependent continuation) minus the same contrast in neutral noticed continuation.',
        scope_interaction='A_K = K_continued_same - K_continued_separate. Compare E16 A_M with neutral A_M.',
        interpretation='Tests whether entity accessibility alone accounts for original patient preference. A difference can still reflect predicate-associated lexical retrieval, not a stored event graph.',
        bootstrap_seed=20261005,bootstrap_draws=10000,physical_tasks=528,cells={},contrasts={},per_source={},
        scores_sha256={'E17':cn['scores_sha256'],**{ex:cfg['scores_sha256'] for ex,cfg in configs.items()}},analysis_code_sha256=sha(Path(__file__)))
    def stat(v):
        s=estimate([v[k] for k in sorted(v)]) if len(v)>1 else dict(estimate=next(iter(v.values()),None),ci95=None,n_sets=len(v))
        return dict(s,pair_ids=sorted(v))
    def diff(a,b):return {k:a[k]-b[k] for k in a.keys()&b.keys()}
    for stratum in ('all','eligible','acceptable','neutral_role_clear','episodic_reference'):
        for option in (0,1,'both'):
            rr=[r for r in neutral if stratum=='all' or (r['eligible'] and r[stratum])]
            ix={(r['pair_id'],r['source_np_option'],r['condition'],r['episode_anchor'],r['target_kind']):r for r in rr}
            assert len(ix)==len(rr)
            prefix=f'{stratum}/option{option}';Ds={};Ks={}
            for anchor in ('none','same','continued_separate'):
                vals={'neutral':{},'relation':{}}
                for condition in ('gp','explicit_cue'):
                    for kind in vals:
                        v={}
                        for sid in {r['pair_id'] for r in rr}:
                            choices=(0,1) if option=='both' else (option,);a=[]
                            for o in choices:
                                own=ix.get((sid,o,condition,anchor,'source_np'));other=ix.get((sid,o,condition,anchor,'other_source_np'))
                                if own is None or other is None:break
                                assert own['target_context_sha256']==other['target_context_sha256']
                                if kind=='neutral':a.append(other['target_total_bits']-own['target_total_bits'])
                                else:a.append(rel[(sid,o,condition,anchor)])
                            if len(a)==len(choices):v[sid]=float(np.mean(a))
                        vals[kind][condition]=v
                        result['cells'][f'{prefix}/{kind}/{anchor}/{condition}']=stat(v)
                ds={kind:diff(v['gp'],v['explicit_cue']) for kind,v in vals.items()}
                for kind,d in ds.items():result['contrasts'][f'{prefix}/D_{kind}/{anchor}']=stat(d)
                Ks[anchor]=diff(ds['relation'],ds['neutral']);Ds[anchor]=ds
                result['contrasts'][f'{prefix}/K/{anchor}']=stat(Ks[anchor])
            for kind in ('neutral','relation'):
                result['contrasts'][f'{prefix}/A_{kind}']=stat(diff(Ds['same'][kind],Ds['continued_separate'][kind]))
            result['contrasts'][f'{prefix}/A_K']=stat(diff(Ks['same'],Ks['continued_separate']))
            common=Ks['same'].keys()&Ks['continued_separate'].keys()
            result['per_source'][prefix]=[dict(pair_id=k,**{f'K_{a}':v[k] for a,v in Ks.items() if k in v},
                A_neutral=Ds['same']['neutral'][k]-Ds['continued_separate']['neutral'][k],
                A_relation=Ds['same']['relation'][k]-Ds['continued_separate']['relation'][k]) for k in sorted(common)]
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True)
    b=s.add_parser('build');b.add_argument('--cache',type=Path,required=True);b.add_argument('--out',type=Path,required=True)
    a=s.add_parser('adopt');a.add_argument('--data',type=Path,required=True);a.add_argument('--reviews',type=Path,nargs='+',required=True);a.add_argument('--idmap',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
    n=s.add_parser('analyze');n.add_argument('--cache',type=Path,required=True);n.add_argument('--new',type=Path,required=True);n.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    if args.action=='build':print(json.dumps(build(args.cache,args.out),indent=2))
    elif args.action=='adopt':print(json.dumps(adopt_neutral(args.data,args.reviews,args.idmap,args.out),indent=2))
    else:args.out.write_text(json.dumps(analyze(args.cache,args.new),indent=2)+'\n')
