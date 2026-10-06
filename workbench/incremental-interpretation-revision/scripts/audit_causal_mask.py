"""E52 mask instrument: 2D versus equivalent 4D causal, no relaxed future edges."""
import argparse
import json
from pathlib import Path
import time

import torch
from transformers import AutoConfig,AutoModelForCausalLM,AutoTokenizer,Gemma3ForConditionalGeneration
from data import sha
from reading_map import generate_tasks,encode_choices,sequence_scores


def causal_4d(mask,dtype):
    batch,width=mask.shape
    allowed=torch.ones(width,width,device=mask.device,dtype=torch.bool).tril()[None,None].expand(batch,1,width,width)
    allowed=allowed & mask[:,None,None,:].bool()
    return torch.zeros(allowed.shape,dtype=dtype,device=mask.device).masked_fill(~allowed,torch.finfo(dtype).min)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,required=True)
    ap.add_argument('--model',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args()
    rows=[json.loads(x) for x in args.data.read_text().splitlines()]
    tokenizer=AutoTokenizer.from_pretrained(args.model,local_files_only=True,padding_side='left')
    if tokenizer.pad_token_id is None:tokenizer.pad_token=tokenizer.eos_token
    config=AutoConfig.from_pretrained(args.model,local_files_only=True)
    klass=Gemma3ForConditionalGeneration if config.model_type=='gemma3' else AutoModelForCausalLM
    start=time.monotonic();torch.manual_seed(52);torch.set_num_threads(8)
    model=klass.from_pretrained(args.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='sdpa').to('cuda').eval()
    tasks=list(generate_tasks(rows,tokenizer,['B'],['R0'],'sequence'))
    comparisons=[];independent=[]
    # Prefix-only next-token probabilities independently check causal indexing:
    # no candidate answer token is present in this reference forward pass.
    for task in tasks[:2]:
        sequences,common=encode_choices(tokenizer,task)
        reference_ids=torch.tensor([sequences[0][:common]],device=model.device)
        with torch.inference_mode():reference=model(input_ids=reference_ids,use_cache=False).logits[0,-1].float().log_softmax(-1)
        actual=sequence_scores(model,sequences,[common]*len(sequences),tokenizer.pad_token_id)
        assert all(len(s)==common+1 for s in sequences),'This next-token check requires single-token options'
        expected=[float(reference[s[common]]) for s in sequences]
        independent.append(dict(task_sha256=sha_text(task['prompt']),prefix_only_scores=expected,sequence_scores=actual,
            delta=max(abs(a-b) for a,b in zip(actual,expected)),prefix_start=sequences[0][:8]))
    def hook(module,positional,kwargs):
        mask=kwargs['attention_mask'];assert mask.ndim==2
        kwargs['attention_mask']=causal_4d(mask,model.dtype)
        return positional,kwargs
    for begin in range(0,len(tasks),8):
        batch=tasks[begin:begin+8];sequences=[];common=[]
        for task in batch:
            encoded,n=encode_choices(tokenizer,task);sequences.extend(encoded);common.extend([n]*len(encoded))
        baseline=sequence_scores(model,sequences,common,tokenizer.pad_token_id)
        handle=model.register_forward_pre_hook(hook,with_kwargs=True)
        try:explicit=sequence_scores(model,sequences,common,tokenizer.pad_token_id)
        finally:handle.remove()
        comparisons.extend(dict(task_sha256=sha_text(task['prompt']),scores_2d=baseline[i*2:i*2+2],scores_4d=explicit[i*2:i*2+2]) for i,task in enumerate(batch))
    errors=[abs(a-b) for r in comparisons for a,b in zip(r['scores_2d'],r['scores_4d'])]
    report=dict(model_path=str(args.model),model_manifest_sha256=sha(args.model/'manifest.json'),data_sha256=sha(args.data),
        dtype='float32',seed=52,tasks=len(tasks),maximum_logprob_delta=max(errors),mean_logprob_delta=sum(errors)/len(errors),
        decision_flips=sum((r['scores_2d'][0]>r['scores_2d'][1])!=(r['scores_4d'][0]>r['scores_4d'][1]) for r in comparisons),
        comparisons=comparisons,code_sha256=sha(Path(__file__)),gpu_hours=(time.monotonic()-start)/3600,
        independent_prefix_only_checks=independent,
        interpretation='Equivalent causal masks only. No oracle/patch or scientific revision effect was tested.')
    args.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='comparisons'}))


def sha_text(text):
    import hashlib
    return hashlib.sha256(text.encode()).hexdigest()


if __name__=='__main__':main()
