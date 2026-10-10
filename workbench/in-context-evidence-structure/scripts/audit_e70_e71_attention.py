"""POST-HOC audit of saved fixed-prefix statistics; D0 prefix is Mark."""
import hashlib
import json
from pathlib import Path
import random
import statistics


def ci(values):
    rng = random.Random(810)
    boots = sorted(statistics.mean(rng.choices(values, k=len(values))) for _ in range(4000))
    return dict(mean=statistics.mean(values), ci95=[boots[100], boots[3899]], n_contexts=len(values))


def main():
    out = {'status': 'POST-HOC; aggregate weights are descriptive, not a native causal decomposition',
           'D0_warning': 'E71 prefix position holds Mark in D0; actual code is at Tag and was not saved.',
           'datasets': {}}
    for sub in ['e70/qwen3_confirmation', 'e71/qwen3_confirmation']:
        path = Path('results') / sub / 'behavior.jsonl'
        rows = [json.loads(x) for x in path.read_text().splitlines()]
        first = rows[0]['attention']
        wanted = ['isolated', 'common', 'shared_frame', 'blind'] if sub.startswith('e70') else [
            'linked.D0', 'linked.D1', 'linked.isolated', 'linked.common', 'linked.shared_frame', 'linked.blind']
        data = {'source_sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'conditions': {}, 'contrasts': {}}
        raw = {}
        for key in wanted:
            if key not in first:
                continue
            nl = len(first[key])
            data['conditions'][key], raw[key] = {}, {}
            for site in ['prefix', 'label']:
                for stat in ['mass', 'within_source']:
                    if site not in first[key]['0']:
                        continue
                    values = [statistics.mean(v for l in range(nl) for v in r['attention'][key][str(l)][site][stat][:4])
                              for r in rows]
                    raw[key][site+'.'+stat] = values
                    data['conditions'][key][site+'.'+stat] = ci(values)
        iso = 'isolated' if sub.startswith('e70') else 'linked.isolated'
        for key in raw:
            if key == iso or iso not in raw:
                continue
            data['contrasts'][key+'.minus_isolated'] = {stat: ci([x-y for x,y in zip(values,raw[iso][stat])])
                                                       for stat,values in raw[key].items()}
        out['datasets'][sub] = data
    dest = Path('results/e70_e71_attention_audit_posthoc.json')
    dest.write_text(json.dumps(out, indent=2))
    print(json.dumps({k: d['conditions'] for k,d in out['datasets'].items()}, ensure_ascii=False))


if __name__ == '__main__':
    main()
