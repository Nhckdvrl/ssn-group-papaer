"""E35 paired authority instruction; frozen E34 cohorts, no prompt selection."""
import argparse
import collections
import json
from pathlib import Path
import numpy as np
from data import sha
from analyze_source_ablation import stat, diff


def analyze(base, recovery, parent):
    configs=[]; rows={}
    for label,path in [('base',base),('current_world',recovery)]:
        c=json.loads((path/'config.json').read_text())
        assert sha(path/'predictions.jsonl')==c['predictions_sha256']
        rr=list(map(json.loads,(path/'predictions.jsonl').read_text().splitlines()))
        assert len(rr)==2304 and c['task_count']==2304
        configs.append(c);rows[label]=rr
    for k in ('model_manifest','dtype','tf32','attention','seed','frozen','thinking','batch_size','data_sha256','base_definition'):
        assert configs[0][k]==configs[1][k], k
    assert configs[1]['mode']=='current_world'
    index={label:{(r['item_id'],r['mapping_shift']):r for r in rr} for label,rr in rows.items()}
    assert index['base'].keys()==index['current_world'].keys()
    cohorts=json.loads(parent.read_text())['nli']['cohorts']
    out=dict(experiment='E35',tasks=2304,actual_gpu_hours=configs[1]['gpu_hours'],units='percentage points',
             bootstrap_unit='12 verb families, two sources averaged; paired mappings',
             bootstrap_draws=10000,bootstrap_seed=20261005,parent_sha256=sha(parent),
             scores_sha256={label:c['predictions_sha256'] for label,c in zip(rows,configs)},
             authority_instruction=configs[1]['current_world_repair'],cells={},contrasts={},per_family={})
    for co,keep in cohorts.items():
        vals={}; per={f:{} for f in keep}
        for status in ('factual_report','hypothetical_example'):
            for conflict in (False,True):
                for kind in ('old_source_patient','old_reference_patient','other_actor_new_activity','unrelated_unknown_control'):
                    for mapping,maps in [('all',(0,1,2)),('map0',(0,)),('map1',(1,)),('map2',(2,))]:
                        for final in ('balanced','reference_only','initial_patient_only'):
                            for measure in ('correct','p_correct','p_entailed','p_contradicted','p_undetermined','choice_mass','greedy_label_valid'):
                                key=f'{status}/conflict{int(conflict)}/{kind}/{mapping}/{final}/{measure}'
                                for label,rr in rows.items():
                                    vv={}
                                    for f,sids in keep.items():
                                        obs=[r for r in rr if r['pair_id'] in sids and r['initial_status']==status and r['history_conflict']==conflict and r['readout_kind']==kind and r['mapping_shift'] in maps and (final=='balanced' or r['final_role']==final)]
                                        assert len(obs)==(4 if final=='balanced' else 2)*len(maps)
                                        vv[f]=100*float(np.mean([r['p_relation'][measure[2:]] if measure in ('p_entailed','p_contradicted','p_undetermined') else r[measure] for r in obs]))
                                    vals[label,key]=vv;out['cells'][f'{co}/{label}/{key}']=stat(vv)
                                    if final=='balanced' and measure=='correct':
                                        for f in keep:per[f][label+'/'+key]=vv[f]
                                out['contrasts'][f'{co}/current_world_minus_base/{key}']=stat(diff(vals['current_world',key],vals['base',key]))
        out['per_family'][co]=[dict(verb_family=f,**per[f]) for f in sorted(keep)]
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--recovery',type=Path,required=True);p.add_argument('--parent',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    a.out.write_text(json.dumps(analyze(a.base,a.recovery,a.parent),indent=2)+'\n')
