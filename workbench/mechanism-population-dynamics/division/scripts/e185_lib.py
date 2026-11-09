"""E185 shared machinery: floor-corrected (conditional) mutual information on per-token routing stores.

Card: division/experiments/E185-routing-variance-atlas.md.  Reads ~/mechpop_cache/e18{0,2,4} (read-only).
I_hat(e;X)   = I_plugin(e;X)   - mean_r I_plugin(e; pi_r X)        (global permutation of X, 3 draws, seed 185)
I_hat(e;X|S) = I_plugin(e;X|S) - mean_r I_plugin(e; pi^S_r X | S)  (permutation of X inside each S stratum)
X values with < 3 occurrences (inside the view) are pooled into one 'rare' bucket; strata S are never pooled.
"""
import json
import numpy as np

CACHE = "/home/xiang/mechpop_cache"
SEED = 185
NSHUF = 3
RARE = 3
BANDS = {"qwen3": ((list(range(0, 4)) + list(range(44, 48))), list(range(7, 35))),
         "qwen3base": ((list(range(0, 4)) + list(range(44, 48))), list(range(7, 35))),
         "gptoss": ([0, 1, 22, 23], list(range(4, 18))),
         "olmoe": ([0, 1, 14, 15], list(range(2, 12)))}
HF = {"qwen3": "Qwen/Qwen3-30B-A3B", "qwen3base": "Qwen/Qwen3-30B-A3B-Base",
      "gptoss": "openai/gpt-oss-20b", "olmoe": "allenai/OLMoE-1B-7B-0125-Instruct"}
NAMES = {"qwen3": "Qwen3-30B-A3B", "qwen3base": "Qwen3-30B-A3B-Base", "gptoss": "GPT-OSS-20B",
         "olmoe": "OLMoE-1B-7B-0125-Inst"}


# ---------------------------------------------------------------- entropy helpers
def H_keys(keys):
    """plug-in entropy (bits) of an int64 key array."""
    n = keys.size
    if n == 0:
        return 0.0
    mx = int(keys.max())
    if mx < 20_000_000:
        c = np.bincount(keys)
        c = c[c > 0]
    else:
        _, c = np.unique(keys, return_counts=True)
    c = c.astype(np.float64)
    return float(np.log2(n) - (c * np.log2(c)).sum() / n)


def dense(x):
    """dense int64 codes 0..n-1 of an arbitrary int array."""
    _, inv = np.unique(x, return_inverse=True)
    return inv.astype(np.int64).ravel()


def pool_rare(codes, k=RARE):
    c = np.bincount(codes)
    rare = c[codes] < k
    out = codes.copy()
    out[rare] = -1
    return dense(out)


def pair(a, b):
    return dense(a.astype(np.int64) * (int(b.max()) + 1) + b)


def shuffle_within(x, s, rng):
    """permute x inside each stratum of s."""
    stable = np.argsort(s, kind="stable")
    rnd = np.lexsort((rng.random(s.size), s))
    out = np.empty_like(x)
    out[stable] = x[rnd]
    return out


# ---------------------------------------------------------------- factor plans
class Plan:
    """Precomputed codes for one token view. marg[name] / cond[name] -> dict with codes on the view's subset."""

    def __init__(self, view_idx):
        self.idx = view_idx                    # int64 indices of tokens in this view
        self.marg, self.cond = {}, {}
        self.rng = np.random.default_rng(SEED)

    def add_marg(self, name, x, sub=None):
        """x: factor over all tokens; sub: optional bool mask over all tokens (factor defined only there)."""
        idx = self.idx if sub is None else self.idx[sub[self.idx]]
        X = pool_rare(dense(x[idx]))
        sh = [X[self.rng.permutation(X.size)] for _ in range(NSHUF)]
        self.marg[name] = dict(idx=idx, X=X, HX=H_keys(X), nX=int(X.max()) + 1, sh=sh)

    def add_cond(self, name, x, s, sub=None):
        idx = self.idx if sub is None else self.idx[sub[self.idx]]
        S = dense(s[idx])
        X = pool_rare(dense(x[idx]))
        SX = pair(S, X)
        shs = [pair(S, shuffle_within(X, S, self.rng)) for _ in range(NSHUF)]
        # fraction of tokens in strata with >= 2 occurrences (coverage of the conditional estimate)
        cs = np.bincount(S)
        cov = float((cs[S] >= 2).mean())
        self.cond[name] = dict(idx=idx, S=S, SX=SX, HS=H_keys(S), HSX=H_keys(SX),
                               nS=int(S.max()) + 1, nSX=int(SX.max()) + 1, sh=shs, cov=cov)


def mi_marg(e, f, E):
    """e: expert ids on f['idx'] tokens (top-1) or (n, K) slots. returns (I_hat, I_plugin, floor_sd, H(e))."""
    if e.ndim == 2:
        K = e.shape[1]
        ee = e.reshape(-1).astype(np.int64)
        rep = lambda a: np.repeat(a, K)
    else:
        ee = e.astype(np.int64)
        rep = lambda a: a
    He = H_keys(ee)
    I = He + f["HX"] - H_keys(rep(f["X"]) * E + ee)
    fl = [He + f["HX"] - H_keys(rep(x) * E + ee) for x in f["sh"]]
    return I - float(np.mean(fl)), I, float(np.std(fl)), He


def mi_cond(e, f, E, HSe_cache=None):
    if e.ndim == 2:
        K = e.shape[1]
        ee = e.reshape(-1).astype(np.int64)
        rep = lambda a: np.repeat(a, K)
    else:
        ee = e.astype(np.int64)
        rep = lambda a: a
    HSe = H_keys(rep(f["S"]) * E + ee)
    I = HSe - f["HS"] - H_keys(rep(f["SX"]) * E + ee) + f["HSX"]
    fl = [HSe - f["HS"] - H_keys(rep(x) * E + ee) + f["HSX"] for x in f["sh"]]
    return I - float(np.mean(fl)), I, float(np.std(fl)), H_keys(ee)


def tokclass_table(model):
    """token_class code for every vocab id: 1 let, 2 non, 3 frag, 4 apos, 5 empty, plus decoded strings."""
    import os, sys
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    sys.path.insert(0, os.path.dirname(__file__))
    from e182_common import token_class
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(HF[model])
    V = max(len(tok), tok.vocab_size)
    strs = [tok.decode([i]) for i in range(V)]
    code = {"let": 1, "non": 2, "frag": 3, "apos": 4, "empty": 5}
    cls = np.array([code[token_class(s)] for s in strs], np.int8)
    return tok, strs, cls


def jdump(path, obj):
    def conv(o):
        if isinstance(o, (np.floating,)):
            return float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.ndarray):
            return o.tolist()
        raise TypeError(type(o))
    with open(path, "w") as f:
        json.dump(obj, f, default=conv, ensure_ascii=False)
