"""Seam-overlap AR rollout (OVL_MODE=regen|clamp, OVL_W=overlap width) for HY-WorldPlay (E27 ported; source patch of _ar_rollout_inner, vendor tree untouched).

Standard: chunks start at 0,4,8,... Overlap: chunks start at 0,3,6,... (last start clamped to F-4); the latents a
chunk shares with already-kept output are re-generated from fresh noise and then restored to the kept version,
so every new latent is generated at chunk position >= 1. WorldPlay rebuilds the context of each chunk from
latents outside the chunk, so the overlapped latent is never in its own context.
"""
import inspect
import os
import textwrap

import torch

from hyvideo.pipelines import worldplay_video_pipeline as wvp


MODE = os.environ.get("OVL_MODE", "regen")  # regen: re-generate overlap from noise; clamp: pin it to the kept
# latent; ctx: pin it AND keep it in the chunk's clean context (so the chunk/context seam carries no pose change)
WIDTH = int(os.environ.get("OVL_W", "1"))  # latents shared with the previous chunk


def _starts(F, nb=4, w=None):
    w = WIDTH if w is None else w
    out = [0]
    while out[-1] + nb < F:
        out.append(min(out[-1] + nb - w, F - nb))
    return out


def install():
    raw = inspect.getsource(wvp.HunyuanVideo_1_5_Pipeline._ar_rollout_inner)
    src = textwrap.dedent(raw)
    off = len(raw) - len(raw.lstrip(" "))  # indentation removed by dedent (method level)

    def d(t):  # dedent an anchor/replacement written with the original (in-class) indentation
        return "\n".join(ln[off:] if ln.startswith(" " * off) else ln for ln in t.split("\n"))
    rep = [
        ("        for chunk_i in range(self.chunk_num):\n",
         "        _starts = _ovl_starts(latents.shape[2], self.chunk_latent_frames)\n"
         "        _kept_end = 0\n"
         "        for chunk_i, _cs in enumerate(_starts):\n"
         "            _nk0 = max(0, _kept_end - _cs)\n"),
        ("                selected_frame_indices = sorted(list(set(selected_frame_indices)))\n",
         "                selected_frame_indices = sorted(list(set(selected_frame_indices)))\n"
         "                if _OVL_MODE == 'ctx':\n"
         "                    selected_frame_indices = sorted(set(selected_frame_indices) | set(range(_cs, _cs + _nk0)))\n"),
        ("                to_remove = list(\n                    range(\n"
         "                        current_frame_idx, current_frame_idx + self.chunk_latent_frames\n",
         "                to_remove = list(\n                    range(\n"
         "                        current_frame_idx + (_nk0 if _OVL_MODE == 'ctx' else 0),"
         " current_frame_idx + self.chunk_latent_frames\n"),
        ("current_frame_idx = (\n                    chunk_i * self.chunk_latent_frames\n                )",
         "current_frame_idx = _cs"),
        ("            start_idx = chunk_i * self.chunk_latent_frames\n"
         "            end_idx = chunk_i * self.chunk_latent_frames + self.chunk_latent_frames\n",
         "            start_idx = _cs\n"
         "            end_idx = _cs + self.chunk_latent_frames\n"
         "            _nk = max(0, _kept_end - start_idx)\n"
         "            _keep = latents[:, :, start_idx:start_idx + _nk].clone()\n"
         "            if _nk:\n"
         "                latents[:, :, start_idx:start_idx + _nk] = torch.randn_like(_keep)\n"),
        ("                for i, t in enumerate(timesteps):\n",
         "                _eps = torch.randn_like(_keep)\n"
         "                for i, t in enumerate(timesteps):\n"
         "                    if _nk and _OVL_MODE in ('clamp', 'ctx'):\n"
         "                        _sg = float(t) / 1000.0\n"
         "                        latents[:, :, start_idx:start_idx + _nk] = (1 - _sg) * _keep + _sg * _eps\n"),
    ]
    rep = [(d(a), d(b)) for a, b in rep]
    for a, b in rep:
        assert a in src, f"patch anchor not found: {a[:60]!r}"
        src = src.replace(a, b, 1)
    # restore the kept latents after each chunk's denoising loop: insert before the next chunk iteration
    anchor = "        return latents\n"
    lines = src.split("\n")
    # find the line that closes the per-chunk body: the last statement inside the for-loop is the progress-bar
    # update; we append the restore at the end of the loop body by locating the loop's indentation level.
    out, in_loop = [], False
    for i, ln in enumerate(lines):
        ind = " " * (8 - off)
        if ln.startswith(ind + "for chunk_i, _cs in enumerate(_starts):"):
            in_loop = True
        elif in_loop and ln.startswith(ind) and not ln.startswith(ind + " ") and ln.strip():
            out.append(ind + "    if _nk:")
            out.append(ind + "        latents[:, :, start_idx:start_idx + _nk] = _keep")
            out.append(ind + "    _kept_end = end_idx")
            in_loop = False
        out.append(ln)
    src = "\n".join(out)
    assert "_kept_end = end_idx" in src, "failed to place restore block"
    ns = dict(vars(wvp))
    ns["_ovl_starts"] = _starts
    ns["torch"] = torch
    ns["_OVL_MODE"] = MODE
    exec(compile(src, "<wp_overlap>", "exec"), ns)
    wvp.HunyuanVideo_1_5_Pipeline._ar_rollout_inner = ns["_ar_rollout_inner"]
    return src
