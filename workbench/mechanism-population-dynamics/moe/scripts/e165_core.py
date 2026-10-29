"""Native OLMoE source assembly and calibration; original forward is retained."""
from contextlib import contextmanager
import copy
import hashlib
import json

import numpy as np
import torch
from torch import nn

from e164_routing import RoutingEngine, permute_trace


def blocks(models):
    return [[layer.mlp for layer in m.model.layers] for m in models]


def assemble(models, original, case):
    dense, gate, expert = case
    target = models[dense]
    for i, layer in enumerate(target.model.layers):
        template = original[dense][i]
        block = copy.copy(template)
        for name in ('_modules', '_parameters', '_buffers', '_forward_hooks', '_forward_pre_hooks'):
            setattr(block, name, copy.copy(getattr(template, name)))
        block.gate = original[gate][i].gate
        block.experts = nn.ModuleList(list(original[expert][i].experts))
        layer.mlp = block
    return target


def restore(models, original):
    for model, group in zip(models, original):
        for layer, block in zip(model.model.layers, group):
            layer.mlp = block


@contextmanager
def restricted(model, keep):
    keep = torch.as_tensor(np.asarray(keep).copy(), dtype=torch.bool,
                           device=next(model.parameters()).device)
    layers = model.model.layers
    if keep.shape != (len(layers), layers[0].mlp.num_experts):
        raise ValueError('Incorrect native gate mask')
    if (keep.sum(-1) < layers[0].mlp.top_k).any():
        raise ValueError('Pool smaller than routing width')
    handles = []
    try:
        for i, layer in enumerate(layers):
            def mask(module, args, output, i=i):
                if output.ndim != 2 or output.shape[-1] != keep.shape[1]:
                    raise ValueError('Native OLMoE gate interface changed')
                return output.masked_fill(~keep[i][None, :], -torch.inf)
            handles.append(layer.mlp.gate.register_forward_hook(mask))
        yield
    finally:
        for handle in handles:
            handle.remove()


@contextmanager
def zero_moe(model):
    handles = []
    try:
        def zero(module, args, output):
            if not isinstance(output, tuple) or len(output) != 2:
                raise ValueError('Expected original OLMoE output tuple')
            return torch.zeros_like(output[0]), output[1]
        for layer in model.model.layers:
            handles.append(layer.mlp.register_forward_hook(zero))
        yield
    finally:
        for handle in handles:
            handle.remove()


class StopAtGate(Exception):
    pass


@torch.no_grad()
def greedy(model, sequences, pad, keep_count=16, batch_size=2):
    layers = model.model.layers
    experts = layers[0].mlp.num_experts
    keep = np.ones((len(layers), experts), bool)
    probabilities = np.empty_like(keep, dtype=np.float64)
    counts = []
    device = next(model.parameters()).device
    for index in range(len(layers)):
        total = np.zeros(experts, np.float64); tokens = 0
        for start in range(0, len(sequences), batch_size):
            rows = sequences[start:start+batch_size]; length = max(map(len, rows))
            ids = torch.full((len(rows), length), pad, dtype=torch.long, device=device)
            valid = torch.zeros_like(ids, dtype=torch.bool)
            for i, seq in enumerate(rows):
                ids[i, :len(seq)] = torch.as_tensor(np.asarray(seq, dtype=np.int64), device=device)
                valid[i, :len(seq)] = True
            captured = []
            def collect(module, args, output):
                prob = output.float().softmax(-1).reshape(len(rows), length, experts)
                captured.append((prob.double()*valid[:, :, None]).sum((0, 1)).cpu().numpy())
                raise StopAtGate()
            with restricted(model, keep):
                handle = layers[index].mlp.gate.register_forward_hook(collect)
                try:
                    model(input_ids=ids, attention_mask=valid, use_cache=False,
                          output_router_logits=False, return_dict=True)
                    raise RuntimeError('Calibration did not stop at target gate')
                except StopAtGate:
                    pass
                finally:
                    handle.remove()
            if len(captured) != 1:
                raise ValueError('Expected one calibration capture')
            total += captured[0]; tokens += int(valid.sum())
        if tokens <= 0:
            raise ValueError('Empty calibration population')
        probabilities[index] = total/tokens
        chosen = np.argsort(-total, kind='stable')[:keep_count]
        keep[index] = False; keep[index, chosen] = True; counts.append(tokens)
    assert np.all(keep.sum(-1) == keep_count)
    return keep, probabilities, counts


def hook_fingerprint(model):
    counts = [(len(m._forward_pre_hooks), len(m._forward_hooks)) for m in model.modules()]
    return {'modules': len(counts), 'sha256': hashlib.sha256(json.dumps(counts).encode()).hexdigest(),
            'total_pre': sum(x[0] for x in counts), 'total_post': sum(x[1] for x in counts)}


def sequences(a, question):
    return [a['test_ids'][a['test_offsets'][4*question+i]:a['test_offsets'][4*question+i+1]]
            for i in range(4)]


def calibration(a, subject):
    return [a['cal_ids'][a['cal_offsets'][i]:a['cal_offsets'][i+1]]
            for i in np.flatnonzero(a['cal_subject'] == subject)]
