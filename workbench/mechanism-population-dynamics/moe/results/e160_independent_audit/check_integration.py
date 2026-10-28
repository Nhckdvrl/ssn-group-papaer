"""CPU author-summary/comparator fixture; reads no experimental result arrays.

Only this test imports author statistics. Independent formulas stay in audit.py.
"""
import copy
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import numpy as np
WB=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(WB/'scripts'))
import e160_analyze as author
spec=importlib.util.spec_from_file_location('independent160_fixture',Path(__file__).with_name('audit.py'))
independent=importlib.util.module_from_spec(spec);spec.loader.exec_module(independent)


def main():
    rng=np.random.default_rng(7);gold=rng.integers(0,4,128)
    full=rng.normal(size=(3,3,128,4));full[:,:,:32]=-4
    full[:,:,np.arange(32),gold[:32]]=1
    full[1,2,64:]=0
    full[1,2,np.arange(64,128),(gold[64:]+1)%4]=3
    raw={'clamped_candidate_loglikelihood':full,
         'natural_candidate_loglikelihood':np.stack([full[i,i] for i in range(3)]),
         'without_shared_candidate_loglikelihood':rng.normal(size=(3,128,4)),
         'without_routed_fixed_shared_candidate_loglikelihood':rng.normal(size=(3,128,4)),
         'without_routed_natural_shared_candidate_loglikelihood':rng.normal(size=(128,4)),
         'without_both_candidate_loglikelihood':rng.normal(size=(128,4)),
         'gold':gold,'subject':np.repeat([0,1],64),'answer_tokens':rng.integers(1,8,(128,4)),
         'answer_chars':rng.integers(4,30,(128,4)),
         'consumer_names':np.array(['P','A','B']),'producer_names':np.array(['P','A','B']),
         'shared_signal_hashes':np.full((3,128),'a'*64,dtype='U64')}
    summary=author.summarize(raw)
    with tempfile.TemporaryDirectory(prefix='e160-summary-cpu-') as directory:
        plan=Path(directory)/'plan.json';plan.write_text('{}')
        manifest={'raw':{'sha256':'fixture'},'source_sha256':{'e160_analyze.py':'analysis_fixture'}}
        summary.update(raw_sha256='fixture',plan_sha256=independent.sha(plan),analysis_source_sha256='analysis_fixture')
        result=independent.compare_summary(raw,summary,manifest,plan)
        assert result['status']=='passed',result
        changes=[]
        for kind in ('point','interval','count','null'):
            altered=copy.deepcopy(summary)
            primary=altered['metrics']['true_answer_token_NLL']['primary']['conditions']['full'][0][1]
            if kind=='point':primary['point']+=.1
            elif kind=='interval':primary['question_ci95'][0]+=.1
            elif kind=='count':primary['count']-=1
            else:altered['metrics']['raw_accuracy']['secondary']['conditions']['full'][0][0]['point']=0
            rejected=independent.compare_summary(raw,altered,manifest,plan)
            assert rejected['status']=='failed',(kind,rejected)
            changes.append(kind)
    report={'status':'passed','CPU_only':True,'scientific_raw_read':False,
            'comparison':result,'intentional_corruptions_rejected':changes,
            'fixture':'all 128 primary inputs, selected cohort absent in math, all metrics and contrast matrices',
            'audit_source_sha256':independent.sha(Path(__file__).with_name('audit.py')),
            'fixture_source_sha256':independent.sha(__file__)}
    Path(__file__).with_name('integration_test.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
