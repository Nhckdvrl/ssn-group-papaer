"""Closed-form routed-energy calibration and native expert-output gains."""
from contextlib import contextmanager
import copy

import numpy as np
import torch
from torch import nn
from e163_geometry import first, with_first


class ZeroShared(nn.Module):
    def forward(self, value):return torch.zeros_like(value)


def donor_shadow(parent, donor, shared):
    block=copy.copy(parent)
    for name in ('_modules','_parameters','_buffers','_forward_hooks','_forward_pre_hooks'):
        setattr(block,name,copy.copy(getattr(parent,name)))
    gate=copy.copy(parent.gate)
    for name in ('_modules','_parameters','_buffers','_forward_hooks','_forward_pre_hooks'):
        setattr(gate,name,copy.copy(getattr(parent.gate,name)))
    # Calibration precedes routing interception; refuse accidental inherited hooks.
    if gate._forward_hooks or gate._forward_pre_hooks or block._forward_hooks:
        raise ValueError('Build calibration shadows before installing observers')
    block.gate=gate
    block.experts=nn.ModuleList(list(donor.experts[:-1])+[ZeroShared()] if shared else list(donor.experts))
    return block


class EnergyCalibration:
    """Observe P's native full trajectory; compare both functions on its same inputs."""
    def __init__(self,parent,donor_blocks,shared):
        self.model=parent;self.shared=shared;self.handles=[]
        self.shadows=[donor_shadow(layer.mlp,other,shared)
                      for layer,other in zip(parent.model.layers,donor_blocks)]
        self.sums=torch.zeros((len(self.shadows),3),dtype=torch.float64,
                              device=next(parent.parameters()).device)
        self.tokens=np.zeros(len(self.shadows),np.int64)

    def _begin(self,module,args,kwargs):
        self.valid=kwargs.get('attention_mask')
        if self.valid is None or self.valid.ndim!=2:raise ValueError('Explicit cal position mask required')
        self.saved={};self.seen=[]

    def _shared(self,index,out):
        if index in self.saved:raise ValueError('Shared function called twice')
        self.saved[index]=out.detach()
        return torch.zeros_like(out)

    def _block(self,index,args,out):
        rp=first(out);rd=first(self.shadows[index](args[0]))
        if rp.shape!=rd.shape or rp.shape[:2]!=self.valid.shape:
            raise ValueError('Same-input native routed frame differs')
        x=rp[self.valid].float();y=rd[self.valid].float()
        # Products FP32, reductions FP64; no target label or predictive loss used.
        self.sums[index]+=torch.stack((x.square().double().sum(),y.square().double().sum(),
                                      (x*y).double().sum()))
        self.tokens[index]+=int(self.valid.sum());self.seen.append(index)
        if self.shared:
            s=self.saved.pop(index).reshape_as(rp)
            return with_first(out,rp+s)
        return out

    def _end(self,module,args,out):
        if self.seen!=list(range(len(self.shadows))) or self.saved:
            raise ValueError('Incomplete calibration observation')

    def __enter__(self):
        self.handles=[self.model.register_forward_pre_hook(self._begin,with_kwargs=True),
                      self.model.register_forward_hook(self._end)]
        for i,layer in enumerate(self.model.model.layers):
            if self.shared:
                self.handles.append(layer.mlp.experts[-1].register_forward_hook(
                    lambda m,a,o,i=i:self._shared(i,o)))
            self.handles.append(layer.mlp.register_forward_hook(lambda m,a,o,i=i:self._block(i,a,o)))
        return self

    def result(self):
        values=self.sums.cpu().numpy()
        if not np.isfinite(values).all() or np.any(values[:,:2]<=0) or np.any(self.tokens<=0):
            raise ValueError('Finite nonzero routed calibration energy required')
        gain=np.sqrt(values[:,1]/values[:,0]);effective=gain.astype(np.float32)
        return {'P_energy':values[:,0],'donor_energy':values[:,1],'dot_product':values[:,2],
                'tokens':self.tokens.copy(),'gain_FP64':gain,'gain':effective,
                'cosine':values[:,2]/np.sqrt(values[:,0]*values[:,1]),
                'scalar_residual_fraction':(effective.astype(np.float64)**2*values[:,0]+values[:,1]-2*effective*values[:,2])/values[:,1]}

    def __exit__(self,*error):
        for h in self.handles:h.remove()
        self.handles=[]


@contextmanager
def gains(model,values,shared):
    if len(values)!=len(model.model.layers) or not np.isfinite(values).all() or np.any(np.asarray(values)<0):
        raise ValueError('One finite nonnegative gain per layer required')
    handles=[]
    try:
        for i,layer in enumerate(model.model.layers):
            routed=layer.mlp.experts[:-1] if shared else layer.mlp.experts
            factor=float(np.float32(values[i]))
            def scale(module,args,out,factor=factor):
                if not isinstance(out,torch.Tensor):raise ValueError('Native expert output must be Tensor')
                return (out.float()*factor).to(out.dtype)
            for expert in routed:handles.append(expert.register_forward_hook(scale))
        yield
    finally:
        for h in handles:h.remove()
