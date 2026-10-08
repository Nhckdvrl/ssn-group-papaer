"""E108 frozen source data and free belief writing; CPU preparation only."""
import argparse
import json
from pathlib import Path
from data import sha
from reconstruction_reward import INSTRUCTION
from current_open_baseline import RULE

RECOVERY='Read the whole observation and revise any initial interpretation before updating your belief.'

def prompt(row,side,tok,recovery=False):
    user=('Your past belief state was: <belief>No prior information.</belief>\n'
          'Your past action: <action>Read the next sentence.</action>\n'
          'Your past environment feedback: <environment>'+row['sources'][side]['sentence']+'</environment>\n'
          'Update your belief state with this observation. Preserve relevant information. Output only the new belief state.')
    if recovery:user+='\n'+RECOVERY
    return tok.apply_chat_template([dict(role='system',content=INSTRUCTION),dict(role='user',content=user)],
                                  tokenize=False,add_generation_prompt=True,enable_thinking=False)

def reader_prompt(text,question,tok):
    user='Read this memory carefully.\nMemory:\n'+text+'\nQuestion:\n'+question+'\nAnswer only Yes or No.'
    return tok.apply_chat_template([dict(role='system',content=RULE),dict(role='user',content=user)],
                                  tokenize=False,add_generation_prompt=True,enable_thinking=False)

def build(root):
    parent=root.parent/'E96/data-v1.jsonl';rows=[json.loads(line) for line in parent.read_text().splitlines()]
    assert len(rows)==len({r['item_id'] for r in rows})==50
    root.mkdir(exist_ok=True);out=root/'data-v1.jsonl';assert not out.exists();out.write_bytes(parent.read_bytes())
    assert sha(out)==sha(parent)
    report=dict(parent=str(parent),data_sha256=sha(out),pairs=50,source_questions=sum(len(r['questions']) for r in rows),
                writer_code_sha256=sha(Path(__file__)),system=INSTRUCTION,recovery=RECOVERY,
                primary_candidates=8,reference_candidates=2,Source_reaudit=0,GPU=0,API=0,
                scope='Belief-update adaptation, not exact full author pipeline or trained policy reproduction.')
    out.with_suffix('.manifest.json').write_text(json.dumps(report,indent=2)+'\n');print(report)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('operation',choices=['build']);p.add_argument('--root',type=Path,required=True)
    args=p.parse_args();build(args.root)
