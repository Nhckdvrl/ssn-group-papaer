"""Literal upstream three-token parser on the fixed 14-item instrument subset."""
import ast
import collections
import json
import os
from pathlib import Path
import string
import time
import argparse

import numpy as np
import torch
from transformers import AutoTokenizer,Gemma3ForCausalLM
from data import CACHE,sha,write_jsonl
from reading_map import generate_tasks


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--data',type=Path,required=True)
    parser.add_argument('--model',type=Path,required=True);parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();args.out.mkdir(parents=True,exist_ok=True)
    assert not (args.out/'predictions.jsonl').exists()
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com')
    source=CACHE/'upstream/amouyal/inference/textgen_inference/fastchat_inference.py'
    # Execute the original function AST, excluding unused FastChat imports only.
    tree=ast.parse(source.read_text());functions=ast.Module(body=[n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))],type_ignores=[])
    namespace=dict(torch=torch,np=np,defaultdict=collections.defaultdict,string_funcs=string,Dict=dict,List=list,PreTrainedTokenizer=object)
    exec(compile(functions,str(source),'exec'),namespace)
    tokenizer=AutoTokenizer.from_pretrained(args.model,local_files_only=True)
    start=time.monotonic();model=Gemma3ForCausalLM.from_pretrained(args.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='sdpa').to('cuda').eval()
    torch.backends.cuda.matmul.allow_tf32=False
    rows=[json.loads(x) for x in args.data.read_text().splitlines()]
    tasks=list(generate_tasks(rows,tokenizer,['A'],['R0'],'legacy'))
    records=[]
    for seed in (52,53):
        torch.manual_seed(seed)
        for i,t in enumerate(tasks):
            inputs=tokenizer(t['prompt'],return_tensors='pt').to(model.device)
            inputs.pop('token_type_ids',None)
            with torch.inference_mode():generated=model.generate(**inputs,return_dict_in_generate=True,output_scores=True,max_new_tokens=3,pad_token_id=tokenizer.eos_token_id)
            result=namespace['parse_mc_generation_results'](generated,tokenizer,t['legacy_options'])
            a,b=result['probs']['correct'],result['probs']['incorrect'];mass=a+b
            r=t['row'];record={k:r[k] for k in ('item_id','sentence_sha256','construction','condition','question_target','pair_id','cluster_id','matched_question_exact')}
            record.update(format='A',reading='R0',order=t['order'],prompt_index=t['prompt_index'],mapping=0,repair=False,mode='legacy',
                seed=seed,p_correct=a/mass if mass else None,correct=a>b if mass else None,
                original_probs=dict(result['probs']),original_unnormalized=dict(result['unnormalized_probs']),
                generated_ids=generated.sequences[0,inputs['input_ids'].shape[1]:].tolist(),
                generated_text=tokenizer.decode(generated.sequences[0,inputs['input_ids'].shape[1]:],skip_special_tokens=False),
                prompt=t['prompt'],prompt_sha256=__import__('hashlib').sha256(t['prompt'].encode()).hexdigest())
            records.append(record)
            if i%32==0:print('seed',seed,i,'/',len(tasks),flush=True)
    write_jsonl(args.out/'predictions.jsonl',records)
    config=dict(model_path=str(args.model),model_manifest_sha256=sha(args.model/'manifest.json'),data_sha256=sha(args.data),
        arguments=dict(dtype='float32'),seeds=[52,53],upstream_source_sha256=sha(source),
        predictions_sha256=sha(args.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600,
        description='Unmodified upstream parser; one unpadded prompt per generate(), source sampling defaults; both fixed seeds reported, never selected.')
    (args.out/'config.json').write_text(json.dumps(config,indent=2)+'\n');(args.out/'original_parser_smoke.py').write_bytes(Path(__file__).read_bytes())


if __name__=='__main__':main()
