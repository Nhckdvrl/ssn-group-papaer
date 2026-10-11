"""Fixed relational features; no query gold, orientation, or donor output."""
import numpy as np

FEATURES = ['intercept', 'demo_order', 'source_match', 'kind_match', 'source_x_kind',
            'demo_label_identity', 'source_x_label', 'kind_x_label']
MODELS = dict(B=[0, 1], R=[0, 1, 2, 3], RJ=[0, 1, 2, 3, 4], RY=list(range(8)))


def features(context, source_flip=False):
    queries, demos = context['queries'][:4], context['demos']
    out = np.empty((len(queries), len(demos), len(FEATURES)), dtype=np.float64)
    for qi, q in enumerate(queries):
        for di, d in enumerate(demos):
            s = 2*int(q['source'] == d['source']) - 1
            if source_flip:
                s = -s
            k = 2*int(q['kind'] == d['kind']) - 1
            y = 2*d['label'] - 1
            out[qi, di] = [1, 2*di/(len(demos)-1)-1, s, k, s*k, y, s*y, k*y]
    return out


def predict(beta, context, source_flip=False):
    # layer, head, query, demonstration
    return np.einsum('lhf,qdf->lhqd', beta, features(context, source_flip))


def prediction_error(target, pred, log_r_tag):
    error = pred - target
    centered_error = error - error.mean(-1, keepdims=True)
    centered_target = target - target.mean(-1, keepdims=True)
    # Label mass conditional on being outside actual code G, not gold-weighted.
    weight = np.exp(log_r_tag).sum(-1)
    return dict(mse=float(np.square(error).mean()),
                allocation_mse=float(np.square(centered_error).mean()),
                target_energy=float(np.square(target).mean()),
                allocation_energy=float(np.square(centered_target).mean()),
                conditional_mass_weighted_mse=float((np.square(error).mean(-1)*weight).sum()/weight.sum()),
                conditional_mass_weighted_allocation_mse=float((np.square(centered_error).mean(-1)*weight).sum()/weight.sum()),
                conditional_mass_weighted_energy=float((np.square(target).mean(-1)*weight).sum()/weight.sum()),
                conditional_mass_weighted_allocation_energy=float((np.square(centered_target).mean(-1)*weight).sum()/weight.sum()))
