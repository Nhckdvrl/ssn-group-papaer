"""E53 question-free, faithful two-sentence generation on immutable published text."""
import argparse
import collections
import json
import os
from pathlib import Path
import re
import time

from data import sha,write_jsonl
from data_v2 import digest
from reading_map import REPAIR

INSTRUCTION=('You are a linguistic experiment subject. You will be presented with a sentence, '
    'and you will need to split it into two sentences that convey the exact same '
    'situation as the original sentence. Note: keep the sentences as simple as possible.')
# Amouyal et al. ACL2025 Appendix H / Fig10 (CC BY 4.0), original example typo retained.
EXAMPLES='''Example 1:
Sentence: The dog ran in the courtyard, and the man fell.
Splitted:
1. The dog ran in the courtyard.
2. The man fell.
Example 2:
Sentence: Sarah met her boss in the park when the plane crashed.
Splitted:
1. Sarah met her boss in the park.
2. The plane crashed.
Example 3:
Sentence: She cleaned the mess that her sister made.
Splitted:
1. She cleaned the mess.
2. Her sister made the mess.
Example 4:
Sentence: They looked for the treasure, hoping to find salvation.
Splitted:
1. The looked for the treasure.
2. They hoped to find salvation.'''


def sentence_parts(text):
    text=text.rsplit('</think>',1)[-1].strip()
    text=re.sub(r'^Splitted:\s*','',text,flags=re.IGNORECASE)
    # Numbering is formatting, not an additional sentence. Keep all prose.
    text=re.sub(r'(?:^|(?<=[.!?])\s+)\d+[.)]\s*',' ',text,flags=re.MULTILINE).strip()
    return [x.strip() for x in re.split(r'(?<=[.!?])\s+',text) if x.strip()]


def build(data,out):
    grouped=collections.defaultdict(list)
    for row in map(json.loads,data.read_text().splitlines()):
        if row['needs_revision']:grouped[row['sentence_sha256']].append(row)
    rows=[]
    for fingerprint,members in sorted(grouped.items()):
        assert all(digest(r['sentence'])==fingerprint for r in members)
        rows.append(dict(item_id='E53-source:'+fingerprint[:20],sentence_sha256=fingerprint,
            sentence=members[0]['sentence'],member_ids=[r['item_id'] for r in members],
            constructions=sorted({r['construction'] for r in members}),
            conditions=sorted({r['condition'] for r in members})))
    write_jsonl(out,rows)
    out.with_suffix('.manifest.json').write_text(json.dumps(dict(source_data_sha256=sha(data),
        data_sha256=sha(out),unique_sentences=len(rows),original_QA=sum(len(r['member_ids']) for r in rows)),indent=2)+'\n')


def prompt(tokenizer,sentence,fmt,reading):
    text=sentence+'\n'+sentence if reading=='R1' else sentence
    content=INSTRUCTION+('\n'+REPAIR if reading=='R8' else '')
    if fmt=='P-A':content+='\nYou will be provided with a few examples.\n'+EXAMPLES
    content+='\nSentence: '+text+'\nSplitted:'
    # Use the native template, but no comprehension-question system instruction.
    messages=[dict(role='user',content=content)]
    if tokenizer.chat_template:
        return tokenizer.apply_chat_template(messages,tokenize=False,add_generation_prompt=True,enable_thinking=False)
    return content+'\n'


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data',type=Path,required=True)
    ap.add_argument('--build-out',type=Path);ap.add_argument('--model',type=Path);ap.add_argument('--out',type=Path)
    ap.add_argument('--limit',type=int);ap.add_argument('--cap',type=int,default=256);args=ap.parse_args()
    if args.build_out:build(args.data,args.build_out);return
    assert args.model and args.out
    os.environ.update(HF_HUB_OFFLINE='1',TRANSFORMERS_OFFLINE='1',HF_ENDPOINT='https://hf-mirror.com',
        HF_HUB_DISABLE_TELEMETRY='1',VLLM_NO_USAGE_STATS='1',DO_NOT_TRACK='1')
    from transformers import AutoTokenizer
    from vllm import LLM,SamplingParams
    import torch,transformers,vllm
    rows=[json.loads(x) for x in args.data.read_text().splitlines()]
    if args.limit:rows=rows[:args.limit]
    args.out.mkdir(parents=True,exist_ok=True);assert not (args.out/'predictions.jsonl').exists()
    tokenizer=AutoTokenizer.from_pretrained(args.model,local_files_only=True)
    start=time.monotonic()
    engine=LLM(model=str(args.model),tokenizer=str(args.model),dtype='bfloat16',seed=52,tensor_parallel_size=1,
        max_model_len=4096,max_num_seqs=64,gpu_memory_utilization=.80,enforce_eager=True,disable_log_stats=True)
    tasks=[(r,fmt,reading,prompt(tokenizer,r['sentence'],fmt,reading)) for r in rows for fmt in ('P-A','P-B') for reading in ('R0','R1','R8')]
    config=dict(model_path=str(args.model),model_manifest_sha256=sha(args.model/'manifest.json'),data_sha256=sha(args.data),
        seed=52,dtype='bfloat16',cap=args.cap,temperature=0,tasks=len(tasks),code_sha256=sha(Path(__file__)),
        torch=torch.__version__,transformers=transformers.__version__,vllm=vllm.__version__,
        instruction=INSTRUCTION,examples=EXAMPLES,repair=REPAIR,prompt_source='https://aclanthology.org/2025.acl-long.403/')
    (args.out/'paraphrase_map.py').write_bytes(Path(__file__).read_bytes())
    (args.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    params=SamplingParams(temperature=0,max_tokens=args.cap,seed=52)
    with (args.out/'predictions.jsonl').open('w') as stream:
        for begin in range(0,len(tasks),256):
            batch=tasks[begin:begin+256]
            inputs=[dict(prompt_token_ids=tokenizer.encode(t[3],add_special_tokens=not bool(tokenizer.chat_template))) for t in batch]
            outputs=engine.generate(inputs,params,use_tqdm=False)
            for (row,fmt,reading,p),generated in zip(batch,outputs):
                completion=generated.outputs[0]
                # Simple source-paper format statistic only; T4 is authoritative.
                parts=sentence_parts(completion.text)
                record=dict(item_id=row['item_id'],sentence_sha256=row['sentence_sha256'],format=fmt,reading=reading,
                    prompt=p,prompt_sha256=digest(p),prompt_tokens=len(generated.prompt_token_ids),
                    prompt_start_token_ids=list(generated.prompt_token_ids[:8]),add_special_tokens=not bool(tokenizer.chat_template),
                    text=completion.text,text_sha256=digest(completion.text),generated_token_ids=list(completion.token_ids),
                    finish_reason=completion.finish_reason,capped=completion.finish_reason=='length',
                    automatic_sentence_parts=parts,automatic_two_sentences=len(parts)==2)
                stream.write(json.dumps(record)+'\n')
            stream.flush();print(begin+len(batch),'/',len(tasks),flush=True)
    config.update(predictions_sha256=sha(args.out/'predictions.jsonl'),gpu_hours=(time.monotonic()-start)/3600)
    (args.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')


if __name__=='__main__':main()
