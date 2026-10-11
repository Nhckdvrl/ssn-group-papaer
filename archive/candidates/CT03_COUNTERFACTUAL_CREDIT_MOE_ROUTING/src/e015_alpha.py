"""CT03 E01.5 -- alpha-interpolation attribution of the shallow-layer weakness.

Frozen design: docs/E015_DESIGN.md. Nothing here trains anything.

The proxy is exactly linear in alpha (px(a) = a * g^T dh), so its ranking of
candidates is alpha-invariant. Any change in rho across alpha is caused purely
by the exact side becoming more linear -- which is what makes this a clean test
of "finite perturbation" vs "structural".
"""

import argparse, json, random, time
import torch
import torch.nn.functional as F
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

from e01_credit import MODEL, Capture

ALPHAS = [0.125, 0.25, 0.5, 1.0]


@torch.no_grad()
def replay_ce(model, l, H, start, targets, capture_pos=None, chunk=64, **attn_kwargs):
    """Replay layers l+1.. and return (per-position CE, per-layer position-t deltas).

    capture_pos: if not None, also return the hidden state at that position for
    every downstream layer, so the caller can measure how the perturbation drifts
    from its linear response as depth accumulates.
    """
    mm = model.model
    B, T, _ = H.shape
    kw = dict(attn_kwargs)
    pe = kw.get("position_embeddings")
    if pe is not None and pe[0].shape[0] != B:
        kw["position_embeddings"] = (pe[0].expand(B, -1, -1), pe[1].expand(B, -1, -1))
    am = kw.get("attention_mask")
    if am is not None and am.shape[0] != B:
        kw["attention_mask"] = am.expand(B, *am.shape[1:])
    pid = kw.get("position_ids")
    if pid is not None and pid.shape[0] != B:
        kw["position_ids"] = pid.expand(B, -1)

    traj = []
    for layer in mm.layers[l + 1:]:
        H = layer(H, use_cache=False, past_key_values=None, **kw)[0]
        if capture_pos is not None:
            traj.append(H[:, capture_pos].clone())
    Hn = mm.norm(H[:, start:-1])
    tgt = targets[start:]
    out = torch.zeros(B, Hn.shape[1], device=Hn.device, dtype=torch.float32)
    for a in range(0, Hn.shape[1], chunk):
        logits = model.lm_head(Hn[:, a:a + chunk]).float()
        out[:, a:a + chunk] = F.cross_entropy(
            logits.reshape(-1, logits.shape[-1]), tgt[a:a + chunk].repeat(B),
            reduction="none").view(B, -1)
    return out, traj


def depth_drift(traj, n_cand, n_alpha):
    """Per-layer direction/magnitude drift of the actual response away from the
    linear (smallest-alpha) response. Rows: [zero, zero, (c,a) ...]."""
    amin = ALPHAS[0]
    out = []
    for d_layer in traj:                                  # (B, D) at position t
        d = (d_layer - d_layer[0]).float()                # delta vs the zero row
        rec = []
        for c in range(n_cand):
            base = d[2 + c * n_alpha] / amin              # per-unit linear response
            bn = base.norm()
            for ai, a in enumerate(ALPHAS):
                act = d[2 + c * n_alpha + ai] / a
                rec.append((float(F.cosine_similarity(act, base, dim=0)),
                            float(act.norm() / bn) if bn > 0 else float("nan")))
        out.append(rec)
    return out


def run(args):
    torch.manual_seed(args.seed); random.seed(args.seed)
    dev = "cuda"
    tok = AutoTokenizer.from_pretrained(MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL, dtype=torch.float32, attn_implementation="sdpa").to(dev).eval()
    for p in model.parameters():
        p.requires_grad_(False)

    cfg = model.config
    K = cfg.num_experts_per_tok
    assert not cfg.norm_topk_prob
    layers = [int(x) for x in args.layers.split(",")]
    nA = len(ALPHAS)

    ds = load_dataset("HuggingFaceH4/MATH-500", split="test")
    idxs = list(range(len(ds)))
    random.Random(args.seed).shuffle(idxs)

    fout = open(args.out, "w")
    fdrift = open(args.drift_out, "w")
    print("META", json.dumps(dict(model=MODEL, alphas=ALPHAS, layers=layers,
                                 m=args.m, n_problems=args.n_problems,
                                 tok_per_stratum=args.tok_per_stratum)), flush=True)

    done = 0
    for qi in idxs:
        if done >= args.n_problems:
            break
        ex = ds[qi]
        prompt = tok.apply_chat_template([{"role": "user", "content": ex["problem"]}],
                                         tokenize=False, add_generation_prompt=True)
        p_ids = tok(prompt, add_special_tokens=False).input_ids
        s_ids = tok(ex["solution"], add_special_tokens=False).input_ids
        ids = p_ids + s_ids
        if len(ids) > args.max_len or len(s_ids) < args.min_sol:
            continue
        done += 1
        input_ids = torch.tensor([ids], device=dev)
        T = input_ids.shape[1]
        targets = input_ids[0, 1:]
        first = len(p_ids) - 1

        with Capture(model, layers) as cap:
            with torch.enable_grad():
                emb = model.model.embed_tokens(input_ids).detach().requires_grad_(True)
                logits = model(inputs_embeds=emb, use_cache=False).logits
                ce = F.cross_entropy(logits[0, :-1].float(), targets, reduction="none")
                ce[first:].sum().backward()
        base_ce = ce.detach().clone()
        g_shared = {l: cap.mlp_out[l].grad[0].detach().clone() for l in layers}
        mlp_in = {l: cap.mlp_in[l].detach() for l in layers}
        layer_out = {l: cap.layer_out[l].detach() for l in layers}
        attn_kwargs = cap.attn_kwargs
        del logits, ce, emb, cap
        torch.cuda.empty_cache()

        scored = base_ce[first:]
        order = torch.argsort(scored)
        q = max(1, len(order) // 4)
        rng = random.Random(args.seed * 7919 + qi)
        picks = ([(first + int(i), "easy") for i in
                  rng.sample(order[:q].tolist(), min(args.tok_per_stratum, q))]
                 + [(first + int(i), "hard") for i in
                    rng.sample(order[-q:].tolist(), min(args.tok_per_stratum, q))])

        for l in layers:
            moe = model.model.layers[l].mlp
            for ti, (t, stratum) in enumerate(picks):
                x = mlp_in[l][0, t]
                w = F.softmax(moe.gate(x).float(), dim=-1)
                rank = torch.argsort(w, descending=True)
                sel = rank[:K].tolist()
                i_rep = sel[-1]
                boundary = rank[K:K + args.m].tolist()
                far = rank[K + args.m:].tolist()
                random.Random(args.seed * 104729 + qi * 97 + t * 13 + l).shuffle(far)
                cands = ([(j, "boundary") for j in boundary]
                         + [(j, "random") for j in far[:args.m]])

                with torch.no_grad():
                    e_i = moe.experts[i_rep](x) * w[i_rep]
                    dhs = torch.stack([moe.experts[j](x) * w[j] - e_i for j, _ in cands])
                px_base = (dhs.float() @ g_shared[l][t].float()).tolist()

                # rows: [zero, zero(floor probe), then candidate x alpha]
                nC = len(cands)
                patch = torch.zeros(2 + nC * nA, dhs.shape[1], device=dev, dtype=dhs.dtype)
                for c in range(nC):
                    for ai, a in enumerate(ALPHAS):
                        patch[2 + c * nA + ai] = dhs[c] * a
                H = layer_out[l].expand(patch.shape[0], -1, -1).clone()
                H[:, t] += patch

                grab = (args.drift and stratum == "hard" and ti % 4 == 0
                        and l <= args.drift_max_layer and done <= args.drift_problems)
                t0 = time.perf_counter()
                all_ce, traj = replay_ce(model, l, H, t, targets,
                                         capture_pos=t if grab else None, **attn_kwargs)
                torch.cuda.synchronize()
                batch_s = time.perf_counter() - t0

                b_row = all_ce[0]
                dL_seq = (all_ce - b_row).sum(dim=1)
                dL_tok = all_ce[:, 0] - b_row[0]
                floor_seq, floor_tok = float(dL_seq[1]), float(dL_tok[1])

                for c, (j, pool) in enumerate(cands):
                    for ai, a in enumerate(ALPHAS):
                        r = 2 + c * nA + ai
                        px = px_base[c] * a
                        ds_ = float(dL_seq[r])
                        fout.write(json.dumps(dict(
                            q=qi, layer=l, pos=t, stratum=stratum, pool=pool,
                            alpha=a, i=i_rep, j=j, w_i=float(w[i_rep]), w_j=float(w[j]),
                            rank_j=int((rank == j).nonzero()[0]),
                            base_ce=float(base_ce[t]),
                            dh_norm=float(dhs[c].norm()) * a,
                            dL_seq=ds_, dL_tok=float(dL_tok[r]),
                            px_shared=px, px_base=px_base[c],
                            lin_ratio=(ds_ / px) if px != 0 else float("nan"),
                            floor_seq=floor_seq, floor_tok=floor_tok,
                            batch_s=batch_s, n_rows=int(patch.shape[0]),
                        )) + "\n")
                if grab and traj:
                    dr = depth_drift(traj, nC, nA)
                    fdrift.write(json.dumps(dict(
                        q=qi, layer=l, pos=t, n_cand=nC, alphas=ALPHAS,
                        pools=[p for _, p in cands],
                        depth=[{"rel_depth": di + 1, "abs_layer": l + 1 + di,
                                "cos_lin": [c for c, _ in rec],
                                "norm_ratio": [n for _, n in rec]}
                               for di, rec in enumerate(dr)])) + "\n")
                fout.flush()
        fdrift.flush()
        print(f"[{done}/{args.n_problems}] q={qi} T={T}", flush=True)
        del g_shared, mlp_in, layer_out
        torch.cuda.empty_cache()
    fout.close(); fdrift.close()


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="results/e015_records.jsonl")
    ap.add_argument("--drift-out", dest="drift_out", default="results/e015_drift.jsonl")
    ap.add_argument("--layers", default="1,3,5,7,15")
    ap.add_argument("--m", type=int, default=6)
    ap.add_argument("--n-problems", dest="n_problems", type=int, default=24)
    ap.add_argument("--tok-per-stratum", dest="tok_per_stratum", type=int, default=4)
    ap.add_argument("--max-len", dest="max_len", type=int, default=640)
    ap.add_argument("--min-sol", dest="min_sol", type=int, default=64)
    ap.add_argument("--drift", type=int, default=1)
    ap.add_argument("--drift-problems", dest="drift_problems", type=int, default=8)
    ap.add_argument("--drift-max-layer", dest="drift_max_layer", type=int, default=7)
    ap.add_argument("--seed", type=int, default=0)
    run(ap.parse_args())
