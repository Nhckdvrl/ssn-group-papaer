"""Capture/replay native gate logits before the common selector's mask.

The expert forward, softmax, top-k, multiplication and accumulation are untouched.
Register this engine before restricted_gates: that later hook applies the same
selector to captured/replayed logits. No source representation is learned.
"""
import torch


class RoutingEngine:
    def __init__(self, model):
        self.model = model
        self.capture = False
        self.trace = None
        self.captured = None
        self.seen = []
        self.handles = []

    def __enter__(self):
        self.handles = [self.model.register_forward_pre_hook(self._begin),
                        self.model.register_forward_hook(self._finish)]
        for index, layer in enumerate(self.model.model.layers):
            self.handles.append(layer.mlp.gate.register_forward_hook(self._hook(index)))
        return self

    def configure(self, *, capture=False, trace=None):
        if capture and trace is not None:
            raise ValueError('Capture and replay are distinct modes')
        if trace is not None and len(trace) != len(self.model.model.layers):
            raise ValueError('Incomplete route trajectory')
        self.capture, self.trace = capture, trace

    def _begin(self, module, args):
        self.seen = []
        self.captured = []

    def _finish(self, module, args, output):
        if self.seen != list(range(len(self.model.model.layers))):
            raise ValueError('Missing/repeated gate interception')

    def _hook(self, index):
        def apply(module, args, output):
            if output.ndim != 2 or output.dtype != args[0].dtype:
                raise ValueError('Native flat gate interface changed')
            if not torch.isfinite(output).all():
                raise ValueError('Capture/replay must precede the common masking hook')
            self.seen.append(index)
            if self.capture:
                self.captured.append(output.detach().clone())
            if self.trace is not None:
                fixed = self.trace[index]
                if fixed.shape != output.shape or fixed.dtype != output.dtype or fixed.device != output.device:
                    raise ValueError('Route trajectory does not match the actual causal batch')
                if not torch.isfinite(fixed).all():
                    raise ValueError('Invalid route trajectory')
                return fixed
            return None
        return apply

    def __exit__(self, *exc):
        for handle in self.handles:
            handle.remove()
        self.handles = []
        self.captured, self.trace = None, None


def permute_trace(trace, permutation, batch):
    result = []
    for value in trace:
        if value.shape[0] % batch:
            raise ValueError('Invalid route trace batch')
        shaped = value.reshape(batch, -1, value.shape[-1])
        result.append(shaped[permutation].reshape_as(value))
    return tuple(result)


@torch.no_grad()
def route_differences(left, right, keep, valid, top_k=7):
    """Per-layer actual support/weight differences; not causal allocations."""
    rows = []
    batch, length = valid.shape
    for layer, (a, b) in enumerate(zip(left, right)):
        allowed = keep[layer, :-1].to(device=a.device, dtype=torch.bool)
        pa = a[:, :-1].float().masked_fill(~allowed[None, :], -torch.inf).softmax(-1)
        pb = b[:, :-1].float().masked_fill(~allowed[None, :], -torch.inf).softmax(-1)
        wa, ia = pa.topk(top_k, -1); wb, ib = pb.topk(top_k, -1)
        wa = wa.to(a.dtype).float(); wb = wb.to(b.dtype).float()
        support = (ia[:, :, None] == ib[:, None, :]).sum((-1, -2)).float()/top_k
        qa = torch.zeros_like(pa).scatter_(1, ia, wa)
        qb = torch.zeros_like(pb).scatter_(1, ib, wb)
        fields = torch.stack((support, (qa-qb).abs().sum(-1), wa.sum(-1), wb.sum(-1)), -1)
        fields = fields.reshape(batch, length, 4)
        mask = valid.to(device=a.device, dtype=torch.float32)
        rows.append((fields*mask[:, :, None]).sum((0, 1))/mask.sum())
    return torch.stack(rows).cpu().numpy()
