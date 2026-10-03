"""Original Mayn 24 materials. Explicit text migration, never new inference gold."""
import hashlib
import json
from pathlib import Path
import pandas as pd

WORDS = ['triangle', 'circle', 'red', 'green']
SHAPES = {'tr': 'triangle', 'ci': 'circle', 'sq': 'square'}
COLORS = {'re': 'red', 'gr': 'green', 'bl': 'blue'}
CODE = {'tr': 'triangle', 'ci': 'circle', 're': 'red', 'gr': 'green'}
IDENTITY = {'unspecified': 'The speaker is a person.', 'adult': 'The speaker is an adult.',
            'child': 'The speaker is a four-year-old child.'}


def specs(root):
    from run_iqap_queue import models
    selected = [z for z in models() if z[0] in ['Qwen2.5-3B-Instruct', 'Qwen3-4B', 'Qwen3-8B', 'Qwen3-14B',
        'OLMoE-1B-7B-0125-SFT', 'OLMoE-1B-7B-0125-DPO']]
    for manifest, name in [('qwen25-14-stage-manifest.json', 'Qwen2.5-14B-Instruct'),
                           ('mistral-stage-manifest.json', 'Mistral-7B-Instruct-v0.3')]:
        m = next(m for m in json.loads((root/'models'/manifest).read_text()) if m['id'].split('/')[-1] == name)
        selected.append((name, m['id'], m['sha']))
    assert len(selected) == 8 and len({z[0] for z in selected}) == 8
    return selected


def tokenizer_path(root, cp):
    if cp.startswith('OLMoE'): return root/'models/OLMoE-1B-7B-0125-SFT'
    return root/'models'/cp


def descriptor(code):
    s, c = code.split('_')
    return COLORS[c] + ' ' + SHAPES[s]


def prepare(root):
    p = root/'upstream/mayn-speaker-reasoning-2025'
    sha = lambda f: hashlib.sha256(f.read_bytes()).hexdigest()
    audit = json.loads((Path(__file__).resolve().parents[1]/'results/E47-speaker-selection-source-audit.json').read_text())
    assert audit['gate_pass']
    mats, norms = None, {}
    files = {}
    for exp in [1, 2]:
        folder = p/f'experiment{exp}'
        rawfile, exclude = folder/f'exp{exp}_results.csv', folder/f'exp{exp}_exclusion_list.csv'
        for f in [rawfile, exclude]:
            files[f.name] = sha(f)
            assert files[f.name] == audit['mayn'][f'experiment{exp}']['source_sha256'][f.name]
        raw = pd.read_csv(rawfile)
        kept = raw[~raw.participant_id.isin(pd.read_csv(exclude).participant_id)]
        mm = raw[['itemid','itemtype','msg','target','competitor','distractor','condition']].drop_duplicates().sort_values('itemid').to_dict('records')
        if mats is None: mats = mm
        else: assert mm == mats
        assert len(mm) == 24
        for (item, speaker), g in kept.groupby(['itemid','speaker']):
            values = g[['prob_target','prob_competitor','prob_distr']].to_numpy(dtype=float).tolist()
            norms[exp, int(item), speaker] = {'n':len(g), 'mean': [float(g[c].mean()) for c in ['prob_target','prob_competitor','prob_distr']], 'responses': values}
    rows = []
    for r in mats:
        objs = [r[k] for k in ['target','competitor','distractor']]
        for identity in IDENTITY:
            for rotation in range(3):
                roles = [(j+rotation) % 3 for j in range(3)]
                scene = '\n'.join(f'Object {j+1}: {descriptor(objs[k])}.' for j,k in enumerate(roles))
                common = ('In a reference game there are exactly three objects. Both the speaker and the listener see all three.\n'
                    + scene + '\nThe speaker must use exactly one of these four available words to tell the listener which object the speaker means: triangle, circle, red, green.\n'
                    + IDENTITY[identity] + '\n')
                received = CODE[r['msg']]
                question = (f'The listener hears the speaker say "{received}".\n'
                    'Allocate 100 probability points across Object 1, Object 2, and Object 3 for which object the speaker means. '
                    'Reply only with a JSON list of three integers in that order, each from 0 to 100, summing to 100.')
                rows.append(dict(id=f"{r['itemid']}/{identity}/listener/r{rotation}", task='listener', item_id=int(r['itemid']),
                    identity=identity, condition=r['condition'], source=r, rotation=rotation, output_roles=roles,
                    human_norm={str(exp):norms[exp,int(r['itemid']),identity] for exp in [1,2]} if identity != 'unspecified' else {},
                    prompt=common+question))
            # Each possible referent, preserving the original material's role order.
            scene = '\n'.join(f'Object {j+1}: {descriptor(obj)}.' for j,obj in enumerate(objs))
            for target in range(3):
                for order in range(4):
                    words = WORDS[order:]+WORDS[:order]
                    prompt = ('In a reference game there are exactly three objects. Both the speaker and the listener see all three.\n'
                        + scene + '\nThe speaker must use exactly one of these four available words to tell the listener which object the speaker means: triangle, circle, red, green.\n'
                        + IDENTITY[identity] + f'\nThe speaker wants the listener to identify Object {target+1}.\n'
                        + 'Predict the word this speaker would choose. Allocate 100 probability points across '+', '.join(words)
                        + '. Reply only with a JSON list of four integers in that order, each from 0 to 100, summing to 100.')
                    rows.append(dict(id=f"{r['itemid']}/{identity}/speaker/t{target}/o{order}", task='speaker', item_id=int(r['itemid']),
                        identity=identity, condition=r['condition'], source=r, target_role=target, word_order=words,
                        order=order, human_norm={}, prompt=prompt))
    assert len(rows) == len({r['id'] for r in rows}) == 1080
    assert sum(r['task']=='listener' for r in rows) == 216
    return rows, {'source_sha256':files, 'source_items':mats, 'n':len(rows), 'human_filter':'author exclusion lists unchanged',
        'migration':'Text objects and identity; original photographs/practice/history absent. Speaker task is derived, not original human measurement.'}


def parse(text, task):
    try: value = json.loads(text)
    except (ValueError, TypeError): return None
    n = 3 if task == 'listener' else 4
    if not isinstance(value,list) or len(value)!=n or any(type(x) is not int or not 0<=x<=100 for x in value) or sum(value)!=100: return None
    return value


def inputs(tok, rows):
    texts = [tok.apply_chat_template([{'role':'user','content':r['prompt']}],tokenize=False,
        add_generation_prompt=True,enable_thinking=False) for r in rows]
    ids = [tok.encode(t, add_special_tokens=False) for t in texts]
    fingerprint = hashlib.sha256(json.dumps(ids).encode()).hexdigest()
    return texts, ids, fingerprint


if __name__ == '__main__':
    import argparse
    from transformers import AutoTokenizer
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True);ap.add_argument('--output',type=Path,required=True)
    a=ap.parse_args();assert not a.output.exists()
    rows,audit=prepare(a.root)
    assert parse('[0,100,0]','listener') == [0,100,0]
    for invalid in ['[true,99,0]','[0,100,0] explanation','[0,0,0]','[0,101,-1]','[0.0,100,0]']:
        assert parse(invalid,'listener') is None
    assert parse('[0,0,50,50]','speaker') == [0,0,50,50]
    fp={}
    for cp,mid,revision in specs(a.root):
        assert (a.root/'models'/cp/'DOWNLOAD_COMPLETE.json').exists()
        tok=AutoTokenizer.from_pretrained(tokenizer_path(a.root,cp),local_files_only=True)
        texts,ids,h=inputs(tok,rows)
        fp[cp]={'input_token_sha256':h,'max_input_tokens':max(map(len,ids)),'n':len(ids)}
    assert fp['OLMoE-1B-7B-0125-SFT']==fp['OLMoE-1B-7B-0125-DPO']
    out=dict(source_audit=audit,models=fp,parser_gate_pass=True,gate_pass=True,
        helper_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(fp,indent=2))
