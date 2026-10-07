"""E84: source-bank consumer K/V projections, preserving explicit BASE replay."""
import argparse
from contextlib import contextmanager
import fcntl
import json
import math
import os
from pathlib import Path
import time
from data import CACHE,sha
from data_v2 import digest
from natural_cue_patching import blocks
from shared_source_cross_use import prepare
from source_bank_routes import bank_hooks,qa_score,last_logits
from model_identity import manifest_identity


@contextmanager
def projection_hooks(decoder,banks,uid,positions,target,mode,verified=None):
    import torch
    handles=[];target=list(target)
    source_verified=[] if verified is not None else None
    with bank_hooks(decoder,banks,uid,positions,target,'BASE_BANK',source_verified):
        for layer,block in enumerate(decoder):
            if layer==0:continue
            refs=torch.stack([banks['PAIR'][uid][layer-1][p] for p in target]).to(next(block.parameters()).device)
            with torch.inference_mode():normalized=block.input_layernorm(refs)
            for channel,projection in [('KEY',block.self_attn.k_proj),('VALUE',block.self_attn.v_proj)]:
                replace=mode=='BOTH' or mode=='KEY_ONLY' and channel=='KEY' or mode=='VALUE_ONLY' and channel=='VALUE'
                def hook(module,inputs,output,layer=layer,channel=channel,replace=replace,normalized=normalized):
                    assert output.shape[0]==1
                    if replace:
                        changed=output.clone()
                        with torch.inference_mode():ref=torch.nn.functional.linear(normalized,module.weight,module.bias)
                        changed[0,target]=ref
                    else:changed=output
                    if verified is not None:
                        untouched=[i for i in range(output.shape[1]) if i not in set(target)]
                        assert bool((changed[0,untouched]==output[0,untouched]).all())
                        if not replace:assert bool((changed==output).all())
                        verified.append(dict(layer=layer,channel=channel,replaced=replace))
                    return changed
                handles.append(projection.register_forward_hook(hook))
        try:
            yield
            if source_verified is not None:assert source_verified==list(range(len(decoder)))
        finally:
            for handle in handles:handle.remove()


def score(model,decoder,banks,tokens,t,target,mode,verified=None):
    import torch
    seqs,length=t['encoded'];uid=t['original_row']['source_unit']
    ids=torch.tensor([seqs[0][:length]],device=model.device)
    with projection_hooks(decoder,banks,uid,tokens[uid],target[uid],mode,verified):
        with torch.inference_mode():lp=model(input_ids=ids,attention_mask=torch.ones_like(ids),use_cache=False,**last_logits(model)).logits[0,-1].float().log_softmax(-1)
    return [float(lp[s[length]]) for s in seqs]


def run(a):
    import torch
    from transformers import AutoConfig,AutoTokenizer,AutoModelForCausalLM,Gemma3ForConditionalGeneration
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    lock=(CACHE/'E52/gpu-slots'/str(a.gpu)).open('a');fcntl.flock(lock,fcntl.LOCK_EX)
    torch.manual_seed(84);torch.set_num_threads(4);torch.backends.cuda.matmul.allow_tf32=False
    parent=a.parent/'runs-v1'/a.model.name;pcfg=json.loads((parent/'config.json').read_text());manifest_identity(pcfg)
    assert pcfg['data_sha256']==sha(a.data) and pcfg['source_banks_sha256']==sha(parent/'source-banks.pt')
    assert pcfg['qa_predictions_sha256']==sha(parent/'qa-predictions.jsonl')
    old={(p['item_id'],p['operation'],p['readout'],p['mapping']):p for p in map(json.loads,(parent/'qa-predictions.jsonl').read_text().splitlines())}
    tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True,padding_side='left')
    if tok.pad_token_id is None:tok.pad_token=tok.eos_token
    rows=list(map(json.loads,a.data.read_text().splitlines()));tasks,gens,prefixes,tokens,excluded=prepare(rows,tok,pcfg['layer'])
    assert sorted(prefixes)==pcfg['cohort'];target={g['row']['source_unit']:g['patch_tokens'] for g in gens}
    tasks=[t for t in tasks if t['operation']=='BASE' and int(t['original_row']['sentence_sha256'][:16],16)%a.shards==a.shard]
    for t in tasks:
        p=old[t['original_row']['item_id'],'BASE_BANK',t['readout'],t['mapping']]
        assert p['prompt_sha256']==digest(t['prompt']) and p['candidate_gold']==t['candidate_gold']
        t['target_tokens']=target[t['original_row']['source_unit']]
    banks=torch.load(parent/'source-banks.pt',map_location='cpu',weights_only=False)
    cfg=AutoConfig.from_pretrained(a.model,local_files_only=True);klass=Gemma3ForConditionalGeneration if cfg.model_type=='gemma3' else AutoModelForCausalLM
    start=time.monotonic();model=klass.from_pretrained(a.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='eager').to('cuda').eval()
    decoder=blocks(model);fixed=min(t['original_row']['source_unit'] for t in tasks);checks=[]
    for t in [t for t in tasks if t['original_row']['source_unit']==fixed]:
        uid=t['original_row']['item_id'];base=qa_score(model,decoder,banks,tokens,t,'BASE_BANK');both=score(model,decoder,banks,tokens,t,target,'BOTH')
        oldbase=old[uid,'BASE_BANK',t['readout'],t['mapping']]['candidate_logprobs'];oldtarget=old[uid,'TARGET_BANK',t['readout'],t['mapping']]['candidate_logprobs']
        bdelta=max(abs(x-y) for x,y in zip(base,oldbase));tdelta=max(abs(x-y) for x,y in zip(both,oldtarget));assert max(bdelta,tdelta)<.001
        channels={}
        for mode in ['KEY_ONLY','VALUE_ONLY']:
            verified=[];score(model,decoder,banks,tokens,t,target,mode,verified)
            assert len(verified)==2*(len(decoder)-1);channels[mode]=len(verified)
        checks.append(dict(item_id=uid,readout=t['readout'],mapping=t['mapping'],BASE_parent_LP_max_delta=bdelta,BOTH_target_parent_LP_max_delta=tdelta,
            projection_invariants=channels))
    a.out.mkdir(parents=True,exist_ok=True);assert not (a.out/'predictions.jsonl').exists()
    config=dict(data_sha256=sha(a.data),model_manifest_sha256=sha(a.model/'manifest.json'),parent_model_manifest_sha256=pcfg['model_manifest_sha256'],
        parent_qa_predictions_sha256=pcfg['qa_predictions_sha256'],source_banks_sha256=pcfg['source_banks_sha256'],code_sha256=sha(Path(__file__)),
        dependencies={n:sha(Path(__file__).with_name(n)) for n in ['source_bank_routes.py','shared_source_cross_use.py','natural_cue_patching.py']},
        dtype='float32',attention='eager',seed=84,shard=a.shard,shards=a.shards,gpu=a.gpu,QA_tasks=len(tasks),new_tasks=2*len(tasks),
        cohort=sorted({t['original_row']['source_unit'] for t in tasks}),parent_cohort=pcfg['cohort'],instrument=checks,
        scope='Source block outputs replay BASE at all layers; target Source K or V projections modified at next layers. Source internal queries may change, but outputs overwritten; not native encoding/propagation proof.')
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    with (a.out/'predictions.jsonl').open('w') as f:
        for i,t in enumerate(tasks):
            for mode in ['KEY_ONLY','VALUE_ONLY']:
                lp=score(model,decoder,banks,tokens,t,target,mode);mx=max(lp);den=mx+math.log(sum(math.exp(x-mx) for x in lp));r=t['original_row'];g=t['candidate_gold']
                f.write(json.dumps(dict(item_id=r['item_id'],source_unit=r['source_unit'],operation=mode,readout=t['readout'],mapping=t['mapping'],
                    candidate_gold=g,candidate_logprobs=lp,correct=max(range(2),key=lp.__getitem__)==g,p_correct=math.exp(lp[g]-den),prompt_sha256=digest(t['prompt'])))+'\n')
            if i%64==0:f.flush();print('E84',a.model.name,a.shard,i+1,'/',len(tasks),flush=True)
    config.update(predictions_sha256=sha(a.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600)
    (a.out/'config.json').write_text(json.dumps(config,indent=2)+'\n');(a.out/Path(__file__).name).write_bytes(Path(__file__).read_bytes());print('E84 complete',a.model.name,a.shard,config['gpu_hours'],flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ['data','parent','model','out']:p.add_argument('--'+n,type=Path,required=True)
    p.add_argument('--gpu',type=int,required=True);p.add_argument('--shard',type=int,default=0);p.add_argument('--shards',type=int,default=1)
    run(p.parse_args())
