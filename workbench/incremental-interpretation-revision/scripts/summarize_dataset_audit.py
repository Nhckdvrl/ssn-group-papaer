"""D0-v2 self-review: coverage, semantic reliability, grammar and landmark eligibility."""
import argparse
import collections
import json
from pathlib import Path
from data import sha
from analyze_reading_map import estimate,load


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    rows=load(args.data);labelled=[r for r in rows if r.get('step5_status') in ('agreed','adjudicated')]
    scope=[r for r in rows if r['needs_revision']]
    both=[r for r in scope if r.get('step5_passes')]
    def semantic(a):return a['label'],tuple(a['option_labels'])
    def aggregate(values):
        grouped=collections.defaultdict(list)
        for row,value in values:grouped[row['cluster_id']].append(value)
        return estimate({k:sum(v)/len(v) for k,v in grouped.items()})
    agreement=aggregate([(r,float(semantic(r['step5_passes'][0])==semantic(r['step5_passes'][1]))) for r in both])
    output=dict(data_sha256=sha(args.data),rows=len(rows),annotation_scope=len(scope),
        complete_final=len(labelled),complete_both=len(both),status_counts=dict(collections.Counter(r['step5_status'] for r in scope)),
        semantic_agreement_cluster_bootstrap=agreement,
        semantic_agreement_micro=(sum(semantic(r['step5_passes'][0])==semantic(r['step5_passes'][1]) for r in both)/len(both)) if both else None,
        annotation_failures_never_pass=True,model='step-5-preview',by_construction={},source_gold_consistency={},
        genuine_pairs_by_construction={},landmarks={})
    for construction in sorted({r['construction'] for r in scope}):
        subset=[r for r in labelled if r['construction']==construction]
        yn=[r for r in subset if r['question_format']=='yn']
        output['by_construction'][construction]=dict(rows=len([r for r in scope if r['construction']==construction]),
            final_complete=len(subset),semantic_labels_yn=dict(collections.Counter(r['step5_annotation']['label'] for r in yn)),
            strata=dict(collections.Counter(r['semantic_stratum'] for r in subset)),
            grammar_two_pass=dict(collections.Counter('/'.join(a['grammar'] for a in r['step5_passes']) for r in subset)),
            genuine_pairs=len({r['pair_id'] for r in subset if r['genuine']}))
        output['genuine_pairs_by_construction'][construction]=output['by_construction'][construction]['genuine_pairs']
    for gold in ('Yes','No'):
        subset=[r for r in labelled if r['question_format']=='yn' and r['source_gold']==gold]
        output['source_gold_consistency'][gold]=dict(rows=len(subset),literal_labels=dict(collections.Counter(r['step5_annotation']['label'] for r in subset)))
    pairs=collections.defaultdict(list)
    for r in rows:pairs[(r.get('analysis_pair_id',r['pair_id']),r['question'])].append(r)
    matched=[group for group in pairs.values() if {r.get('analysis_condition',r['condition']) for r in group}=={'gp','control'}]
    output['landmarks']=dict(rows_available=sum(r['disamb_word_index'] is not None for r in rows),
        paired_questions_usable=sum(all(r['disamb_word_index'] is not None and r['disamb_word_index']>0 for r in group) for group in matched),
        position_origin_counts=dict(collections.Counter(str(r.get('position_origin')) for r in scope)))
    output['interpretation']='Agreement is reliability of two independent shuffled calls to the same annotator model, not a proof of semantic truth. Wh placeholder NEITHER labels are excluded from YN label counts. Empty genuine strata are missing evidence, not absence of model errors.'
    args.out.write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n')


if __name__=='__main__':main()
