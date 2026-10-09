"""Native function-family validity gate after inconclusive E74."""
import argparse
import hashlib
import json
import platform
import subprocess
import time
from pathlib import Path
import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer
from e74_completion import make_contexts, variant, oracle, encode
from audit_e72_e73_format import decorated_answer
from e72_native import parse_answer


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', required=True);ap.add_argument('--out', required=True)
    ap.add_argument('--n', type=int, default=18);ap.add_argument('--seed', type=int, default=75001)
    a = ap.parse_args();t0 = time.time()
    torch.set_num_threads(6);torch.manual_seed(0)
    d = Path(a.out);d.mkdir(parents=True, exist_ok=True)
    cs = make_contexts('discovery', a.n, a.seed)
    tok = AutoTokenizer.from_pretrained(a.model, local_files_only=True);tok.padding_side = 'left'
    if tok.pad_token_id is None:tok.pad_token_id = tok.eos_token_id
    rows = []
    for c in cs:
        for coverage, family in [('full','bijective'),('held','bijective'),('held','independent')]:
            cv = variant(c, coverage, 'base');o = oracle(cv, family);pre, _ = encode(tok, cv, family, True)
            for s in [0,1]:
                qi = s*3+c['missing_kind'];gold = o[qi]['gold']
                assert gold == (3 if family == 'independent' else cv['maps'][s][c['missing_kind']])
                body = tok.decode(pre, skip_special_tokens=False)
                body += f'Category: {c["classes"][c["missing_kind"]]}\nSource: {c["names"][s]}\nLabel:'
                body += '\n\nComplete the final record. Return the final answer on a line of the form Answer: <code>, using '+', '.join(c['labels'])+', or Unknown.'
                prompt = tok.apply_chat_template([{'role':'user','content':body}],tokenize=False,add_generation_prompt=True,
                                                 enable_thinking=True,reasoning_effort='medium')
                rows.append({'uid':f'{c["context"]}.{coverage}.{family}.{s}','context':c['context'],'source':s,
                    'condition':coverage+'.'+family,'labels':c['labels']+['Unknown'],'gold':gold,'oracle':o[qi],
                    'prompt':prompt,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest()})
    assert len(rows)==6*a.n and len({r['uid'] for r in rows})==len(rows)
    (d/'contexts.jsonl').write_text(''.join(json.dumps(c)+'\n' for c in cs))
    (d/'prompts.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in rows))
    model, loading = AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,dtype=torch.bfloat16,
        device_map='cuda',output_loading_info=True);model.eval()
    assert not loading.get('missing_keys') and not loading.get('unexpected_keys') and not loading.get('mismatched_keys'),loading
    assert model.generation_config.forced_eos_token_id is None and model.generation_config.forced_bos_token_id is None
    eos = model.generation_config.eos_token_id;eos = [eos] if isinstance(eos,int) else list(eos)
    (d/'loading_info.json').write_text(json.dumps(loading,indent=2,default=lambda x:sorted(x) if isinstance(x,set) else str(x)))
    with torch.inference_mode(),(d/'generations.jsonl').open('w') as f:
        for bi,start in enumerate(range(0,len(rows),4)):
            batch = rows[start:start+4]
            inputs = tok([r['prompt'] for r in batch],return_tensors='pt',padding=True,add_special_tokens=False).to('cuda')
            torch.manual_seed(750000+bi)
            outputs = model.generate(**inputs,max_new_tokens=4096,do_sample=True,temperature=.6,top_p=.95,top_k=20,disable_compile=True)
            for r,whole in zip(batch,outputs[:,inputs['input_ids'].shape[1]:].tolist()):
                end = next((i+1 for i,v in enumerate(whole) if v in eos),len(whole))
                ids = whole[:end];ended = bool(ids and ids[-1] in eos);text = tok.decode(ids,skip_special_tokens=False)
                pred,status = decorated_answer(text,r['labels'],True)
                strict,strict_status = parse_answer(text,[v.lower() for v in r['labels']],True)
                f.write(json.dumps({k:v for k,v in r.items() if k!='prompt'} | {'prediction':pred,'parser_status':status,
                    'strict_prediction':strict,'strict_status':strict_status,'tokens':len(ids),'ended':ended,
                    'truncated':not ended and len(ids)>=4096,'text':text,'decode_seed':750000+bi})+'\n')
            f.flush();print(bi,round(time.time()-t0,1),flush=True)
    files = ['e75_native_constraint.py','e74_completion.py','audit_e72_e73_format.py','e72_native.py']
    run = {'args':vars(a),'seconds':time.time()-t0,'torch':torch.__version__,'transformers':transformers.__version__,
        'host':platform.node(),'gpu':torch.cuda.get_device_name(),'model_class':type(model).__name__,
        'config_sha256':hashlib.sha256((Path(a.model)/'config.json').read_bytes()).hexdigest(),
        'template_sha256':hashlib.sha256(str(tok.chat_template).encode()).hexdigest(),
        'source_sha256':{fn:hashlib.sha256((Path(__file__).parent/fn).read_bytes()).hexdigest() for fn in files},
        'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()}
    (d/'run.json').write_text(json.dumps(run,indent=2))


if __name__=='__main__':main()
