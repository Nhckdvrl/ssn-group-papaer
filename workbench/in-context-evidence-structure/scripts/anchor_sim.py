"""E33 readout: similarity of Alex's and Sam's label words (model-internal anchor states + bge embeddings).
usage: anchor_sim.py --model M --out JSON   (bge computed when --model BAAI/bge-large-en-v1.5)"""
import argparse, json, sys
from pathlib import Path
import numpy as np, torch
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_vocabsep import GRADED  # noqa

LW = {"sst": ["negative", "positive"], "mag_nat": ["small", "large"]}
CTX = {"sst": ["Review: the acting is wooden and the plot drags .", "Review: a warm , funny and moving film ."],
       "mag_nat": ["Number: 23", "Number: 71"]}


def words(task, v):
    lw = LW[task]
    return lw if v is None else [w.upper() for w in lw] if v == "CASE" else None if v == "NONCE" else v


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--model"); ap.add_argument("--out"); a = ap.parse_args()
    nonce = json.load(open(Path(__file__).resolve().parents[1] / "data" / "lexicon.json"))["labels"]
    rng = np.random.default_rng(0); nz_pairs = [list(rng.choice(nonce, 2, replace=False)) for _ in range(20)]
    res = {}
    if "bge" in a.model:
        from transformers import AutoModel, AutoTokenizer
        btok = AutoTokenizer.from_pretrained(a.model); bm = AutoModel.from_pretrained(a.model).cuda().eval()

        @torch.no_grad()
        def emb(ws):   # bge: CLS pooling + L2 normalisation
            x = btok(list(ws), padding=True, return_tensors="pt").to("cuda")
            e = bm(**x).last_hidden_state[:, 0].float(); return torch.nn.functional.normalize(e, dim=-1).cpu().numpy()
        for task, lst in GRADED.items():
            for name, v in lst:
                pairs = nz_pairs if v == "NONCE" else [words(task, v)]
                cs = []
                for sv in pairs:
                    E1, E2 = emb(LW[task]), emb([str(w) for w in sv]); cs.append(float(np.mean([E1[k] @ E2[k] for k in (0, 1)])))
                res[f"{task}:{name}"] = {"bge": float(np.mean(cs))}
    else:
        from transformers import AutoModelForCausalLM, AutoTokenizer
        tok = AutoTokenizer.from_pretrained(a.model)
        model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda").eval()
        nL = model.config.num_hidden_layers; layers = {"mid": nL // 2, "two_thirds": (2 * nL) // 3}

        @torch.no_grad()
        def state(task, k, w):
            text = f"{CTX[task][k]}\nLabel: {w}"
            ids = tok(text, return_tensors="pt").input_ids.cuda()
            hs = model(ids, output_hidden_states=True).hidden_states
            return {n: hs[l][0, -1].float().cpu().numpy() for n, l in layers.items()}
        for task, lst in GRADED.items():
            base = [state(task, k, LW[task][k]) for k in (0, 1)]
            for name, v in lst:
                pairs = nz_pairs if v == "NONCE" else [words(task, v)]
                out = {n: [] for n in layers}
                for sv in pairs:
                    for k in (0, 1):
                        s = state(task, k, str(sv[k]))
                        for n in layers:
                            x, y = base[k][n], s[n]; out[n].append(float(x @ y / np.linalg.norm(x) / np.linalg.norm(y)))
                res[f"{task}:{name}"] = {f"cos_{n}": float(np.mean(v_)) for n, v_ in out.items()}
    json.dump(res, open(a.out, "w"), indent=1); print(json.dumps(res)[:400])


if __name__ == "__main__":
    main()
