"""Read-only softmax-normalizer observer around the frozen E150 model driver."""
import argparse
import os
_p=argparse.ArgumentParser(add_help=False)
_p.add_argument("--physical-gpu",type=int,default=0)
_early,_=_p.parse_known_args()
if os.environ.get("CUDA_VISIBLE_DEVICES") not in (None,"",str(_early.physical_gpu)):
    raise ValueError("Requested physical GPU and visibility differ")
os.environ["CUDA_VISIBLE_DEVICES"]=str(_early.physical_gpu)
os.environ["CUBLAS_WORKSPACE_CONFIG"]=":4096:8"
from contextlib import contextmanager
import json
import math
import numpy as np
import torch
import e150_native as n


def normalizer_values(logits,keeps,valid):
    """Mean retained full-router probability, and mean inverse, per sequence."""
    policies,batch,experts=keeps.shape
    probability=logits[:,:-1].float().softmax(-1).reshape(batch,-1,experts-1)
    result=[]
    for policy in range(policies):
        mass=(probability*keeps[policy,:,None,:-1]).sum(-1)
        if not bool((mass>0).all()): raise ArithmeticError("Retained full-softmax mass underflowed")
        result.append(torch.stack(((mass*valid).sum(-1)/valid.sum(-1),((1/mass)*valid).sum(-1)/valid.sum(-1)),-1))
    return torch.stack(result)


def test():
    logits=torch.tensor([[math.log(4),math.log(2),0.,100.]])
    keeps=torch.tensor([[[False,True,True,True]],[[True,True,True,True]]])
    value=normalizer_values(logits,keeps,torch.ones(1,1))
    expected=torch.tensor([[[3/7,7/3]],[[1.,1.]]])
    assert torch.allclose(value,expected,atol=3e-7)
    proof={"status":"passed","CPU_only":True,"observer_source_sha256":n.sha(__file__),
           "retained_mass_known_answer":3/7,"inverse_mass_known_answer":7/3,
           "scope":"Full FP32 routed softmax denominator before BF16 cast; shared slot excluded, not top7-only coverage."}
    n.write(n.RESULT/"normalizer_observer_test.json",proof)
    return proof


def evaluate(physical):
    check=n.read(n.RESULT/"normalizer_observer_test.json")
    if check["status"]!="passed" or check["observer_source_sha256"]!=n.sha(__file__): raise ValueError("Known-answer observer test required")
    original=n.restricted.routing_coverage
    events=[]
    @contextmanager
    def observed(model,keeps,valid_targets):
        device=next(model.parameters()).device
        keep=torch.as_tensor(keeps,dtype=torch.bool,device=device)
        valid=torch.as_tensor(valid_targets,dtype=torch.float32,device=device)
        result=np.empty((keep.shape[0],keep.shape[1],keep.shape[2],2),np.float32)
        handles=[]
        def hook(layer):
            def capture(module,args,output):
                result[:,:,layer]=normalizer_values(output,keep[:,:,layer],valid).cpu().numpy()
            return capture
        try:
            with original(model,keeps,valid_targets) as standard:
                handles=[gate.register_forward_hook(hook(i)) for i,gate in enumerate(n.restricted.gates(model))]
                yield standard
        finally:
            for handle in handles:handle.remove()
        events.append(result)
    info={"experiment":"E150","status":"running","execution_adapter_sha256":n.sha(__file__),
          "frozen_core_source_sha256":n.proof(),"model_math_inputs_and_condition_set_unchanged":True,
          "addition":"Read-only observation of full routed softmax retained probability / inverse; no additional model forwards."}
    n.write(n.RESULT/"execution_adapter.json",info)
    n.restricted.routing_coverage=observed
    try:
        output=n.evaluate(physical)
        if len(events)!=16*16: raise ValueError("Every full cell/batch must have one normalizer record")
        # Events follow batch -> case; concatenate real sequence slices.
        values=np.stack([np.concatenate([events[b*16+i] for b in range(16)],axis=1) for i in range(16)],axis=1)
        if values.shape!=(2,16,64,16,2): raise ValueError("Normalizer sidecar axes differ")
        path=n.RAW/"normalizer_observations.npz"
        if path.exists(): raise ValueError("Refusing to replace normalizer sidecar")
        np.savez_compressed(path,values=values,fields=np.array(["mean_retained_full_routed_probability","mean_inverse_retained_probability"]))
        info.update(status="complete",raw={"path":str(path),"sha256":n.sha(path),"size_bytes":path.stat().st_size})
        manifest=n.read(n.RESULT/"manifest.json");manifest["normalizer_observation"]=info;n.write(n.RESULT/"manifest.json",manifest)
        return output
    except BaseException as error:
        info.update(status="failed",error=f"{type(error).__name__}: {error}");raise
    finally:
        n.restricted.routing_coverage=original
        n.write(n.RESULT/"execution_adapter.json",info)


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("mode",choices=("test","evaluate"));p.add_argument("--physical-gpu",type=int,default=0)
    args=p.parse_args();torch.set_num_threads(4)
    print(json.dumps(test() if args.mode=="test" else evaluate(args.physical_gpu),indent=2),flush=True)
