"""E106 null-new-belief baseline; pinned E103 observations and original scorer."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
from data import sha, write_jsonl
from data_v2 import digest
from current_open_baseline import MODELS, tokenizer
from reconstruction_reward import prepare
from gpu_deadline import ensure_gpu_allowed


def build(root, launch):
    ensure_gpu_allowed()
    parent = root.parent/'E103'; original = parent/'data-v1.jsonl'
    assert sha(original) == '387f20470b08b24c70f43d1b99b9fa00a3f18b72c04980a06fbfd1c89f072666'
    pairs = list(map(json.loads, original.read_text().splitlines()))
    rows = [dict(r['sources']['gp'], item_id=r['item_id'], generator='NO_NEW_BELIEF',
        operation='NO_NEW_BELIEF', interpretation='No prior information.') for r in pairs]
    assert len(rows) == 50
    root.mkdir(exist_ok=True); data = root/'data-v1.jsonl'; assert not data.exists()
    write_jsonl(data, rows)
    manifest = dict(data_sha256=sha(data), E103_data_sha256=sha(original), sources=50,
        null_belief='No prior information.', new_scores=150, new_P=0, new_API=0,
        builder_sha256=sha(Path(__file__)), baseline_is_not_a_quality_candidate=True)
    data.with_suffix('.manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    runs = json.loads((parent/'runner-pids-v1.json').read_text())
    for model in MODELS:
        tok = tokenizer(root.parent/'models'/model); by_id = {}
        for run in [r for r in runs if r['model'] == model]:
            out = Path(run['out']); cfg = json.loads((out/'config.json').read_text())
            assert cfg['predictions_sha256'] == sha(out/'predictions.jsonl')
            for p in map(json.loads, (out/'predictions.jsonl').read_text().splitlines()):
                if p['candidate'] == 0:
                    by_id[p['item_id']] = p
        for r in rows:
            assert digest(r['sentence']) == r['sentence_sha256']
            task = prepare(r, tok)
            assert [task['ids'][i] for i in task['target_positions']] == by_id[r['item_id']]['scores']['target_ids']
        print('E106 null baseline preflight', model, len(rows), flush=True)
    if launch:
        launch_runs = []
        for model, gpu in zip(MODELS, [0, 1, 4]):
            ensure_gpu_allowed()
            out = root/'runs-v1'/model/'0'; log = root/('run-v1-'+model+'.log')
            args = [sys.executable, str(Path(__file__).with_name('run_reconstruction_reward.py')),
                '--root', str(root), '--model', str(root.parent/'models'/model), '--out', str(out),
                '--gpu', str(gpu), '--shard', '0', '--shards', '1']
            with log.open('w') as f:
                p = subprocess.Popen(args, stdout=f, stderr=subprocess.STDOUT, start_new_session=True,
                    env=dict(os.environ, CUDA_VISIBLE_DEVICES=str(gpu), HF_HUB_OFFLINE='1', TRANSFORMERS_OFFLINE='1', HF_ENDPOINT='https://hf-mirror.com'))
            launch_runs.append(dict(model=model, gpu=gpu, shard=0, shards=1, out=str(out), log=str(log), pid=p.pid))
        (root/'runner-pids-v1.json').write_text(json.dumps(launch_runs, indent=2)+'\n')
        print('E106 launched', [(r['gpu'],r['pid']) for r in launch_runs], flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('--root', type=Path, required=True); p.add_argument('--launch', action='store_true')
    a = p.parse_args(); build(a.root, a.launch)
