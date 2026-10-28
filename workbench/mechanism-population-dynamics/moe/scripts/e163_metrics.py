"""First-answer full-vocabulary KL with the inherited E155/E162 reduction."""
import torch


def first_token_KL(reference,current):
    if reference.ndim!=1 or reference.shape!=current.shape or reference.dtype!=torch.float32 or current.dtype!=torch.float32:
        raise ValueError('Expected matching one-position FP32 log-probability vectors')
    # Match the original product precision and the FP64 summation exactly.
    return float((reference.exp()*(reference-current)).double().sum())
