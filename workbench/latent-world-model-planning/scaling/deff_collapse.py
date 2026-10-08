"""E23 (POST-HOC): does closed-loop L2-planning success collapse onto one curve of the latent effective dimension
D_eff across both interventions (model size, SIGReg weight)? TwoRoom, every final checkpoint with a kernel_bound file.
Writes results/E23_deff_collapse.json and results/figs/E23_deff_collapse.png."""
import glob, json, re
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt

R = Path(__file__).resolve().parents[1] / 'results'
rows = []
for f in glob.glob('/home/xiang/.cache/latent-wm-results/scaling/tworoom_*/eval/kbound_model_0060000.json') + glob.glob('/tmp/latent-wm-runs/scaling/tworoom_*/eval/kbound_model_0060000.json'):
    rd = Path(f).parents[1]
    m = re.match(r'tworoom_(XXS|XS|S|M|L)_ep0_s(\d)_st60000(sigreg_w[0-9.]+)?$', rd.name)
    if not m:
        continue
    lam = float(m[3][8:]) if m[3] else 0.09
    if lam < 0.005:  # collapsed regime (P(K>=.5) D_eff ~0.3: not an isotropic embedding)
        continue
    sr = {}
    for off in (25, 50, 75):
        g = rd / 'eval' / f'0060000_off{off}_300x30_n200.json'
        if g.exists():
            sr[off] = json.loads(g.read_text())['success_rate']
    if len(sr) == 3:
        rows.append({'run': rd.name, 'size': m[1], 'lam': lam, 'deff': json.loads(Path(f).read_text())['deff'], **{f'sr{k}': v for k, v in sr.items()}})
out = {'n_runs': len(rows), 'rows': rows}
fig, axes = plt.subplots(1, 3, figsize=(14, 4))
for ax, off in zip(axes, (25, 50, 75)):
    x = np.log10([r['deff'] for r in rows]); y = np.array([r[f'sr{off}'] for r in rows])
    b = np.polyfit(x, y, 1); res = y - np.polyval(b, x); r2 = 1 - res.var() / y.var()
    # does model size add anything once D_eff is known? residual vs size
    sz = np.array([['XXS', 'XS', 'S', 'M', 'L'].index(r['size']) for r in rows])
    out[f'off{off}'] = {'spearman_deff': float(spearmanr(x, y).statistic), 'slope_per_decade_deff': float(b[0]), 'r2': float(r2),
                        'spearman_resid_vs_size': float(spearmanr(sz, res).statistic),
                        'spearman_resid_vs_lambda': float(spearmanr([r['lam'] for r in rows], res).statistic)}
    for lam, mk in [(0.01, 'v'), (0.03, 's'), (0.09, 'o'), (0.27, '^')]:
        sel = [i for i, r in enumerate(rows) if r['lam'] == lam]
        ax.scatter(np.array([rows[i]['deff'] for i in sel]), y[sel], marker=mk, c=sz[sel], cmap='viridis', vmin=0, vmax=4, label=f'SIGReg λ={lam}')
    xx = np.linspace(x.min(), x.max(), 50); ax.plot(10 ** xx, np.polyval(b, xx), 'k--', lw=1)
    ax.set_xscale('log'); ax.set_xlabel('latent effective dimension D_eff'); ax.set_ylabel(f'success, goal offset {off}')
    ax.set_title(f'TwoRoom off{off}: R²={r2:.2f}, ρ={out[f"off{off}"]["spearman_deff"]:.2f}'); ax.grid(alpha=.3)
axes[0].legend(fontsize=7, title='colour = size XXS→L', title_fontsize=7)
fig.tight_layout(); fig.savefig(R / 'figs' / 'E23_deff_collapse.png', dpi=150)
(R / 'E23_deff_collapse.json').write_text(json.dumps(out, indent=1))
print(json.dumps({k: v for k, v in out.items() if k != 'rows'}, indent=1))
