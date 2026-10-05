"""E01: paired effects with explicit pair intersection and independent audit strata."""
import collections
import json
from pathlib import Path
import numpy as np
from analyze import estimate

def analyze_revision(rows):
    out={'cells':{},'paired_effects':{},'interactions':{},'joint':{},
         'interpretation':'Responses are separate frozen calls, not evidence of internal simultaneous parses.'}
    for stratum in ('eligible','acceptable'):
        selected=[r for r in rows if stratum=='eligible' or r['clean_stratum']]
        index={}
        for r in selected:
            key=(r['pair_id'],r['prompt_id'],r['condition'],r['extended'],r['question_type'])
            assert key not in index,'duplicate experiment row'
            index[key]=r
        def measure(values):
            if len(values)==1:
                return {'n_sets':1,'estimate':float(next(iter(values.values()))),'ci95':None,'pair_ids':sorted(values),
                        'uncertainty_note':'Only one lexical set: a bootstrap interval would give spurious zero-width precision.'}
            return dict(estimate(list(values.values())),pair_ids=sorted(values)) if values else {'n_sets':0,'estimate':None,'ci95':None,'pair_ids':[]}
        prompts=sorted({r['prompt_id'] for r in selected})
        for family in ('NPZ','NPS','MVRR'):
            sub=[r for r in selected if r['construction']==family]
            ids=sorted({r['pair_id'] for r in sub});conditions=sorted({r['condition'] for r in sub});qs=sorted({r['question_type'] for r in sub})
            def vals(pid,c,e,q,metric):
                return {sid:index[(sid,pid,c,e,q)][metric] for sid in ids if (sid,pid,c,e,q) in index and index[(sid,pid,c,e,q)][metric] is not None}
            def diff(a,b):return {s:a[s]-b[s] for s in a.keys()&b.keys()}
            for pid in prompts:
                prefix=f'{stratum}/{family}/{pid}'
                for q in qs:
                    for metric in ('p_yes','correct','choice_mass'):
                        for c in conditions:
                            for e in (False,True):
                                out['cells'][f'{prefix}/{c}/{int(e)}/{q}/{metric}']=measure(vals(pid,c,e,q,metric))
                            out['paired_effects'][f'{prefix}/{c}/extension_minus_short/{q}/{metric}']=measure(diff(vals(pid,c,True,q,metric),vals(pid,c,False,q,metric)))
                        for c in conditions:
                            if c=='gp':continue
                            for e in (False,True):
                                out['paired_effects'][f'{prefix}/{c}_minus_gp/{int(e)}/{q}/{metric}']=measure(diff(vals(pid,c,e,q,metric),vals(pid,'gp',e,q,metric)))
                        gp_ext=diff(vals(pid,'gp',True,q,metric),vals(pid,'gp',False,q,metric))
                        cue_ext=diff(vals(pid,'explicit_cue',True,q,metric),vals(pid,'explicit_cue',False,q,metric))
                        out['interactions'][f'{prefix}/extension_DiD_gp_minus_cue/{q}/{metric}']=measure(diff(gp_ext,cue_ext))
                    for c in conditions:
                        for e in (False,True):
                            for kind,final,initial in [('role','intended','lingering'),('semantic','intended_semantic','lingering_semantic')]:
                                a=vals(pid,c,e,final,'p_yes');b=vals(pid,c,e,initial,'p_yes')
                                out['joint'][f'{prefix}/{c}/{int(e)}/{kind}/both_supported']=measure({s:int(a[s]>.5 and b[s]>.5) for s in a.keys()&b.keys()})
                                if kind=='role':
                                    consistent={s for s in a.keys()&b.keys() if index[(s,pid,c,e,final)]['gold']=='Yes' and index[(s,pid,c,e,initial)]['gold']=='No'}
                                    out['joint'][f'{prefix}/{c}/{int(e)}/role/correct_final_and_incorrect_initial']=measure({s:int(a[s]>.5 and b[s]>.5) for s in consistent})
            for frame in ('neutral','upstream'):
                for repair in ('base','repair'):
                    p1=f'{frame}_reg_{repair}';p2=f'{frame}_rev_{repair}'
                    for q in qs:
                        for c in conditions:
                            if c=='gp':continue
                            for e in (False,True):
                                d1=diff(vals(p1,c,e,q,'p_yes'),vals(p1,'gp',e,q,'p_yes'))
                                d2=diff(vals(p2,c,e,q,'p_yes'),vals(p2,'gp',e,q,'p_yes'))
                                out['interactions'][f'{stratum}/{family}/{frame}/{repair}/{c}/cue_by_order/{int(e)}/{q}']=measure(diff(d1,d2))
    return out
