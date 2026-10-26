"""Prefix-only fixed expert budgets and coverage; no labels or future-token selection."""
from contextlib import contextmanager
import numpy as np
import torch


def gates(model): return [layer.mlp.gate for layer in model.model.layers]


@torch.no_grad()
def prefix_keep(model, prefix_ids, keep_total=32):
    batch, length = prefix_ids.shape
    layers = len(model.model.layers)
    experts = model.model.layers[0].mlp.num_experts
    if not 2 <= keep_total <= experts: raise ValueError("Invalid fixed expert budget")
    scores = np.empty((batch,layers,experts-1),np.float32)
    handles = []
    def hook(layer):
        def collect(module, args, output):
            probability = output[:,:-1].float().softmax(-1)
            weight, selected = probability.topk(model.model.layers[layer].mlp.top_k-1,-1)
            weight = weight.to(args[0].dtype).float()
            q = torch.zeros_like(probability).scatter_add_(1,selected,weight)
            scores[:,layer] = q.reshape(batch,length,experts-1).sum(1).cpu().numpy()
        return collect
    try:
        handles = [gate.register_forward_hook(hook(i)) for i,gate in enumerate(gates(model))]
        model(input_ids=prefix_ids, attention_mask=torch.ones_like(prefix_ids),use_cache=False,
              output_router_logits=False,return_dict=True)
    finally:
        for handle in handles: handle.remove()
    keep = np.zeros((batch,layers,experts),bool)
    keep[:,:,-1] = True
    order = np.argsort(-scores,axis=-1,kind="stable")[:,:,:keep_total-1]
    np.put_along_axis(keep,order,True,axis=-1)
    if not np.all(keep.sum(-1) == keep_total): raise ValueError("Incorrect routed/shared budget")
    return keep


@contextmanager
def restricted_gates(model, keep):
    device = next(model.parameters()).device
    keep = torch.as_tensor(keep,dtype=torch.bool,device=device)
    batch = len(keep); handles=[]
    if not bool(keep[:,:,-1].all()): raise ValueError("Shared expert must always remain available")
    def hook(layer):
        def apply(module,args,output):
            if len(output) % batch: raise ValueError("Router batch/position mismatch")
            mask=keep[:,layer,None,:].expand(batch,len(output)//batch,output.shape[-1]).reshape_as(output)
            return output.masked_fill(~mask,-torch.inf)
        return apply
    try:
        handles=[gate.register_forward_hook(hook(i)) for i,gate in enumerate(gates(model))]
        yield
    finally:
        for handle in handles: handle.remove()


@contextmanager
def routing_coverage(model, keeps, valid_targets):
    device=next(model.parameters()).device
    keeps=torch.as_tensor(keeps,dtype=torch.bool,device=device)
    valid=torch.as_tensor(valid_targets,dtype=torch.float32,device=device)
    policies,batch,layers,experts=keeps.shape
    result=np.empty((policies,batch,layers,3),np.float32)
    handles=[]
    def hook(layer):
        def collect(module,args,output):
            probability=output[:,:-1].float().softmax(-1)
            weight, selected=probability.topk(model.model.layers[layer].mlp.top_k-1,-1)
            weight=weight.to(args[0].dtype).float()
            weight=weight.reshape(batch,-1,weight.shape[-1]);selected=selected.reshape_as(weight).long()
            if valid.shape != weight.shape[:2]: raise ValueError("Coverage score mask differs")
            for policy in range(policies):
                allowed=keeps[policy,:,layer,None,:-1].expand(batch,weight.shape[1],experts-1)
                included=allowed.gather(-1,selected).float()
                counts=included.mean(-1)
                mass=(weight*included).sum(-1)/weight.sum(-1)
                result[policy,:,layer,0]=((counts*valid).sum(1)/valid.sum(1)).cpu().numpy()
                result[policy,:,layer,1]=((mass*valid).sum(1)/valid.sum(1)).cpu().numpy()
                result[policy,:,layer,2]=((weight.sum(-1)*valid).sum(1)/valid.sum(1)).cpu().numpy()
        return collect
    try:
        handles=[gate.register_forward_hook(hook(i)) for i,gate in enumerate(gates(model))]
        yield result
    finally:
        for handle in handles: handle.remove()
