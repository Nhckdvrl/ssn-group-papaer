"""E192 helper: print training args (common.pt) and the tensor keys / sizes of a FLAME Megatron torch_dist checkpoint,
including optimizer-state keys (chained_*), so that the official Adam moments + fp32 master params can be mapped.
usage: e192_inspect.py DIR"""
import os, sys, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from e191_fetch import patch_pickle, PM  # noqa: E402
import torch

d = sys.argv[1]
patch_pickle()
from torch.distributed.checkpoint import FileSystemReader
from torch.distributed.checkpoint.metadata import TensorStorageMetadata
md = FileSystemReader(d).read_metadata()
c = torch.load(os.path.join(d, "common.pt"), map_location="cpu", weights_only=False, pickle_module=PM)
print("common keys:", list(c.keys()))
a = vars(c["args"])
for k in sorted(a):
    if any(s in k for s in ("lr", "decay", "beta", "eps", "clip", "dropout", "moe", "batch", "seq", "init", "seed", "warmup",
                            "iters", "train", "loss", "mask", "reset", "bf16", "fp16", "parallel", "data", "tokeniz", "optim",
                            "grad", "attention", "norm", "position", "rotary", "accumulate", "overlap", "sample")):
        print(f"  {k} = {a[k]!r}"[:300])
for k in c:
    if k not in ("args",):
        v = c[k]
        print("common", k, type(v), (str(v)[:800] if not isinstance(v, dict) else {kk: str(vv)[:300] for kk, vv in v.items()}))
cnt = collections.Counter(); ex = {}
for k, m in md.state_dict_metadata.items():
    if isinstance(m, TensorStorageMetadata):
        p = k.split(".")[0] if k.startswith("chained") else "model"
        sub = ".".join(k.split(".")[:4]) if k.startswith("chained") else "model"
        cnt[sub] += 1; ex.setdefault(sub, []).append((k, tuple(m.size), str(m.properties.dtype)))
    else:
        print("non-tensor", k, type(m), str(m)[:200])
for s, n in cnt.items():
    print(s, n)
    for e in ex[s][:6]:
        print("   ", e)
print("planner/other md fields:", [x for x in dir(md) if not x.startswith("_")])
