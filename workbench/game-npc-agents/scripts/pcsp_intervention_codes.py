"""E41 train-only C interventions; retain original canonical vectors exactly."""
import argparse
import ast
import copy
import hashlib
import json
import os
from pathlib import Path
import time


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp'))
    ap.add_argument('--baseline-codes',type=Path,default=Path('/home/xiang/.cache/game-npc-research/runs/e23_embedding_context/proper_pool.npy'))
    ap.add_argument('--model',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
    import numpy as np
    import torch
    from transformers import AutoModel,AutoTokenizer
    torch.set_num_threads(1);start=time.monotonic()
    rows=json.loads((args.source/'research/data/personas/train_400_v3.json').read_text())
    held=json.loads((args.source/'research/data/personas/test_100_v3.json').read_text())
    skeleton=lambda r:tuple(r['big_five'][k] for k in ['E','N','A','O'])
    assert not set(map(skeleton,rows))&set(map(skeleton,held))
    syntax=ast.parse((args.source/'research/scripts/generate_personas_500.py').read_text())
    desc=next(ast.literal_eval(n.value) for n in syntax.body if isinstance(n,ast.Assign)
        and any(isinstance(t,ast.Name) and t.id=='_BF_DESC' for t in n.targets))
    def text(row):return f"{row['age']}세 {row['occupation']}. "+', '.join(desc[f'{k}_{v}'] for k,v in row['big_five'].items())+'.'
    assert all(text(r)==r['text'] for r in rows)
    assert [r['id'] for r in rows]==list(range(1,401))
    levels=['low','mid','high'];variants=[];texts=[]
    for original in rows:
        group=[]
        for level in levels:
            changed=copy.deepcopy(original);changed['big_five']['C']=level;changed['text']=text(changed)
            assert all(changed[k]==original[k] for k in ['decay_modifiers','preferred_actions','age','occupation'])
            group.append(changed);texts.append(changed['text'])
        variants.append(group)
    (args.out/'variants.json').write_text(json.dumps({'levels':levels,'personas':variants},ensure_ascii=False,indent=2)+'\n')
    tokenizer=AutoTokenizer.from_pretrained(args.model,local_files_only=True)
    lengths=[len(tokenizer(t)['input_ids']) for t in texts];assert max(lengths)<=256
    model=AutoModel.from_pretrained(args.model,local_files_only=True,dtype=torch.float16).to('cuda').eval().requires_grad_(False)
    vectors=[]
    with torch.inference_mode():
        for offset in range(0,len(texts),32):
            tok=tokenizer(texts[offset:offset+32],padding=True,truncation=False,return_tensors='pt').to('cuda')
            hidden=model(**tok).last_hidden_state
            pos=torch.arange(tok['attention_mask'].shape[1],device='cuda')
            last=torch.where(tok['attention_mask'].bool(),pos,-1).max(-1).values
            pooled=hidden[torch.arange(len(last),device='cuda'),last]
            vectors.append(torch.nn.functional.normalize(pooled,dim=-1).float().cpu().numpy())
    vectors=np.concatenate(vectors).reshape(400,3,1024)
    canonical=np.load(args.baseline_codes).astype(np.float32)[:400]
    repeated=np.stack([vectors[i,levels.index(r['big_five']['C'])] for i,r in enumerate(rows)])
    cos=np.sum(canonical.astype(np.float64)*repeated,axis=-1)/(np.linalg.norm(canonical,axis=-1)*np.linalg.norm(repeated,axis=-1))
    np.save(args.out/'canonical_repeat.npy',repeated)
    for i,row in enumerate(rows):vectors[i,levels.index(row['big_five']['C'])]=canonical[i]
    assert all(np.array_equal(vectors[i,levels.index(r['big_five']['C'])],canonical[i]) for i,r in enumerate(rows))
    np.save(args.out/'C_variants.npy',vectors)
    result={'base_train_personas':400,'encoded_texts':len(texts),'new_C_variants':800,'levels':levels,
        'train_nonC_backgrounds':20,'held_nonC_backgrounds':5,'background_overlap':0,
        'canonical_original_vectors_byte_identical':True,'canonical_repeat_cos_min':float(cos.min()),
        'canonical_repeat_cos_mean':float(cos.mean()),'max_token_length':max(lengths),
        'source_sha':'5420f7b4fa0fdb6110e131402af9f5386ce2d0cf','model_revision':args.model.name,
        'baseline_codes_sha256':hashlib.sha256(args.baseline_codes.read_bytes()).hexdigest(),
        'text_metadata_sha256':hashlib.sha256((args.out/'variants.json').read_bytes()).hexdigest(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'cloud_calls':0,
        'wall_seconds':time.monotonic()-start}
    (args.out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)


if __name__=='__main__':main()
