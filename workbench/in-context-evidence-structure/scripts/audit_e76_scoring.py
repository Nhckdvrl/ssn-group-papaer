"""Post-run numerical audit of cached exact candidate scoring, no case selection."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from e76_operator import encode, offsets


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--model',required=True);ap.add_argument('directories',nargs='+');a=ap.parse_args()
    torch.set_num_threads(6)
    tok=AutoTokenizer.from_pretrained(a.model,local_files_only=True)
    model=AutoModelForCausalLM.from_pretrained(a.model,local_files_only=True,dtype=torch.float32,device_map='cuda',attn_implementation='eager').eval()
    with torch.inference_mode():
        for name in a.directories:
            d=Path(name);c=json.loads((d/'contexts.jsonl').read_text().splitlines()[0])
            r=json.loads((d/'behavior.jsonl').read_text().splitlines()[0]);checks=[]
            for ins in [0,1]:
                pre,_=encode(tok,c,offsets(c,'base'),ins)
                for qi in [0,1,3,4]:
                    q=c['queries'][qi]
                    query=tok.encode(f'Input: {q["input"]}\nSource: {c["names"][q["source"]]}\nLabel:',add_special_tokens=False)
                    enc=[tok.encode(' '+str(y),add_special_tokens=False) for y in c['candidates']]
                    cp=enc[0][:-1];assert all(e[:-1]==cp for e in enc)
                    # Candidate itself is fed; score its every token from preceding
                    # logits. This differs from the runner's common-prefix shortcut.
                    values=[]
                    for seq in enc:
                        ids=pre+query+seq
                        logits=model(input_ids=torch.tensor([ids],device='cuda'),logits_to_keep=len(seq)+1).logits[0].float().log_softmax(-1)
                        values.append(float(sum(logits[j,tokid] for j,tokid in enumerate(seq))))
                    cached=np.array(r['scores'][f'{ins}.base'][qi]);err=float(np.max(np.abs(cached-values)))
                    checks.append({'context':0,'instruction':ins,'query':qi,'max_error':err})
                    assert err<=.1,(name,checks[-1],values,cached.tolist())
            out={'kind':'POST-RUN numerical scoring audit, not a new scientific readout','checks':checks,
                 'max_error':max(x['max_error'] for x in checks),'threshold':.1,
                 'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
            (d/'scoring_audit.json').write_text(json.dumps(out,indent=2));print(name,out['max_error'],flush=True)


if __name__=='__main__':main()
