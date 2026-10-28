"""Restore P/A/B temporary copies without rewriting their frozen provenance."""
import argparse
import hashlib
from pathlib import Path
import socket
import stage_mature_local as stage


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', required=True, type=Path,
                        help='New durable receipt path; existing files are refused.')
    args = parser.parse_args()
    if socket.gethostname() != 'fvcrc20':
        parser.error('The frozen P/A/B execution paths belong to fvcrc20.')
    original = stage.DETAIL
    original_sha = hashlib.sha256(original.read_bytes()).hexdigest()
    receipt = args.receipt.expanduser().resolve()
    summary = receipt.with_suffix('.summary.json')
    if receipt == original.resolve() or receipt.exists() or summary.exists():
        parser.error('Use a new receipt, preserving the original immutable manifest.')
    stage.DETAIL, stage.REPORT = receipt, summary
    stage.main()
    if hashlib.sha256(original.read_bytes()).hexdigest() != original_sha:
        raise RuntimeError('Original immutable manifest changed')
    print('P/A/B restored from canonical public weights; original provenance retained.')


if __name__ == '__main__':
    main()
