"""Two source interpretations share E83's exact frozen coefficients."""
import copy
import numpy as np
from e83_reader_features import predict, prediction_error


def predict_all(beta, context, use_code=False):
    predictions = []
    for q in context['queries']:
        qc = dict(q)
        if use_code:
            qc['source'] = qc['code'] ^ context['code_permutation']
        view = dict(context, queries=[qc])
        predictions.append(predict(beta, view))
    return np.concatenate(predictions, axis=2)


def prediction_scopes(target, pred, tag):
    return {name: prediction_error(target[:,:,indices],pred[:,:,indices],tag[:,:,indices])
            for name,indices in [('natural',slice(0,4)),('conflict',slice(4,8))]}


def output_components(z, signs):
    aa,bb,ab,ba = z[...,0:2],z[...,2:4],z[...,4:6],z[...,6:8]
    sign = signs[...,0:2]
    return dict(field=sign*(aa+ab-ba-bb)/4,code=sign*(aa+ba-ab-bb)/4,
                interaction=sign*(aa+bb-ab-ba)/4,common=(aa+bb+ab+ba)/4)
