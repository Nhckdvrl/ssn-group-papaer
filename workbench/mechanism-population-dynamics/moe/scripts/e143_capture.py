"""E143 capture: router inputs and routing choices of a public MoE at UD word positions.

  e143_capture.py KEY        KEY in MODELS below
Per MoE layer: router input h at the last sub-token of each selected anchor word and of the cal words, router weight W.
Checks that topk(h W^T) agrees with the model's own routing in the same forward pass.
Output (NVMe): STORE/KEY/capture.pt ; summary results/e143/capture_KEY.json
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

WB = Path(__file__).resolve().parents[1]
RES = WB / "results/e143"
STORE = Path("/tmp/xiang-moe-20261026/e143")
LOCAL = Path("/tmp/xiang-moe-20261026/models")
HF = Path.home() / ".cache/huggingface/hub"
MODELS = {
    "olmoe0924": Path.home() / "mechpop_cache/hf_olmoe/main",
    "olmoe600k": Path.home() / "mechpop_cache/hf_olmoe/step600000-tokens2516B",
    "olmoe0125": LOCAL / "olmoe0125",
    "qwen15moe": LOCAL / "qwen15moe",
    "dsv2lite": LOCAL / "dsv2lite",
    "granite3b": LOCAL / "granite3b",
    "qwen3moe": next((HF / "models--Qwen--Qwen3-30B-A3B/snapshots").glob("*"), None),
}


def moe_layers(model):
    """[(layer_index, moe_module, gate_weight (E,d), k, own_routing_module, kind)] for routed-MoE layers."""
    out = []
    for i, layer in enumerate(model.model.layers):
        m = getattr(layer, "mlp", None)
        if m is not None and hasattr(m, "gate") and hasattr(m.gate, "weight") and m.gate.weight.dim() == 2 and hasattr(m, "experts"):
            k = m.top_k if hasattr(m, "top_k") else m.gate.top_k
            kind = "deepseek" if type(m.gate).__name__.endswith("MoEGate") else "linear"
            out.append((i, m, m.gate.weight, k, m.gate, kind))
        elif hasattr(layer, "block_sparse_moe"):
            m = layer.block_sparse_moe
            out.append((i, m, m.router.layer.weight, m.router.top_k, m.router, "granite"))
    return out


def word_token_index(offsets, spans):
    """Token index covering the last character of each word span; -1 if that token runs past the word end."""
    ends = np.array([e for _, e in offsets])
    starts = np.array([s for s, _ in offsets])
    res = []
    for s, e in spans:
        cand = np.where((starts <= e - 1) & (ends >= e) & (ends > starts))[0]
        if len(cand) == 0:
            res.append(-1)
            continue
        t = cand[0]
        res.append(int(t) if ends[t] == e else -1)
    return res


def main(key):
    t0 = time.time()
    path = MODELS[key]
    data = json.loads((RES / "passages.json").read_text())
    P, W = data["passages"], data["words"]
    sel, cal = data["sel"], data["cal"]
    want = {n: ("a", r) for r, n in enumerate(sel)}
    want.update({n: ("c", r) for r, n in enumerate(cal)})
    tok = AutoTokenizer.from_pretrained(path)
    model = AutoModelForCausalLM.from_pretrained(path, torch_dtype=torch.bfloat16, device_map="cuda")
    model.eval()
    layers = moe_layers(model)
    L, d = len(layers), model.config.hidden_size
    E, k = layers[0][2].shape[0], layers[0][3]
    Ha = torch.zeros(L, len(sel), d, dtype=torch.float16)
    Hc = torch.zeros(L, len(cal), d, dtype=torch.float16)
    va, vc = torch.zeros(len(sel), dtype=torch.bool), torch.zeros(len(cal), dtype=torch.bool)
    agree = np.zeros(L)
    n_agree = 0
    by_p = {}
    for n in want:
        by_p.setdefault(W[n][0], []).append(n)
    buf = {}

    def pre_hook(li):
        def f(mod, args, kwargs=None):
            buf[li] = (args[0] if args else kwargs["hidden_states"]).detach()
        return f

    def own_hook(li, kind):
        def f(mod, args, out):
            if kind == "linear":
                buf[("own", li)] = out.detach().float().topk(layers[li][3], -1).indices
            elif kind == "deepseek":
                buf[("own", li)] = out[0].detach()
            else:  # granite: forward returns (..., logits)
                buf[("own", li)] = out[-1].detach().float().topk(layers[li][3], -1).indices
        return f

    hooks = []
    for li, (_, m, _, _, own, kind) in enumerate(layers):
        hooks.append(m.register_forward_pre_hook(pre_hook(li), with_kwargs=True))
        hooks.append(own.register_forward_hook(own_hook(li, kind)))
    Wf = [w.detach().float() for _, _, w, _, _, _ in layers]
    dropped = 0
    with torch.no_grad():
        for pid, ns in sorted(by_p.items()):
            enc = tok(P[pid]["text"], return_offsets_mapping=True, return_tensors="pt", truncation=True, max_length=2048)
            offs = enc.pop("offset_mapping")[0].tolist()
            ti = word_token_index(offs, [(W[n][1], W[n][2]) for n in ns])
            model(input_ids=enc["input_ids"].cuda(), attention_mask=enc["attention_mask"].cuda())
            ok = [(n, t) for n, t in zip(ns, ti) if t >= 0]
            dropped += len(ns) - len(ok)
            if not ok:
                continue
            tix = torch.tensor([t for _, t in ok], device="cuda")
            for li in range(L):
                h = buf[li].reshape(-1, d)[tix]
                own = buf[("own", li)].reshape(-1, k)[tix]
                mine = (h.float() @ Wf[li].T).topk(k, -1).indices
                agree[li] += (torch.zeros(len(tix), E, device="cuda").scatter_(1, mine, 1)
                              * torch.zeros(len(tix), E, device="cuda").scatter_(1, own.long(), 1)).sum().item() / k
                hh = h.half().cpu()
                for j, (n, _) in enumerate(ok):
                    s, r = want[n]
                    (Ha if s == "a" else Hc)[li, r] = hh[j]
            n_agree += len(tix)
            for n, _ in ok:
                s, r = want[n]
                (va if s == "a" else vc)[r] = True
            buf.clear()
    for h in hooks:
        h.remove()
    out = STORE / key
    out.mkdir(parents=True, exist_ok=True)
    torch.save({"Ha": Ha, "Hc": Hc, "va": va, "vc": vc, "W": torch.stack([w.cpu() for w in Wf]).half() if len({w.shape for w in Wf}) == 1 else [w.cpu() for w in Wf],
                "k": k, "E": E, "layer_index": [li for li, *_ in layers], "n_layers_total": len(model.model.layers)}, out / "capture.pt")
    summ = {"key": key, "path": str(path), "moe_layers": L, "layer_index": [li for li, *_ in layers],
            "n_layers_total": len(model.model.layers), "E": E, "k": k, "d": d,
            "anchor_valid": int(va.sum()), "anchor_total": len(sel), "cal_valid": int(vc.sum()), "cal_total": len(cal),
            "dropped_alignment": dropped, "routing_agreement_own_vs_topk_hW": (agree / max(n_agree, 1)).tolist(),
            "wall_s": time.time() - t0}
    (RES / f"capture_{key}.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps({k_: v for k_, v in summ.items() if k_ != "routing_agreement_own_vs_topk_hW"}),
          "agree min/mean", float(np.min(summ["routing_agreement_own_vs_topk_hW"])), float(np.mean(summ["routing_agreement_own_vs_topk_hW"])))


if __name__ == "__main__":
    main(sys.argv[1])
