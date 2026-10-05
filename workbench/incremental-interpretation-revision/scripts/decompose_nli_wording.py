"""Separate named/generic NLI use: E30 POST-HOC, E31 preregistered."""
import argparse
import json
from pathlib import Path
import numpy as np
from data import CACHE,sha
from analyze_source_ablation import stat,diff


def analyze(cache,experiment,summary=None):
    jobs=[('separate',cache/'runs/E29-nli')]
    jobs+= [('second',cache/'runs/E30-nli-base')] if experiment=='E30' else [('from_row',cache/'runs/E31-nli-base')]
    rows=[];hashes={}
    for marker,p in jobs:
        cfg=json.loads((p/'config.json').read_text());assert cfg['predictions_sha256']==sha(p/'predictions.jsonl')
        hashes[p.name]=cfg['predictions_sha256']
        rows.extend(dict(r,marker=r['boundary_marker'] if marker=='from_row' else marker) for r in map(json.loads,(p/'predictions.jsonl').read_text().splitlines()) if r['readout_kind'] in ('same_actor_new_activity','other_actor_new_activity'))
    markers=('separate','second') if experiment=='E30' else ('separate','same_began','different_began')
    cohorts={'all':sorted({r['verb_family'] for r in rows})} if summary is None else {co:list(keep) for co,keep in json.loads(summary.read_text())['nli']['cohorts'].items()}
    out=dict(experiment=experiment,analysis_status='POST-HOC wording stratification of registered NLI signed-role readout, no new inference' if experiment=='E30' else 'Preregistered wording stratification after E30 diagnostics, no additional inference',units='percentage points',bootstrap_draws=10000,bootstrap_seed=20261005,source_predictions_sha256=hashes,analysis_code_sha256=sha(Path(__file__)),cells={},contrasts={})
    for co,families in cohorts.items():
        vectors={}
        for marker in markers:
            for kind in ('same_actor_new_activity','other_actor_new_activity'):
                for style in ('named','generic'):
                    rr=[r for r in rows if r['marker']==marker and r['readout_kind']==kind and r['exclusion_style']==style];vv={}
                    for fam in sorted(families):
                        aa=[r for r in rr if r['verb_family']==fam];assert len(aa)==12
                        ref=[r for r in aa if r['role_evidence']=='reference_only'];np_only=[r for r in aa if r['role_evidence']=='initial_patient_only']
                        vv[fam]=50*(np.mean([r['p_relation']['contradicted'] for r in ref])-np.mean([r['p_relation']['contradicted'] for r in np_only])+np.mean([r['p_relation']['entailed'] for r in np_only])-np.mean([r['p_relation']['entailed'] for r in ref]))
                    key=f'{co}/{marker}/{kind}/{style}';out['cells'][key]=dict(stat(vv),per_family=vv);vectors[marker,kind,style]=vv
        if experiment=='E31':
            for kind in ('same_actor_new_activity','other_actor_new_activity'):
                for style in ('named','generic'):
                    vv=diff(vectors['different_began',kind,style],vectors['same_began',kind,style]);out['contrasts'][f'{co}/different_minus_same/{kind}/{style}']=dict(stat(vv),per_family=vv)
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,default=CACHE);p.add_argument('--experiment',choices=['E30','E31'],required=True);p.add_argument('--summary',type=Path);p.add_argument('--out',type=Path,required=True);a=p.parse_args();a.out.write_text(json.dumps(analyze(a.cache,a.experiment,a.summary),indent=2)+'\n')
