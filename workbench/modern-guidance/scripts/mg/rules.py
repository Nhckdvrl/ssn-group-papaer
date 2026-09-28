"""Guidance rules: rule(vc, vu, ctx) -> guided velocity. All tensors float32 (B, N, C).

Prediction-level methods follow RevisitingCFGMethods (commit 51cc9ea) pipelines/flux2_klein_base
line by line, re-expressed as velocity rules so every method runs through one sampler.
Flow convention: x0_hat = x - sigma * v,  eps_hat = x + (1 - sigma) * v.
"""
import torch


def _bdot(a, b):
    return (a * b).flatten(1).sum(1)


def _bview(s, ref):
    return s.view(-1, *([1] * (ref.ndim - 1)))


def none():
    return lambda vc, vu, ctx: vc


def uncond():
    return lambda vc, vu, ctx: vu


def cfg(w):
    return lambda vc, vu, ctx: vu + w * (vc - vu)


def cfg_sched(wfn):
    """CFG with a scale that depends on the step: wfn(ctx) -> float or (B,) tensor."""
    def rule(vc, vu, ctx):
        w = wfn(ctx)
        w = _bview(torch.as_tensor(w, device=vc.device, dtype=vc.dtype).expand(vc.shape[0]), vc)
        return vu + w * (vc - vu)
    return rule


def interval(w, lo, hi, w_out=1.0):
    """CFG with scale w only while lo <= sigma <= hi (Kynkaanniemi et al. 2024); w_out elsewhere."""
    return cfg_sched(lambda ctx: w if lo <= ctx["sigma"] <= hi else w_out)


def cfgpp(lam):
    """CFG++ (Chung et al. 2025) in flow/Euler form == CFG with w_t = lam*s(1-s')/(s-s')."""
    def rule(vc, vu, ctx):
        s, sn = ctx["sigma"], ctx["sigma_next"]
        return vu + (lam * s * (1.0 - sn) / (s - sn)) * (vc - vu)
    return rule


def cfg_zero_star(w, zero_steps=2, use_star=True):
    """CFG-Zero* (Fan et al. 2025): zero velocity for the first steps, then rescale vu by
    alpha = <vc, vu> / |vu|^2 (per sample)."""
    def rule(vc, vu, ctx):
        if ctx["i"] < zero_steps:
            return torch.zeros_like(vc)
        if use_star:
            a = _bview(_bdot(vc, vu) / (_bdot(vu, vu) + 1e-8), vu)
            vu = vu * a
        return vu + w * (vc - vu)
    return rule


def apg(w, eta=0.0, momentum=-0.5, radius=0.0):
    """APG (Sadat et al. 2025) exactly as in RevisitingCFGMethods flux2 apg.py (x0 space)."""
    def rule(vc, vu, ctx):
        s = ctx["sigma"]
        x = ctx["x"]
        st = ctx["state"]
        p_c = x - s * vc
        p_u = x - s * vu
        upd = p_c - p_u
        buf = st.get("apg_buf")
        if buf is not None and momentum != 0.0:
            upd = upd + momentum * buf
        st["apg_buf"] = upd
        if radius > 0.0:
            n = _bview(upd.flatten(1).norm(dim=1), upd)
            upd = upd * torch.clamp(radius / n.clamp_min(1e-8), max=1.0)
        unit = p_c / _bview(p_c.flatten(1).norm(dim=1).clamp_min(1e-8), p_c)
        par = _bview(_bdot(upd, unit), upd) * unit
        orth = upd - par
        pg = p_c + (w - 1.0) * (orth + eta * par)
        return (x - pg) / s
    return rule


def tcfg(w, rank=1):
    """TCFG (Kwon et al. 2025) as in RevisitingCFGMethods: project vu onto the top right-singular
    subspace of [vc; vu] (per sample), then CFG."""
    def rule(vc, vu, ctx):
        B = vc.shape[0]
        st = torch.stack((vc, vu), 1).reshape(B, 2, -1)
        _, _, vh = torch.linalg.svd(st, full_matrices=False)
        vk = vh.clone()
        vk[:, rank:, :] = 0.0
        vu_p = ((vu.reshape(B, 1, -1) @ vh.transpose(-2, -1)) @ vk).reshape_as(vu)
        return vu_p + w * (vc - vu_p)
    return rule


def project_to_cfg(base):
    """Ablation: keep only the component of base's correction along delta = vc - vu, i.e.
    replace the method by CFG with its own on-trajectory, per-step, per-sample effective scale."""
    def rule(vc, vu, ctx):
        v = base(vc, vu, ctx)
        d = vc - vu
        par = _bdot(v - vu, d) / _bdot(d, d).clamp_min(1e-12)
        return vu + _bview(par, d) * d
    return rule


def orth_only(base, w):
    """Ablation: constant-w CFG plus base's orthogonal residual (removes base's schedule)."""
    def rule(vc, vu, ctx):
        v = base(vc, vu, ctx)
        d = vc - vu
        g = v - vu
        par = _bdot(g, d) / _bdot(d, d).clamp_min(1e-12)
        return vu + w * d + (g - _bview(par, d) * d)
    return rule


REGISTRY = {
    "none": none, "uncond": uncond, "cfg": cfg, "interval": interval, "cfgpp": cfgpp,
    "cfg0s": cfg_zero_star, "apg": apg, "tcfg": tcfg,
}


def build(spec):
    """spec: dict(name=..., **kwargs, wrap=None|'proj'|('orth', w))."""
    spec = dict(spec)
    name = spec.pop("name")
    wrap = spec.pop("wrap", None)
    r = REGISTRY[name](**spec)
    if wrap == "proj":
        r = project_to_cfg(r)
    elif isinstance(wrap, (list, tuple)) and wrap[0] == "orth":
        r = orth_only(r, wrap[1])
    return r
