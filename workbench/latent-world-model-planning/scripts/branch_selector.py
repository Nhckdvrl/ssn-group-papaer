"""E16 v0 public-only boundary selector; no simulator/outcome/file inputs."""
import numpy as np


def pbb(cost_estimates, actions, terminals, *, k=30, branches=8, seed=0):
    cost = np.asarray(cost_estimates, dtype=float)
    actions = np.asarray(actions).reshape(cost.shape[1], -1)
    terminals = np.asarray(terminals)
    if cost.ndim != 2 or not np.isfinite(cost).all() or branches > cost.shape[1]:
        raise ValueError('Invalid public prediction bank')
    order = np.argsort(cost, axis=1, kind='stable')
    elite = np.zeros(cost.shape, dtype=bool)
    np.put_along_axis(elite, order[:, :k], True, axis=1)
    p = elite.mean(0)
    safe = np.clip(p, 1e-12, 1-1e-12)
    entropy = np.where((p > 0) & (p < 1), -safe*np.log(safe)-(1-safe)*np.log(1-safe), 0)
    cutoff = np.take_along_axis(cost, order[:, k-1:k], axis=1)
    scale = np.maximum(np.quantile(cost, .9, axis=1)-np.quantile(cost, .1, axis=1), 1e-8)
    proximity = (1/(1+np.abs(cost-cutoff)/scale[:, None])).mean(0)
    weight = entropy*proximity
    if weight.sum() == 0:
        ids = np.random.default_rng(seed).choice(cost.shape[1], branches, replace=False)
        return {'score': 0., 'ids': ids, 'elite_probability': p, 'entropy': entropy,
                'fallback': 'uniform, no estimated elite disagreement'}
    center = np.average(terminals, axis=0, weights=weight)
    spread = np.linalg.norm(terminals-center, axis=-1)
    state_score = np.mean(weight)*np.average(spread, weights=weight)
    selected = [int(np.argmax(weight))]
    distance = np.linalg.norm(terminals-terminals[selected[0]], axis=-1)
    for _ in range(branches-1):
        criterion = weight*(distance/(np.mean(distance)+1e-8)+1)
        criterion[selected] = -np.inf
        idx = int(np.argmax(criterion)); selected.append(idx)
        distance = np.minimum(distance, np.linalg.norm(terminals-terminals[idx], axis=-1))
    return {'score': float(state_score), 'ids': np.asarray(selected),
            'elite_probability': p, 'entropy': entropy,
            'action_prefix_spread': float(np.std(actions[selected], axis=0).mean()),
            'fallback': None}
