"""Fit all frozen E83 readers on E82 discovery; no selection by behavior."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from e83_reader_features import FEATURES, MODELS, features, prediction_error


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source')
    ap.add_argument('out')
    a = ap.parse_args()
    src, dst = Path(a.source), Path(a.out)
    dst.mkdir(parents=True, exist_ok=True)
    contexts = [json.loads(x) for x in (src/'contexts.jsonl').read_text().splitlines()]
    run = json.loads((src/'run.json').read_text())
    assert len(contexts) == 32 and run['args']['seed'] == 82001
    assert run['source_hashes']['e82_label_query_replay.py'] == '671b3bca5a931a1ee34012007f2e3f42058148140bf06e28329c8ea37be32a5d'
    xx, yy, tt, dataset_hashes = [], [], [], {}
    for ci, c in enumerate(contexts):
        p = src/'native_features'/f'{ci:03d}.npz'
        dataset_hashes[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
        z = np.load(p)
        # Stored shape layer, query, head, receiver, demonstration.
        own, donor = [z[f'D{layout}_label_log_r'][:, :, :, -1, :].transpose(0, 2, 1, 3).astype(np.float64)
                      for layout in (0, 1)]
        x = features(c)
        assert x.shape == (4, 16, 8) and np.isfinite(own).all() and np.isfinite(donor).all()
        xx.append(x.reshape(-1, 8))
        yy.append((donor-own).reshape(own.shape[0]*own.shape[1], -1).T)
        tt.append(own)
    x, y = np.stack(xx), np.stack(yy)
    nl, nh = tt[0].shape[:2]
    def fit(which, indices):
        xf = x[indices][:, :, which].reshape(-1, len(which))
        yf = y[indices].reshape(-1, nl*nh)
        b, _, rank, singular = np.linalg.lstsq(xf, yf, rcond=None)
        assert rank == len(which)
        out = np.zeros((nl, nh, 8), dtype=np.float64)
        out[..., which] = b.T.reshape(nl, nh, len(which))
        return out, float(singular[-1]/singular[0])
    rng = np.random.default_rng(830)
    true = rng.normal(size=(8, 5))
    testx = x.reshape(-1, 8)
    testb = np.linalg.lstsq(testx, testx@true, rcond=None)[0]
    cpu_error = float(np.abs(testb-true).max())
    assert cpu_error < 1e-8
    models, cv, train, ranks = {}, {}, {}, {}
    for name, cols in MODELS.items():
        cv[name] = []
        for fold in range(8):
            selected = np.arange(32)%8 != fold
            b, _ = fit(cols, selected)
            for ci in np.flatnonzero(~selected):
                pred = np.einsum('lhf,qdf->lhqd', b, x[ci].reshape(4,16,8))
                target = y[ci].T.reshape(nl,nh,4,16)
                cv[name].append(dict(context=int(ci), **prediction_error(target, pred, tt[ci])))
        b, rank_ratio = fit(cols, np.ones(32, dtype=bool))
        models[name], ranks[name], train[name] = b, rank_ratio, []
        for ci in range(32):
            pred = np.einsum('lhf,qdf->lhqd', b, x[ci].reshape(4,16,8))
            train[name].append(prediction_error(y[ci].T.reshape(nl,nh,4,16), pred, tt[ci]))
    means = lambda rows: {k: float(np.mean([r[k] for r in rows])) for k in rows[0] if k != 'context'}
    train_means = {k: means(v) for k,v in train.items()}
    assert all(train_means[a]['mse']+1e-10 >= train_means[b]['mse'] for a,b in [('B','R'),('R','RJ'),('RJ','RY')])
    coeff = dst/'coefficients.npz'
    np.savez_compressed(coeff, **models)
    meta = dict(source=str(src.resolve()), source_run=run, n_contexts=32, n_layers=nl, n_heads=nh,
                features=FEATURES, models=MODELS, max_parameters=nl*nh*8, cpu_coefficient_error=cpu_error,
                coefficient_sha256=hashlib.sha256(coeff.read_bytes()).hexdigest(),
                source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in [Path(__file__), Path(__file__).with_name('e83_reader_features.py')]},
                dataset_hashes=dataset_hashes, rank_ratios=ranks, train=train_means,
                cross_validation={k:means(v) for k,v in cv.items()}, cross_validation_rows=cv,
                selection='None: all four prespecified models frozen, no behavioral fitting.',
                weight_definition='Native Tag label probability conditional on outside actual code G.')
    (dst/'metadata.json').write_text(json.dumps(meta, indent=2))
    print(json.dumps({k:meta[k] for k in ['coefficient_sha256','cpu_coefficient_error','max_parameters','cross_validation']}, indent=2))


if __name__ == '__main__':
    main()
