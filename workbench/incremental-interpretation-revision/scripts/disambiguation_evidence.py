"""E83 post-hoc scoring object; eligibility depends only on existing input T2."""
import argparse
import collections
import json
import math
from pathlib import Path
import re
from data import sha,write_jsonl
from joint_relation_use import MODELS


def build(parent,root):
    assert json.loads((parent/'complete-map-v1.json').read_text())['all_models_complete']
    rows=list(map(json.loads,(parent/'data-v1.jsonl').read_text().splitlines()))
    sources=collections.defaultdict(list);pairs=collections.defaultdict(lambda:collections.defaultdict(set))
    for r in rows:
        sources[r['source_unit']].append(r);pairs[r['analysis_pair_id']][r['condition']].add(r['source_unit'])
    landmarks={};excluded=[];eligible=[]
    for pair,conditions in sorted(pairs.items()):
        reason=None
        if set(conditions)!={'gp','control'} or any(len(v)!=1 for v in conditions.values()):
            reason='Input pair has missing/multiple Source units'
        else:
            gpuid=next(iter(conditions['gp']));cueuid=next(iter(conditions['control']))
            gp=sources[gpuid];cue=sources[cueuid]
            nonnull={r['disamb_word_index'] for r in gp if r['disamb_word_index'] is not None}
            agreed={r['disamb_word_index'] for r in gp if r['step5_position_agreed'] and r['disamb_word_index'] is not None}
            if len(nonnull)!=1 or len(agreed)!=1 or nonnull!=agreed:
                reason='GP T2 missing/conflicting or no two-pass agreed nonnull index'
            else:
                index=next(iter(agreed));word=gp[0]['sentence'].split()[index]
                if index==0:reason='No earlier Source prefix before GP T2'
                else:
                    clean=lambda s:s.strip('.,;:?!').casefold()
                    matches=[i for i,w in enumerate(cue[0]['sentence'].split()) if clean(w)==clean(word)]
                    if len(matches)!=1:reason='Cue has no unique original GP landmark word'
                    else:
                        for uid,ix in [(gpuid,index),(cueuid,matches[0])]:
                            if uid in landmarks:assert landmarks[uid]==ix
                            landmarks[uid]=ix
                        eligible.append(pair)
        if reason:excluded.append(dict(pair_id=pair,reason=reason))
    selected=[dict(r,e83_landmark_word_index=landmarks[r['source_unit']]) for r in rows
              if r['analysis_pair_id'] in set(eligible)]
    assert selected and {r['condition'] for r in selected}=={'gp','control'}
    root.mkdir(exist_ok=True,parents=True);assert not (root/'data-v1.jsonl').exists();write_jsonl(root/'data-v1.jsonl',selected)
    manifest=dict(parent_data_sha256=sha(parent/'data-v1.jsonl'),data_sha256=sha(root/'data-v1.jsonl'),
        QA=len(selected),sources=len({r['source_unit'] for r in selected}),
        clusters=len({r['analysis_cluster_id'] for r in selected}),pairs=len(eligible),
        sources_by_construction_condition=dict(collections.Counter(r['construction']+'/'+r['condition']
            for uid,r in {r['source_unit']:r for r in selected}.items())),excluded=excluded,
        eligibility='Input-only existing final nonnull T2 must agree across Source QA and have an independently two-pass-agreed witness; cue anchor is unique original word. Null in other QA is retained uncertainty, not a conflict. All original QA included per qualified pair.')
    (root/'data-v1.manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('INPUT_ELIGIBILITY',json.dumps({k:v for k,v in manifest.items() if k!='excluded'}),flush=True)


def derive(parent,root):
    from transformers import AutoTokenizer
    rows=list(map(json.loads,(root/'data-v1.jsonl').read_text().splitlines()));byid={r['item_id']:r for r in rows}
    mother_runs=json.loads((parent/'runner-pids-v1.json').read_text());runs=[]
    for model in MODELS:
        tok=AutoTokenizer.from_pretrained(root.parent/'models'/model,local_files_only=True)
        index={};configs=[]
        for run in [r for r in mother_runs if r['model']==model]:
            p=Path(run['out']);cfg=json.loads((p/'config.json').read_text())
            assert cfg['predictions_sha256']==sha(p/'predictions.jsonl')
            configs.append(cfg)
            for x in map(json.loads,(p/'predictions.jsonl').read_text().splitlines()):
                if x['item_id'] in byid:
                    key=x['item_id'],x['readout'],x['mapping'];assert key not in index;index[key]=x
        assert len(index)==4*len(rows)
        predictions=[];checks=[]
        for (uid,ro,mp),p in sorted(index.items()):
            r=byid[uid];sentence=r['sentence'];ids=p['source_token_ids']
            encoded=tok(sentence,add_special_tokens=False,return_offsets_mapping=True)
            # All original targets begin at the assistant boundary; verify exact token identity.
            assert encoded['input_ids']==ids,(model,uid,'Source tokenization changed')
            words=list(re.finditer(r'\S+',sentence));word_start=words[r['e83_landmark_word_index']].start()
            boundary=next(i for i,(a,b) in enumerate(encoded['offset_mapping']) if b>word_start)
            assert 0<=boundary<len(ids)
            whole=p['candidate_logprobs'];lps=p['source_token_logprobs']
            assert all(abs(sum(v)-total)<1e-8 for v,total in zip(lps,whole))
            earlier=[sum(v[:boundary]) for v in lps];late=[sum(v[boundary:]) for v in lps]
            error=max(abs(a+b-c) for a,b,c in zip(earlier,late,whole));assert error<1e-8
            checks.append(dict(item_id=uid,readout=ro,mapping=mp,word_index=r['e83_landmark_word_index'],
                token_boundary=boundary,source_tokens=len(ids),reconstruction_error=error))
            for op,lp in [('WHOLE_EVIDENCE',whole),('LATE_EVIDENCE',late)]:
                mx=max(lp);den=mx+math.log(sum(math.exp(v-mx) for v in lp));gold=p['candidate_gold']
                predictions.append(dict(item_id=uid,source_unit=r['source_unit'],operation=op,
                    readout=ro,mapping=mp,candidate_gold=gold,candidate_logprobs=lp,
                    correct=max(range(2),key=lp.__getitem__)==gold,p_correct=math.exp(lp[gold]-den),
                    prompt_tokens=p['prompt_tokens'],source_tokens_scored=len(ids) if op=='WHOLE_EVIDENCE' else len(ids)-boundary))
        out=root/'runs-v1'/model/'0';out.mkdir(parents=True,exist_ok=True);write_jsonl(out/'predictions.jsonl',predictions)
        (out/'boundaries.jsonl').write_text('\n'.join(json.dumps(x) for x in checks)+'\n')
        cfg=dict(data_sha256=sha(root/'data-v1.jsonl'),model_manifest_sha256=configs[0]['model_manifest_sha256'],
            parent_predictions_sha256=configs[0]['parent_predictions_sha256'],
            code_sha256=sha(Path(__file__)),predictions_sha256=sha(out/'predictions.jsonl'),
            instrument=[c for cfg in configs for c in cfg['instrument']],
            score_reconstruction_max_error=max(x['reconstruction_error'] for x in checks),
            parent_shard_prediction_sha256=[c['predictions_sha256'] for c in configs],
            QA=len(rows),tasks=len(predictions),gpu_hours=0,post_hoc=True,
            no_model_forward=True,no_new_annotation=True)
        (out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
        runs.append(dict(model=model,shard=0,shards=1,out=str(out)))
    (root/'runner-pids-v1.json').write_text(json.dumps(runs,indent=2)+'\n');print('E83 all CPU scores derived',flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['build','derive'])
    p.add_argument('--parent',type=Path,required=True);p.add_argument('--root',type=Path,required=True)
    a=p.parse_args();globals()[a.mode](a.parent,a.root)
