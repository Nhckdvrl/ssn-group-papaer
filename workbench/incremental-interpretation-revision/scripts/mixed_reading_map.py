"""Supplementary Bayesian logistic mixed model; bootstrap remains primary."""
import argparse
import collections
import json
from pathlib import Path
import time
import warnings
import numpy as np
import pandas as pd
from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM
from data import sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data',type=Path,required=True)
    parser.add_argument('--runs',type=Path,nargs='+',required=True);parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--stratum',choices=['genuine','initial_all'],default='genuine');args=parser.parse_args()
    metadata={r['item_id']:r for r in map(json.loads,args.data.read_text().splitlines())}
    observations=[];seen=set()
    for directory in args.runs:
        config=json.loads((directory/'config.json').read_text());assert config['predictions_sha256']==sha(directory/'predictions.jsonl')
        model=Path(config['model_path']).name
        with (directory/'predictions.jsonl').open() as stream:
            for line in stream:
                r=json.loads(line);m=metadata[r['item_id']]
                eligible=m['genuine'] if args.stratum=='genuine' else m.get('analysis_question_target',m['question_target'])=='initial'
                if not eligible or r['format']!='B' or r['mode']!='sequence' or r['repair'] or r['correct'] is None or not r['matched_question_exact']:continue
                if r['reading'] not in ('R0','R1','R2','R3','R5'):continue
                key=model,r['item_id'],r['reading'],r['mapping'];assert key not in seen;seen.add(key)
                observations.append(dict(correct=int(r['correct']),model=model,pair=m['cluster_id'],
                    question_pair=(m.get('analysis_pair_id',m['pair_id']),m['question']),
                    construction=m['construction'],condition=m.get('analysis_condition',m['condition']),reading=r['reading'],mapping=r['mapping']))
    paired=collections.defaultdict(set)
    for r in observations:paired[(r['model'],r['question_pair'],r['reading'])].add(r['condition'])
    before=len(observations)
    observations=[r for r in observations if paired[(r['model'],r['question_pair'],r['reading'])]=={'gp','control'}]
    report=dict(data_sha256=sha(args.data),stratum=args.stratum,observations=len(observations),unpaired_rows_excluded=before-len(observations),seed=52,
        formula='correct ~ C(condition)*C(reading)*C(construction) + C(mapping)',
        random_intercepts=['lexical cluster (SAP shared across constructions)','model'],
        method='statsmodels BinomialBayesMixedGLM variational Bayes; posterior normal intervals, not cluster-bootstrap CIs',
        priors=dict(fixed_normal_sd=2,log_random_sd_normal_sd=1),warnings=[])
    if not observations:
        report['status']='No qualified observations; not an estimated zero effect'
    else:
        table=pd.DataFrame(observations);np.random.seed(52);start=time.monotonic()
        try:
            with warnings.catch_warnings(record=True) as caught:
                warnings.simplefilter('always')
                model=BinomialBayesMixedGLM.from_formula(report['formula'],{'pair':'0+C(pair)','model':'0+C(model)'},table,vcp_p=1,fe_p=2)
                result=model.fit_vb(minim_opts=dict(maxiter=200,gtol=1e-5))
                report['warnings']=[str(w.message) for w in caught]
            report.update(status='fit',optimizer_success=bool(result.optim_retvals['success']),
                optimizer_message=str(result.optim_retvals['message']),
                fixed={name:dict(mean=float(mean),posterior_sd=float(sd),posterior_interval95=[float(mean-1.96*sd),float(mean+1.96*sd)])
                    for name,mean,sd in zip(model.exog_names,result.fe_mean,result.fe_sd)},
                random_log_sd={name:dict(mean=float(mean),posterior_sd=float(sd)) for name,mean,sd in zip(model.vcp_names,result.vcp_mean,result.vcp_sd)},
                wall_seconds=time.monotonic()-start)
        except Exception as error:report.update(status='failed',error=type(error).__name__+': '+str(error),wall_seconds=time.monotonic()-start)
    args.out.write_text(json.dumps(report,indent=2)+'\n')


if __name__=='__main__':main()
