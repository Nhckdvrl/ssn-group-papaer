"""Full-vocabulary summary for the Gemma E123 runs, with the same readouts as e123_wave_report.output_metrics."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from e123_wave_report import output_metrics

for dest in map(Path, sys.argv[1:]):
    raw = [json.loads(x) for x in (dest / 'behavior.jsonl').read_text().splitlines()]
    pre = json.loads((dest / 'preflight.json').read_text())
    (dest / 'full_output_summary.json').write_text(json.dumps(output_metrics(raw, pre), indent=2) + '\n')
    print('wrote', dest)
