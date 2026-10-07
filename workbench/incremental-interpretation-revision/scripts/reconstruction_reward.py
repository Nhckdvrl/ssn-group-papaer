"""E91 fixed actual interpretations and source-support labels; no new annotations."""
import argparse
import collections
import json
from pathlib import Path
from data import sha, write_jsonl
from data_v2 import digest


INSTRUCTION = 'Maintain a concise faithful interpretation of observed events.'


def context(row):
    return ('Global Instruction: '+INSTRUCTION+'\n'
            'Your new belief state is: <belief>'+row['interpretation']+'</belief>\n'
            'Your past belief state was: <belief>No prior information.</belief>\n'
            'Your past action: <action>Read the next sentence.</action>\n'
            'Your past environment feedback: <environment>\n')


def prepare(row, tok):
    prefix = context(row)
    text = prefix+row['sentence']
    e = tok(text, add_special_tokens=False, return_offsets_mapping=True)
    positions = [i for i, (a, b) in enumerate(e['offset_mapping']) if b > len(prefix)]
    assert positions and positions[0] > 0
    assert e['offset_mapping'][positions[0]][0] == len(prefix)
    assert e['input_ids'][:positions[0]] == tok.encode(prefix, add_special_tokens=False)
    assert positions == list(range(positions[0], len(e['input_ids'])))
    return dict(row=row, ids=e['input_ids'], target_positions=positions,
                context_sha256=digest(prefix), prompt_sha256=digest(text))


def build(root):
    parent = root.parent/'E70'
    assignments = [json.loads(s) for s in (parent/'assignments-v1.jsonl').read_text().splitlines()]
    packets = {r['item_id']: r for r in map(json.loads, (parent/'packets-v1.jsonl').read_text().splitlines())}
    labels = {r['item_id']: r for r in map(json.loads, (parent/'step5/annotated.jsonl').read_text().splitlines())}
    summary = json.loads((parent/'step5/summary.json').read_text())
    assert summary['complete_both'] == 1280 and summary['unresolved'] == 0
    scope = json.loads((parent/'scope-v1.json').read_text())
    sources = {r['item_id']: r for r in map(json.loads, (root.parent/'E63/sources-v1.jsonl').read_text().splitlines())}
    texts = {}
    for run in scope['runs']:
        if run['experiment'] != 'E64':
            continue
        p = Path(run['path'])
        cfg = json.loads((p/'config.json').read_text())
        assert sha(p/'predictions.jsonl') == cfg['predictions_sha256']
        model = Path(cfg['model_path']).name
        for r in map(json.loads, (p/'predictions.jsonl').read_text().splitlines()):
            if r['reading'] in ('BASE_BANK', 'TARGET_BANK'):
                key = model, r['item_id'], r['reading']
                assert key not in texts
                texts[key] = r
    rows = []
    for a in assignments:
        source = sources[a['source_unit']]
        assert source['sentence_sha256'] == a['sentence_sha256'] == digest(source['sentence'])
        output = texts[a['model'], a['source_unit'], a['operation']]
        text = output['text'].rsplit('</think>', 1)[-1]
        gold = collections.defaultdict(list)
        atom_labels = []
        for q in a['questions']:
            uid = a['atom_packets'].get(q['question_id'])
            label = 'UNKNOWN'
            if uid:
                assert packets[uid]['sentence'] == text
                assert labels[uid]['step5_status'] in ('agreed', 'adjudicated')
                label = labels[uid]['step5_annotation']['label']
                assert label in ('ENTAILED', 'CONTRADICTED', 'NEITHER')
            gold[q['source_gold']].append(label)
            atom_labels.append(dict(question_id=q['question_id'], question=q['text'],
                                    source_gold=q['source_gold'], paraphrase_label=label))
        def mean(g, predicate):
            return sum(predicate(x) for x in gold[g])/len(gold[g]) if gold[g] else None
        pos = mean('Yes', lambda x: x == 'ENTAILED')
        over = mean('No', lambda x: x == 'ENTAILED')
        rows.append(dict(item_id='E91:'+digest(str([a['model'], a['source_unit'], a['operation']])),
                         generator=a['model'], source_unit=a['source_unit'], operation=a['operation'],
                         construction=a['construction'], condition=a['condition'], cluster_id=a['cluster_id'],
                         sentence=source['sentence'], sentence_sha256=a['sentence_sha256'],
                         interpretation=text, interpretation_sha256=digest(text), atoms=atom_labels,
                         positive_retention=pos, unsupported_assertion=over,
                         positive_contradiction=mean('Yes', lambda x: x == 'CONTRADICTED'),
                         positive_omission=mean('Yes', lambda x: x == 'NEITHER'),
                         semantic_fidelity=None if pos is None or over is None else pos-over,
                         unknown_atoms=sum(x['paraphrase_label'] == 'UNKNOWN' for x in atom_labels),
                         unfinished=a['unfinished_thinking'], capped=a['capped']))
    assert len(rows) == 648
    groups = collections.defaultdict(list)
    for r in rows:
        groups[r['generator'], r['source_unit']].append(r)
    assert len(groups) == 324 and all({r['operation'] for r in rs} == {'BASE_BANK', 'TARGET_BANK'} for rs in groups.values())
    root.mkdir(exist_ok=True)
    out = root/'data-v1.jsonl'
    assert not out.exists()
    write_jsonl(out, rows)
    manifest = dict(data_sha256=sha(out), assignments_sha256=sha(parent/'assignments-v1.jsonl'),
                    packets_sha256=sha(parent/'packets-v1.jsonl'), annotation_sha256=sha(parent/'step5/annotated.jsonl'),
                    source_sha256=sha(root.parent/'E63/sources-v1.jsonl'), rows=len(rows), matched_pairs=len(groups),
                    unknown_atoms=sum(r['unknown_atoms'] for r in rows), new_api_calls=0,
                    constructions=dict(collections.Counter(r['construction'] for r in rows)),
                    scope='All E70 completed frozen actual outputs, all source-support atoms retained; no outcome selection.')
    out.with_suffix('.manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print(manifest, flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--root', type=Path, required=True)
    build(p.parse_args().root)
