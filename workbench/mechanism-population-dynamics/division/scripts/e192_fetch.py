"""E192: fetch a FLAME-MoE Megatron torch_dist checkpoint from the HF hub with HTTP range requests (e191_fetch.py), either
model tensors only (anchors) or model + distributed-optimizer state (fp32 master params, Adam exp_avg / exp_avg_sq) for the
training start points.  --full writes _fetched_full.json, which e192_train.load_official checks.
usage: e192_fetch.py --repo CMU-FLAME/FLAME-MoE-290M-1.3B --iter iter_0001080 --out /tmp/xiang_e192/ckpt [--full]"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e191_fetch  # noqa: E402

if __name__ == "__main__":
    full = "--full" in sys.argv
    if full:
        sys.argv.remove("--full")
        e191_fetch.want = lambda fqn: not fqn.startswith(("rng_state", "rerun")) and "_extra_state" not in fqn
    e191_fetch.main()
    if full:
        a = sys.argv; d = os.path.join(a[a.index("--out") + 1], a[a.index("--iter") + 1])
        json.dump(json.load(open(os.path.join(d, "_fetched.json"))), open(os.path.join(d, "_fetched_full.json"), "w"))
