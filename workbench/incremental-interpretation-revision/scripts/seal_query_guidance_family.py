"""E98 interim full registered family, using only complete blind audit phases."""
import argparse
import json
from pathlib import Path
import shutil
from data import sha, write_jsonl
from analyze_query_guidance_fidelity import analyze


def seal(root, model):
    phase = root/'phase-audits-v1'/model
    assert (phase/'step5/summary.json').exists()
    rows = list(map(json.loads, (root/'data-v1.jsonl').read_text().splitlines()))
    runs = [r for r in json.loads((root/'runner-pids-v1.json').read_text()) if r['model'] == model]
    assert {r['shard'] for r in runs} == set(range(runs[0]['shards']))
    for r in runs:
        out = Path(r['out']); cfg = json.loads((out/'config.json').read_text())
        assert cfg['predictions_sha256'] == sha(out/'predictions.jsonl')
    assignments = list(map(json.loads, (phase/'assignments-v1.jsonl').read_text().splitlines()))
    assert {(a['item_id'],a['mode']) for a in assignments} == {(r['item_id'],m) for r in rows for m in ['NATIVE','GOAL','QUESTION_ONLY']}
    needed = {a['audit_id'] for a in assignments}
    previous = list(map(Path, json.loads((root/'finish-pid-v1.json').read_text())['previous']))
    previous.extend(p.parent.parent for p in sorted((root/'phase-audits-v1').glob('*/step5/summary.json')))
    labels, provenance = {}, []
    for parent in previous:
        path = parent/'step5/annotated.jsonl'; assert (parent/'step5/summary.json').exists()
        provenance.append(dict(path=str(parent), annotations_sha256=sha(path), summary_sha256=sha(parent/'step5/summary.json')))
        for z in map(json.loads, path.read_text().splitlines()):
            if z['item_id'] not in needed:
                continue
            if z['item_id'] in labels:
                assert labels[z['item_id']] == z
            labels[z['item_id']] = z
    temp = root/('interim-complete-'+model+'-inputs-v1'); assert not temp.exists(); temp.mkdir()
    shutil.copyfile(root/'data-v1.jsonl', temp/'data-v1.jsonl')
    (temp/'runner-pids-v1.json').write_text(json.dumps(runs, indent=2)+'\n')
    write_jsonl(temp/'assignments-v1.jsonl', assignments)
    (temp/'step5').mkdir(); write_jsonl(temp/'step5/annotated.jsonl', [labels[k] for k in sorted(labels)])
    (temp/'sealed-inputs-v1.json').write_text(json.dumps(dict(model=model, complete_registered_sources=100,
        data_sha256=sha(temp/'data-v1.jsonl'), annotations_sha256=sha(temp/'step5/annotated.jsonl'),
        assignments_sha256=sha(temp/'assignments-v1.jsonl'), audit_provenance=provenance,
        missing_packet_ids=sorted(needed-labels.keys()), no_partial_family=True), indent=2)+'\n')
    filename = 'interim-complete-'+model+'-v1.json'
    analyze(temp, [model], filename)
    dest = root/filename; assert not dest.exists(); shutil.copyfile(temp/filename, dest)
    (root/(filename+'.sealed-inputs.json')).write_text((temp/'sealed-inputs-v1.json').read_text())
    print('E98 complete-family interim',model,sha(dest),flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--root', type=Path, required=True); p.add_argument('--model', required=True)
    a = p.parse_args(); seal(a.root, a.model)
