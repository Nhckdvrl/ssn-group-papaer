"""E47 source audit, no model predictions or invented unlicensed labels."""
import argparse,hashlib,json,subprocess
from pathlib import Path
import numpy as np
import pandas as pd

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args();assert not a.output.exists();p=a.root/'upstream/mayn-speaker-reasoning-2025'
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
available={'tr','ci','re','gr'}
def messages(obj):
    shape,color=obj.split('_');assert shape in ['tr','ci','sq'] and color in ['re','gr','bl']
    return available.intersection({shape,color})
out={};theory=[]
for n in [1,2]:
    folder=p/('experiment'+str(n));rawfile=folder/f'exp{n}_results.csv';exfile=folder/f'exp{n}_exclusion_list.csv'
    raw=pd.read_csv(rawfile);excluded=pd.read_csv(exfile);kept=raw[~raw.participant_id.isin(excluded.participant_id)]
    # Source Exp1 has one 48-row ID that the original exclusion list removes.
    # Preserve that source anomaly; require the retained original sample to have 24 each.
    assert kept.groupby('participant_id').size().eq(24).all() and kept.participant_id.nunique()==[79,160][n-1]
    assert kept.groupby('participant_id').speaker.nunique().eq(1).all()
    assert not raw[['msg','target','competitor','distractor','targetpos','prob_target','prob_competitor','prob_distr']].isna().any().any()
    assert raw.targetpos.isin([1,2,3]).all() and raw.msg.isin(available).all()
    columns=['prob_target','prob_competitor','prob_distr']
    assert raw[columns].ge(0).all().all() and raw[columns].le(100).all().all()
    sum_error=(raw[columns].sum(1)-100).abs();assert sum_error.max()<1e-6
    assert len(kept)==kept.participant_id.nunique()*24
    means=kept.groupby(['speaker','condition']).prob_target.mean()
    critical={speaker:float(means[speaker,'critical']) for speaker in ['adult','child']}
    assert [round(critical[s],1) for s in ['adult','child']]==[[70.8,57.3],[70.7,62.2]][n-1]
    mats=raw[['itemid','itemtype','msg','target','competitor','distractor','condition']].drop_duplicates()
    assert len(mats)==24 and mats.itemid.nunique()==24
    checks=[]
    for r in mats.to_dict('records'):
        objects=[r[k] for k in ['target','competitor','distractor']]
        literal=np.array([r['msg'] in o.split('_') for o in objects],float)
        assert literal[0] and literal.sum()>0
        l0=literal/literal.sum()
        likelihood=np.array([literal[i]/len(messages(o)) for i,o in enumerate(objects)])
        l1=likelihood/likelihood.sum()
        if r['condition']=='critical':assert abs(l0[0]-.5)<1e-9 and abs(l1[0]-2/3)<1e-9
        elif r['condition']=='filler ambiguous':assert abs(l0[0]-.5)<1e-9 and abs(l1[0]-.5)<1e-9
        else:assert r['condition']=='filler unambiguous' and l0[0]==l1[0]==1
        checks.append({**r,'l0_target':float(l0[0]),'bayes_on_literal_s0_target':float(l1[0]),
            'available_truthful_message_counts':[len(messages(o)) for o in objects]})
    if n==1:theory=checks
    else:assert checks==theory
    out['experiment'+str(n)]={'raw_rows':len(raw),'raw_participants':raw.participant_id.nunique(),
        'raw_rows_per_participant_distribution':{str(k):int(v) for k,v in raw.groupby('participant_id').size().value_counts().items()},
        'excluded_ids_n':len(excluded),'kept_rows':len(kept),'kept_participants':kept.participant_id.nunique(),
        'condition_counts':kept.condition.value_counts().to_dict(),'critical_means':critical,
        'probability_sum_max_error':float(sum_error.max()),'source_sha256':{rawfile.name:sha(rawfile),exfile.name:sha(exfile)}}
q=a.root/'upstream/bayesian-persuasion';files=['data/replication.csv','data/prolificData.csv','data/initial_sample.csv',
    'models/model-comparison/input/replication_data_full.csv','models/model-comparison/input/original_data_full.csv']
assets={name:{'exists':(q/name).exists(),**({'sha256':sha(q/name),'rows':len(pd.read_csv(q/name))} if (q/name).exists() else {})} for name in files}
criterion=q/'models/model-comparison/output/model-criterion-scores.csv';d=pd.read_csv(criterion)
comparison=d[d.model.isin(['rsa-het-speakers','rsa-het-speakers-hi'])].to_dict('records')
result={'mayn':out,'reference_material_theory_audit':theory,'mayn_original_models_sha256':sha(p/'models.R'),
    'bayesian_persuasion':{'repo_commit':subprocess.check_output(['git','-C',str(q),'rev-parse','HEAD'],text=True).strip(),
        'assets':assets,'criterion_sha256':sha(criterion),'two_distinct_cached_speaker_variants':comparison,
        'final_paper_n':723,'final_human_filter_reproduction_available':False},
    'gate_pass':True,'limits':['CPU source/theory audit, no LLM behavior and no pragmatic false-alarm gold.',
        'Mayn source descriptive rounding reproduced, not full brms posterior, exclusion decisions or photographs.',
        'Weak-evidence final raw replication filter unavailable here; processed 727 rows not silently changed to 723.',
        'No new annotation, no closed/free-model judging; existing human source kept.']}
a.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps({'gate_pass':True,'mayn':out,'weak_evidence_assets':assets}))
