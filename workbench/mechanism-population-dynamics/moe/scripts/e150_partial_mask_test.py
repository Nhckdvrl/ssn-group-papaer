"""A closed-form oracle for the unmodified native routed/shared mask interface."""
import json
import math
from types import SimpleNamespace
import torch
from torch import nn
import e150_native as n
import e150_restricted as restriction


class FixedGate(nn.Module):
    def __init__(self):
        super().__init__()
        self.logits=nn.Parameter(torch.tensor([math.log(4),math.log(2),0.,100.]),requires_grad=False)
    def forward(self,x): return self.logits.expand(len(x),-1)


class Constant(nn.Module):
    def __init__(self,value): super().__init__(); self.value=value
    def forward(self,x): return torch.full_like(x,self.value)


@torch.no_grad()
def main():
    errors=[]
    for source in range(2):
        cfg_cls,_,_=n.classes(source)
        module=__import__(f"codex_e150_source_{source}.modeling_emo",fromlist=["EmoSparseMoeBlock"])
        cfg=cfg_cls(hidden_size=4,intermediate_size=4,num_experts=4,num_experts_per_tok=2,num_shared_experts=1,norm_topk_prob=False)
        block=module.EmoSparseMoeBlock(cfg,4,1,None)
        block.gate=FixedGate();block.experts=nn.ModuleList([Constant(v) for v in (2.,4.,8.,10.)])
        layer=nn.Module();layer.mlp=block
        inner=nn.Module();inner.layers=nn.ModuleList([layer])
        model=nn.Module();model.model=inner
        h=torch.ones(1,6,4)
        full=block(h)[0]
        # R logits [log4, log2, 0] imply top1 mass 4/7; S always has weight 1.
        errors.append(float((full-(10+2*4/7)).abs().max()))
        keep=torch.tensor([[[False,True,True,True]]])
        with restriction.restricted_gates(model,keep): masked=block(h)[0]
        # Removing R0 gives R1 mass 2/3, so the complete answer is 10 + 4*2/3.
        errors.append(float((masked-(10+4*2/3)).abs().max()))
        assert torch.isfinite(masked).all()
        block.gate.logits[-1]=-100.
        assert torch.equal(block(h)[0],full)
        with restriction.restricted_gates(model,keep): assert torch.equal(block(h)[0],masked)
        assert not block.gate._forward_hooks
    assert max(errors)<2e-6,errors
    result={"status":"passed","CPU_only":True,"source_sha256":n.proof(),"oracle_source_sha256":n.sha(__file__),
            "full_known_answer":10+8/7,"partial_known_answer":10+8/3,"max_absolute_error":max(errors),
            "checks":{"omitted_route_replaced_by_next_available_route":True,"normalization_over_remaining_routed_slots":True,
                      "shared_value_preserved":True,"shared_gate_logit_irrelevant":True,"hooks_removed":True},
            "scope":"Constant-expert mathematical oracle, not new pretrained-model observations or a change to the frozen E150 driver."}
    n.write(n.RESULT/"partial_mask_known_answer.json",result)
    print(json.dumps({"status":"passed","max_absolute_error":max(errors)},indent=2))


if __name__=="__main__":torch.set_num_threads(1);main()
