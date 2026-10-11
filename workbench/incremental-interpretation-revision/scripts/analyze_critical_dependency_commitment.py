"""E107 new commitment dimension; original role-only maps stay immutable."""
import argparse
import collections
import json
from pathlib import Path
import time
from data import sha
from current_open_baseline import MODELS
from critical_dependency_audit import PATTERNS
from analyze_correct_answer_carry import estimate


def load(path):
    return list(map(json.loads,path.read_text().splitlines()))


def analyze(root, audit=None, output='critical-dependency-commitment-map-v1.json', marker='complete-map-v1.json'):
    audit = audit or root/'step5'
    parent = root.parent/'E103'
    oldpath = parent/'native-pool-revision-credit-map-v1.json'
    old = json.loads(oldpath.read_text())
    innovation_path = root.parent/'E106/positive-innovation-credit-map-v1.json'
    innovation = json.loads(innovation_path.read_text())
    extra = {(r['model'],r['item_id']):r['selected'] for r in innovation['records']}
    assignments = {(a['model'],a['item_id'],a['candidate']):a for a in load(root/'assignments-v1.jsonl')}
    labels = {a['item_id']:a for a in load(audit/'annotated.jsonl')}
    records,panels,counts = [],[],[]
    for r in old['records']:
        model,uid = r['model'],r['item_id']; candidates,categories = {},{}
        for j in range(8):
            a = assignments[model,uid,j];z = labels.get(a['audit_id'])
            category = PATTERNS[tuple(z['step5_annotation']['option_labels'])] if z and z['step5_status'] in ['agreed','adjudicated'] else None
            known = a['stopped'] and not a['unfinished_thinking'] and category is not None
            v = dict(unknown=float(not known),capped=float(a['capped']))
            for cat in PATTERNS.values():
                v[cat+'_lower'] = float(known and category == cat)
                v[cat+'_upper'] = float(not known or category == cat)
            v['explicit_or_implicit_lower'] = float(known and category in ['EXPLICIT_FINAL','IMPLICIT_FINAL'])
            v['explicit_or_implicit_upper'] = float(not known or category in ['EXPLICIT_FINAL','IMPLICIT_FINAL'])
            candidates[j],categories[j] = v,category
        selected = dict(r['selected'],POSITIVE_INNOVATION=extra[model,uid])
        values = {policy:candidates[j] for policy,j in selected.items()}
        values['UNIFORM_POOL'] = {k:sum(candidates[j][k] for j in range(8))/8 for k in candidates[0]}
        metrics = {policy+'/'+k:v for policy,vs in values.items() for k,v in vs.items()}
        for after,before in [('REVISION_EVIDENCE','WHOLE'),('REVISION_EVIDENCE','GREEDY'),
            ('WHOLE','GREEDY'),('POSITIVE_INNOVATION','WHOLE')]:
            for k in candidates[0]:
                other = k[:-6]+'_upper' if k.endswith('_lower') else k[:-6]+'_lower' if k.endswith('_upper') else k
                metrics[after+'-minus-'+before+'/'+k] = values[after][k]-values[before][other]
        for criterion in ['EXPLICIT_FINAL','explicit_or_implicit']:
            for bound in ['lower','upper']:
                metrics['POOL_ORACLE/'+criterion+'_'+bound] = max(candidates[j][criterion+'_'+bound] for j in range(8))
        # Old/new labels are distinct constructs. Agreement here diagnoses granularity,
        # not an automatic invalidation of the previous role protocol.
        for policy,j in selected.items():
            old_correct = r['candidate_metrics'][str(j)]['CORRECT_ROLES_lower']
            metrics[policy+'/old_role_correct_and_explicit'] = old_correct*candidates[j]['EXPLICIT_FINAL_lower']
            metrics[policy+'/old_role_correct_and_implicit'] = old_correct*candidates[j]['IMPLICIT_FINAL_lower']
            metrics[policy+'/old_role_correct_and_unbound'] = old_correct*candidates[j]['GENERIC_UNBOUND_lower']
        records.append(dict(model=model,item_id=uid,cluster_id=r['cluster_id'],
            sentence_sha256=r['sentence_sha256'],construction=r['construction'],selected=selected,
            candidate_categories=categories,candidate_metrics=candidates,metrics=metrics))
    assert len(records) == 150
    for model in MODELS:
        for ct in ['ALL','MVRR','NPZ','NPS']:
            rs = [r for r in records if r['model'] == model and (ct == 'ALL' or r['construction'] == ct)]
            counts.append(dict(model=model,construction=ct,sources=len(rs),
                candidate_categories=dict(collections.Counter(c for r in rs for c in r['candidate_categories'].values()))))
            for metric in sorted(rs[0]['metrics']):
                panels.append(dict(model=model,construction=ct,metric=metric,
                    **estimate(rs,[r['metrics'][metric] for r in rs],seed=107)))
    out = root/output; assert not out.exists()
    out.write_text(json.dumps(dict(models=MODELS,E103_map_sha256=sha(oldpath),
        E106_map_sha256=sha(innovation_path),audit_summary=json.loads((audit/'summary.json').read_text()),
        annotations_sha256=sha(audit/'annotated.jsonl'),audit_path=str(audit),records=records,panels=panels,counts=counts,
        new_GPU_hours=0,new_P=0,
        scope='POST-HOC new critical-dependency commitment dimension, all frozen original candidates/sources. Explicit versus coherent implicit support reported separately.',
        limits='Implicit discourse is not automatically wrong. This dimension is not unique latent parse or full-world faithfulness; old role-only maps preserved.'),indent=2)+'\n')
    manifest = dict(map_sha256=sha(out),panels=len(panels),new_GPU_hours=0,new_P=0)
    (root/marker).write_text(json.dumps(manifest,indent=2)+'\n');print('E107 sealed',manifest,flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);p.add_argument('--wait',action='store_true')
    p.add_argument('--audit',type=Path);p.add_argument('--output',default='critical-dependency-commitment-map-v1.json')
    p.add_argument('--marker',default='complete-map-v1.json')
    a = p.parse_args()
    while a.wait and not ((a.audit or a.root/'step5')/'summary.json').exists():time.sleep(20)
    analyze(a.root,a.audit,a.output,a.marker)
