"""LeWM-family world models at configurable scale, plus GPU-resident data.

The objective and predictor/action-encoder/projector modules are the official LeWM ones
(vendor/le-wm module.py, jepa.py); only the encoder is built directly from HF ViTConfig so that
width/depth can be scaled, and pixels are low-resolution arrays held on the GPU.
"""
import math
import os
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from torch import nn

LEWM = Path(__file__).resolve().parents[1] / 'vendor' / 'le-wm'
sys.path.insert(0, str(LEWM))
from module import ARPredictor, Embedder, MLP, SIGReg  # noqa: E402
from jepa import JEPA  # noqa: E402

IMNET_MEAN = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
IMNET_STD = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)

# width -> (enc layers, enc heads); predictor keeps LeWM's 6-layer AdaLN design, all hidden
# sizes scaled by width/192 so that size 'S' (192) is the official LeWM configuration.
SIZES = {
    'XXS': dict(width=64, enc_layers=6, enc_heads=2),
    'XS': dict(width=96, enc_layers=8, enc_heads=3),
    'S': dict(width=192, enc_layers=12, enc_heads=3),
    'M': dict(width=384, enc_layers=12, enc_heads=6),
    'L': dict(width=768, enc_layers=12, enc_heads=12),
}


class HFViT(nn.Module):
    def __init__(self, width, layers, heads, img, patch):
        super().__init__()
        from transformers import ViTConfig, ViTModel
        cfg = ViTConfig(hidden_size=width, num_hidden_layers=layers, num_attention_heads=heads,
                        intermediate_size=4 * width, image_size=img, patch_size=patch,
                        hidden_dropout_prob=0.0, attention_probs_dropout_prob=0.0)
        cfg._attn_implementation = 'sdpa'
        self.vit = ViTModel(cfg, add_pooling_layer=False)

    def forward(self, pixels, interpolate_pos_encoding=True):
        return self.vit(pixel_values=pixels, interpolate_pos_encoding=interpolate_pos_encoding)


def build_model(size, img=64, patch=8, action_dim=10, history=3, latent=None):
    s = SIZES[size]
    w = s['width']
    d = latent or w  # latent (embedding) dim; default = width as in LeWM
    r = w / 192
    enc = HFViT(w, s['enc_layers'], s['enc_heads'], img, patch)
    pred = ARPredictor(num_frames=history, depth=6, heads=16, mlp_dim=int(2048 * r), input_dim=d,
                       hidden_dim=w, output_dim=d, dim_head=max(16, int(64 * r)), dropout=0.1)
    act = Embedder(input_dim=action_dim, emb_dim=d)
    proj = MLP(input_dim=w, output_dim=d, hidden_dim=int(2048 * r), norm_fn=nn.BatchNorm1d)
    pproj = MLP(input_dim=d, output_dim=d, hidden_dim=int(2048 * r), norm_fn=nn.BatchNorm1d)
    return JEPA(enc, pred, act, proj, pproj)


def n_params(m):
    return sum(p.numel() for p in m.parameters())


class GPUData:
    """Windows of `num_steps` frames spaced by `frameskip`; actions concatenated per block."""

    def __init__(self, task, res=64, frameskip=5, num_steps=4, device='cuda', episodes=None,
                 val_frac=0.05, split_seed=0, pixels_on=None):
        root = Path(os.environ.get('LWM_DATA', '/tmp/latent-wm-data/lowres')) / f'{task}_{res}'
        meta = np.load(root / 'meta.npz')
        self.task, self.fs, self.T = task, frameskip, num_steps
        ep_off, ep_len = meta['ep_offset'].astype(np.int64), meta['ep_len'].astype(np.int64)
        n_ep = len(ep_len)
        rng = np.random.default_rng(split_seed)
        perm = rng.permutation(n_ep)
        n_val = int(round(val_frac * n_ep))
        self.val_eps, self.train_pool = np.sort(perm[:n_val]), perm[n_val:]
        train_eps = self.train_pool if episodes is None else np.sort(self.train_pool[:episodes])
        self.train_eps = np.sort(train_eps)
        act = meta['action'].astype(np.float32)
        # action normalizer over the full dataset column (LeWM: column StandardScaler, NaN rows
        # at sequence boundaries are zeroed after normalization)
        self.act_mean, self.act_std = np.nanmean(act, 0), np.nanstd(act, 0) + 1e-6
        span = (num_steps - 1) * frameskip + frameskip  # frames needed incl. last action block
        self.span = span

        def starts(eps):
            out = []
            for e in eps:
                L = ep_len[e]
                if L >= span:
                    out.append(ep_off[e] + np.arange(L - span + 1))
            return np.concatenate(out)

        self.train_starts = torch.as_tensor(starts(self.train_eps), device=device)
        self.val_starts = torch.as_tensor(starts(self.val_eps), device=device)
        need = np.zeros(len(act), dtype=bool)
        for e in np.concatenate([self.train_eps, self.val_eps]):
            need[ep_off[e]:ep_off[e] + ep_len[e]] = True
        px = np.load(root / 'pixels.npy', mmap_mode='r')
        # keep full index space on GPU only for needed episodes: store a remap
        idx = np.nonzero(need)[0]
        remap = -np.ones(len(act), dtype=np.int64)
        remap[idx] = np.arange(len(idx))
        self.remap = torch.as_tensor(remap, device=device)
        pdev = pixels_on or device
        self.pixels = torch.empty((len(idx), res, res, 3), dtype=torch.uint8, device=pdev)
        B = 200_000
        for i in range(0, len(idx), B):
            self.pixels[i:i + B] = torch.from_numpy(np.ascontiguousarray(px[idx[i:i + B]])).to(pdev)
        self.actions = torch.as_tensor(np.nan_to_num((act - self.act_mean) / self.act_std, nan=0.0), device=device)
        self.mean, self.std = IMNET_MEAN.to(device), IMNET_STD.to(device)
        self.device = device
        self.meta = meta

    def n_train_transitions(self):
        return int(len(self.train_starts))

    def batch(self, B, gen, val=False):
        pool = self.val_starts if val else self.train_starts
        s = pool[torch.randint(len(pool), (B,), device=self.device, generator=gen)]
        frame_idx = s[:, None] + torch.arange(self.T, device=self.device)[None] * self.fs  # (B,T)
        px = self.pixels[self.remap[frame_idx]]  # (B,T,H,W,3)
        px = px.permute(0, 1, 4, 2, 3).float().div_(255)
        px = ((px.flatten(0, 1) - self.mean) / self.std).view(B, self.T, 3, px.shape[-2], px.shape[-1])
        a_idx = s[:, None] + torch.arange(self.T * self.fs, device=self.device)[None]
        act = self.actions[a_idx].view(B, self.T, self.fs * self.actions.shape[-1])
        return {'pixels': px, 'action': act}


def add_aux_heads(model, aux, action_dim=10):
    """Attach heads for representative 2026 LeWM follow-up objectives (kept in the model object)."""
    d = model.pred_proj.net[-1].out_features
    if aux == 'idm':  # inverse dynamics on latent pairs (Perception-for-Action / Keeping-Plannable style)
        model.idm_head = MLP(input_dim=2 * d, output_dim=action_dim, hidden_dim=512, norm_fn=nn.LayerNorm)
    return model


def lewm_loss(model, sigreg, batch, history=3, num_preds=1, lambd=0.09, aux='', aux_w=0.1):
    out = model.encode(batch)
    emb, act_emb = out['emb'], out['act_emb']
    ctx_emb, ctx_act = emb[:, :history], act_emb[:, :history]
    tgt = emb[:, num_preds:]
    pred = model.predict(ctx_emb, ctx_act)
    pred_loss = (pred - tgt).pow(2).mean()
    sig = sigreg(emb.transpose(0, 1))
    loss = pred_loss + lambd * sig
    if aux == 'idm':
        act = batch['action'][:, :history]
        a_enc = model.idm_head(torch.cat([emb[:, :-1], emb[:, 1:]], -1).flatten(0, 1)).view_as(act)
        a_pred = model.idm_head(torch.cat([emb[:, :-1], pred], -1).flatten(0, 1)).view_as(act)
        loss = loss + aux_w * ((a_enc - act).pow(2).mean() + (a_pred - act).pow(2).mean())
    elif aux == 'straight':  # temporal straightening: curvature of encoder latent trajectories
        v = emb[:, 1:] - emb[:, :-1]
        cos = F.cosine_similarity(v[:, 1:], v[:, :-1], dim=-1)
        loss = loss + aux_w * (1 - cos).mean()
    elif aux == 'multistep':  # open-loop multi-horizon prediction (RC-aux time axis)
        cur = emb[:, :1]
        ol = []
        for t in range(history):
            p = model.predict(cur[:, -history:], act_emb[:, max(0, t + 1 - history):t + 1])[:, -1:]
            ol.append(p)
            cur = torch.cat([cur, p], 1)
        ol = torch.cat(ol, 1)
        loss = loss + (ol[:, 1:] - emb[:, 2:]).pow(2).mean()
    return loss, pred_loss.detach(), sig.detach(), emb.detach()
