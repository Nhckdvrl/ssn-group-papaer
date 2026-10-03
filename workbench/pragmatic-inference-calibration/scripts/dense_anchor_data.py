"""E52 cached Qwen2.5-14B pair; exactly the E51 original source contracts."""
import argparse
import hashlib
import json
from pathlib import Path
from transformers import AutoTokenizer, AutoConfig
from dense_stage_data import prepare, fingerprint, sha, dependency_shas as parent_shas


def specs(root):
    ms=json.loads((root/'models/qwen25-14-stage-manifest.json').read_text())
    assert [m['id'] for m in ms]==['Qwen/Qwen2.5-14B','Qwen/Qwen2.5-14B-Instruct']
    return [{**m,'stage':stage} for m,stage in zip(ms,['Base','Instruct'])]


def common_path(root):
    return root/'models/Qwen2.5-14B-Instruct'


def dependency_shas():
    return {**parent_shas(),'dense_stage_data.py':sha(Path(__file__).with_name('dense_stage_data.py'))}


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();assert not a.output.exists()
    tok=AutoTokenizer.from_pretrained(common_path(a.root),local_files_only=True)
    natives={}
    for m in specs(a.root):
        p=a.root/'models'/m['id'].split('/')[-1];native=AutoTokenizer.from_pretrained(p,local_files_only=True)
        marker=json.loads((p/'DOWNLOAD_COMPLETE.json').read_text());assert marker['revision']==m['sha'] and marker['model']==m['id']
        assert native.backend_tokenizer.to_str()==tok.backend_tokenizer.to_str()
        assert native.get_vocab()==tok.get_vocab()
        cfg=AutoConfig.from_pretrained(p,local_files_only=True);assert cfg.max_position_embeddings>=4096
        natives[m['id']]={'complete_backend_sha256':hashlib.sha256(native.backend_tokenizer.to_str().encode()).hexdigest(),'match':True,'native_special_tokens_map':native.special_tokens_map,'native_eos_token_id':native.eos_token_id,'common_special_tokens_map':tok.special_tokens_map,'common_eos_token_id':tok.eos_token_id}
    e51=json.loads((Path(__file__).resolve().parents[1]/'results/E51-source-preflight.json').read_text());assert e51['gate_pass']
    tasks={}
    for task in ['iqap','circa']:
        rows,audit,nulls=prepare(a.root,tok,task)
        assert audit==e51['tasks'][task]['source_audit']
        tasks[task]={'source_audit':audit,'n':len(rows),'input_sha256':fingerprint(rows,nulls),
            'max_input_and_candidate_tokens':max(len(ids) for r in rows for ids in r['plan']['ids'])}
    out={'models':specs(a.root),'tasks':tasks,'native_tokenizers':natives,'gate_pass':True,
        'helper_sha256':sha(Path(__file__)),'dependency_sha256':dependency_shas()}
    a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:{'n':v['n'],'max_tokens':v['max_input_and_candidate_tokens']} for k,v in tasks.items()}))
