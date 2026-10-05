"""E28 three-way event facts; derived relation gold is separate from source QA."""
import argparse
import csv
import json
from pathlib import Path
import time
import subprocess
import torch
import transformers
from transformers import AutoModelForCausalLM,AutoTokenizer
from data import CACHE,sha,write_jsonl
from event_identity import digest

RELATIONS=('entailed','contradicted','undetermined')
REPAIR='Apply participant descriptions to the actor and activity they specify; a different activity may have an unspecified patient.'
BASE='Classify the relation of the proposed fact to the passage. Entailed means it necessarily follows; contradicted means it cannot be true together with the passage; undetermined means neither. Answer only the indicated letter.'


def build(cache,out):
    assert not out.exists()
    p=cache/'E24-material-preparation-v1';fs={r['id']:r for r in json.loads((p/'fields-v3.json').read_text())['rows']}
    old=list(map(json.loads,(cache/'E26-material-preparation-v1/audited-v1.jsonl').read_text().splitlines()))
    allowed=list(map(json.loads,(cache/'E27-material-preparation-v1/audited-v1.jsonl').read_text().splitlines()))
    unrelated=next(csv.DictReader((cache/'upstream/cehakova2025/stimuli/filler_items.csv').open()))['sentence']
    rows=[]
    for r in old+allowed:
        if r['readout_kind']!='scope_compatibility' or r['question_polarity']!='consistent':continue
        kind='old_supported' if r['item_id'].startswith('E27:') else 'old_excluded' if r['scope']=='original_activity' else r['scope']
        proposition=r['proposition']
        # Both new event branches use exactly the same source NP under both
        # prior role facts, enabling bidirectional scope-carryover diagnosis.
        if kind in ('same_actor_new_activity','other_actor_new_activity'):
            f=fs[r['pair_id'].split(':')[1]];a=fs[next(x['donor_source_item'] for x in map(json.loads,(p/'audited-v1.jsonl').read_text().splitlines()) if x['pair_id']==r['pair_id'])] if kind=='other_actor_new_activity' else f
            proposition='In that new '+f['activity_np']+', '+a['actor']+' '+a['auxiliary']+' '+f['progressive_vp']+' '+f['source_core_patient_np']+'.'
        nr=dict(r,item_id='E28:'+r['item_id'],question=None,proposition=proposition,proposition_sha256=digest(proposition),
                gold=None,gold_relation=None,proposed_relation='entailed' if kind=='old_supported' else 'contradicted' if kind=='old_excluded' else 'undetermined',readout_kind=kind,
                relation_semantics='Three-way support, contradiction or underdetermination. New activity patient is not logically fixed by the only statement about the earlier actor/activity.')
        for k in ('audit','audit_review_sha256','proposed_gold','question_sha256'):nr.pop(k,None)
        rows.append(nr)
        if kind=='old_excluded':
            rows.append(dict(nr,item_id=nr['item_id']+':unrelated_filler',proposition=unrelated,proposition_sha256=digest(unrelated),readout_kind='unrelated_unknown_control',proposed_relation='undetermined',control_source='Published first filler item; exact sentence, no invented unrelated action.'))
    assert len(rows)==960 and len({r['item_id'] for r in rows})==960
    write_jsonl(out,rows);return dict(variants=len(rows),candidate_sha256=sha(out),source_items=24,verb_families=12)


def adopt(data,reviews,idmap,out):
    mapping=json.loads(idmap.read_text());ann={}
    for p in reviews:
        j=json.loads(p.read_text());assert j['model']=='gpt-6-luna'
        for a in j['relation_reviews']:
            key=mapping[a['id']];assert key not in ann;ann[key]=(a,sha(p))
    rows=list(map(json.loads,data.read_text().splitlines()));assert set(ann)=={r['item_id'] for r in rows}
    for r in rows:
        a,h=ann[r['item_id']]
        for k in ('sentence_sha256','proposition_sha256'):assert a[k]==r[k]
        assert a['relation'] in (*RELATIONS,None) and a['certainty'] in ('clear','interpretation_dependent','invalid')
        r.update(gold_relation=a['relation'] if a['certainty']=='clear' else None,audit=a,audit_review_sha256=h)
    write_jsonl(out,rows)
    report=dict(variants=960,source_items=24,verb_families=12,candidate_sha256=sha(data),audited_sha256=sha(out),clear_gold=sum(r['gold_relation'] is not None for r in rows),
                proposed_relation_agreement=sum(r['gold_relation']==r['proposed_relation'] for r in rows),review_sha256=[sha(p) for p in reviews],
                gold_schema='Original source QA gold stays separate; gold_relation is independently annotated derived NLI relation, no source answer overwritten.')
    out.with_suffix('.audit.json').write_text(json.dumps(report,indent=2)+'\n');return report


def run(args):
    assert not args.out.exists();report=json.loads(args.data.with_suffix('.audit.json').read_text());assert report['audited_sha256']==sha(args.data)
    rows=list(map(json.loads,args.data.read_text().splitlines()));assert len(rows)==report['variants'] and len({r['item_id'] for r in rows})==len(rows)
    tok=AutoTokenizer.from_pretrained(args.model,local_files_only=True,padding_side='left');tok.pad_token_id=tok.eos_token_id
    labels={letter:[i for word,i in tok.get_vocab().items() if word.replace('Ġ','').replace('▁','').strip()==letter] for letter in 'ABC'};assert all(labels.values())
    configs=[('base',0),('base',1),('base',2)] if args.mode=='base' else [('repair',0)]
    tasks=[]
    for mode,shift in configs:
        mapping={RELATIONS[i]:'ABC'[(i+shift)%3] for i in range(3)}
        lines='\n'.join(f'{letter}: {relation}' for relation,letter in sorted(mapping.items(),key=lambda q:q[1]))
        for r in rows:
            assert digest(r['passage'])==r['sentence_sha256'] and digest(r['proposition'])==r['proposition_sha256']
            prompt=tok.apply_chat_template([{'role':'system','content':BASE+('\n'+REPAIR if mode=='repair' else '')},{'role':'user','content':'Passage:\n'+r['passage']+'\n\nProposed fact:\n'+r['proposition']+'\n\nLabels:\n'+lines}],tokenize=False,add_generation_prompt=True,enable_thinking=False)
            tasks.append((r,mode,shift,mapping,prompt))
    torch.manual_seed(0);torch.set_num_threads(8);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    args.out.mkdir(parents=True);start=time.time()
    model=AutoModelForCausalLM.from_pretrained(args.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='sdpa').to('cuda').eval()
    for p in model.parameters():p.requires_grad_(False)
    cfg=dict(experiment=args.experiment,mode=args.mode,model=str(args.model),model_manifest=json.loads((args.model/'manifest.json').read_text()),dtype='float32',tf32=False,attention='sdpa',seed=0,frozen=True,thinking=False,
             task_count=len(tasks),data_sha256=sha(args.data),audit_sha256=sha(args.data.with_suffix('.audit.json')),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
             code_sha256=sha(Path(__file__)),torch=torch.__version__,transformers=transformers.__version__,gpu=torch.cuda.get_device_name(),batch_size=8,
             class_labels=labels,base_definition=BASE,scope_repair=REPAIR,mapping_policy='Three cyclic mappings for base; canonical map0 paired repair. Compare repair only with base map0.')
    (args.out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    with (args.out/'predictions.jsonl').open('w') as f,torch.inference_mode():
        for off in range(0,len(tasks),8):
            batch=tasks[off:off+8];inputs=tok([x[4] for x in batch],return_tensors='pt',padding=True).to('cuda');logits=model(**inputs,logits_to_keep=1).logits[:,-1,:].float();probs=logits.softmax(-1)
            for i,(r,mode,shift,mapping,prompt) in enumerate(batch):
                masses={rel:float(probs[i,labels[letter]].sum()) for rel,letter in mapping.items()};mass=sum(masses.values());assert mass>0
                pp={rel:v/mass for rel,v in masses.items()};pred=max(pp,key=pp.get);gold=r['gold_relation'];token=tok.decode([int(logits[i].argmax())]);letter=token.replace('Ġ','').replace('▁','').strip()
                o={k:v for k,v in r.items() if k not in ('passage','proposition','question','audit','relation_semantics')}
                o.update(mode=mode,mapping_shift=shift,p_relation=pp,predicted_relation=pred,choice_mass=mass,greedy_token=token,
                         greedy_label_valid=letter in 'ABC' and len(letter)==1,correct=None if gold is None else int(pred==gold),
                         p_correct=None if gold is None else pp[gold],prompt_sha256=digest(prompt))
                f.write(json.dumps(o)+'\n')
            f.flush()
            if off%160==0:print(f'{off+len(batch)}/{len(tasks)} elapsed={time.time()-start:.1f}s',flush=True)
    elapsed=time.time()-start;cfg.update(wall_seconds=elapsed,gpu_hours=elapsed/3600,peak_gpu_bytes=torch.cuda.max_memory_allocated(),predictions_sha256=sha(args.out/'predictions.jsonl'))
    (args.out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True)
    b=s.add_parser('build');b.add_argument('--cache',type=Path,default=CACHE);b.add_argument('--out',type=Path,required=True)
    a=s.add_parser('adopt');a.add_argument('--data',type=Path,required=True);a.add_argument('--reviews',type=Path,nargs='+',required=True);a.add_argument('--idmap',type=Path,required=True);a.add_argument('--out',type=Path,required=True)
    r=s.add_parser('run');r.add_argument('--data',type=Path,required=True);r.add_argument('--mode',choices=['base','repair'],required=True);r.add_argument('--experiment',choices=['E28','E29','E30','E31','E34'],default='E28');r.add_argument('--model',type=Path,default=CACHE/'models/Qwen3-8B');r.add_argument('--out',type=Path,required=True)
    x=p.parse_args()
    if x.action=='build':print(json.dumps(build(x.cache,x.out),indent=2))
    elif x.action=='adopt':print(json.dumps(adopt(x.data,x.reviews,x.idmap,x.out),indent=2))
    else:run(x)
