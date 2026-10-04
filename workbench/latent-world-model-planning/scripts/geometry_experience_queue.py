"""One geometry per independent GPU; both preregistered data conditions."""
import argparse
import gc
from types import SimpleNamespace
import torch
import geometry_experience as g
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--geometry',choices=g.GEOMETRIES,required=True);args=p.parse_args()
 for arm in g.DATA:
  g.train(SimpleNamespace(cache='/tmp/latent-wm-data/E16-base100-trainseed-cache',bank='/tmp/latent-effect-data/20261004-E20-legal-effect-bank44',geometry=args.geometry,arm=arm))
  gc.collect();torch.cuda.empty_cache()
