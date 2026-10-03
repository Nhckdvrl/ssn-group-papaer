"""E40: reproduce released filters without repairing flags to match a paper."""
import argparse,collections,hashlib,json
from pathlib import Path
import openpyxl
from scipy.stats import ttest_rel

ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
a=ap.parse_args();assert not a.output.exists();root=a.root/'upstream/implicit-dominance-2026';out={}
for i in [1,2,3]:
    path=root/f'Experiment_{i}_data.xlsx';it=openpyxl.load_workbook(path,read_only=True,data_only=True).active.values
    fields=next(it);rows=[dict(zip(fields,z)) for z in it];by=collections.defaultdict(list)
    for z in rows:by[z['participants']].append(z)
    kept={k:v for k,v in by.items() if sum(z['is_corr_q1']==0 for z in v)<=2}
    pr=[z for vs in kept.values() for z in vs];target=[z for z in pr if z['question_type'] in ['literal','meaning']]
    good=[z for z in pr if z['ans_match']==1];assert all(z in target for z in good)
    report={'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'raw_n':len(rows),'participants_raw':len(by),
        'participants_retained':len(kept),'target_n':len(target),'retained_correct_interpretation_n':len(good),
        'expected_paper_correct_n':[708,703,1253][i-1],
        'participant_and_target_counts_match_paper':len(kept)==[91,93,85][i-1] and len(target)==[728,744,1360][i-1],
        'correct_interpretation_count_matches_paper':len(good)==[708,703,1253][i-1],
        'cell_counts':{str(k):v for k,v in collections.Counter((z['question_type'],z['SoA_explicit'],z['SoA_implicit']) for z in good).items()}}
    if i==1:
        paired=collections.defaultdict(lambda:collections.defaultdict(list))
        for z in good:
            if z['type_SOA'] in ['literal_true_meaning_true','literal_false_meaning_false']:
                paired[z['participants']][z['question_type']].append(float(z['slider_commitment.response']))
        complete=[v for v in paired.values() if v['literal'] and v['meaning']]
        x=[sum(v['literal'])/len(v['literal']) for v in complete];y=[sum(v['meaning'])/len(v['meaning']) for v in complete]
        t=ttest_rel(x,y);report['paired_t_aligned_truth_explicit_minus_implicit']={'n':len(x),'t':float(t.statistic),
            'p':float(t.pvalue),'paper_t':5.247,'exact_parity':bool(abs(t.statistic-5.247)<.001)}
    out[str(i)]=report;print(json.dumps({'experiment':i,**report}))
a.output.write_text(json.dumps({'experiments':out,'gpu_gate_pass':False,
    'limits':['Original released flags preserved; mismatching published trial counts are not silently repaired.',
              'R mixed models unavailable; no regression coefficient replication.',
              'The original dialogue images have not been transcribed or independently audited.']},indent=2)+'\n')
