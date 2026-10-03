"""E51 frozen original E33/E34 contracts, full common SFT tokenizer."""
import argparse
import hashlib
import json
from pathlib import Path
from transformers import AutoConfig, AutoTokenizer
import iqap_data
import circa_pair_data


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def specs(root):
    models = json.loads((root/'models/olmo2-dense-stage-manifest.json').read_text())
    assert [m['stage'] for m in models] == ['Base', 'SFT', 'DPO', 'RLVR']
    assert [m['id'] for m in models] == ['allenai/OLMo-2-1124-13B'+s for s in ['', '-SFT', '-DPO', '-Instruct']]
    assert all(len(m['sha']) == 40 for m in models)
    return models


def common_path(root):
    return root/'models/OLMo-2-1124-13B-SFT'


def prepare(root, tok, task):
    rows = []
    if task == 'iqap':
        source, data_sha = iqap_data.prepare(root)
        audit = {'data_sha256':data_sha, 'n_source_items':len(source),
                 'categories':iqap_data.CATEGORIES, 'targets':iqap_data.TARGETS}
        for interface in ['bare', 'common-chat']:
            for r in source:
                rows.append({'id':r['Item']+'/'+interface, 'source':r, 'interface':interface,
                    'plan':iqap_data.sequences(tok, iqap_data.prompt(r), interface)})
        nulls = {i:iqap_data.sequences(tok, iqap_data.prompt({'Question':'[not provided]', 'Answer':'[not provided]'}), i)
                 for i in ['bare', 'common-chat']}
    else:
        assert task == 'circa'
        source, pairs, audit = circa_pair_data.prepare(root)
        audit = json.loads(json.dumps(audit))
        nulls = {}
        for interface in ['bare', 'common-chat']:
            for order in [0, 1]:
                options = circa_pair_data.CATEGORIES if order == 0 else list(reversed(circa_pair_data.CATEGORIES))
                for r in source:
                    text = circa_pair_data.render(tok, r, order, interface)
                    prefix = tok.encode(text, add_special_tokens=False)
                    ids = [tok.encode(text+str(i), add_special_tokens=False) for i in range(1, 9)]
                    assert all(p[:len(prefix)] == prefix and len(p) > len(prefix) for p in ids)
                    # This source contract scores the complete numeric content, not EOS.
                    plan = {'ids':ids, 'first':len(prefix), 'content_ends':[len(p) for p in ids],
                            'prompt_sha256':hashlib.sha256(text.encode()).hexdigest()}
                    rows.append({'id':r['id']+'/'+interface+'/'+str(order), 'source':r,
                        'interface':interface, 'order':order, 'options':options, 'plan':plan})
        audit = {**audit, 'pairs':pairs}
    assert len(rows) == len({r['id'] for r in rows})
    for r in rows:
        p = r['plan']
        assert 0 < p['first'] < min(map(len, p['ids']))
        assert all(p['first'] < end <= len(ids) < 4096 for ids, end in zip(p['ids'], p['content_ends']))
    return rows, audit, nulls


def fingerprint(rows, nulls):
    return hashlib.sha256(json.dumps({'rows':rows, 'nulls':nulls}, sort_keys=True).encode()).hexdigest()


def dependency_shas():
    return {name:sha(Path(__file__).with_name(name)) for name in ['iqap_data.py', 'circa_pair_data.py']}


if __name__ == '__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--root', type=Path, required=True);ap.add_argument('--output', type=Path, required=True)
    a=ap.parse_args();assert not a.output.exists()
    common=AutoTokenizer.from_pretrained(common_path(a.root), local_files_only=True)
    assert common.chat_template and common.eos_token_id is not None
    vocab=common.get_vocab();native={}
    for m in specs(a.root):
        p=a.root/'models'/m['id'].split('/')[-1]
        tok=AutoTokenizer.from_pretrained(p, local_files_only=True);cfg=AutoConfig.from_pretrained(p, local_files_only=True)
        assert tok.get_vocab() == vocab and tok.special_tokens_map == common.special_tokens_map
        assert cfg.vocab_size > max(vocab.values()) and cfg.max_position_embeddings == 4096
        assert cfg.model_type == 'olmo2'
        native[m['id']]={'revision':m['sha'], 'vocab_size':cfg.vocab_size,
                        'native_chat_template_present':bool(tok.chat_template), 'full_vocab_and_special_tokens_match':True}
    tasks={}
    for task in ['iqap', 'circa']:
        rows, audit, nulls=prepare(a.root, common, task)
        tasks[task]={'n':len(rows), 'source_audit':audit, 'input_sha256':fingerprint(rows, nulls),
            'max_input_and_candidate_tokens':max(len(ids) for r in rows for ids in r['plan']['ids']),
            'content_span_lengths':sorted({end-r['plan']['first'] for r in rows for end in r['plan']['content_ends']})}
    out={'models':specs(a.root), 'native_tokenizers':native, 'tasks':tasks,
         'helper_sha256':sha(Path(__file__)), 'dependency_sha256':dependency_shas(), 'gate_pass':True}
    a.output.write_text(json.dumps(out, indent=2)+'\n')
    print(json.dumps({k:{'n':v['n'], 'max_tokens':v['max_input_and_candidate_tokens']} for k,v in tasks.items()}))
