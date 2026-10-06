"""Blindly import entire independent pass-2 packets before the primary pass starts."""
import argparse
import json
import os
from pathlib import Path
import time

from data import sha


def import_packets(source, destination, total_batches, safety_margin=16):
    assert json.loads((source/'protocol.json').read_text()) == json.loads((destination/'protocol.json').read_text())
    finished = len(list(destination.glob('p1-*-a0.review.json')))
    # The already-running primary driver cannot share a new lock. Stop well before
    # it can reach pass 2; retain every remaining packet in the independent folder.
    if (destination/'pass1.jsonl').exists() or finished >= total_batches-safety_margin:
        return {'stop': True, 'reason': 'Primary pass 2 approaching or started'}
    imported = 0
    for review in sorted(source.glob('p2-*.review.json')):
        prefix = review.name.removesuffix('.review.json')
        request = source/(prefix+'.request.json')
        report = json.loads(review.read_text())
        assert report['pass_number'] == 2 and sha(request) == report['request_sha256']
        target_request = destination/request.name
        if target_request.exists():
            assert sha(target_request) == sha(request), 'Same packet ID with different request'
            continue  # Primary packet always takes precedence, regardless of labels.
        packets = [request, *sorted(source.glob(prefix+'.response-t*.json')), review]
        if report['status'] == 'complete':
            assert any(sha(p) == report['response_sha256'] for p in packets[1:-1])
        for packet in packets:
            # Atomic publication, review last. Neither interpretation nor status is
            # used to choose a response; schema failures are imported too.
            temporary = destination/(packet.name+'.importing')
            temporary.write_bytes(packet.read_bytes())
            os.link(temporary, destination/packet.name)
            temporary.unlink()
        imported += 1
    return {'stop': False, 'imported_packets': imported, 'primary_pass1_finished_batches': finished}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--total-batches', type=int, required=True)
    parser.add_argument('--watch', action='store_true')
    args = parser.parse_args()
    total = 0
    while True:
        result = import_packets(args.source, args.destination, args.total_batches)
        total += result.get('imported_packets', 0)
        result['total_imported_packets'] = total
        if result.get('imported_packets') or result['stop']: print(json.dumps(result), flush=True)
        (args.destination/'pass2-import-status.json').write_text(json.dumps(result, indent=2)+'\n')
        if not args.watch or result['stop']: break
        time.sleep(10)


if __name__ == '__main__': main()
