"""E55 steps 1-2: is source (annotator) information present at the label anchors, and do the label-reading heads use it?
usage: e55_present_unused.py --model Qwen/Qwen3-8B --out NPZ [--pairs 40 --queries 20]
Saves: anchor residuals at every 4th layer (per pair, from the mixed shared-word prefix), anchor metadata
(annotator role, name, label), log-attention from the answer position to the 16 anchors for every head in layers
>= L/2 (per pair x who x query), and bge cosine similarity between each query and each demo text."""
import argparse, sys
from pathlib import Path
import numpy as np, torch
from transformers import AutoModel, AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from e46_perspective import build, HEAD, WORDS  # noqa


@torch.no_grad()
def bge_embed(texts):
    tok = AutoTokenizer.from_pretrained("BAAI/bge-large-en-v1.5"); m = AutoModel.from_pretrained("BAAI/bge-large-en-v1.5").cuda().eval()
    out = []
    for i in range(0, len(texts), 64):
        x = tok(texts[i:i + 64], padding=True, truncation=True, max_length=256, return_tensors="pt").to("cuda")
        e = m(**x).last_hidden_state[:, 0]; out.append(torch.nn.functional.normalize(e, dim=-1).cpu())
    del m; torch.cuda.empty_cache()
    return torch.cat(out).numpy()


@torch.no_grad()
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model"); ap.add_argument("--out"); ap.add_argument("--pairs", type=int, default=40); ap.add_argument("--queries", type=int, default=20)
    a = ap.parse_args()
    pairs, qs = build(120); pairs = pairs[: a.pairs]; qs = qs[: a.queries]
    demo_texts = [t for p in pairs for t, _ in p["A"] + p["B"]]
    E = bge_embed(demo_texts + qs); Ed, Eq = E[: len(demo_texts)], E[len(demo_texts):]
    tok = AutoTokenizer.from_pretrained(a.model)
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda", attn_implementation="eager").eval()
    L = model.config.num_hidden_layers; H = model.config.num_attention_heads
    layers_res = list(range(0, L + 1, 4)); L0 = L // 2
    enc = lambda s: tok(s, add_special_tokens=False)["input_ids"]
    RES, META, ATT, SIM = [], [], [], []
    di = 0
    for pi, p in enumerate(pairs):
        nA, nB = p["names"]
        blocks = [(t, nA, WORDS["shared"][1 - y], 0, y, di + k) for k, (t, y) in enumerate(p["A"])] + \
                 [(t, nB, WORDS["shared"][1 - y], 1, y, di + 8 + k) for k, (t, y) in enumerate(p["B"])]
        di += 16
        blocks = [blocks[j] for j in p["order"]]
        ids, anchor = enc(HEAD), []
        for t, name, w, role, y, gid in blocks:
            ids += enc(f"Comment: {t}\nAnnotator: {name}\nLabel:"); anchor.append(len(ids)); ids += enc(" " + w) + enc("\n\n")
        hs = model(input_ids=torch.tensor([ids]).cuda(), output_hidden_states=True).hidden_states
        RES.append(np.stack([hs[l][0, anchor].float().cpu().numpy() for l in layers_res]))          # [nL, 16, D]
        META.append([(pi, role, int(name == "Sam"), y, gid) for (_, name, _, role, y, gid) in blocks])
        anc = torch.tensor(anchor)
        for wi in (0, 1):
            name = nA if wi == 0 else nB
            for qi, qt in enumerate(qs):
                full = ids + enc(f"Comment: {qt}\nAnnotator: {name}\nLabel:")
                att = model(input_ids=torch.tensor([full]).cuda(), output_attentions=True).attentions
                ATT.append(np.stack([torch.log(att[l][0, :, -1, anc] + 1e-9).float().cpu().numpy() for l in range(L0, L)]))  # [L-L0, H, 16]
                SIM.append((pi, wi, qi, np.array([float(Ed[g] @ Eq[qi]) for (*_, g) in blocks])))
        print(pi, flush=True)
    np.savez_compressed(a.out, res=np.stack(RES).astype(np.float16), meta=np.array(META), att=np.stack(ATT).astype(np.float16),
                        sim_idx=np.array([s[:3] for s in SIM]), sim=np.stack([s[3] for s in SIM]), layers_res=np.array(layers_res), L0=L0)
    print("done")


if __name__ == "__main__":
    main()
