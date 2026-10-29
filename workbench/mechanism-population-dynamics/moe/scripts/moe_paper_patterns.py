"""Describe complete E166 subject patterns and calibration, without new inference."""
import hashlib
import json
from pathlib import Path
import numpy as np

MOE=Path(__file__).resolve().parents[1]
ROOT=MOE/'results/e166'


def read(p):return json.loads(Path(p).read_text())


def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    end=read(ROOT/'execution_complete.json');audit=read(ROOT/'independent_audit.json');plan=read(ROOT/'plan.json')
    assert end['status']=='complete' and audit['status']=='passed'
    result={'kind':'POST-HOC description of complete frozen results; no new hypotheses, CIs or model runs',
            'status':'complete','source_script_sha256':sha(__file__),'families':{}}
    for family in ('emo','olmoe'):
        path=ROOT/(family+'_summary.json');s=read(path);m=read(ROOT/(family+'_manifest.json'))
        assert sha(path)==end['summary_sha256'][family]==audit['families'][family]['summary_sha256']
        names=plan['families'][family]['subjects'];assert len(names)==55
        records={}
        for field in ('true_answer_token_NLL','choice_CE','raw_accuracy','per_char_accuracy'):
            for policy in ('full','pool'):
                keys=[policy+'/S1/'+label for label in ('donor_minus_P','GainP_minus_P')]
                x,y=[np.array([s[field][key]['per_subject'][n]['point'] for n in names]) for key in keys]
                sign=1 if field.endswith('accuracy') else -1
                records[field+'/'+policy]={'summary_json_paths':[[field,key,'per_subject'] for key in keys],
                    'subjects':55,'donor_improves':int((sign*x>0).sum()),'gain_improves':int((sign*y>0).sum()),
                    'both_improve':int(((sign*x>0)&(sign*y>0)).sum()),
                    'subject_effect_correlation':float(np.corrcoef(x,y)[0,1]) if x.std()>0 and y.std()>0 else None}
        cal=m['calibration'];assert sha(cal['path'])==cal['sha256']
        with np.load(cal['path'],allow_pickle=False) as z:
            coefficients={k:z[k].tolist() for k in ('gain','gain_FP64','cosine','scalar_residual_fraction','tokens')}
        result['families'][family]={'summary_path':str(path),'summary_sha256':sha(path),
                'raw_sha256':m['raw']['sha256'],'calibration':cal,'calibration_arrays':coefficients,
                'patterns':records,'interpretation':'Descriptive subject correspondence, not causal mediation or equivalence testing.'}
    out=MOE/'paper/e166_descriptive_patterns.json';out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':'complete','path':str(out),'families':2}))


if __name__=='__main__':main()
