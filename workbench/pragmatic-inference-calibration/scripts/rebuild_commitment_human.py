"""E40: executable source join and original Exp2 OLS parity; no mixed-model claim."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from commitment_data import table,prepare

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args();assert not a.output.exists();rows,audit=prepare(a.root)
raw=table(a.root/'upstream/implicit-dominance-2026/Experiment_2_data.xlsx');participants={r['participants'] for r in raw}
kept={p for p in participants if sum(r['is_corr_q1']==0 for r in raw if r['participants']==p)<=2}
r=[z for z in raw if z['participants'] in kept and z['ans_match']==1 and z['question_type']=='meaning']
x=np.array([[1,z['SoA_implicit'],z['SoA_explicit'],z['SoA_implicit']*z['SoA_explicit']] for z in r],dtype=float)
y=np.array([z['slider_commitment.response'] for z in r],dtype=float)
beta=np.linalg.lstsq(x,y,rcond=None)[0];expected=[9.27,2.98,18.28]
assert len(r)==356 and all(round(float(b),2)==v for b,v in zip(beta[1:],expected))
out={'source_audit':audit,'source_join_gate_pass':True,'original_meaning_lm':{'n':len(r),
    'terms':['Intercept','SoA_implicit','SoA_explicit','SoA_implicit:SoA_explicit'],
    'coefficients':beta.tolist(),'published_rounded_nonintercept':expected,'rounded_parity_pass':True},
    'source_code_sha256':hashlib.sha256((a.root/'upstream/implicit-dominance-2026/notebook_what_is.Rmd').read_bytes()).hexdigest(),
    'limits':['Exp2 released code uses OLS for meaning after convergence failure; not reproducing the other R mixed models.',
        'Exp1 filtering mismatch remains isolated; this audit does not claim all three experiments are exact.',
        'Transcription rechecked by root, no independent human audit.']}
a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out['original_meaning_lm']))
