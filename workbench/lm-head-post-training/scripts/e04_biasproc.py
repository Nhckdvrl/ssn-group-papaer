"""vLLM V1 logits processor that adds one context-independent bias vector to every row of logits.

The vector is read from the npz named by env E04_BIAS (key E04_BIAS_KEY, default 'b'), multiplied by
E04_BIAS_SCALE (default 1). Applied before temperature, so the sampled logits are (z + scale*b)/T.
To realise τ·z + b use T = 1/τ and scale the stored b by 1/τ (done by e04_generate.py)."""
import os

import numpy as np
import torch
from vllm.v1.sample.logits_processor import LogitsProcessor


class GlobalBias(LogitsProcessor):
    def __init__(self, vllm_config, device, is_pin_memory):
        path = os.environ.get("E04_BIAS")
        self.bias = None
        if path:
            b = np.load(path)[os.environ.get("E04_BIAS_KEY", "b")].astype(np.float32)
            b = b * float(os.environ.get("E04_BIAS_SCALE", "1"))
            self.bias = torch.tensor(b, device=device)

    def is_argmax_invariant(self):
        return False

    def update_state(self, batch_update):
        pass

    def apply(self, logits):
        if self.bias is None:
            return logits
        V = min(logits.shape[-1], self.bias.shape[0])
        logits[:, :V] += self.bias[:V].to(logits.dtype)
        return logits


class EntropyGatedTemperature(LogitsProcessor):
    """Multiply a row's logits by E04_GATE_TAU only where that row's entropy (at T=1) is below (mode 'low') or at/above
    (mode 'high') E04_GATE_THR nats. Lets us ask whether a global temperature gain comes from confident or from
    uncertain positions."""

    def __init__(self, vllm_config, device, is_pin_memory):
        self.thr = float(os.environ.get("E04_GATE_THR", "0.5"))
        self.tau = float(os.environ.get("E04_GATE_TAU", "2.0"))
        self.mode = os.environ.get("E04_GATE_MODE", "low")

    def is_argmax_invariant(self):
        return True   # positive per-row scaling never changes the argmax

    def update_state(self, batch_update):
        pass

    def apply(self, logits):
        lp = torch.log_softmax(logits.float(), -1)
        H = -(lp.exp() * lp).sum(-1)
        gate = (H < self.thr) if self.mode == "low" else (H >= self.thr)
        scale = torch.where(gate, torch.full_like(H, self.tau), torch.ones_like(H))
        return logits * scale[:, None].to(logits.dtype)


class EntropyGatedArgmax(LogitsProcessor):
    """B1 in a single model (E08): where the row's entropy at T=1 is >= E04_ARGMAX_THR nats, keep only the argmax
    (all other logits -> -inf); elsewhere leave logits untouched so the usual temperature / top-p sampling applies.
    NOT argmax-invariant on purpose, so vLLM applies it BEFORE temperature and the entropy is measured at T=1,
    matching e04_hybrid.py's fork definition."""

    def __init__(self, vllm_config, device, is_pin_memory):
        self.thr = float(os.environ.get("E04_ARGMAX_THR", "0.5"))

    def is_argmax_invariant(self):
        return False

    def update_state(self, batch_update):
        pass

    def apply(self, logits):
        lp = torch.log_softmax(logits.float(), -1)
        H = -(lp.exp() * lp).sum(-1)
        gate = H >= self.thr
        if not bool(gate.any()):
            return logits
        am = logits.argmax(-1)
        onehot = torch.full_like(logits, float("-inf"))
        onehot.scatter_(1, am[:, None], 0.0)
        return torch.where(gate[:, None], onehot, logits)
