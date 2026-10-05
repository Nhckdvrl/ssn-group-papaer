"""Combine disjoint E01 family jobs after complete inference and hash checks."""
import argparse
import hashlib
import json
from pathlib import Path
from transformers import AutoTokenizer
from data import sha, write_jsonl
from stimuli import tasks_jurayj


def combine(data, runs, out):
    assert not out.exists(), 'Immutable combined run'
    configs = []
    rows = []
    families = []
    for run in runs:
        cfg = json.loads((run / 'config.json').read_text())
        assert cfg['predictions_sha256'] == sha(run / 'predictions.jsonl')
        rr = list(map(json.loads, (run / 'predictions.jsonl').read_text().splitlines()))
        assert cfg['task_count'] == len(rr) and cfg['experiment'] == 'E01'
        assert cfg['data_sha256'] == sha(data) and len(cfg['families']) == 1
        families += cfg['families']
        configs.append(cfg)
        rows += rr
    assert len(families) == 3 and set(families) == {'NPZ', 'NPS', 'MVRR'}
    common = ('model_manifest', 'dtype', 'torch', 'transformers', 'cuda', 'softmax',
              'attention', 'system_frame', 'frozen', 'thinking', 'seed', 'batch_size', 'code_sha256', 'git_commit')
    for key in common:
        assert all(c[key] == configs[0][key] for c in configs), key
    choices = [{k: sorted(v) for k, v in c['choice_token_ids'].items()} for c in configs]
    assert all(c == choices[0] for c in choices)
    t = AutoTokenizer.from_pretrained(configs[0]['model'], local_files_only=True)
    tasks = tasks_jurayj(data, t, 'E01', configs[0]['system_frame'])
    expected = {(r['item_id'], pid): hashlib.sha256(p.encode()).hexdigest() for r, pid, p in tasks}
    actual = {(r['item_id'], r['prompt_id']): r['prompt_sha256'] for r in rows}
    assert len(actual) == len(rows) == len(expected) and actual == expected
    rows.sort(key=lambda r: (r['item_id'], r['prompt_id']))
    out.mkdir(parents=True)
    write_jsonl(out / 'predictions.jsonl', rows)
    cfg = dict(experiment='E01', task_count=len(rows), data_sha256=sha(data),
               predictions_sha256=sha(out / 'predictions.jsonl'), inference_subruns=configs,
               merge_code_sha256=sha(Path(__file__)), disjoint_families=families,
               prompt_hash_coverage_verified=True, choice_token_set_identity_verified=True,
               new_inference_tasks=len(rows), reused_inference_tasks=0,
               gpu_hours=sum(c['gpu_hours'] for c in configs),
               interpretation='Probabilities primary; correctness measures independent model annotation agreement, not human gold or proof of simultaneous parses.')
    (out / 'config.json').write_text(json.dumps(cfg, indent=2) + '\n')
    print('combined', len(rows), 'tasks', flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--runs', nargs=3, type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    combine(a.data, a.runs, a.out)
