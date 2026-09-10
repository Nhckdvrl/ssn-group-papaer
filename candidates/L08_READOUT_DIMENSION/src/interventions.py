"""Compression/intervention families, all applied as reversible context managers.

The point of this module is that the SAME protocol x depth x content factorial can be
run against several intervention families.  The literature's evidence that compression
damages reasoning selectively is almost always a comparison between ranking-scored
knowledge/classification benchmarks and generation-scored reasoning benchmarks; if
that comparison is confounded, it is confounded for every family, not just for readout
truncation.

Families:
  readout   halve the final hidden->vocabulary readout (the parent's intervention);
            changes nothing about the model's computation
  prune     global magnitude pruning of all transformer linear weights; removes
            parameters and therefore changes the computation
  quant     round-to-nearest weight-only quantization of all transformer linear
            weights to n bits, per-output-channel scale; the standard PTQ baseline
"""
from __future__ import annotations

import torch


def _linear_modules(model):
    skip = ("lm_head",)
    for name, mod in model.named_modules():
        if isinstance(mod, torch.nn.Linear) and not name.endswith(skip):
            if "layers." in name:                 # transformer blocks only
                yield name, mod


class NoOp:
    def __enter__(self): return self
    def __exit__(self, *e): pass


class MagnitudePrune:
    """Zero the globally smallest `frac` of transformer linear weights."""

    def __init__(self, model, frac=0.5):
        self.model, self.frac, self.saved = model, frac, {}

    def __enter__(self):
        mods = list(_linear_modules(self.model))
        # global threshold from a bounded subsample: torch.quantile caps input size,
        # and a few million weights estimate the quantile to well within precision
        per = max(1, 4_000_000 // max(1, len(mods)))
        sample = torch.cat([m.weight.detach().abs().flatten()[::97][:per]
                            for _, m in mods]).float()
        thr = torch.quantile(sample, self.frac).to(mods[0][1].weight.dtype)
        for name, m in mods:
            self.saved[name] = m.weight.detach().to("cpu", copy=True)
            m.weight.data[m.weight.data.abs() < thr] = 0
        self.threshold = float(thr)
        return self

    def __exit__(self, *e):
        for name, m in _linear_modules(self.model):
            if name in self.saved:
                m.weight.data.copy_(self.saved[name].to(m.weight.device))
        self.saved.clear()


class RTNQuantize:
    """Weight-only round-to-nearest quantization to `bits`, per output channel."""

    def __init__(self, model, bits=3):
        self.model, self.bits, self.saved = model, bits, {}

    def __enter__(self):
        q = 2 ** (self.bits - 1) - 1
        for name, m in _linear_modules(self.model):
            w = m.weight.data
            self.saved[name] = w.detach().to("cpu", copy=True)
            s = w.abs().amax(dim=1, keepdim=True).clamp(min=1e-8) / q
            m.weight.data.copy_(torch.round(w / s).clamp(-q - 1, q) * s)
        return self

    def __exit__(self, *e):
        for name, m in _linear_modules(self.model):
            if name in self.saved:
                m.weight.data.copy_(self.saved[name].to(m.weight.device))
        self.saved.clear()


def make(model, family, level, mask_mode="first"):
    """level: readout -> keep fraction; prune -> pruned fraction; quant -> bits."""
    if family == "none":
        return NoOp()
    if family == "readout":
        from src.readout import ReadoutTruncation, build_mask
        return ReadoutTruncation(
            model, build_mask(model.config.hidden_size, mask_mode, level))
    if family == "prune":
        return MagnitudePrune(model, level)
    if family == "quant":
        return RTNQuantize(model, int(level))
    raise ValueError(family)
