"""Positive/negative controls for lmhead_geom (E01/E02 tool validation). Run: python test_geom.py"""
import torch

from lmhead_geom import (ce_logit_grad_stats, effective_rank, head_basis, leverage, rho_gamma,
                         rho_gamma_from_gh, subspace_cosines)

torch.manual_seed(0)
V, d = 3000, 64
ok = True


def check(name, cond, val=""):
    global ok
    ok &= bool(cond)
    print(f"{'PASS' if cond else 'FAIL'}  {name} {val}")


for label, W in [("full-rank", torch.randn(V, d, dtype=torch.float64)),
                 ("low-rank r=20", torch.randn(V, 20, dtype=torch.float64) @ torch.randn(20, d, dtype=torch.float64))]:
    b = head_basis(W)
    U, S, Rt = torch.linalg.svd(W, full_matrices=False)
    r = int((S > 1e-6 * S[0]).sum())
    check(f"[{label}] numerical rank", b.rank == r, f"{b.rank} vs {r}")
    Ur = U[:, :r]
    g_in = Ur @ torch.randn(r, 5, dtype=torch.float64)                     # in column space
    g_out = torch.randn(V, 5, dtype=torch.float64); g_out -= Ur @ (Ur.T @ g_out)   # orthogonal
    g_mix = g_in + g_out
    rin, _ = rho_gamma(g_in.T, W, b); rout, _ = rho_gamma(g_out.T, W, b); rmix, gmix = rho_gamma(g_mix.T, W, b)
    explicit = ((Ur.T @ g_mix) ** 2).sum(0) / (g_mix ** 2).sum(0)
    check(f"[{label}] rho=1 in col space", torch.allclose(rin, torch.ones(5, dtype=torch.float64), atol=1e-8), f"{rin.min():.10f}")
    check(f"[{label}] rho=0 orthogonal", rout.abs().max() < 1e-8, f"{rout.abs().max():.2e}")
    check(f"[{label}] closed form == explicit U", torch.allclose(rmix, explicit, atol=1e-10))
    r2, g2 = rho_gamma(g_mix.T, 7.0 * W, head_basis(7.0 * W))
    check(f"[{label}] rho scale-invariant, gamma scales", torch.allclose(r2, rmix, atol=1e-10) and torch.allclose(g2, 7 * gmix, rtol=1e-8))
    lev = leverage(W, b)
    check(f"[{label}] sum leverage == rank", abs(lev.sum().item() - r) < 1e-6, f"{lev.sum().item():.6f}")
    z = torch.zeros(1, V, dtype=torch.float64)
    rz, gz = rho_gamma(z, W, b)
    check(f"[{label}] zero gradient undefined (NaN)", torch.isnan(rz).all() and torch.isnan(gz).all())

# CE closed form vs autograd (fp32 logits, fp64 reference)
W = torch.randn(V, d) * 0.05
h = torch.randn(7, d, requires_grad=True)
tgt = torch.randint(0, V, (7,))
logits = h @ W.T
loss = torch.nn.functional.cross_entropy(logits, tgt, reduction="sum")
loss.backward()
g_h, g2, p_a, ent = ce_logit_grad_stats(logits.detach(), tgt, W)
check("CE g_h == autograd dL/dh", torch.allclose(g_h, h.grad, atol=1e-5), f"maxdiff {(g_h - h.grad).abs().max():.2e}")
p = torch.softmax(logits.detach().double(), -1); e = torch.nn.functional.one_hot(tgt, V).double()
check("CE ||g||^2 closed form", torch.allclose(g2, ((p - e) ** 2).sum(-1), atol=1e-10))

# Near-deterministic token (p_a ≈ 1 - 1e-7): stable formula vs FP64 reference
W2s = torch.randn(V, d) * 0.05
hc = torch.zeros(1, d); zc = torch.full((1, V), -20.0); zc[0, 5] = 0.0      # p_a ≈ 1 - (V-1) e^-20
g_hs, g2s, pas, _ = ce_logit_grad_stats(zc, torch.tensor([5]), W2s)
p64 = torch.softmax(zc.double(), -1); e64 = torch.nn.functional.one_hot(torch.tensor([5]), V).double()
ref2 = ((p64 - e64) ** 2).sum(-1); refh = (p64 - e64) @ W2s.double()
check("stable ||g||^2 near p_a=1", torch.allclose(g2s, ref2, rtol=1e-3, atol=0), f"{g2s.item():.3e} vs {ref2.item():.3e}")
check("stable g_h near p_a=1", torch.allclose(g_hs.double(), refh, rtol=1e-3, atol=1e-3 * refh.abs().max().item()))

# Advantage-weighted: c(p-e_a) => rho invariant for c != 0, sign flip only
b = head_basis(W.double())
c = torch.tensor([1.0, -2.0, 0.5, 3.0, -0.1, 1.0, 0.0])
g_hc, g2c, _, _ = ce_logit_grad_stats(logits.detach(), tgt, W, coef=c)
r1, _ = rho_gamma_from_gh(g_h, g2, b); rc, _ = rho_gamma_from_gh(g_hc, g2c, b)
check("rho invariant to nonzero advantage", torch.allclose(r1[:6], rc[:6], atol=1e-6) and torch.isnan(rc[6]))

# Group aggregate with cancellation: +g and -g sum to zero -> undefined
G = torch.stack([g_h[0], -g_h[0]]).sum(0, keepdim=True)
check("cancelling group aggregate has zero g_h", G.abs().max() < 1e-6)

# Principal angles: identical -> all 1; independent random -> small
W1 = W.double(); b1 = head_basis(W1)
cs = subspace_cosines(W1, W1, b1, b1)
check("subspace cosines identical == 1", torch.allclose(cs, torch.ones_like(cs), atol=1e-8))
W2 = torch.randn(V, d, dtype=torch.float64); b2 = head_basis(W2)
cs2 = subspace_cosines(W1, W2, b1, b2)
check("subspace cosines random << 1", cs2.max() < 0.5, f"max {cs2.max():.3f}")
er = effective_rank(torch.ones(10))
check("effective rank of flat spectrum", abs(er["erank"] - 10) < 1e-9 and abs(er["stable_rank"] - 10) < 1e-9)
print("ALL PASS" if ok else "SOME FAILED")
