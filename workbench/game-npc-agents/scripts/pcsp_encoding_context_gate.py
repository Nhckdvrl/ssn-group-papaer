#!/usr/bin/env python3
"""E23 source artifact parity and same-text batch/pooling invariance gate."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp'))
    ap.add_argument('--model',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    import numpy as np
    import torch
    from transformers import AutoTokenizer,AutoModel
    torch.set_num_threads(1)
    device=torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    dump=lambda name,obj:(args.out/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    records=json.loads((args.source/'research/data/personas/personas_500.json').read_text())
    records=sorted(records,key=lambda r:int(r['id']))
    assert [int(r['id']) for r in records]==list(range(1,501))
    texts=[r['text'] for r in records]
    cached=np.load(args.source/'results/embeddings/persona_embeddings_500.npy').astype(np.float32)
    tok=AutoTokenizer.from_pretrained(args.model,local_files_only=True)
    lengths=np.asarray([len(tok(t,truncation=True,max_length=128)['input_ids']) for t in texts])
    manifest={'source_sha':'5420f7b4fa0fdb6110e131402af9f5386ce2d0cf',
        'source_encoder_sha256':hashlib.sha256((args.source/'research/scripts/compute_embeddings_500.py').read_bytes()).hexdigest(),
        'model':str(args.model),'model_revision':args.model.name,'padding_side':tok.padding_side,
        'tokenizer_config_sha256':hashlib.sha256((args.model/'tokenizer_config.json').read_bytes()).hexdigest(),
        'model_weights_sha256':hashlib.sha256((args.model/'model.safetensors').read_bytes()).hexdigest(),
        'torch_version':torch.__version__,'max_length':128,'source_batch_size':32,
        'token_length_range':[int(lengths.min()),int(lengths.max())],'cloud_calls':0}
    dump('manifest.json',manifest);print(json.dumps(manifest),flush=True)
    start=time.monotonic()
    model=AutoModel.from_pretrained(args.model,dtype=torch.float16,local_files_only=True).to(device).eval()
    model.requires_grad_(False)

    def encode(batch,padding=True):
        tokens=tok(batch,return_tensors='pt',padding=padding,truncation=True,max_length=128).to(device)
        with torch.inference_mode():
            hidden=model(**tokens).last_hidden_state
            raw=torch.nn.functional.normalize(hidden[:,-1,:],dim=-1)
            mask=tokens['attention_mask']
            if bool(torch.all(mask[:,-1]==1)):
                correct=raw
            else:
                # Right-padding-aware official last-token pooling.
                idx=mask.sum(-1)-1
                correct=torch.nn.functional.normalize(hidden[torch.arange(len(batch),device=device),idx],dim=-1)
        return raw.float().cpu().numpy(),correct.float().cpu().numpy(),mask[:,-1].cpu().numpy()

    # Original table generation: identical text, sorted IDs, original batch32,
    # fp16, tokenizer default, truncation128, no instruction prefix.
    raw_parts=[];correct_parts=[];pad_parts=[]
    for offset in range(0,500,32):
        raw,correct,mask=encode(texts[offset:offset+32])
        raw_parts.append(raw);correct_parts.append(correct);pad_parts.append(mask)
    raw_source=np.concatenate(raw_parts);proper_source=np.concatenate(correct_parts)
    last_real=np.concatenate(pad_parts)
    np.save(args.out/'source_batch32_recomputed.npy',raw_source)
    np.save(args.out/'proper_batch32.npy',proper_source)
    cos=lambda a,b:np.sum(a*b,axis=-1)/(np.linalg.norm(a,axis=-1)*np.linalg.norm(b,axis=-1))
    raw_cos=cos(raw_source,cached);proper_cos=cos(proper_source,cached)
    parity={'source_pool_cosine_min':float(raw_cos.min()),'source_pool_cosine_mean':float(raw_cos.mean()),
        'source_pool_rows_ge_0999':int((raw_cos>=.999).sum()),'source_pool_rows_ge_09999':int((raw_cos>=.9999).sum()),
        'proper_pool_cosine_min':float(proper_cos.min()),'proper_pool_cosine_mean':float(proper_cos.mean()),
        'proper_pool_rows_ge_0999':int((proper_cos>=.999).sum()),
        'last_column_padding_rows':int((last_real==0).sum()),
        'source_vs_proper_cosine_mean':float(cos(raw_source,proper_source).mean()),
        'cached_array_sha256':hashlib.sha256((args.source/'results/embeddings/persona_embeddings_500.npy').read_bytes()).hexdigest()}
    dump('parity.json',parity);print(json.dumps({'parity':parity}),flush=True)
    # Gate only the source/script attribution. Retain diagnostics if another
    # pooling recipe matches; never rewrite the published cache or policy.
    parity_pass=bool(np.all(raw_cos>=.999))
    shortest=int(np.argmin(lengths));longest=int(np.argmax(lengths))
    summaries=[];variants={'cached':cached,'source_recomputed':raw_source,'proper_pool':proper_source}
    singleton=[];long_peer=[];maxpad=[];proper_long=[]
    for index,text in enumerate(texts):
        own,proper,_=encode([text]);singleton.append(own[0])
        # Peer contributes to batch padding length only, never to target keys.
        peer=longest if index!=longest else int(np.argsort(lengths)[-2])
        longer,proper_l,_=encode([text,texts[peer]])
        long_peer.append(longer[0]);proper_long.append(proper_l[0])
        fixed,_,_=encode([text],padding='max_length');maxpad.append(fixed[0])
        if int(records[index]['id']) in [1,2,401,402]:
            short,proper_s,_=encode([text,texts[shortest]])
            again,_,_=encode(texts[index//32*32:min(500,index//32*32+32)])
            slot=index%32
            summaries.append({'persona_id':int(records[index]['id']),'token_length':int(lengths[index]),
                'source_repeat_cos':float(cos(raw_source[index],again[slot])),
                'source_repeat_maxabs':float(np.max(np.abs(raw_source[index]-again[slot]))),
                'raw_single_vs_long_cos':float(cos(own[0],longer[0])),
                'proper_single_vs_long_cos':float(cos(proper[0],proper_l[0])),
                'raw_single_vs_short_cos':float(cos(own[0],short[0])),
                'proper_single_vs_short_cos':float(cos(proper[0],proper_s[0]))})
    variants.update(singleton=np.stack(singleton),long_peer=np.stack(long_peer),fixed_max128=np.stack(maxpad))
    proper_long=np.stack(proper_long)
    for name,array in variants.items():np.save(args.out/f'{name}.npy',array)
    np.save(args.out/'proper_long_peer.npy',proper_long)
    invariance={'selected_controls':summaries,
        'raw_single_vs_long_cosine_mean':float(cos(variants['singleton'],variants['long_peer']).mean()),
        'raw_single_vs_long_cosine_min':float(cos(variants['singleton'],variants['long_peer']).min()),
        'proper_source_vs_long_cosine_mean':float(cos(proper_source,proper_long).mean()),
        'proper_source_vs_long_cosine_min':float(cos(proper_source,proper_long).min()),
        'source_parity_pass':parity_pass}
    dump('invariance.json',invariance);print(json.dumps({'invariance':invariance}),flush=True)
    if not parity_pass:
        dump('summary.json',{'parity':parity,'invariance':invariance,'policy_scoring_skipped':True,
            'reason':'Source artifact does not match current source recipe; resolve before assigning policy consequences.',
            'scientific_increment':0})
        dump('runtime.json',{'wall_seconds':time.monotonic()-start,'cloud_calls':0})
        return
    del model;torch.cuda.empty_cache() if device.type=='cuda' else None
    sys.path.insert(0,str(args.source/'research'))
    from src.training.pcsp_trainer import PCSPActorCritic
    from src.env.v3_constants import OBS_DIM_V3_LARGE,N_ACTIONS_V3
    policy_results={}
    run_cache=Path('/home/xiang/.cache/game-npc-research/runs')
    for seed in [42,43,44]:
        for mode in ['full','no_consist']:
            policy=PCSPActorCritic(OBS_DIM_V3_LARGE,N_ACTIONS_V3)
            file=args.source/f'research/results/pcsp_v3_large/{mode}_seed{seed}/{mode}/policy.pt'
            policy.load_state_dict(torch.load(file,map_location='cpu',weights_only=True),strict=True)
            policy.to(device).eval().requires_grad_(False)
            with np.load(run_cache/f'e17_full_no{seed}/{mode}_test.npz') as data:
                obs=torch.from_numpy(data['obs']).to(device);ids=data['ids'].astype(int)-1
            with torch.inference_mode():
                base=policy.action_logits(obs.reshape(-1,OBS_DIM_V3_LARGE),
                    torch.from_numpy(cached[ids]).to(device)[:,None,:].expand(-1,200,-1).reshape(-1,1024)).softmax(-1)
                report={}
                for name,array in variants.items():
                    code=torch.from_numpy(array[ids]).to(device)[:,None,:].expand(-1,200,-1).reshape(-1,1024)
                    probs=policy.action_logits(obs.reshape(-1,OBS_DIM_V3_LARGE),code).softmax(-1)
                    mixture=(probs+base)/2
                    js=.5*((base*(base.clamp_min(1e-30).log()-mixture.clamp_min(1e-30).log())).sum(-1)+
                        (probs*(probs.clamp_min(1e-30).log()-mixture.clamp_min(1e-30).log())).sum(-1))
                    report[name]={'same_native_state_mean_js':float(js.mean()),
                        'same_state_top_action_changed':float((probs.argmax(-1)!=base.argmax(-1)).float().mean())}
                policy_results[f'{mode}_seed{seed}']=report
    dump('summary.json',{'parity':parity,'invariance':invariance,'policy_scores':policy_results,
        'scope':'Same text/state, encoding-context diagnostic; no changed world/utility, no new semantic personality claim',
        'scientific_increment':0})
    dump('runtime.json',{'wall_seconds':time.monotonic()-start,'cloud_calls':0,'gpu':str(device)})
    print(json.dumps({'policy_scores':policy_results}),flush=True)


if __name__=='__main__':main()
