#!/usr/bin/env python3
"""CPU-only cohort builder (2026-10-12 review). Reads the frozen D0 qualified-v3 item table
(1732 released GP/control QA) and lists, per source sentence, the three question roles that the
restructured program needs: replacement-dependency (initial target, grounded Yes), misreading
rejection (initial target, grounded No) and main-clause fact (final target). No model calls.
Output: results/REPLACEMENT_DEPENDENCY_COHORT_2026-10-12.json (metadata + item ids only)."""
import json, hashlib, collections, sys, pathlib
SRC = pathlib.Path('/data1/xiangding/work/incremental-interpretation-revision/E52/qualified-v3.jsonl')
OUT = pathlib.Path(__file__).resolve().parents[1] / 'results' / 'REPLACEMENT_DEPENDENCY_COHORT_2026-10-12.json'
raw = SRC.read_bytes(); sha = hashlib.sha256(raw).hexdigest()
rows = [json.loads(l) for l in raw.decode().splitlines() if l.strip()]
E82 = pathlib.Path('/data1/xiangding/work/incremental-interpretation-revision/E82/data-v1.jsonl')
E82_IDS = {json.loads(l)['item_id'] for l in E82.read_text().splitlines() if l.strip()} if E82.exists() else set()
def lit(r):
    return r.get('literal_label') or (r.get('step5_annotation') or {}).get('label')
def role(r):
    t, g = r.get('analysis_question_target'), str(r.get('grounded_gold') if r.get('grounded_gold') is not None else r.get('source_gold'))
    if t == 'initial' and g == 'Yes': return 'REPLACEMENT_DEPENDENCY'
    if t == 'initial' and g == 'No': return 'MISREADING_REJECTION'
    if t == 'final': return 'MAIN_CLAUSE_FACT'
    return 'OTHER'
by_pair = collections.defaultdict(lambda: {'gp': {}, 'control': {}})
for r in rows:
    cond = r.get('analysis_condition') or r.get('condition')
    key = r.get('analysis_pair_id') or r.get('pair_id')
    by_pair[key]['construction'] = r.get('construction'); by_pair[key]['source'] = r.get('source')
    by_pair[key]['cluster'] = r.get('analysis_cluster_id')
    by_pair[key][cond].setdefault(role(r), []).append({'item_id': r['item_id'], 'question': r['question'], 'sentence': r['sentence'], 'literal': lit(r), 'in_E82_cohort': r['item_id'] in E82_IDS, 'step5_status': r.get('step5_status'), 'control_type': r.get('analysis_control_type') or r.get('control_type')})
cohort = []
for k, v in by_pair.items():
    rd = v['gp'].get('REPLACEMENT_DEPENDENCY', [])
    if not rd: continue
    cohort.append({'pair_id': k, 'construction': v['construction'], 'source': v['source'], 'cluster': v['cluster'],
                   'gp_replacement': rd, 'gp_misreading': v['gp'].get('MISREADING_REJECTION', []), 'gp_final': v['gp'].get('MAIN_CLAUSE_FACT', []),
                   'control_replacement': v['control'].get('REPLACEMENT_DEPENDENCY', []), 'control_misreading': v['control'].get('MISREADING_REJECTION', [])})
cnt = collections.Counter((c['construction'], c['source']) for c in cohort)
clusters = collections.Counter(c['construction'] for c in {c['cluster']: c for c in cohort}.values())
allroles = collections.Counter((r.get('construction'), r.get('analysis_condition') or r.get('condition'), role(r)) for r in rows)
summary = {'source_file': str(SRC), 'source_sha256': sha, 'rows': len(rows), 'E82_cohort_ids_available': bool(E82_IDS), 'pairs_with_replacement_question': len(cohort),
           'by_construction_source': {f'{a}/{b}': n for (a, b), n in sorted(cnt.items())}, 'lexical_clusters_by_construction': dict(clusters),
           'all_role_counts': {f'{a}/{b}/{c}': n for (a, b, c), n in sorted(allroles.items())},
           'note': 'CPU-only selection from frozen released items; grounded_gold comes from the completed D0 Step-5 audit, not new annotation. Replacement-dependency questions exist only for NPZ (Cehakova 2025 RAT reflexive/reciprocal) and MVRR (Cehakova 2025 ditransitive passive + 1 SAP). The MVRR final-target No questions ask about the misread object (e.g. did the file deserve investigation) and function as a second misreading probe.',
           'replacement_literal_label_counts': {f'{c["construction"]}/{x["literal"]}': 0 for c in cohort for x in c['gp_replacement']}, 'cohort': cohort}
for c in cohort:
    for x in c['gp_replacement']:
        k=f'{c["construction"]}/{x["literal"]}'; summary['replacement_literal_label_counts'][k]+=1
OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=1))
print(json.dumps({k: summary[k] for k in ('rows', 'pairs_with_replacement_question', 'by_construction_source', 'lexical_clusters_by_construction')}, ensure_ascii=False, indent=1))
for k, n in sorted(summary['all_role_counts'].items()): print(k, n)
