"""CPU summary-contract fixture using old B as simulated F, not new F outcomes.

This harness imports the author summary; audit.py itself has independent formulas.
"""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import time
import numpy as np

WB=Path(__file__).resolve().parents[2];ROOT=WB/'results'
sys.path.insert(0,str(WB/'scripts'))
import e162_analyze as author
spec=importlib.util.spec_from_file_location('independent162_fixture',Path(__file__).with_name('audit.py'))
ind=importlib.util.module_from_spec(spec);spec.loader.exec_module(ind)


def old(number,name='manifest.json'):
    manifest=json.loads((ROOT/f'e{number}'/name).read_text())
    with np.load(manifest['raw']['path'],allow_pickle=False) as file:return {k:file[k] for k in file.files}


def main():
    if (ROOT/'e162/manifest.json').exists():raise RuntimeError('Run fixture before actual F outcomes')
    a151=old(151);a152=old(152);parent=old(154);tasks=[old(155,f'manifest_{x}.json') for x in 'PAB']
    pcond={str(x):i for i,x in enumerate(parent['conditions'])}
    random_plan=json.loads((ROOT/'e151/plan.json').read_text())
    with np.load(random_plan['random_masks']['path'],allow_pickle=False) as file:random=file['masks'].copy()
    mask_plan=json.loads((ROOT/'e152/plan.json').read_text())
    with np.load(mask_plan['masks']['path'],allow_pickle=False) as file:prefix_B=file['masks'][1].copy()
    ref={'lm_native_metrics':np.concatenate((parent['metrics'][[pcond[c] for c in author.BRANCHES[:3]]][None],a151['metrics'][:,:3])),
         'lm_budget_AB':np.stack([a152['metrics'][i,[1+2*i+r for r in range(2)]+list(range(5,11))] for i in range(2)]).reshape(2,4,2,64,512,4),
         'lm_budget_P_pool':parent['metrics'][[pcond[c] for c in author.MASKS]],'lm_random_masks':random,
         'lm_valid':a151['valid'],'lm_suffix_valid':a151['suffix_valid'],
         'task_candidate_loglikelihood':np.stack([x['candidate_loglikelihood'] for x in tasks]),
         'task_first_answer_token_KL':np.stack([x['first_answer_token_KL'] for x in tasks]),
         **{k:tasks[0][k] for k in ('gold','subject','answer_tokens','answer_chars')}}
    new={'lm_metrics':np.concatenate((ref['lm_native_metrics'][2],ref['lm_native_metrics'][2,0:1],ref['lm_budget_AB'][1].reshape(8,64,512,4))),
         'lm_prefix_keep':prefix_B,'lm_random_masks':random,'lm_valid':a151['valid'],'lm_suffix_valid':a151['suffix_valid'],
         'lm_conditions':np.array(author.LM_CONDITIONS),'task_candidate_loglikelihood':tasks[2]['candidate_loglikelihood'],
         'task_first_answer_token_KL':tasks[2]['first_answer_token_KL'],'task_conditions':np.array(author.BRANCHES),
         **{k:tasks[0][k] for k in ('gold','subject','answer_tokens','answer_chars')}}
    groups=[x['file_id'] for x in json.loads((ROOT/'e150/plan.json').read_text())['selected']]
    start=time.monotonic();summary=author.summarize(new,ref,groups)
    result=ind.compare(new,ref,summary,groups)
    if result['status']!='passed':raise AssertionError(result)
    bad=copy.deepcopy(summary);bad['task']['true_answer_token_NLL']['F']['absolute']['native']['point']+=.1
    rejected=ind.compare(new,ref,bad,groups)
    assert rejected['status']=='failed'
    report={'status':'passed','CPU_only':True,'new_F_prediction_data_read':False,
        'fixture':'Old B simulated as F, real inherited masks/answer lengths. The placeholder D-only LM value is not scientific data.',
        'comparison':result,'intentional_point_corruption_rejected':True,'elapsed_seconds':time.monotonic()-start,
        'audit_source_sha256':ind.sha(Path(__file__).with_name('audit.py')),
        'analysis_source_sha256':ind.sha(WB/'scripts/e162_analyze.py'),'fixture_source_sha256':ind.sha(__file__)}
    Path(__file__).with_name('integration_test.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
