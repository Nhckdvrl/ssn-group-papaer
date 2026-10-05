"""E37 natural time-indexed role retrieval; independent input/output audits."""
import argparse
import collections
import json
from pathlib import Path
import subprocess
import time
import torch
import transformers
from transformers import AutoModelForCausalLM,AutoTokenizer
from data import CACHE,sha,write_jsonl
from event_identity import digest
from event_constraint_state import CURRENT_WORLD

BASE='Answer the question in one short phrase, using the passage.'
SELECTION_SCOPE='Report an unreported selection outcome as unspecified, while answering chance questions from the stated probabilities for the new selection.'
EARLIER_ROLE_SCOPE='Apply the participant description only to the actor and the earlier activity named in the question.'
AVAILABILITY_SCOPE='Answer readiness questions from the new activity description, treating unreported conditions as unspecified; for earlier participant questions, use the explicitly reported earlier activity.'


def build(cache,directory):
    fields=json.loads((directory/'question-fields-v1.json').read_text());assert fields['model']=='gpt-6-luna';ff={r['id']:r for r in fields['rows']};assert len(ff)==24
    hist=[r for r in map(json.loads,(cache/'E34-material-preparation-v1/nli-audited-v3.jsonl').read_text().splitlines()) if r['readout_kind']=='other_actor_new_activity'];assert len(hist)==192
    anchor=[]
    for ex,ver,kind in [('E29','v2','old_supported'),('E31','v1','other_actor_new_activity')]:
        path=cache/f'{ex}-material-preparation-{"v2" if ex=="E29" else "v1"}/nli-audited-{ver}.jsonl'
        rr=[r for r in map(json.loads,path.read_text().splitlines()) if r['readout_kind']==kind and r['exclusion_style']=='named' and (ex=='E29' or r['boundary_marker']=='same_began')]
        assert len(rr)==48;anchor.extend((r,'current' if ex=='E29' else 'new') for r in rr)
    packets=[];rows=[]
    for r,query,context in [(r,q,'history') for r in hist for q in ('current','initial','new')]+[(r,q,'anchor') for r,q in anchor]:
        f=ff[r['pair_id'].split(':')[1]];question=f[('anchor_current' if context=='anchor' and query=='current' else query)+'_question']
        role=r['initial_role'] if query=='initial' else r['role_evidence'] if query=='current' else None
        proposed='source_patient' if role=='initial_patient_only' else 'reference_patient' if role=='reference_only' else 'unspecified'
        cid=f'E37:{r["item_id"]}:{context}:{query}';packet=dict(id=cid,passage=r['passage'],passage_sha256=digest(r['passage']),question=question,question_sha256=digest(question),query=query,context=context)
        packets.append(packet)
        for mode in (('base','priority') if context=='history' and query!='initial' else ('base',)):
            rows.append(dict(packet,item_id=cid+':'+mode,context_id=cid,mode=mode,pair_id=r['pair_id'],verb_family=r['verb_family'],
                             initial_status=r.get('initial_status'),initial_role=r.get('initial_role'),final_role=r.get('final_role',r['role_evidence']),history_conflict=r.get('history_conflict'),
                             proposed_answer_class=proposed,gold_answer_class=None,eligible=False))
    assert len(packets)==672 and len(rows)==1056 and len({r['item_id'] for r in rows})==1056
    write_jsonl(directory/'candidates-v1.jsonl',rows)
    for i in range(2):(directory/f'review-packets-{i}.json').write_text(json.dumps(dict(packets=packets[i::2]),indent=2)+'\n')
    return dict(contexts=672,variants=1056,question_fields_sha256=sha(directory/'question-fields-v1.json'),candidate_sha256=sha(directory/'candidates-v1.jsonl'))


def adopt(directory,reviews):
    annotations={}
    for path in reviews:
        a=json.loads(path.read_text());assert a['model']=='gpt-6-luna'
        for r in a['reviews']:
            assert r['id'] not in annotations;annotations[r['id']]=(r,sha(path))
    assert len(annotations)==672
    rows=list(map(json.loads,(directory/'candidates-v1.jsonl').read_text().splitlines()));assert len(rows)==1056
    for r in rows:
        a,h=annotations[r['context_id']];assert a['passage_sha256']==r['passage_sha256'] and a['question_sha256']==r['question_sha256']
        assert a['answer_class'] in ('source_patient','reference_patient','unspecified',None) and a['certainty'] in ('clear','interpretation_dependent','invalid')
        assert a['grammar'] in ('acceptable','marginal','unacceptable')
        r.update(gold_answer_class=a['answer_class'] if a['certainty']=='clear' else None,eligible=a['certainty']=='clear' and a['grammar']!='unacceptable',audit=a,audit_review_sha256=h)
    out=directory/'audited-v1.jsonl';assert not out.exists();write_jsonl(out,rows)
    report=dict(variants=1056,contexts=672,audited_sha256=sha(out),candidate_sha256=sha(directory/'candidates-v1.jsonl'),review_sha256=[sha(p) for p in reviews],eligible=sum(r['eligible'] for r in rows),proposed_agreement=sum(r['gold_answer_class']==r['proposed_answer_class'] for r in rows))
    out.with_suffix('.audit.json').write_text(json.dumps(report,indent=2)+'\n');return report


def run(args):
    assert not args.out.exists();a=json.loads(args.data.with_suffix('.audit.json').read_text());assert sha(args.data)==a['audited_sha256']
    allrows=list(map(json.loads,args.data.read_text().splitlines()));expected={'E37':1056,'E38':1536,'E39':288,'E40':192,'E41':1152,'E43':96,'E44':576}[args.experiment]
    assert len(allrows)==a['variants']==expected
    rows=[r for r in allrows if r['query']==args.query]
    assert len(rows)=={'E37':{'initial':192,'current':432,'new':432},'E38':{'current':1152,'fair':384},'E39':{'current':288},'E40':{'current':192},'E41':{'current':576,'availability':576},'E43':{'current':96},'E44':{'current':384,'availability':192}}[args.experiment][args.query]
    recovery={'E37':CURRENT_WORLD,'E38':SELECTION_SCOPE,'E39':EARLIER_ROLE_SCOPE,'E40':EARLIER_ROLE_SCOPE,'E41':AVAILABILITY_SCOPE,'E43':EARLIER_ROLE_SCOPE,'E44':AVAILABILITY_SCOPE}[args.experiment]
    tok=AutoTokenizer.from_pretrained(args.model,local_files_only=True,padding_side='left');tok.pad_token_id=tok.eos_token_id
    prompts={}
    for r in rows:
        assert digest(r['passage'])==r['passage_sha256'] and digest(r['question'])==r['question_sha256']
        prompt=tok.apply_chat_template([dict(role='system',content=BASE+('\n'+recovery if r['mode']=='priority' else '')),dict(role='user',content='Passage:\n'+r['passage']+'\n\nQuestion:\n'+r['question'])],tokenize=False,add_generation_prompt=True,enable_thinking=False)
        prompts[r['item_id']]=prompt
    torch.manual_seed(0);torch.set_num_threads(8);torch.backends.cuda.matmul.allow_tf32=False;torch.backends.cudnn.allow_tf32=False
    args.out.mkdir(parents=True);start=time.time()
    model=AutoModelForCausalLM.from_pretrained(args.model,local_files_only=True,torch_dtype=torch.float32,attn_implementation='sdpa').to('cuda').eval()
    for p in model.parameters():p.requires_grad_(False)
    cfg=dict(experiment=args.experiment,query=args.query,task_count=len(rows),model_manifest=json.loads((args.model/'manifest.json').read_text()),dtype='float32',tf32=False,attention='sdpa',seed=0,frozen=True,thinking=False,batch_size=8,
             do_sample=False,max_new_tokens=48,data_sha256=sha(args.data),audit_sha256=sha(args.data.with_suffix('.audit.json')),git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),code_sha256=sha(Path(__file__)),
             torch=torch.__version__,transformers=transformers.__version__,gpu=torch.cuda.get_device_name(),base_instruction=BASE,priority_instruction=recovery)
    (args.out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
    with (args.out/'generations.jsonl').open('w') as f,torch.inference_mode():
        for off in range(0,len(rows),8):
            rr=rows[off:off+8];pp=[prompts[r['item_id']] for r in rr];inputs=tok(pp,return_tensors='pt',padding=True).to('cuda')
            gen=model.generate(**inputs,do_sample=False,max_new_tokens=48,pad_token_id=tok.pad_token_id,eos_token_id=tok.eos_token_id,use_cache=True)
            for i,r in enumerate(rr):
                ids=gen[i,inputs['input_ids'].shape[1]:].tolist()
                if tok.eos_token_id in ids:ids=ids[:ids.index(tok.eos_token_id)+1]
                answer=tok.decode(ids,skip_special_tokens=True)
                f.write(json.dumps(dict(r,answer=answer,answer_sha256=digest(answer),generated_token_ids=ids,prompt_sha256=digest(pp[i]),eos_reached=bool(ids and ids[-1]==tok.eos_token_id),cap_reached=len(ids)==48 and ids[-1]!=tok.eos_token_id))+'\n')
            f.flush()
            if off%64==0:print(f'{off+len(rr)}/{len(rows)} elapsed={time.time()-start:.1f}s',flush=True)
    elapsed=time.time()-start;cfg.update(gpu_hours=elapsed/3600,wall_seconds=elapsed,generations_sha256=sha(args.out/'generations.jsonl'),peak_gpu_bytes=torch.cuda.max_memory_allocated());(args.out/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')


if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True)
    b=s.add_parser('build');b.add_argument('--cache',type=Path,default=CACHE);b.add_argument('--directory',type=Path,required=True)
    a=s.add_parser('adopt');a.add_argument('--directory',type=Path,required=True);a.add_argument('--reviews',type=Path,nargs='+',required=True)
    r=s.add_parser('run');r.add_argument('--data',type=Path,required=True);r.add_argument('--experiment',choices=['E37','E38','E39','E40','E41','E43','E44'],default='E37');r.add_argument('--query',choices=['current','initial','new','fair','availability'],required=True);r.add_argument('--model',type=Path,default=CACHE/'models/Qwen3-8B');r.add_argument('--out',type=Path,required=True)
    x=p.parse_args()
    if x.action=='build':print(json.dumps(build(x.cache,x.directory),indent=2))
    elif x.action=='adopt':print(json.dumps(adopt(x.directory,x.reviews),indent=2))
    else:run(x)
