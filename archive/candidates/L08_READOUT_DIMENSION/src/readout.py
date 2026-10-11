"""Final-readout dimensional truncation for causal LMs.

Parent intervention (Takeshita et al., EMNLP 2025 main.1410):
  "removing half of the last hidden representations before they are projected
   to the vocabulary space ... and reduce the unembedding matrix correspondingly."

Let h_t in R^d be the representation fed to the unembedding, and W_U in R^{V x d}.
Keeping coordinate set S gives

    logits'_t = W_U[:, S] h_t[S] = W_U h_t - W_U[:, S^c] h_t[S^c].

So truncation is exactly equivalent to zeroing the complement coordinates of the
lm_head input.  We implement it as a forward pre-hook on `lm_head`, which leaves
every transformer weight and every layer's computation untouched: only the
hidden -> vocabulary readout channel is modified.

Two placements are supported because the parent wording is ambiguous:
  post_norm (default): mask the input of lm_head, i.e. after the final RMSNorm.
                       This is the exact algebraic identity above.
  pre_norm:            mask the last decoder layer's output, before the final
                       RMSNorm.  The norm then renormalises over surviving mass,
                       which changes logit scale as well as direction.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import torch


def build_mask(d: int, mode: str, keep_frac: float = 0.5, seed: int = 0) -> torch.Tensor:
    """Boolean keep-mask over the d readout coordinates."""
    k = int(round(d * keep_frac))
    mask = torch.zeros(d, dtype=torch.bool)
    if mode == "full":
        mask[:] = True
    elif mode == "first":
        mask[:k] = True
    elif mode == "last":
        mask[d - k:] = True
    elif mode == "random":
        g = torch.Generator().manual_seed(seed)
        mask[torch.randperm(d, generator=g)[:k]] = True
    else:
        raise ValueError(f"unknown mask mode: {mode}")
    return mask


def mask_id(mask: torch.Tensor) -> str:
    return hashlib.sha256(mask.numpy().tobytes()).hexdigest()[:12]


@dataclass
class ReadoutTruncation:
    """Context manager applying a readout mask to a HF causal LM."""

    model: torch.nn.Module
    mask: torch.Tensor
    placement: str = "post_norm"
    logit_bias: torch.Tensor = None   # E03b: rank-one correction added to logits

    def __post_init__(self) -> None:
        self._handle = None
        self._bias_handle = None
        self._enabled = False

    def _target_module(self) -> torch.nn.Module:
        if self.placement == "post_norm":
            return self.model.lm_head
        if self.placement == "pre_norm":
            return self.model.model.norm
        raise ValueError(f"unknown placement: {self.placement}")

    def __enter__(self) -> "ReadoutTruncation":
        if bool(self.mask.all()) and self.logit_bias is None:
            return self  # full readout, no correction: no hook at all
        dev = self.model.lm_head.weight.device
        keep = self.mask.to(dev)

        if not bool(self.mask.all()):
            def pre_hook(_module, args):
                (x,) = args
                return (x * keep.to(x.dtype),)
            self._handle = self._target_module().register_forward_pre_hook(pre_hook)

        if self.logit_bias is not None:
            b = self.logit_bias.to(dev)

            def post_hook(_module, _args, out):
                return out + b.to(out.dtype)

            self._bias_handle = self.model.lm_head.register_forward_hook(post_hook)
        self._enabled = True
        return self

    def __exit__(self, *exc) -> None:
        for name in ("_handle", "_bias_handle"):
            h = getattr(self, name, None)
            if h is not None:
                h.remove()
                setattr(self, name, None)
        self._enabled = False
