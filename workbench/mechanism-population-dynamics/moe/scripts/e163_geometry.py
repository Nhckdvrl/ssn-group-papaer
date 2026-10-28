"""Causal message substitution for the pinned native EMO interface.

Only local hooks are installed. Original parameters and the original MoE router
are used. One last-slot shared expert has coefficient one. The native routed
sum is obtained from the original block with its shared output temporarily zero;
adding the captured shared output restores the native sum.
"""
from contextlib import AbstractContextManager
import torch

TARGETS = ('R', 'S', 'RS')
DIAGNOSTICS = ('FP32_norm_error', 'FP32_projection_error', 'cast_norm_error',
               'cast_projection_error', 'actual_residual_norm_error',
               'orthogonal_energy_fraction', 'proposal_fallback_count',
               'zero_background_count', 'zero_message_count')


def first(value):
    return value[0] if isinstance(value, (tuple, list)) else value


def with_first(value, tensor):
    if isinstance(value, tuple):
        return (tensor, *value[1:])
    if isinstance(value, list):
        return [tensor, *value[1:]]
    return tensor


def replace_message(u, background, direction, rule):
    """Return FP32 (or analytical FP64) proxy and numerical witnesses.

    Gram uses the orthogonal residual's norm to evaluate sqrt(r^2-p^2)
    stably. Only its scalar radius and the parallel coefficient enter the
    replacement; the original orthogonal direction never enters it.
    """
    if rule not in ('norm', 'gram'):
        raise ValueError('Unknown geometric rule')
    if u.shape != background.shape or u.ndim < 2 or u.shape[-1] < 2:
        raise ValueError('Matching vector shapes with dimension >=2 required')
    dtype = torch.float64 if u.dtype == torch.float64 else torch.float32
    x, b, d = u.to(dtype), background.to(dtype), direction.to(dtype)
    d = torch.broadcast_to(d, x.shape)
    tiny = 1e-12
    radius = torch.linalg.vector_norm(x, dim=-1, keepdim=True)
    bnorm = torch.linalg.vector_norm(b, dim=-1, keepdim=True)
    bhat = b / bnorm.clamp_min(tiny)
    parallel = (x * bhat).sum(-1, keepdim=True)
    orthogonal = x - parallel * bhat
    orthogonal_radius = torch.linalg.vector_norm(orthogonal, dim=-1, keepdim=True)
    if rule == 'norm':
        dnorm = torch.linalg.vector_norm(d, dim=-1, keepdim=True)
        fallback = dnorm <= tiny
        basis = torch.zeros_like(d)
        basis[..., 0] = 1
        chosen = torch.where(fallback, basis, d / dnorm.clamp_min(tiny))
        value = radius * chosen
    else:
        perpendicular = d - (d * bhat).sum(-1, keepdim=True) * bhat
        dnorm = torch.linalg.vector_norm(d, dim=-1, keepdim=True)
        pnorm = torch.linalg.vector_norm(perpendicular, dim=-1, keepdim=True)
        fallback = (pnorm <= 1e-6 * dnorm) | (pnorm <= tiny)
        # The least aligned coordinate is bounded away from parallel to b.
        coordinate = bhat.abs().argmin(-1, keepdim=True)
        basis = torch.zeros_like(d).scatter_(-1, coordinate, 1)
        basis = basis - (basis * bhat).sum(-1, keepdim=True) * bhat
        basis = basis / torch.linalg.vector_norm(basis, dim=-1, keepdim=True).clamp_min(tiny)
        chosen = torch.where(fallback, basis, perpendicular / pnorm.clamp_min(tiny))
        value = parallel * bhat + orthogonal_radius * chosen
    # Exact proposal/witness equality is a mathematical identity. Preserve its
    # actual program, including at zero coordinates, rather than a round trip.
    value = torch.where((d == x).all(-1, keepdim=True), x, value)
    # Explicit zero handling prevents roundoff-generated signals.
    value = torch.where(radius <= tiny, torch.zeros_like(value), value)
    witnesses = {'radius': radius, 'bhat': bhat, 'parallel': parallel,
                 'orthogonal_radius': orthogonal_radius, 'fallback': fallback,
                 'zero_background': bnorm <= tiny, 'zero_message': radius <= tiny}
    return value, witnesses


class GeometryEngine(AbstractContextManager):
    def __init__(self, model, check_geometry=True):
        self.model = model
        self.check_geometry = check_geometry
        self.handles = []
        self.configure()

    def configure(self, target=None, mode='native', proposal=None, *,
                  directions=None, witnesses=None, capture=False, probes=False):
        if mode not in ('native', 'zero', 'norm', 'gram', 'raw'):
            raise ValueError('Unknown substitution mode')
        if mode != 'native' and target not in TARGETS:
            raise ValueError('A target message is required')
        if witnesses is not None and target != 'S':
            raise ValueError('Clean trajectory witnesses are only used for shared replay')
        self.target, self.mode, self.proposal = target, mode, proposal
        self.directions, self.witnesses = directions, witnesses
        self.capture, self.save_probes = capture, probes
        self.last_diagnostics = None
        self.last_native_geometry = None
        self.probes = []

    def _begin(self, module, args, kwargs):
        self.residuals, self.shared = {}, {}
        self.seen = []
        self.layer_diagnostics = []
        self.native_geometry = []
        self.captured = {name: [] for name in TARGETS}
        self.attention = kwargs.get('attention_mask')
        self.probes = []

    def _finish(self, module, args, output):
        if self.seen != list(range(len(self.model.model.layers))) or self.residuals or self.shared:
            raise ValueError('Incomplete or repeated native message interception')
        if self.layer_diagnostics:
            self.last_diagnostics = torch.stack(self.layer_diagnostics)
        if self.native_geometry:
            self.last_native_geometry = torch.stack(self.native_geometry, dim=1)
        if self.check_geometry and self.last_diagnostics is not None and self.mode in ('norm', 'gram'):
            maxima = self.last_diagnostics.max(0).values
            if bool(maxima[0] > 1e-4) or bool(maxima[2] > .01):
                raise ValueError('Message norm preservation exceeded the preregistered numerical bound')
            if self.mode == 'gram' and (bool(maxima[1] > 1e-4) or bool(maxima[3] > .01) or bool(maxima[4] > .02)):
                raise ValueError('Projection/residual norm preservation exceeded its numerical bound')

    def _valid(self, tensor):
        if self.attention is None:
            return torch.ones(tensor.shape[:-1], dtype=torch.bool, device=tensor.device)
        if self.attention.shape != tensor.shape[:-1]:
            raise ValueError('Message positions differ from the actual causal input mask')
        return self.attention.to(device=tensor.device, dtype=torch.bool)

    def _save_residual(self, index, args):
        if index in self.residuals:
            raise ValueError('Repeated pre-feedforward normalization')
        self.residuals[index] = args[0].detach()

    def _capture_shared(self, index, output):
        if index in self.shared or output.ndim != 2:
            raise ValueError('Expected one complete flat shared output per layer')
        self.shared[index] = output.detach()
        return torch.zeros_like(output)

    def _patch(self, index, output):
        r = first(output)
        h = self.residuals.pop(index)
        s = self.shared.pop(index).reshape_as(r)
        if r.shape != h.shape or r.dtype != h.dtype:
            raise ValueError('Actual residual and MoE output do not share the native frame')
        native = r + s
        values = {'R': r, 'S': s, 'RS': native}
        backgrounds = {'R': h.float() + s.float(), 'S': h.float() + r.float(), 'RS': h.float()}
        valid = self._valid(r)
        if self.capture:
            for name in TARGETS:
                self.captured[name].append(values[name].detach().clone())
        self.seen.append(index)
        if self.mode == 'native':
            geometry = []
            for name in TARGETS:
                x, b = values[name].float(), backgrounds[name]
                r2 = x.square().sum(-1)
                b2 = b.square().sum(-1)
                cosine = (x * b).sum(-1) / (r2 * b2).sqrt().clamp_min(1e-24)
                geometry.append(torch.stack((r2[valid].mean(), cosine[valid].mean(), cosine[valid].square().mean())))
            self.native_geometry.append(torch.stack(geometry))
            return with_first(output, native)
        u = values[self.target]
        if self.witnesses is not None:
            supplied = self.witnesses[index]
            if supplied.shape != u.shape or supplied.dtype != u.dtype or supplied.device != u.device:
                raise ValueError('Clean shared witness frame differs')
            u = supplied
        b = backgrounds[self.target]
        if self.mode == 'zero':
            replacement = torch.zeros_like(u)
            precise = replacement.float()
            proof = None
            direction = torch.zeros_like(u)
        else:
            direction = self.directions[index] if self.directions is not None else self.proposal[index]
            if self.mode == 'raw':
                if direction.shape != u.shape or direction.dtype != u.dtype or direction.device != u.device:
                    raise ValueError('Raw shared source frame differs')
                replacement, precise, proof = direction.clone(), direction.float(), None
            else:
                precise, proof = replace_message(u, b, direction, self.mode)
                replacement = precise.to(u.dtype)
        if self.target == 'R':
            changed, reference = replacement + s, u + s
        elif self.target == 'S':
            changed, reference = r + replacement, r + u
        else:
            changed, reference = replacement, u
        if proof is not None:
            radius = proof['radius'].squeeze(-1)
            bhat = proof['bhat']
            parallel = proof['parallel'].squeeze(-1)
            denominator = radius.clamp_min(1e-12)
            def error(v):
                norm = torch.linalg.vector_norm(v.float(), dim=-1)
                projection = (v.float() * bhat).sum(-1)
                return ((norm - radius).abs() / denominator)[valid].max(), ((projection - parallel).abs() / denominator)[valid].max()
            fp_norm, fp_projection = error(precise)
            q_norm, q_projection = error(replacement)
            old_residual = (h + reference).float()
            new_residual = (h + changed).float()
            actual = (torch.linalg.vector_norm(new_residual, dim=-1) - torch.linalg.vector_norm(old_residual, dim=-1)).abs()
            actual = (actual / torch.linalg.vector_norm(old_residual, dim=-1).clamp_min(1e-12))[valid].max()
            fraction = (proof['orthogonal_radius'].squeeze(-1) / denominator).square()[valid].mean()
            stats = torch.stack((fp_norm, fp_projection, q_norm, q_projection, actual, fraction,
                                 proof['fallback'].squeeze(-1)[valid].sum(),
                                 proof['zero_background'].squeeze(-1)[valid].sum(),
                                 proof['zero_message'].squeeze(-1)[valid].sum()))
            self.layer_diagnostics.append(stats)
            if self.save_probes and index in (0, len(self.model.model.layers)//2, len(self.model.model.layers)-1):
                positions = torch.tensor([0, u.shape[1]-1], device=u.device)
                expanded = torch.broadcast_to(direction, u.shape)
                self.probes.append({'layer': index, 'u': u[0, positions].float().cpu().numpy(),
                    'b': b[0, positions].float().cpu().numpy(), 'direction': expanded[0, positions].float().cpu().numpy(),
                    'precise': precise[0, positions].float().cpu().numpy(), 'cast': replacement[0, positions].float().cpu().numpy(),
                    'native_residual': old_residual[0, positions].cpu().numpy(), 'changed_residual': new_residual[0, positions].cpu().numpy()})
        return with_first(output, changed)

    def __enter__(self):
        try:
            self.handles.append(self.model.register_forward_pre_hook(self._begin, with_kwargs=True))
            self.handles.append(self.model.register_forward_hook(self._finish))
            for index, decoder in enumerate(self.model.model.layers):
                block = decoder.mlp
                if block.num_shared_experts != 1 or block.norm_topk_prob or block.always_active_experts not in (None, []):
                    raise ValueError('Requires original EMO single coefficient-one shared path')
                self.handles.append(decoder.pre_feedforward_layernorm.register_forward_pre_hook(
                    lambda m, args, i=index: self._save_residual(i, args)))
                self.handles.append(block.experts[-1].register_forward_hook(
                    lambda m, args, out, i=index: self._capture_shared(i, out)))
                self.handles.append(block.register_forward_hook(
                    lambda m, args, out, i=index: self._patch(i, out)))
            return self
        except BaseException:
            self.__exit__(None, None, None)
            raise

    def __exit__(self, *args):
        for handle in reversed(self.handles):
            handle.remove()
        self.handles = []
        self.residuals, self.shared = {}, {}
        return False
