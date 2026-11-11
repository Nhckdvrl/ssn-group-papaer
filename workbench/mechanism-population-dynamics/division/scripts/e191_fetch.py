"""E191 (card: division/experiments/E191-flame-early-trajectory-decomposition.md): fetch only the bf16 MODEL tensors of a
FLAME-MoE Megatron torch_dist checkpoint from the HF hub, without Megatron and without the optimizer state.
  1. curl .metadata / common.pt / metadata.json of the iter;
  2. unpickle .metadata with a stub for megatron classes (MCoreSavePlan), list storage items of non-optimizer tensors;
  3. create sparse local .distcp files of full size and fill only those byte ranges with HTTP range requests.
The result loads with torch.distributed.checkpoint (FileSystemReader) on CPU.  usage:
  e191_fetch.py --repo CMU-FLAME/FLAME-MoE-290M-1.3B --iter iter_0000540 --out /tmp/xiang_flame/290m"""
import argparse, collections, concurrent.futures as cf, json, os, pickle, subprocess, sys, time


class _Stub:
    def __init__(self, *a, **k): self.__dict__.update(k)

    def __setstate__(self, st):
        if isinstance(st, dict): self.__dict__.update(st)


class StubUnpickler(pickle.Unpickler):
    def find_class(self, mod, name):
        try:
            return super().find_class(mod, name)
        except Exception:
            return type(name, (_Stub,), {})


def patch_pickle():
    """torch.distributed.checkpoint uses pickle.load for .metadata; megatron classes are stubbed."""
    pickle.load = lambda f, *a, **k: StubUnpickler(f, *a, **k).load()


class PM:                      # pickle_module for torch.load(common.pt)
    Unpickler = StubUnpickler
    load = staticmethod(lambda f, **k: StubUnpickler(f).load())


def want(fqn):
    return not fqn.startswith(("chained_", "rng_state", "rerun")) and "_extra_state" not in fqn


def curl(url, out, rng=None):
    cmd = ["curl", "-sL", "--max-time", "900", "-o", out, url]
    if rng: cmd[1:1] = ["-r", rng]
    return subprocess.run(cmd).returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True); ap.add_argument("--iter", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--workers", type=int, default=12)
    a = ap.parse_args()
    t0 = time.time()
    d = os.path.join(a.out, a.iter); os.makedirs(d, exist_ok=True)
    url = f"https://huggingface.co/{a.repo}/resolve/main/{a.iter}"
    for f in (".metadata", "common.pt", "metadata.json"):
        if not os.path.exists(os.path.join(d, f)):
            assert curl(f"{url}/{f}", os.path.join(d, f)) == 0, f
    patch_pickle()
    from torch.distributed.checkpoint import FileSystemReader
    md = FileSystemReader(d).read_metadata()
    items, fsize = [], collections.Counter()
    for idx, si in md.storage_data.items():
        fsize[si.relative_path] = max(fsize[si.relative_path], si.offset + si.length)
        if want(idx.fqn): items.append((si.relative_path, si.offset, si.length))
    items.sort(); ranges = []
    for p, o, l in items:            # merge ranges closer than 1 MB
        if ranges and ranges[-1][0] == p and ranges[-1][1] + ranges[-1][2] >= o - (1 << 20):
            r = ranges[-1]; r[2] = max(r[1] + r[2], o + l) - r[1]
        else:
            ranges.append([p, o, l])
    done_f = os.path.join(d, "_fetched.json")
    if os.path.exists(done_f):
        print("already fetched", a.iter); return
    for p, sz in fsize.items():
        fp = os.path.join(d, p)
        if not os.path.exists(fp) or os.path.getsize(fp) < sz:
            with open(fp, "ab") as f: f.truncate(sz)

    def get(r):
        p, o, l = r; tmp = os.path.join(d, f".part_{p}_{o}")
        for _ in range(5):
            if curl(f"{url}/{p}", tmp, f"{o}-{o + l - 1}") == 0 and os.path.getsize(tmp) == l: break
        else:
            return False
        with open(os.path.join(d, p), "r+b") as f, open(tmp, "rb") as g:
            f.seek(o); f.write(g.read())
        os.remove(tmp); return True
    with cf.ThreadPoolExecutor(a.workers) as ex:
        ok = list(ex.map(get, ranges))
    assert all(ok), f"{ok.count(False)} ranges failed"
    json.dump({"repo": a.repo, "iter": a.iter, "n_ranges": len(ranges), "bytes": sum(r[2] for r in ranges),
               "wall_s": time.time() - t0}, open(done_f, "w"))
    print(f"[{time.time() - t0:.0f}s] fetched {a.iter}: {len(ranges)} ranges, {sum(r[2] for r in ranges) / 1e9:.2f} GB", flush=True)


if __name__ == "__main__":
    main()
