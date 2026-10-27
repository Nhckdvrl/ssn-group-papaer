"""E153 RC scoring and sequential task-calibration harness."""
import json
import numpy as np
import torch
from types import SimpleNamespace
import e150_native as n


class StopAtGate(Exception):
    pass


def padded(sequences,pad,device):
    length=max(map(len,sequences))
    ids=torch.full((len(sequences),length),pad,dtype=torch.long,device=device)
    attention=torch.zeros_like(ids,dtype=torch.bool)
    for i,seq in enumerate(sequences):
        ids[i,:len(seq)]=torch.as_tensor(np.asarray(seq,dtype=np.int64),device=device)
        attention[i,:len(seq)]=True
    return ids,attention


@torch.no_grad()
def score_candidates(model,sequences,prompt_tokens,pad,check_causal=True):
    device=next(model.parameters()).device
    batch,am=padded(sequences,pad,device)
    logits=n.fwd(model,batch[:,:-1],am[:,:-1])
    if check_causal:
        for row in range(1,len(sequences)):
            if not torch.equal(logits[0,prompt_tokens-1],logits[row,prompt_tokens-1]):
                raise ValueError("Identical candidate prefix produced different first-answer logits")
    score_mask=am[:,1:]&(torch.arange(logits.shape[1],device=device)[None,:]>=prompt_tokens-1)
    selected=logits[score_mask].float().log_softmax(-1)
    targets=batch[:,1:][score_mask]
    token_ll=selected.gather(-1,targets[:,None]).squeeze(-1)
    rows=score_mask.nonzero()[:,0].cpu().numpy()
    scores=np.bincount(rows,weights=token_ll.double().cpu().numpy(),minlength=len(sequences))
    first=logits[0,prompt_tokens-1].float().log_softmax(-1)
    counts=score_mask.sum(1).cpu().numpy()
    del logits,selected,token_ll,batch,am
    return scores,counts,first


@torch.no_grad()
def greedy_masks(model,cal_sequences,pad,keep_total=32,batch_size=2,progress=None):
    layers=len(model.model.layers);experts=model.model.layers[0].mlp.num_experts
    keep=np.ones((layers,experts),bool)
    probabilities=np.empty((layers,experts-1),np.float64)
    token_counts=[]
    device=next(model.parameters()).device
    for layer in range(layers):
        total=np.zeros(experts-1,np.float64);tokens=0
        for start in range(0,len(cal_sequences),batch_size):
            seqs=cal_sequences[start:start+batch_size]
            ids,am=padded(seqs,pad,device)
            repeated=np.broadcast_to(keep,(len(seqs),layers,experts)).copy()
            captured=[]
            def collect(module,args,output):
                probability=output[:,:-1].float().softmax(-1).reshape(len(seqs),ids.shape[1],experts-1)
                captured.append((probability.double()*am[:,:,None]).sum((0,1)).cpu().numpy())
                raise StopAtGate()
            with n.restricted.restricted_gates(model,repeated):
                handle=model.model.layers[layer].mlp.gate.register_forward_hook(collect)
                try:
                    model(input_ids=ids,attention_mask=am,use_cache=False,output_router_logits=False,return_dict=True)
                    raise RuntimeError("Greedy calibration failed to stop at the requested gate")
                except StopAtGate:
                    pass
                finally:
                    handle.remove()
            if len(captured)!=1:raise ValueError("Expected exactly one layer-gate capture")
            total+=captured[0];tokens+=int(am.sum())
            del ids,am
        if tokens<=0:raise ValueError("Empty task calibration")
        probabilities[layer]=total/tokens
        chosen=np.argsort(-total,kind="stable")[:keep_total-1]
        keep[layer,:-1]=False;keep[layer,chosen]=True;keep[layer,-1]=True
        token_counts.append(tokens)
        if progress is not None:progress(layer,keep[layer],probabilities[layer])
    if not np.all(keep.sum(-1)==keep_total) or not keep[:,-1].all():raise ValueError("Incorrect sequential expert budget")
    return keep,probabilities,token_counts


def self_test():
    torch.manual_seed(153);torch.set_num_threads(1)
    class ConstantLM(torch.nn.Module):
        def __init__(self):
            super().__init__();self.anchor=torch.nn.Parameter(torch.zeros(()),requires_grad=False)
        def forward(self,input_ids,**kwargs):
            l=torch.arange(1,9,dtype=torch.float32).log()
            return SimpleNamespace(logits=l.expand(input_ids.shape[0],input_ids.shape[1],8).clone())
    sequences=[np.array(v) for v in [(1,2,3,4),(1,2,3,5,6),(1,2,3,4),(1,2,3,6)]]
    model=ConstantLM()
    scores,counts,_=score_candidates(model,sequences,3,0)
    expected=np.log(np.array([5/36,(6/36)*(7/36),5/36,7/36]))
    assert np.allclose(scores,expected,atol=1e-6) and np.array_equal(counts,[1,2,1,1])
    order=[2,0,3,1]
    permuted,_,_=score_candidates(model,[sequences[i] for i in order],3,0)
    assert np.array_equal(permuted,scores[order])
    for source in range(2):
        cfg_cls,cls,_=n.classes(source)
        cfg=cfg_cls(vocab_size=64,hidden_size=16,intermediate_size=8,num_hidden_layers=2,num_attention_heads=2,num_key_value_heads=2,
                    num_experts=4,num_experts_per_tok=2,num_shared_experts=1,norm_topk_prob=False,pad_token_id=63,eos_token_id=62,
                    max_position_embeddings=32,attention_dropout=0.,output_router_logits=False)
        cfg._attn_implementation="eager";tiny=cls(cfg).eval()
        for layer in tiny.model.layers:layer.mlp.gate.weight.data.zero_()
        state=n.old.tensor_hash(tiny.state_dict());buffers=n.old.tensor_hash(n.buffers(tiny))
        masks,probabilities,counts=greedy_masks(tiny,[np.array([1,2,3,4]),np.array([5,6,7])],63,3,2)
        assert np.array_equal(masks,np.array([[1,1,0,1],[1,1,0,1]],bool))
        assert np.allclose(probabilities,1/3) and counts==[7,7]
        observed=[]
        handle=tiny.model.layers[1].mlp.gate.register_forward_pre_hook(lambda m,args:observed.append(args[0].detach().clone()))
        ids,am=padded([np.array([1,2,3,4]),np.array([5,6,7])],63,"cpu")
        n.fwd(tiny,ids,am)
        previous_only=np.ones((2,2,4),bool);previous_only[:,0]=masks[0]
        with n.restricted.restricted_gates(tiny,previous_only):n.fwd(tiny,ids,am)
        handle.remove()
        assert len(observed)==2 and not torch.equal(observed[0],observed[1])
        assert n.old.tensor_hash(tiny.state_dict())==state and n.old.tensor_hash(n.buffers(tiny))==buffers
        assert all(not gate._forward_hooks for gate in n.restricted.gates(tiny))
    return {"status":"passed","constant_logit_multiple_token_scores":True,"padding_ignored":True,
            "candidate_permutation_equivariant":True,"uniform_gate_sequential_keep_known_answer":True,
            "prior_layer_restriction_changes_next_gate_input":True,
            "source_parameters_buffers_and_hooks_restored":True}
