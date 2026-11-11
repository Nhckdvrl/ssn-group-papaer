"""E189 addendum (11-11, POST-HOC; card section '追加（11-11）'): §7 router logit margins / softmax saturation,
§8 per-layer arrival times of R / H / O (from decomp.json), §9 energy share of xhat_t in readout subspaces.
Node-local: reads /tmp/xiang_e186/hidden/*, e189/decomp.json; writes e189/extra.json."""
import json, os, time
import numpy as np
import torch

torch.set_num_threads(int(os.environ.get("NT", 8)))
BASE = "/tmp/xiang_e186"; OUT = f"{BASE}/e189"
KEYS = ["olmoe0924_s5k", "olmoe0924_s20k", "olmoe0924_s80k", "olmoe0924_s140k", "olmoe0924_s200k",
        "olmoe0924_s260k", "olmoe0924_s320k", "olmoe0924_s1220k", "olmoe0924_main"]
TOKX = [20e9, 83e9, 335e9, 587e9, 838e9, 1.09e12, 1.34e12, 5.1e12]
NK, F, L, E, K = 9, 8, 16, 64, 8
t0 = time.time()
RT = [np.load(f"{BASE}/hidden/{k}/router.npz") for k in KEYS]
W = torch.tensor(np.stack([r["gate"] for r in RT])); G = torch.tensor(np.stack([r["post_attention_layernorm"] for r in RT]))
MM = [np.load(f"{BASE}/hidden/{k}/toksub.npy", mmap_mode="r") for k in KEYS]
q = lambda v: [float(x) for x in np.quantile(v, [.25, .5, .75])]
gen = torch.Generator().manual_seed(18990)
RAND = []
for _ in range(8):
    Q_, R_ = torch.linalg.qr(torch.randn(2048, 63, generator=gen, dtype=torch.float64))
    RAND.append(Q_.float())


def basis(Wm):
    Wc = Wm.double() - Wm.double().mean(0, keepdim=True)
    _, S, Vh = torch.linalg.svd(Wc, full_matrices=False)
    return Vh[: int((S > 1e-6 * S[0]).sum())].T.float()


def share(x, V):
    return float(((x @ V).pow(2).sum(1) / x.pow(2).sum(1)).mean())


res = {"margins": {}, "share": {}}
for l in range(L):
    X = [torch.tensor(np.asarray(MM[k][l], dtype=np.float32)) / G[k, l] for k in range(NK)]
    PF = basis(W[F, l] * G[F, l])
    for t in range(NK):
        We = W[t, l] * G[t, l]
        z = X[t] @ We.T
        zs = z.sort(-1, descending=True).values
        p = torch.softmax(z.double(), -1); ps = p.sort(-1, descending=True).values
        ent = -(p * torch.log2(p.clamp_min(1e-300))).sum(-1)
        res["margins"][f"{l}_{t}"] = {
            "gap12": q((zs[:, 0] - zs[:, 1]).numpy()), "gap89": q((zs[:, 7] - zs[:, 8]).numpy()),
            "p1": q(ps[:, 0].numpy()), "p8sum": q(ps[:, :8].sum(-1).numpy()), "entropy_bits": q(ent.numpy()),
            "logit_sd": q(z.std(-1).numpy()),
            "rownorm_W": float(W[t, l].norm(dim=1).mean()), "rownorm_Weff": float(We.norm(dim=1).mean()),
            "gain_mean": float(G[t, l].abs().mean())}
        Pt = basis(We)
        xc = X[t] - X[t].mean(0, keepdim=True)
        _, _, Vh = torch.linalg.svd(xc[::4].double(), full_matrices=False)
        PC = Vh[:63].T.float()
        r = {"PF": share(X[t], PF), "Pt": share(X[t], Pt), "PF_c": share(xc, PF), "Pt_c": share(xc, Pt)}
        rr = [share(X[t], V) for V in RAND]; rc = [share(xc, V) for V in RAND]
        r["rand"] = [float(np.mean(rr)), float(min(rr)), float(max(rr))]; r["rand_c"] = [float(np.mean(rc)), float(min(rc)), float(max(rc))]
        r["pc_share_c"] = share(xc, PC)
        r["pa_Pt_PC"] = float(torch.linalg.svdvals(Pt.T @ PC).mean())
        r["pa_PF_PC"] = float(torch.linalg.svdvals(PF.T @ PC).mean())
        r["pa_rand_PC"] = float(np.mean([torch.linalg.svdvals(V.T @ PC).mean() for V in RAND]))
        res["share"][f"{l}_{t}"] = r
    print(f"[{time.time() - t0:.0f}s] layer {l}", flush=True)

# §8 per-layer arrival times
D = json.load(open(f"{OUT}/decomp.json"))


def arrival(vals, ch, thr):
    n = [(v - c) / (1 - c) for v, c in zip(vals, ch)]
    lx = np.log10(TOKX)
    if n[0] >= thr:
        return TOKX[0]
    for i in range(1, 8):
        if n[i - 1] < thr <= n[i]:
            f = (thr - n[i - 1]) / (n[i] - n[i - 1])
            return float(10 ** (lx[i - 1] + f * (lx[i] - lx[i - 1])))
    return None


arr = {}
for l in range(L):
    rec = D["layers"][str(l)]["toF"]
    for c in ("O", "H", "R"):
        for i, nm in ((1, "top8"), (0, "top1")):
            for thr in (.5, .8):
                arr[f"{l}_{c}_{nm}_{thr}"] = arrival([rec[t][c][i] for t in range(8)], [rec[t][c + "_chance"][i] for t in range(8)], thr)
res["arrival_layer"] = arr
json.dump(res, open(f"{OUT}/extra.json", "w"))
print("done", round(time.time() - t0))
