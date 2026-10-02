#!/usr/bin/env python3
"""Exact released BF16 probability arithmetic versus same-logit FP32 controls."""
import hashlib,json,time
from pathlib import Path
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM
from run_implicaturex import prepare

root=Path('/data1/xiangding/work/pragmatic-inference-calibration')
output=root/'runs/E25-Qwen3-4B-source-arithmetic';assert not output.exists()
rows,audit=prepare(root);selected=set()
for t in sorted({r['phenomenon'] for r in rows}):
 ids=sorted({r['item_id'] for r in rows if r['phenomenon']==t});selected.update([ids[0],ids[-1]])
rows=[r for r in rows if r['item_id'] in selected];assert len(rows)==96
cs={(r['system_prompt'],r['prompt']):r for r in map(json.loads,(root/'upstream/ImplicatureX-lfs/Qwen_Qwen3-4B.jsonl').read_text().splitlines())}
output.mkdir(parents=True);start=time.monotonic();torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
tok=AutoTokenizer.from_pretrained(root/'models/Qwen3-4B',local_files_only=True)
model=AutoModelForCausalLM.from_pretrained(root/'models/Qwen3-4B',local_files_only=True,torch_dtype=torch.bfloat16,device_map={'':0},weights_only=True).eval()
labels=[tok.encode(c,add_special_tokens=False)[0] for c in ['1','2']];values=[]
with (output/'predictions.jsonl').open('w') as f:
 for r in rows:
  inp=tok.apply_chat_template([{'role':'system','content':r['system_prompt']},{'role':'user','content':r['prompt']}],
       add_generation_prompt=True,return_dict=True,enable_thinking=False,return_tensors='pt').to(model.device)
  with torch.inference_mode():
   logits=model(**inp,output_hidden_states=True).logits[0,-1]
   global_probs=logits.softmax(-1);target=global_probs[labels];parent=target/target.sum()
   fp32_target=logits.float()[labels].softmax(-1)
   fp32_global=logits.float().softmax(-1)[labels];fp32_global=fp32_global/fp32_global.sum()
  enc={r['true_label']:'True',r['false_label']:'False'}
  old=cs[r['system_prompt'],r['prompt']]['option_probs'];oldvec=[old[enc[c]] for c in ['1','2']]
  rec={'item_id':r['item_id'],'state':r['state'],'true_label':r['true_label'],'model_logit_dtype':str(logits.dtype),
       'parent_probs':parent.tolist(),'parent_sum':float(parent.double().sum()),'fp32_target_probs':fp32_target.tolist(),
       'fp32_global_normalized_probs':fp32_global.tolist(),'source_cache_probs':oldvec,
       'parent_cache_max_delta':max(abs(x-y) for x,y in zip(parent.tolist(),oldvec)),
       'fp32_methods_max_delta':float((fp32_global-fp32_target).abs().max()),
       'input_token_sha256':hashlib.sha256(json.dumps(inp.input_ids.tolist()).encode()).hexdigest()}
  f.write(json.dumps(rec)+'\n');values.append(rec)
summary={'n':len(values),'source_audit':audit,'complete':True,'seconds':time.monotonic()-start,
         'max_fp32_method_delta':max(r['fp32_methods_max_delta'] for r in values),
         'mean_source_cache_max_delta':sum(r['parent_cache_max_delta'] for r in values)/len(values),
         'max_parent_sum_deviation':max(abs(r['parent_sum']-1) for r in values),
         'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(output/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))
