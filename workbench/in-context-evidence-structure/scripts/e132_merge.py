"""Merge sharded E132 behaviour files in context order and run the frozen analysis."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e132_cross_source_edges import analyze

for name in sys.argv[1:]:
    dest = Path(name)
    rows = []
    for f in sorted(dest.glob('behavior.shard*.jsonl')):
        rows += [json.loads(x) for x in f.read_text().splitlines()]
    n = json.loads((dest / 'preflight.json').read_text())['args']['n']
    rows.sort(key=lambda r: r['context'])
    assert [r['context'] for r in rows] == list(range(n)), (name, [r['context'] for r in rows])
    (dest / 'behavior.jsonl').write_text(''.join(json.dumps(r) + '\n' for r in rows))
    analyze(dest)
    print('merged', name, len(rows))
