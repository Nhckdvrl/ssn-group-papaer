"""E41 actual train400 surface edits, preserving every authored fact."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import time


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp'))
    ap.add_argument('--runs',type=Path,default=Path('/home/xiang/.cache/game-npc-research/runs'))
    ap.add_argument('--model',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
    import numpy as np
    import torch
    from transformers import AutoModel,AutoTokenizer
    torch.set_num_threads(1);start=time.monotonic()
    rows=json.loads((args.source/'research/data/personas/train_400_v3.json').read_text())
    old=json.loads((args.runs/'e26_semantic_codes/texts.json').read_text())
    def reverse(text):
        prefix,clauses=text.split('. ',1)
        parts=[part.strip() for part in clauses.rstrip('.').split(',')]
        assert len(parts)>=5
        changed=prefix+'. '+', '.join(reversed(parts))+'.'
        assert sorted(parts)==sorted(changed.split('. ',1)[1].rstrip('.').split(', '))
        return changed
    held=json.loads((args.source/'research/data/personas/test_100_v3.json').read_text())
    original_held=old['variants']['reverse_clauses']
    assert [reverse(r['text']) for r in held]==original_held
    texts=[r['text'] for r in rows]+[reverse(r['text']) for r in rows]
    tokenizer=AutoTokenizer.from_pretrained(args.model,local_files_only=True)
    model=AutoModel.from_pretrained(args.model,local_files_only=True,dtype=torch.float16).to('cuda').eval().requires_grad_(False)
    vectors=[]
    with torch.inference_mode():
        for offset in range(0,len(texts),32):
            tok=tokenizer(texts[offset:offset+32],padding=True,truncation=False,return_tensors='pt').to('cuda')
            h=model(**tok).last_hidden_state
            pos=torch.arange(tok['attention_mask'].shape[1],device='cuda')
            last=torch.where(tok['attention_mask'].bool(),pos,-1).max(-1).values
            v=h[torch.arange(len(last),device='cuda'),last]
            vectors.append(torch.nn.functional.normalize(v,dim=-1).float().cpu().numpy())
    vectors=np.concatenate(vectors)
    canonical=np.load(args.runs/'e23_embedding_context/proper_pool.npy').astype(np.float32)
    output=np.load(args.runs/'e26_semantic_codes/reverse_clauses.npy').astype(np.float32).copy()
    output[:400]=vectors[400:]
    cos=lambda a,b:np.sum(a.astype(np.float64)*b,axis=-1)/(np.linalg.norm(a,axis=-1)*np.linalg.norm(b,axis=-1))
    assert np.all(np.max(np.abs(output[:400]-canonical[:400]),axis=-1)>1e-5)
    assert np.array_equal(output[400:],np.load(args.runs/'e26_semantic_codes/reverse_clauses.npy')[400:])
    np.save(args.out/'reverse_all500.npy',output)
    np.save(args.out/'canonical_train_repeat.npy',vectors[:400])
    (args.out/'texts.json').write_text(json.dumps({'train_ids':[r['id'] for r in rows],
       'canonical':[r['text'] for r in rows],'reverse':[reverse(r['text']) for r in rows]},ensure_ascii=False,indent=2)+'\n')
    result={'train_personas_actually_edited':400,'all_train_rows_different':True,
            'canonical_repeat_cos_min':float(cos(canonical[:400],vectors[:400]).min()),
            'reverse_cos_mean':float(cos(canonical[:400],vectors[400:]).mean()),
            'reverse_cos_min':float(cos(canonical[:400],vectors[400:]).min()),
            'held100_reverse_vectors_byte_unchanged':True,'same_comma_separated_descriptor_multiset':True,
            'same_E26_held_reverse_recipe':True,'model_revision':args.model.name,
            'encoded_texts':len(texts),'wall_seconds':time.monotonic()-start,'cloud_calls':0,
            'array_sha256':hashlib.sha256((args.out/'reverse_all500.npy').read_bytes()).hexdigest(),
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (args.out/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)


if __name__=='__main__':main()
