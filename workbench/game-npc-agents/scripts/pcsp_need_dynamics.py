"""E40: source persona parameters only; preserve the running E34 harness file."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp'))
    ap.add_argument('--runs',type=Path,default=Path('/home/xiang/.cache/game-npc-research/runs'))
    ap.add_argument('--seed',type=int,choices=[42,43,44],required=True)
    ap.add_argument('--iteration',type=int,default=300)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(args.source/'research'))
    import numpy as np
    from src.env.mini_inzoi import PersonaConfig
    import pcsp_interest_edit as legacy
    all_rows=[]
    for split in ['train_400_v3','test_100_v3']:
        all_rows+=json.loads((args.source/f'research/data/personas/{split}.json').read_text())
    mapping={level:{float(row['decay_modifiers'][6]) for row in all_rows if row['big_five']['C']==level}
             for level in ['low','mid','high']}
    assert all(len(values)==1 for values in mapping.values()), 'Source body mapping needs review'
    mapping={level:next(iter(values)) for level,values in mapping.items()}
    original_body={int(row['id']):float(row['decay_modifiers'][6]) for row in all_rows}
    policy_prefix=args.runs/f'e34_eval_s{args.seed}_i{args.iteration}/policy_'
    while not all((Path(str(policy_prefix)+route)/'policy.pt').exists() for route in ['no','full']):time.sleep(15)
    original=PersonaConfig.from_dict; current_body='original'
    @classmethod
    def configured(cls,data):
        row=copy.deepcopy(data)
        if current_body!='original' and row.get('id') in legacy.BASE_IDS:
            row['decay_modifiers'][6]=mapping[current_body]
        return original(row)
    PersonaConfig.from_dict=configured
    controls={}; reports={}; start=time.monotonic()
    for condition,body in [('plain','low'),('plain','high'),('clarified','original')]:
        current_body=body;folder=args.out/f'{condition}_body_{body}'
        sys.argv=['pcsp_interest_edit.py','--mode','run','--source',str(args.source),'--runs',str(args.runs),
            '--codes',str(args.runs/'e33_codes'),'--out',str(folder),'--condition',condition,
            '--policy-prefix',str(policy_prefix),'--training-seed',str(args.seed)]
        legacy.main()
        reports[f'{condition}_{body}']=json.loads((folder/'summary.json').read_text())
        if condition=='plain':
            reference=args.runs/f'e34_eval_s{args.seed}_i{args.iteration}/interest'
            while not (reference/'summary.json').exists():time.sleep(5)
            duplicate_cases=[]; initial_controls=[]
            for route in ['no','full']:
                for pid in legacy.BASE_IDS:
                    for world in legacy.WORLD_SEEDS:
                        for level in ['high','low']:
                            name=f'{route}_{pid}_{level}_s{world}.npz'
                            with np.load(folder/name) as changed, np.load(reference/name) as baseline:
                                assert np.array_equal(changed['obs'][0],baseline['obs'][0])
                                assert np.array_equal(changed['actions'][0],baseline['actions'][0])
                                initial_controls.append(True)
                                if original_body[pid]==mapping[body]:
                                    assert all(np.array_equal(changed[k],baseline[k]) for k in baseline.files)
                                    duplicate_cases.append(name)
            controls[body]={'first_focal_observations_and_first_cycle_actions_equal':all(initial_controls),
                'initial_cases':len(initial_controls),'same_body_complete_replay_cases':len(duplicate_cases)}
        print(json.dumps({'seed':args.seed,'condition':condition,'body':body,'seconds':time.monotonic()-start}),flush=True)
    differences=[]
    for route in ['no','full']:
        for pid in legacy.BASE_IDS:
            for world in legacy.WORLD_SEEDS:
                for level in ['high','low']:
                    name=f'{route}_{pid}_{level}_s{world}.npz'
                    with np.load(args.out/'plain_body_low'/name) as low,np.load(args.out/'plain_body_high'/name) as high:
                        od=np.where(np.any(low['obs']!=high['obs'],axis=1))[0]
                        ad=np.where(np.any(low['actions']!=high['actions'],axis=1))[0]
                        differences.append({'route':route,'id':pid,'world':world,'input_C':level,
                            'first_observation_difference_cycle':int(od[0]) if len(od) else None,
                            'first_any_actor_action_difference_cycle':int(ad[0]) if len(ad) else None})
    result={'seed':args.seed,'iteration':args.iteration,'source_body_work_decay':mapping,'reports':reports,
        'controls':controls,'body_differences':differences,'wall_seconds':time.monotonic()-start,'cloud_calls':0,
        'legacy_clarification_required_field_is_not_a_scientific_decision':True,
        'original_harness_sha256':hashlib.sha256(Path(legacy.__file__).read_bytes()).hexdigest(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (args.out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':main()
