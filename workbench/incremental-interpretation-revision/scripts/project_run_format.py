"""Preserve unaffected A scores from a completed run with invalid native token policy."""
import argparse
import json
from pathlib import Path

from data import sha


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True);ap.add_argument('--format',choices=['A','B'],required=True);args=ap.parse_args()
    config=json.loads((args.source/'config.json').read_text())
    assert config.get('predictions_sha256')==sha(args.source/'predictions.jsonl'),'Source must be complete'
    args.out.mkdir(parents=True,exist_ok=True);assert not (args.out/'predictions.jsonl').exists()
    n=0
    with (args.source/'predictions.jsonl').open() as source,(args.out/'predictions.jsonl').open('w') as target:
        for line in source:
            if json.loads(line)['format']==args.format:target.write(line);n+=1
    config.update(format_projection=dict(source=str(args.source),source_config_sha256=sha(args.source/'config.json'),
        source_predictions_sha256=sha(args.source/'predictions.jsonl'),format=args.format,
        rule='Every task of the selected format, no outcome/label filtering'),tasks=n,predictions_sha256=sha(args.out/'predictions.jsonl'))
    config['arguments']['formats']=[args.format]
    # The source bytes are authoritative; projection is not additional GPU work.
    config['source_gpu_hours']=config.pop('gpu_hours',None);config['gpu_hours']=0
    (args.out/'config.json').write_text(json.dumps(config,indent=2)+'\n')
    (args.out/'reading_map.py').write_bytes((args.source/'reading_map.py').read_bytes())
    print(json.dumps(dict(source=str(args.source),format=args.format,tasks=n)))


if __name__=='__main__':main()
