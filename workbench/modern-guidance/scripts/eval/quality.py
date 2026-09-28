"""Per-image quality / preference / colour statistics and per-prompt diversity for a run directory.

Usage (mg-eval env): python quality.py <run_prompt_dir> [--metrics pick,hps,aes,clip,color,dino]
Writes <run_prompt_dir>/quality.jsonl (one row per image) and diversity.jsonl (one row per prompt).
Resumable: images already scored are skipped.

Metrics
- pick: PickScore_v1 (CLIP-H) image-text logit.
- hps: HPSv2.1 (open_clip ViT-H-14 + HPS_v2.1_compressed.pt).
- aes: LAION improved aesthetic predictor v2 (CLIP ViT-L/14 + linear-MSE MLP), sha256 21dd590f...
- clip: OpenAI CLIP ViT-L/14 image-text cosine x 100.
- color: mean HSV saturation, fraction of near-saturated pixels (S>0.9 and V>0.3), Hasler-Susstrunk
  colourfulness, mean luminance, RMS contrast.
- dino: DINOv2-base CLS embedding; diversity = mean pairwise (1 - cos) across seeds of a prompt.
"""
import argparse
import glob
import json
import os

import numpy as np
import torch
from PIL import Image

MG = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEV = "cuda"


def list_images(root):
    out = []
    for d in sorted(glob.glob(os.path.join(root, "[0-9]" * 5))):
        meta = json.loads(open(os.path.join(d, "metadata.jsonl")).readline())
        for f in sorted(glob.glob(os.path.join(d, "samples", "*.png"))):
            out.append(dict(pidx=int(os.path.basename(d)), seed=int(os.path.basename(f)[:-4]), path=f,
                            prompt=meta["prompt"], tag=meta.get("tag", "")))
    return out


def color_stats(img):
    a = np.asarray(img.convert("RGB")).astype(np.float32) / 255.0
    hsv = np.asarray(img.convert("HSV")).astype(np.float32) / 255.0
    s, v = hsv[..., 1], hsv[..., 2]
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    rg, yb = r - g, 0.5 * (r + g) - b
    colorful = np.sqrt(rg.std() ** 2 + yb.std() ** 2) + 0.3 * np.sqrt(rg.mean() ** 2 + yb.mean() ** 2)
    lum = 0.299 * r + 0.587 * g + 0.114 * b
    return dict(sat_mean=float(s.mean()), sat_hi_frac=float(((s > 0.9) & (v > 0.3)).mean()),
                colorfulness=float(colorful), lum_mean=float(lum.mean()), contrast=float(lum.std()))


class Scorers:
    def __init__(self, metrics):
        self.m = metrics
        if "pick" in metrics:
            from transformers import AutoModel, AutoProcessor
            self.pick_p = AutoProcessor.from_pretrained("laion/CLIP-ViT-H-14-laion2B-s32B-b79K")
            self.pick = AutoModel.from_pretrained("yuvalkirstain/PickScore_v1").eval().to(DEV).half()
        if "hps" in metrics:
            import open_clip
            from huggingface_hub import hf_hub_download
            model, _, pre = open_clip.create_model_and_transforms("ViT-H-14", pretrained=None, precision="amp",
                                                                  device=DEV)
            ck = torch.load(hf_hub_download("xswu/HPSv2", "HPS_v2.1_compressed.pt"), map_location="cpu")
            model.load_state_dict(ck["state_dict"])
            self.hps, self.hps_pre, self.hps_tok = model.eval(), pre, open_clip.get_tokenizer("ViT-H-14")
        if "aes" in metrics or "clip" in metrics:
            import open_clip
            m, _, pre = open_clip.create_model_and_transforms("ViT-L-14", pretrained="openai", device=DEV)
            self.cl, self.cl_pre, self.cl_tok = m.eval(), pre, open_clip.get_tokenizer("ViT-L-14")
            sd = torch.load(os.path.join(MG, "vendor", "aesthetic", "sac+logos+ava1-l14-linearMSE.pth"),
                            map_location="cpu")
            import torch.nn as nn
            mlp = nn.Sequential(nn.Linear(768, 1024), nn.Dropout(0.2), nn.Linear(1024, 128), nn.Dropout(0.2),
                                nn.Linear(128, 64), nn.Dropout(0.1), nn.Linear(64, 16), nn.Linear(16, 1))
            mlp.load_state_dict({k.replace("layers.", ""): v for k, v in sd.items()})
            self.aes = mlp.eval().to(DEV)
        if "dino" in metrics:
            from transformers import AutoImageProcessor, AutoModel
            self.dino_p = AutoImageProcessor.from_pretrained("facebook/dinov2-base")
            self.dino = AutoModel.from_pretrained("facebook/dinov2-base").eval().to(DEV)

    @torch.no_grad()
    def score(self, img, prompt):
        r = {}
        if "pick" in self.m:
            ii = self.pick_p(images=img, return_tensors="pt").to(DEV)
            tt = self.pick_p(text=prompt, padding=True, truncation=True, max_length=77, return_tensors="pt").to(DEV)
            ie = self.pick.get_image_features(pixel_values=ii["pixel_values"].half())
            te = self.pick.get_text_features(**tt)
            ie, te = ie / ie.norm(dim=-1, keepdim=True), te / te.norm(dim=-1, keepdim=True)
            r["pick"] = float(self.pick.logit_scale.exp() * (ie * te).sum())
        if "hps" in self.m:
            x = self.hps_pre(img).unsqueeze(0).to(DEV)
            t = self.hps_tok([prompt]).to(DEV)
            with torch.autocast("cuda"):
                o = self.hps(x, t)
            r["hps"] = float((o["image_features"] @ o["text_features"].T).diag()[0])
        if "aes" in self.m or "clip" in self.m:
            x = self.cl_pre(img).unsqueeze(0).to(DEV)
            ie = self.cl.encode_image(x).float()
            ie = ie / ie.norm(dim=-1, keepdim=True)
            if "aes" in self.m:
                r["aes"] = float(self.aes(ie)[0, 0])
            if "clip" in self.m:
                te = self.cl.encode_text(self.cl_tok([prompt]).to(DEV)).float()
                te = te / te.norm(dim=-1, keepdim=True)
                r["clip"] = float(100 * (ie * te).sum())
        if "color" in self.m:
            r.update(color_stats(img))
        if "dino" in self.m:
            x = self.dino_p(images=img, return_tensors="pt").to(DEV)
            e = self.dino(**x).last_hidden_state[:, 0].float()
            r["_dino"] = (e / e.norm(dim=-1, keepdim=True))[0].cpu().numpy().tolist()
        return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--metrics", default="pick,hps,aes,clip,color,dino")
    a = ap.parse_args()
    metrics = a.metrics.split(",")
    out = os.path.join(a.root, "quality.jsonl")
    done = set()
    if os.path.exists(out):
        done = {(d["pidx"], d["seed"]) for d in map(json.loads, open(out))}
    items = [x for x in list_images(a.root) if (x["pidx"], x["seed"]) not in done]
    if items:
        sc = Scorers(metrics)
        with open(out, "a") as fh:
            for x in items:
                img = Image.open(x["path"]).convert("RGB")
                row = dict(pidx=x["pidx"], seed=x["seed"], tag=x["tag"])
                row.update(sc.score(img, x["prompt"]))
                fh.write(json.dumps(row) + "\n")
    # diversity per prompt from stored DINO embeddings
    rows = [json.loads(l) for l in open(out)]
    by = {}
    for r in rows:
        if "_dino" in r:
            by.setdefault(r["pidx"], []).append(np.asarray(r["_dino"]))
    with open(os.path.join(a.root, "diversity.jsonl"), "w") as fh:
        for p, es in sorted(by.items()):
            if len(es) < 2:
                continue
            E = np.stack(es)
            S = E @ E.T
            iu = np.triu_indices(len(es), 1)
            fh.write(json.dumps(dict(pidx=p, n=len(es), dino_div=float((1 - S[iu]).mean()))) + "\n")


if __name__ == "__main__":
    main()
