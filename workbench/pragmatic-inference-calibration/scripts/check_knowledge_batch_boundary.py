#!/usr/bin/env python3
"""E30 finite POST-HOC debug keys; retain all original E29 predictions."""
import argparse,hashlib,json
from pathlib import Path
import torch
from transformers import AutoTokenizer,AutoModelForCausalLM
from epitome_data import prepare
from run_native_readout import next_logits
ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--stage',choices=['SFT','DPO'],required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args();assert not a.output.exists()
rs,_,audit=prepare(a.root);knowledge=[r for r in rs if r['phase']=='knowledge'];bad={'SFT':'si:32:knowledge:1:3:some','DPO':'si:18:knowledge:2:3:2'}
keys=list(dict.fromkeys([bad[a.stage],bad['DPO' if a.stage=='SFT' else 'SFT'],knowledge[0]['key'],knowledge[-1]['key']]))
tok=AutoTokenizer.from_pretrained(a.root/'models/OLMoE-1B-7B-0125-SFT',local_files_only=True,padding_side='left');tok.pad_token=tok.eos_token
labels=[tok.encode(c,add_special_tokens=False)[0] for c in ['Yes','No']]
torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
model=AutoModelForCausalLM.from_pretrained(a.root/'models'/('OLMoE-1B-7B-0125-'+a.stage),local_files_only=True,torch_dtype=torch.float32,device_map={'':0},weights_only=True).eval()
def encode(r,inter):
 p=r['prompt']
 if inter=='common-chat':p=tok.apply_chat_template([{'role':'user','content':'Reply with only one answer from: Yes, No.\n\n'+p}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
 return tok.encode(p,add_special_tokens=False)
@torch.inference_mode()
def read(rows,inter,index):
 ids=[encode(r,inter) for r in rows];inp=tok.pad({'input_ids':ids,'attention_mask':[[1]*len(x) for x in ids]},padding=True,return_tensors='pt').to(model.device);z=next_logits(model,inp)[index];target=z[labels]
 return {'yes_prob':float(target.softmax(-1)[0]),'support_mass':float((target.logsumexp(-1)-z.logsumexp(-1)).exp()),'input_sha256':hashlib.sha256(json.dumps(ids[index]).encode()).hexdigest(),'batch_keys':[r['key'] for r in rows]}
result={'stage':a.stage,'source_audit':audit,'dtype':'float32','tf32':False,'controls':[],'debug_only':True}
for key in keys:
 source_index=next(i for i,r in enumerate(rs) if r['key']==key);knowledge_index=next(i for i,r in enumerate(knowledge) if r['key']==key);r=rs[source_index]
 for inter in ['bare','common-chat']:
  mixes=[('single',[r],0),('single-repeat',[r],0),('source-mix',rs[source_index//8*8:source_index//8*8+8],source_index%8),('knowledge-mix',knowledge[knowledge_index//8*8:knowledge_index//8*8+8],knowledge_index%8)]
  values={name:read(rows,inter,idx) for name,rows,idx in mixes};assert len({v['input_sha256'] for v in values.values()})==1
  result['controls'].append({'key':key,'interface':inter,'values':values,'max_probability_delta_from_single':max(abs(v['yes_prob']-values['single']['yes_prob']) for v in values.values())})
a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'stage':a.stage,'controls':[{k:r[k] for k in ['key','interface','max_probability_delta_from_single']} for r in result['controls']]}))
