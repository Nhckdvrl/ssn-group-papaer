"""E101/E102 full three-family maps after sealed E96 semantic labels; CPU only."""
import argparse
from pathlib import Path
import time
from analyze_disambiguation_credit import analyze as regions
from analyze_revision_evidence_oracle import analyze as oracle
from current_open_baseline import MODELS


def finish(cache):
    while not (cache/'E96/complete-map-v1.json').exists():
        time.sleep(20)
    semantic = cache/'E96/modern-native-belief-credit-map-v1.json'
    regions(cache/'E101', MODELS, semantic, 'disambiguation-credit-map-v1.json')
    oracle(cache/'E102', cache/'E101/disambiguation-credit-map-v1.json', semantic,
           'revision-evidence-oracle-map-v1.json')


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cache',type=Path,required=True)
    finish(p.parse_args().cache)
