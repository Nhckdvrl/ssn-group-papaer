"""POST-HOC E29: check whether negative J is patient reversal or neutral rise.

No new inference or labels. Report every condition/style and pre-existing
cohort, including unfavorable or uncertain cells.
"""
import argparse
import collections
import json
from pathlib import Path
import numpy as np
from analyze_source_ablation import stat, diff
from aspect_reference import read_run
from data import CACHE, sha


def analyze(cache,summary):
    cohorts=json.loads(summary.read_text())['probability']['cohorts'];rows=[]
    for ex in ('E24','E25','E29-probability'):
        _,rr=read_run(cache/'runs'/ex)
        rows.extend(dict(r,readout_actor_mode='original_activity' if ex=='E24' else r['readout_actor_mode']) for r in rr if r['target_kind']!='source_reference')
    ix={(r['pair_id'],r['condition'],r['readout_actor_mode'],r['role_evidence'],r['exclusion_style'],r['readout_frame'],r['target_kind']):r for r in rows}
    out=dict(experiment='E29',analysis_status='POST-HOC cell decomposition and event interaction of preregistered J, before any E30 inference',
             units='bits',formula='Role effect = M_initialOnly minus M_referenceOnly. Negative at activity means candidate preference shifts opposite to the old patient fact; negative J alone is insufficient.',
             summary_sha256=sha(summary),analysis_code_sha256=sha(Path(__file__)),cells={},contrasts={},per_family={})
    for cohort,keep in cohorts.items():
        vectors={};details={f:{} for f in keep}
        for condition in ('gp','explicit_cue','event_anchor_only'):
            for mode in ('original_activity','same_actor','other_actor'):
                for style in ('named','generic'):
                    for frame in ('activity','neutral_entity'):
                        v={}
                        for f,sids in keep.items():
                            obs=[]
                            for sid in sids:
                                values={}
                                for evidence in ('reference_only','initial_patient_only'):
                                    k=(sid,condition,mode,evidence,style,frame);a,b=ix[(*k,'source_np')],ix[(*k,'other_source_np')]
                                    values[evidence]=b['target_total_bits']-a['target_total_bits']
                                obs.append(values['initial_patient_only']-values['reference_only'])
                            v[f]=float(np.mean(obs))
                        vectors[condition,mode,style,frame]=v;key=f'{condition}/{mode}/{style}/{frame}'
                        out['cells'][cohort+'/'+key]=stat(v)
                        for f in keep:details[f][key]=v[f]
            for mode in ('same_actor','other_actor'):
                for style in ('named','generic'):
                    for frame in ('activity','neutral_entity'):
                        key=f'{condition}/{mode}_minus_original/{style}/{frame}';v=diff(vectors[condition,mode,style,frame],vectors[condition,'original_activity',style,frame]);out['contrasts'][cohort+'/'+key]=stat(v)
                        for f in keep:details[f][key]=v[f]
        out['per_family'][cohort]=[dict(verb_family=f,source_items=keep[f],**details[f]) for f in sorted(keep)]
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--summary',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.write_text(json.dumps(analyze(a.cache,a.summary),indent=2)+'\n')
