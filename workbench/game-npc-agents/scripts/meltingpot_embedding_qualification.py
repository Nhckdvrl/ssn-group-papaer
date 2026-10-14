"""E38 original external encoder recipe, public asset and last-real control."""
import argparse
import ast
import hashlib
import json
import os
from pathlib import Path
import time


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp-meltingpot-audit'))
    ap.add_argument('--asset',type=Path,default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp/results/embeddings/persona_emb_qwen_emb.pt'))
    ap.add_argument('--model',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',TOKENIZERS_PARALLELISM='false')
    import numpy as np
    import torch
    from transformers import AutoModel,AutoTokenizer
    torch.set_num_threads(1);start=time.monotonic()
    source=args.source/'scripts/build_persona_embeddings_qwen.py'
    syntax=ast.parse(source.read_text());selected=[]
    for node in syntax.body:
        if isinstance(node,ast.FunctionDef) and node.name in ['_format_text','_last_token_pool']:
            selected.append(node)
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='DEFAULT_INSTRUCTION' for t in node.targets):
            selected.append(node)
    namespace={'torch':torch}
    exec(compile(ast.Module(body=selected,type_ignores=[]),str(source),'exec'),namespace)
    rows=json.loads((args.source/'research/meltingpot/personas/personas_v0.json').read_text())['personas']
    ids=[r['id'] for r in rows]
    texts=[namespace['_format_text'](r['description'],r['tags'],namespace['DEFAULT_INSTRUCTION']) for r in rows]
    tokenizer=AutoTokenizer.from_pretrained(args.model,padding_side='left',local_files_only=True)
    model=AutoModel.from_pretrained(args.model,dtype=torch.float32,local_files_only=True).to('cuda').eval().requires_grad_(False)
    tokenized=tokenizer(texts,padding=True,truncation=True,max_length=512,return_tensors='pt').to('cuda')
    mask=tokenized['attention_mask'];positions=torch.arange(mask.shape[1],device='cuda')
    last=torch.where(mask.bool(),positions,-1).max(-1).values
    with torch.inference_mode():
        hidden=model(**tokenized).last_hidden_state
        original=torch.nn.functional.normalize(namespace['_last_token_pool'](hidden,mask),dim=-1).cpu()
        correct=torch.nn.functional.normalize(hidden[torch.arange(len(ids),device='cuda'),last],dim=-1).cpu()
        singles=[]
        for text in texts:
            one=tokenizer(text,return_tensors='pt').to('cuda')
            singles.append(torch.nn.functional.normalize(model(**one).last_hidden_state[:,-1],dim=-1).cpu()[0])
        singles=torch.stack(singles)
    asset=torch.load(args.asset,map_location='cpu',weights_only=True)
    assert asset['ids']==ids
    cosine=lambda a,b:torch.nn.functional.cosine_similarity(a.double(),b.double(),dim=-1).tolist()
    lengths=mask.sum(-1).cpu().tolist();wrong=(mask.sum(-1)-1!=last).cpu().tolist()
    result={'ids':ids,'token_lengths':lengths,'padded_length':mask.shape[1],
        'original_index_not_last_real':wrong,'affected_rows':sum(wrong),
        'public_asset_vs_original_recipe_cosines':cosine(asset['embeddings'],original),
        'public_asset_vs_correct_pool_cosines':cosine(asset['embeddings'],correct),
        'correct_batch_vs_single_cosines':cosine(correct,singles),
        'correct_batch_vs_single_max_abs_error':float((correct-singles).abs().max()),
        'default_instruction':namespace['DEFAULT_INSTRUCTION'],'dtype':'float32','model_revision':args.model.name,
        'source_script_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'public_asset_sha256':hashlib.sha256(args.asset.read_bytes()).hexdigest(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'scope':'Encoding implementation qualification; standard last-real pooling, not a scientific contribution.',
        'cloud_calls':0,'wall_seconds':time.monotonic()-start}
    torch.save({'ids':ids,'embeddings':correct},args.out/'persona_emb_correct_pool.pt')
    torch.save({'ids':ids,'embeddings':original},args.out/'persona_emb_source_recipe.pt')
    np.save(args.out/'correct_single.npy',singles.numpy())
    (args.out/'texts.json').write_text(json.dumps(texts,indent=2)+'\n')
    (args.out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
