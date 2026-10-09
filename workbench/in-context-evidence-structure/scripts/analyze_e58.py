"""E58 preregistered context-held-out ridge probes and paired bootstrap."""
import argparse
import json
from pathlib import Path

import numpy as np
from sklearn.linear_model import Ridge


def interval(x, seed=580, nboot=2000):
    x = np.asarray(x, dtype=float)
    rng = np.random.default_rng(seed)
    b = x[rng.integers(len(x), size=(nboot, len(x)))].mean(1)
    return {"mean": float(x.mean()), "ci95": np.quantile(b, [0.025, 0.975]).tolist(), "n_contexts": len(x)}


def probe_layer(X, sources, labels, ntrain, raw=None, target=None):
    # X [context, anchor, dim]: (base - source-swapped) / 2.
    trainX = X[:ntrain].reshape(-1, X.shape[-1])
    scale = trainX.std(0)
    scale = np.maximum(scale, max(float(np.median(scale)) * 0.01, 1e-6))
    scaled = X / scale
    fit_results, models, shuffled, raw_results = {}, {}, {}, {}
    for label in (0, 1):
        mask = labels[:ntrain] == label
        feats, y = scaled[:ntrain][mask], sources[:ntrain][mask] * 2 - 1
        model = Ridge(alpha=1.0, fit_intercept=False, solver="lsqr", tol=1e-6).fit(feats, y)
        # Null: independently permute the identity of the entire train twin pair.
        null_sign = np.random.default_rng(9580 + label).choice([-1, 1], ntrain)
        null_y = (sources[:ntrain] * 2 - 1) * null_sign[:, None]
        null = Ridge(alpha=1.0, fit_intercept=False, solver="lsqr", tol=1e-6).fit(feats, null_y[mask])
        models[label] = (model, scale)
        scores = model.predict(scaled[ntrain:].reshape(-1, X.shape[-1])).reshape(sources[ntrain:].shape)
        null_scores = null.predict(scaled[ntrain:].reshape(-1, X.shape[-1])).reshape(sources[ntrain:].shape)
        for dest in (0, 1):
            m = labels[ntrain:] == dest
            acc = ((scores >= 0) == sources[ntrain:])[m].reshape(-1, 8).mean(1)
            fit_results[f"{label}_to_{dest}"] = interval(acc)
            shuffled[f"{label}_to_{dest}"] = interval(((null_scores >= 0) == sources[ntrain:])[m].reshape(-1, 8).mean(1))
        within = ((scores >= 0) == sources[ntrain:])[labels[ntrain:] == label].reshape(-1, 8).mean(1)
        cross = ((scores >= 0) == sources[ntrain:])[labels[ntrain:] != label].reshape(-1, 8).mean(1)
        fit_results[f"{label}_gap"] = interval(within - cross)
        if raw is not None:
            center = [raw[:ntrain][labels[:ntrain] == y_].mean(0) for y_ in (0, 1)]
            rawscale = raw[:ntrain].reshape(-1, raw.shape[-1]).std(0)
            rawscale = np.maximum(rawscale, max(float(np.median(rawscale)) * 0.01, 1e-6))
            rawmodel = Ridge(alpha=1.0, fit_intercept=False, solver="lsqr", tol=1e-6).fit(
                (raw[:ntrain][mask] - center[label]) / rawscale, y)
            for dest in (0, 1):
                m = labels[ntrain:] == dest
                rscores = rawmodel.predict((raw[ntrain:][m] - center[dest]) / rawscale)
                raw_results[f"{label}_to_{dest}"] = interval(((rscores >= 0) == sources[ntrain:][m]).reshape(-1, 8).mean(1))
    directions = [X[:ntrain][labels[:ntrain] == y] * (2 * sources[:ntrain][labels[:ntrain] == y] - 1)[:, None]
                  for y in (0, 1)]
    directions = [d.mean(0) for d in directions]
    cos = float(directions[0] @ directions[1] / (np.linalg.norm(directions[0]) * np.linalg.norm(directions[1]) + 1e-12))
    return {"paired_probe": fit_results, "shuffled_probe": shuffled, "raw_probe": raw_results,
            "source_effect_cosine": cos}, models


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("directory")
    ap.add_argument("--transfer", help="Independent confirmation output, evaluated without refit")
    ap.add_argument("--probe-only", action="store_true", help="Analyze E59's compatible real anchor features")
    a = ap.parse_args()
    d = Path(a.directory)
    meta = np.load(d / "metadata.npz")
    sources, labels = meta["source"], meta["label"]
    nt = int(meta["train"])
    out = {"probes": {}, "behavior": {}, "ntrain": nt, "ntest": len(sources) - nt}
    for space in ("residual", "key", "value"):
        data = np.load(d / f"{space}.npy", mmap_mode="r")
        layers = meta["residual_layers"] if space == "residual" else meta["attention_layers"]
        results = {}
        if a.transfer:
            target_meta = np.load(Path(a.transfer) / "metadata.npz")
            target_data = np.load(Path(a.transfer) / f"{space}.npy", mmap_mode="r")
        for li, layer in enumerate(layers):
            base = data[:, 0, li].astype(np.float32)
            X = (base - data[:, 1, li].astype(np.float32)) * 0.5
            result, models = probe_layer(X, sources, labels, nt, raw=base)
            if a.transfer:
                tnt = int(target_meta["train"])
                Xtest = (target_data[tnt:, 0, li].astype(np.float32) - target_data[tnt:, 1, li].astype(np.float32)) * 0.5
                tsources, tlabels = target_meta["source"][tnt:], target_meta["label"][tnt:]
                transfer = {}
                for lab, (model, scale) in models.items():
                    scores = model.predict((Xtest / scale).reshape(-1, Xtest.shape[-1])).reshape(tsources.shape)
                    for dest in (0, 1):
                        m = tlabels == dest
                        transfer[f"{lab}_to_{dest}"] = interval(((scores >= 0) == tsources)[m].reshape(-1, 8).mean(1))
                result["task_and_vocabulary_transfer"] = transfer
            # Positive control: output label identity in the unmodified anchor.
            tr = base[:nt].reshape(-1, base.shape[-1])
            scale = np.maximum(tr.std(0), 1e-6)
            labelclf = Ridge(alpha=1.0, solver="lsqr", tol=1e-6).fit(tr / scale, labels[:nt].reshape(-1))
            pred = labelclf.predict(base[nt:].reshape(-1, base.shape[-1]) / scale).reshape(labels[nt:].shape)
            result["label_probe"] = interval(((pred >= 0.5) == labels[nt:]).mean(1))
            results[int(layer)] = result
            print(space, int(layer), json.dumps(result["paired_probe"]), flush=True)
        out["probes"][space] = results
    if a.probe_only:
        out["run"] = json.loads((d / "run.json").read_text())
        (d / "probe_analysis.json").write_text(json.dumps(out, indent=2))
        return
    rows = [json.loads(line) for line in (d / "behavior.jsonl").read_text().splitlines()]
    conditions = list(rows[0]["scores"])
    margins = {c: np.array([np.array(r["scores"][c]) * r["signs"] for r in rows]) for c in conditions}
    for c in conditions:
        out["behavior"][c] = {"accuracy": interval((margins[c] > 0).mean(1)),
                               "correct_margin": interval(margins[c].mean(1)),
                               "base_minus_condition_margin": interval((margins["base"] - margins[c]).mean(1))}
    denom = (margins["base"] - margins["renamed"]).mean(1)
    for c in ("key", "value", "kv"):
        numer = (margins["base"] - margins[c]).mean(1)
        if denom.mean() > 0.20:
            rng = np.random.default_rng(580)
            ix = rng.integers(len(denom), size=(2000, len(denom)))
            db = denom[ix].mean(1)
            ratios = numer[ix].mean(1) / np.maximum(db, 1e-6)
            out["behavior"][c]["fraction_of_source_swap"] = {"mean": float(numer.mean() / denom.mean()),
                                                                "ci95": np.quantile(ratios, [0.025, 0.975]).tolist()}
        else:
            out["behavior"][c]["fraction_of_source_swap"] = {"undefined": "Mean base-renamed effect <= 0.20 nats"}
    out["run"] = json.loads((d / "run.json").read_text())
    (d / "analysis.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out["behavior"], indent=2))


if __name__ == "__main__":
    main()
