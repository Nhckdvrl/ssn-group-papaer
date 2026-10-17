#!/usr/bin/env python3
"""E64 ordinary transmission instructions; identical baseline partner openings."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import native_reciprocal_negotiation as policy


GUIDE = ('If you want the other character to hear words, choose a say, tell, or whisper command. '
         'For an emote or other non-speech action, set utterance to the empty string: '
         'emoting does not transmit that field.')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--baseline', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True); a = ap.parse_args()
    ref = json.loads((a.baseline/'manifest.json').read_text())
    assert (a.baseline/'runtime.json').exists() and not ref['arguments']['profile']
    assert ref['script_sha256'] == hashlib.sha256(Path(policy.__file__).read_bytes()).hexdigest()
    dataset = Path(ref['arguments']['dataset'])
    rows = list(map(json.loads, dataset.read_text().splitlines()))
    seeds = ref['arguments']['seeds']; assert len(rows) == 9
    openings = {}
    for r in map(json.loads, (a.baseline/'episodes.jsonl').read_text().splitlines()):
        key = (r['case_id'], r['seed'])
        if key in openings: assert openings[key] == r['opening']
        openings[key] = r['opening']; assert r['opening'] is not None
    assert len(openings) == 27
    original_identity = policy.identity
    policy.identity = lambda *args: original_identity(*args)+'\n'+GUIDE
    policy.CUES = {'none': ''}

    class FixedOpeningClient(policy.BatchClient):
        def batch(self, jobs):
            if jobs and all(j['stage'] == 'opening' for j in jobs):
                with (a.out/'replayed_openings.jsonl').open('a') as f:
                    for j in jobs:
                        f.write(json.dumps({'case_id': j['case_id'], 'seed': j['episode_seed'],
                            'opening': openings[j['case_id'], j['episode_seed']],
                            'source': str(a.baseline)}, ensure_ascii=False)+'\n')
                return [openings[j['case_id'], j['episode_seed']] for j in jobs]
            return super().batch(jobs)

    a.out.mkdir(parents=True, exist_ok=False)
    manifest = {**ref, 'arguments': {**ref['arguments'], 'out': str(a.out), 'profile': False},
        'source_policy_sha256': ref['script_sha256'],
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'cues': policy.CUES, 'transmission_guide': GUIDE,
        'fixed_opening_source': str(a.baseline), 'opening_replay_count': len(openings),
        'opening_source_raw_sha256': hashlib.sha256((a.baseline/'episodes.jsonl').read_bytes()).hexdigest()}
    (a.out/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    modules = policy.load_event_modules(policy.CACHE/'sources/LIGHT')
    client = FixedOpeningClient(Path(ref['arguments']['model']), a.out, seeds[0])
    start = time.monotonic(); count = 0
    for group in [rows[:1]]+[rows[i:i+3] for i in range(1, len(rows), 3)]:
        count += policy.run_group(group, seeds, client, modules, a.out)
        print(json.dumps({'episodes': count, 'calls': client.calls, 'wall_seconds': time.monotonic()-start}), flush=True)
    assert count == 54
    (a.out/'runtime.json').write_text(json.dumps({'worlds': len(rows), 'episodes': count,
        'calls': client.calls, 'wall_seconds': time.monotonic()-start,
        'model_load_seconds': client.load_seconds, 'replayed_openings': len(openings), 'cloud_calls': 0}, indent=2)+'\n')


if __name__ == '__main__': main()
