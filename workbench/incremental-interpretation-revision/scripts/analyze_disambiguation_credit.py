"""E101 cached LP decomposition at original consensus disambiguation words; no GPU."""
import argparse
import collections
import json
from pathlib import Path
import re
from data import sha
from data_v2 import digest
from current_open_baseline import MODELS, tokenizer
from reconstruction_reward import prepare, context
from analyze_correct_answer_carry import estimate


def load(p):
    return list(map(json.loads, p.read_text().splitlines()))


def analyze(root, models, semantic_map, output_name):
    parent = root.parent/'E96'
    pairs = load(parent/'data-v1.jsonl')
    original = root.parent/'E52/qualified-v3.jsonl'
    positions = collections.defaultdict(list)
    for r in load(original):
        if r.get('step5_position_agreed'):
            positions[r['sentence_sha256']].append(r['step5_annotation']['disamb_word_index'])
    semantic = json.loads(semantic_map.read_text())
    assert semantic['data_sha256'] == sha(parent/'data-v1.jsonl')
    refs = {(r['model'],r['item_id']):r for r in semantic['records'] if r['condition']=='gp'}
    records, provenance = [], []
    for model in models:
        tok, index = tokenizer(root.parent/'models'/model), {}
        for run in json.loads((parent/'runner-pids-v1.json').read_text()):
            if run['model'] != model:continue
            out = Path(run['out']);cfg = json.loads((out/'config.json').read_text())
            assert cfg['predictions_sha256'] == sha(out/'predictions.jsonl')
            provenance.append(dict(model=model,config_sha256=sha(out/'config.json'),predictions_sha256=cfg['predictions_sha256']))
            for p in load(out/'predictions.jsonl'):
                key = (p['item_id'],'GENERATION',p['source_condition'],'') if p['operation']=='GENERATION' else (p['item_id'],'RECONSTRUCTION',p['interpretation_condition'],p['target_condition'])
                assert key not in index
                index[key] = p
        assert len(index)==300
        for pair in pairs:
            s = pair['sources']['gp'];available = set(positions[s['sentence_sha256']])
            boundary = next(iter(available)) if len(available)==1 else None
            r = dict(model=model,item_id=pair['item_id'],cluster_id=pair['cluster_id'],
                sentence_sha256=s['sentence_sha256'],construction=pair['construction'],boundary=boundary,metrics={})
            if boundary is None:
                records.append(r);continue
            words = list(re.finditer(r'\S+',s['sentence']))
            assert 0 <= boundary < len(words)
            r['disambiguating_word'] = words[boundary].group()
            scores, targets = {}, []
            for side in ['gp','control']:
                p = index[pair['item_id'],'GENERATION',side,'']
                z = dict(s,interpretation=p['text'].rsplit('</think>',1)[-1])
                task = prepare(z,tok);old = index[pair['item_id'],'RECONSTRUCTION',side,'gp']
                assert task['prompt_sha256']==old['prompt_sha256'] and task['context_sha256']==old['context_sha256']
                prefix = context(z);encoded = tok(prefix+s['sentence'],add_special_tokens=False,return_offsets_mapping=True)
                offsets = [(a-len(prefix),b-len(prefix)) for i in task['target_positions'] for a,b in [encoded['offset_mapping'][i]]]
                ids = [task['ids'][i] for i in task['target_positions']]
                targets.append((ids,offsets));lp = old['token_logprobs'];assert len(lp)==len(offsets)
                groups = {'before':[],'word':[],'after':[]}
                for value,(a,b) in zip(lp,offsets):
                    region = 'before' if b <= words[boundary].start() else 'after' if a >= words[boundary].end() else 'word'
                    groups[region].append(value)
                scores[side] = {k:sum(v) for k,v in groups.items()}
                scores[side]['from'] = scores[side]['word']+scores[side]['after']
                scores[side]['whole'] = sum(lp)
                assert abs(scores[side]['before']+scores[side]['from']-old['reward_sum']) < 1e-8
            assert targets[0]==targets[1]
            r['region_scores'] = scores
            for region in ['whole','before','word','after','from']:
                delta = scores['control'][region]-scores['gp'][region]
                r['metrics'][region+'_delta_reward'] = delta
                for criterion,z in refs[model,pair['item_id']]['metrics'].items():
                    for bound,fn in [('lower',min),('upper',max)]:
                        r['metrics'][criterion+'_'+region+'_aligned_delta_'+bound] = fn(g*delta for g in z['possible_ranks'])
            records.append(r)
    return finish(root, models, semantic_map, original, parent, records, provenance, output_name)


def finish(root, models, semantic_map, original, parent, records, provenance, output_name):
    panels,counts=[],[]
    for model in models:
        for ct in ['ALL','MVRR','NPZ','NPS']:
            rs=[r for r in records if r['model']==model and (ct=='ALL' or r['construction']==ct)]
            eligible=[r for r in rs if r['boundary'] is not None]
            counts.append(dict(model=model,construction=ct,sources=len(rs),boundary_NA=len(rs)-len(eligible)))
            metrics=sorted({k for r in eligible for k in r['metrics']})
            for metric in metrics:
                used=[r for r in eligible if metric in r['metrics']]
                panels.append(dict(model=model,construction=ct,metric=metric,
                    **estimate(used,[r['metrics'][metric] for r in used],seed=101)))
    root.mkdir(exist_ok=True)
    out=root/output_name;assert not out.exists()
    out.write_text(json.dumps(dict(models=models,records=records,panels=panels,counts=counts,runs=provenance,
        E96_data_sha256=sha(parent/'data-v1.jsonl'),semantic_map_sha256=sha(semantic_map),
        original_T2_metadata_sha256=sha(original),new_GPU_hours=0,new_API_calls=0,
        scope='POST-HOC frozen original consensus disambiguation boundary; full complete registered family cohorts.',
        limits='Additive cached token likelihood diagnosis, not a causal removal or unique latent parse; bits secondary to E96 semantic alignment.'),indent=2)+'\n')
    manifest=dict(map_sha256=sha(out),models=models,panels=len(panels),new_GPU_hours=0,new_API_calls=0)
    (root/(output_name+'.manifest.json')).write_text(json.dumps(manifest,indent=2)+'\n')
    print('E101 sealed',manifest,flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,required=True)
    p.add_argument('--semantic-map',type=Path,required=True)
    p.add_argument('--models',nargs='+',default=MODELS,choices=MODELS)
    p.add_argument('--output-name',default='disambiguation-credit-map-v1.json')
    a=p.parse_args();analyze(a.root,a.models,a.semantic_map,a.output_name)
