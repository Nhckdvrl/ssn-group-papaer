"""E107 secondary conditional content-credit contrasts, fixed before label sealing."""
import argparse
import itertools
import json
from pathlib import Path
import time

from data import sha
from current_open_baseline import MODELS
from analyze_correct_answer_carry import estimate


CONTRASTS = {
    'explicit_vs_initial': ({'EXPLICIT_FINAL'}, {'INITIAL_MISREADING'}),
    'supported_vs_initial': ({'EXPLICIT_FINAL', 'IMPLICIT_FINAL'}, {'INITIAL_MISREADING'}),
    'explicit_vs_unbound': ({'EXPLICIT_FINAL'}, {'GENERIC_UNBOUND'}),
}


def load(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def analyze(root):
    mainpath = root/'critical-dependency-commitment-map-v1.json'
    seal = json.loads((root/'complete-map-v1.json').read_text())
    assert seal['map_sha256'] == sha(mainpath)
    main = json.loads(mainpath.read_text())
    parent = root.parent/'E103'
    scores, provenance = {}, []
    for run in json.loads((parent/'runner-pids-v1.json').read_text()):
        out = Path(run['out']); cfg = json.loads((out/'config.json').read_text())
        assert cfg['predictions_sha256'] == sha(out/'predictions.jsonl')
        provenance.append(dict(model=run['model'],config_sha256=sha(out/'config.json'),
                               predictions_sha256=cfg['predictions_sha256']))
        for p in load(out/'predictions.jsonl'):
            key = run['model'],p['item_id'],p['candidate']
            assert key not in scores
            s = p['scores']
            assert abs(s['whole']-s['before']-s['suffix']) < 1e-5
            scores[key] = s
    assert len(scores) == 1200
    records, panels, counts = [], [], []
    for r in main['records']:
        known = [j for j in range(8) if r['candidate_metrics'][str(j)]['unknown']==0]
        for name,(good,bad) in CONTRASTS.items():
            gs = [j for j in known if r['candidate_categories'][str(j)] in good]
            bs = [j for j in known if r['candidate_categories'][str(j)] in bad]
            pairs = []
            for g,b in itertools.product(gs,bs):
                a,z = scores[r['model'],r['item_id'],g],scores[r['model'],r['item_id'],b]
                delta = {region:a[region]-z[region] for region in ['whole','before','suffix']}
                assert abs(delta['whole']-delta['before']-delta['suffix'])<1e-5
                pairs.append(dict(good_candidate=g,bad_candidate=b,delta=delta))
            metrics = {}
            if pairs:
                for region in ['whole','before','suffix']:
                    metrics[region+'/mean_credit_difference'] = sum(p['delta'][region] for p in pairs)/len(pairs)
                    metrics[region+'/good_rank_share'] = sum(float(p['delta'][region]>0)+.5*float(p['delta'][region]==0) for p in pairs)/len(pairs)
                metrics['prefix_cancellation/pair_share'] = sum(p['delta']['whole']<0 and p['delta']['suffix']>0 for p in pairs)/len(pairs)
                metrics['suffix-minus-whole/good_rank_share'] = metrics['suffix/good_rank_share']-metrics['whole/good_rank_share']
            records.append(dict(model=r['model'],item_id=r['item_id'],cluster_id=r['cluster_id'],
                sentence_sha256=r['sentence_sha256'],construction=r['construction'],contrast=name,
                known_candidates=len(known),unknown_candidates=8-len(known),good_candidates=len(gs),
                bad_candidates=len(bs),pairs=pairs,metrics=metrics,
                any_prefix_cancellation=float(any(p['delta']['whole']<0 and p['delta']['suffix']>0 for p in pairs))))
    assert len(records)==150*len(CONTRASTS)
    for model,ct,name in itertools.product(MODELS,['ALL','MVRR','NPZ','NPS'],CONTRASTS):
        rs = [r for r in records if r['model']==model and r['contrast']==name and (ct=='ALL' or r['construction']==ct)]
        eligible = [r for r in rs if r['pairs']]
        counts.append(dict(model=model,construction=ct,contrast=name,all_sources=len(rs),
            eligible_sources=len(eligible),NA_sources=len(rs)-len(eligible),
            eligible_pairs=sum(len(r['pairs']) for r in eligible),
            unknown_candidates=sum(r['unknown_candidates'] for r in rs)))
        panels.append(dict(model=model,construction=ct,contrast=name,scope='ALL_SOURCES_EXISTENCE',
            metric='any_prefix_cancellation',**estimate(rs,[r['any_prefix_cancellation'] for r in rs],seed=107)))
        for metric in sorted(eligible[0]['metrics']) if eligible else []:
            panels.append(dict(model=model,construction=ct,contrast=name,scope='CONDITIONAL_TWO_CATEGORIES_AVAILABLE',
                metric=metric,**estimate(eligible,[r['metrics'][metric] for r in eligible],seed=107)))
    path = root/'conditional-dependency-credit-map-v1.json'; assert not path.exists()
    result = dict(E107_map_sha256=sha(mainpath),E103_runs=provenance,
        contrasts={name:dict(good=sorted(g),bad=sorted(b)) for name,(g,b) in CONTRASTS.items()},
        records=records,panels=panels,counts=counts,new_GPU_hours=0,new_API=0,
        scope='Secondary readout fixed before E107 sealing; all eight frozen candidate assignments retained; conditional contrast never replaces all-Source selection quality.',
        limits='Explicit vs unbound measures dependency commitment. Implicit discourse is not false. Conditional availability is not all-Source ability. Arithmetic decomposition is not a unique neural mechanism or an actual training result.')
    path.write_text(json.dumps(result,indent=2)+'\n')
    manifest = dict(map_sha256=sha(path),panels=len(panels),records=len(records),new_GPU_hours=0,new_API=0)
    (root/'conditional-dependency-credit-complete-v1.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('E107 secondary complete',manifest,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--wait',action='store_true');args=parser.parse_args()
    while args.wait and not (args.root/'complete-map-v1.json').exists():time.sleep(20)
    analyze(args.root)
