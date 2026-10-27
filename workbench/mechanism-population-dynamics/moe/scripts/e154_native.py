"""E154 public mature parent: ancestry of necessity and restricted-compute traits."""
import argparse
import os
_p=argparse.ArgumentParser(add_help=False)
_p.add_argument("--physical-gpu",type=int,default=0)
_early,_=_p.parse_known_args()
if os.environ.get("CUDA_VISIBLE_DEVICES") not in (None,"",str(_early.physical_gpu)):
    raise ValueError("GPU visibility differs")
os.environ["CUDA_VISIBLE_DEVICES"]=str(_early.physical_gpu)
os.environ["CUBLAS_WORKSPACE_CONFIG"]=":4096:8"
import importlib
import json
import sys
import types
from pathlib import Path
import numpy as np
import torch
from torch import nn
import e150_native as n
import e151_native as v
import e154_assets as a

RESULT=a.RESULT
RAW=Path.home()/"mechpop_cache/e154_native_parent_boundary"
CONDITIONS=("native","own_prefix","prefixA","prefixB","random0","random1","random2","routed_zero","shared_zero")


def metadata(complete=False):
    m=n.read(RESULT/("asset_manifest.json" if complete else "metadata.json"))
    if m["status"]!=("complete" if complete else "metadata_complete"):
        raise ValueError("Matching pinned parent asset stage required")
    files=m["model"]["files"]
    if complete and sum(k.endswith(".safetensors") for k in files)!=11:
        raise ValueError("All eleven parent shards must be verified")
    for name,record in files.items():
        path=Path(record["path"])
        if path.stat().st_size!=record["size_bytes"]:
            raise ValueError("Parent asset size changed")
        if not name.endswith(".safetensors") and n.sha(path)!=record["sha256"]:
            raise ValueError("Parent small asset bytes changed")
    return m


def classes():
    root=Path(metadata()["model"]["path"])
    name="codex_e154_parent"
    if name not in sys.modules:
        package=types.ModuleType(name)
        package.__path__=[str(root)]
        sys.modules[name]=package
    cfg=importlib.import_module(name+".configuration_emo").EmoConfig
    model=importlib.import_module(name+".modeling_emo").EmoForCausalLM
    return cfg,model,root


def proof():
    p={**n.proof(),**{f:n.sha(n.WB/"scripts"/f) for f in ("e151_native.py","e154_native.py","e154_assets.py","e150_prepare_assets.py")}}
    for name in ("config.json","configuration_emo.py","modeling_emo.py","tokenizer.json","tokenizer_config.json"):
        p["parent/"+name]=metadata()["model"]["files"][name]["sha256"]
    return p


@torch.no_grad()
def self_test():
    torch.set_num_threads(1)
    torch.manual_seed(154)
    cfg_cls,cls,_=classes()
    cfg=cfg_cls(vocab_size=64,hidden_size=16,intermediate_size=8,num_hidden_layers=2,num_attention_heads=2,
                num_key_value_heads=2,num_experts=4,num_experts_per_tok=2,num_shared_experts=1,
                norm_topk_prob=False,max_position_embeddings=32,pad_token_id=63,eos_token_id=62,output_router_logits=False)
    cfg._attn_implementation="eager"
    tiny=cls(cfg).eval()
    _,a_cls,_=n.classes(0)
    old=a_cls(cfg).eval()
    old.load_state_dict(tiny.state_dict(),strict=True)
    ids=torch.tensor([[1,2,3,4,5,6],[7,8,9,10,11,12]])
    for dtype in (torch.float32,torch.bfloat16):
        tiny.to(dtype)
        old.to(dtype)
        state=n.old.tensor_hash(tiny.state_dict())
        buffer_hash=n.old.tensor_hash(n.buffers(tiny))
        original=n.fwd(tiny,ids,torch.ones_like(ids))
        assert torch.equal(original,n.fwd(old,ids,torch.ones_like(ids)))
        keep=n.restricted.prefix_keep(tiny,ids[:,:3],3)
        assert keep.shape==(2,2,4) and np.all(keep.sum(-1)==3) and keep[:,:,-1].all()
        with n.restricted.restricted_gates(tiny,np.ones((2,2,4),bool)):
            assert torch.equal(original,n.fwd(tiny,ids,torch.ones_like(ids)))
        with v.suppress(tiny,"routed"):
            assert not torch.equal(original,n.fwd(tiny,ids,torch.ones_like(ids)))
        with v.suppress(tiny,"shared"):
            assert not torch.equal(original,n.fwd(tiny,ids,torch.ones_like(ids)))
        assert n.old.tensor_hash(tiny.state_dict())==state
        assert n.old.tensor_hash(n.buffers(tiny))==buffer_hash
        assert all(not gate._forward_hooks for gate in n.restricted.gates(tiny))
    module=importlib.import_module("codex_e154_parent.modeling_emo")
    cfg=cfg_cls(hidden_size=4,intermediate_size=4,num_experts=4,num_experts_per_tok=2,num_shared_experts=1,norm_topk_prob=False)
    block=module.EmoSparseMoeBlock(cfg,4,1,None)
    block.gate=v.FixedGate()
    block.experts=nn.ModuleList([v.Constant(x) for x in (2.,4.,8.,10.)])
    layer=nn.Module()
    layer.mlp=block
    container=nn.Module()
    container.model=nn.Module()
    container.model.layers=nn.ModuleList([layer])
    h=torch.ones((1,4,4))
    expected=block(h)[0]
    assert torch.allclose(expected,torch.full_like(expected,10+8/7),atol=1e-6)
    with v.suppress(container,"routed"):
        assert torch.equal(container.model.layers[0].mlp(h)[0],torch.full_like(expected,10))
    with v.suppress(container,"shared"):
        assert torch.allclose(container.model.layers[0].mlp(h)[0],torch.full_like(expected,8/7),atol=1e-6)
    assert torch.equal(block(h)[0],expected)
    result={"status":"passed","CPU_only":True,"source_sha256":proof(),"parent_source_tiny_native_equals_A_code_FP32_BF16":True,
            "prefix_budget_and_shared_retained":True,"full_mask_native_exact":True,"R_S_zero_known_answers":[10,8/7],
            "parameters_buffers_hooks_restored":True}
    n.write(RESULT/"self_test.json",result)
    return {"status":"passed"}


def prepare():
    tests=n.read(RESULT/"self_test.json")
    if tests["status"]!="passed" or tests["source_sha256"]!=proof():
        raise ValueError("Matching parent known-answer tests required")
    p=n.read(n.RESULT/"plan.json")
    prior=n.read(n.RESULT/"manifest.json")
    second=n.read(v.RESULT/"manifest.json")
    if any(m["status"]!="complete" or n.sha(m["raw"]["path"])!=m["raw"]["sha256"] for m in (prior,second)):
        raise ValueError("Complete sealed A/B scientific data required")
    inherited=n.read(v.RESULT/"plan.json")["random_masks"]
    if n.sha(inherited["path"])!=inherited["sha256"]:
        raise ValueError("Random masks changed")
    with np.load(prior["raw"]["path"]) as f:
        prefixes=f["prefix_keeps"].copy()
    with np.load(inherited["path"]) as f:
        random=f["masks"].copy()
    keep=np.concatenate((prefixes,random),axis=0)
    assert keep.shape==(5,64,16,128) and np.all(keep.sum(-1)==32) and keep[:,:,:,-1].all()
    RAW.mkdir(exist_ok=True,parents=True)
    path=RAW/"inherited_masks.npz"
    if path.exists():
        with np.load(path) as f:
            assert np.array_equal(keep,f["masks"])
    else:
        np.savez_compressed(path,masks=keep)
    result={"experiment":"E154","status":"prepared","source_sha256":proof(),"parent_metadata_sha256":n.sha(RESULT/"metadata.json"),
            "E150_manifest_sha256":n.sha(n.RESULT/"manifest.json"),"E151_manifest_sha256":n.sha(v.RESULT/"manifest.json"),
            "input_plan_sha256":n.sha(n.RESULT/"plan.json"),"input":{"path":p["path"],"sha256":p["sha256"]},
            "masks":{"path":str(path),"sha256":n.sha(path)},"conditions":list(CONDITIONS),"selected":p["selected"],
            "scope":"One declared public mature parent and two fixed protocol descendants; no independent initialization or strict training-batch causal chain."}
    n.old.immutable_json(RESULT/"plan.json",result)
    return {"status":"prepared"}


class Budget(n.old.Budget):
    def __init__(self):
        self.path,self.experiment,self.phase,self.limit=RESULT/"budget.json","e154","public_parent_cal_and_traits",3600


@torch.no_grad()
def evaluate(physical):
    own=n.read(RESULT/"plan.json")
    tests=n.read(RESULT/"self_test.json")
    assets=metadata(complete=True)
    if own["source_sha256"]!=proof() or tests["source_sha256"]!=proof():
        raise ValueError("Frozen parent source differs")
    for filename,key in ((n.RESULT/"manifest.json","E150_manifest_sha256"),(v.RESULT/"manifest.json","E151_manifest_sha256"),
                         (n.RESULT/"plan.json","input_plan_sha256"),(RESULT/"metadata.json","parent_metadata_sha256")):
        if n.sha(filename)!=own[key]:
            raise ValueError("Frozen parent comparison dependency changed")
    for record in (own["input"],own["masks"]):
        if n.sha(record["path"])!=record["sha256"]:
            raise ValueError("Frozen inherited input/masks changed")
    with np.load(own["input"]["path"]) as f:
        held=f["held"].copy()
        valid=f["held_mask"].copy()
        cal=f["cal"][:2,:129].copy()
        cv=f["cal_mask"][:2,:128].copy()
    with np.load(own["masks"]["path"]) as f:
        fixed=f["masks"].copy()
    lock=None
    try:
        with Budget() as budget:
            lock=n.old.gpu_lock(physical)
            budget.check()
            cfg_cls,cls,root=classes()
            cfg=cfg_cls.from_json_file(root/"config.json")
            model,info=cls.from_pretrained(root,config=cfg,dtype=torch.float32,local_files_only=True,
                                          attn_implementation="sdpa",output_loading_info=True)
            if any(info.get(k) for k in ("missing_keys","unexpected_keys","mismatched_keys","error_msgs")):
                raise ValueError("Parent checkpoint keys do not match source")
            model=model.to("cuda:0").eval().requires_grad_(False)
            if sum(p.numel() for p in model.parameters())!=13568641024:
                raise ValueError("Unexpected parent parameter count")
            ids=torch.from_numpy(cal.astype(np.int64)).to("cuda:0")
            am=torch.cat((torch.ones((2,1),dtype=torch.bool,device="cuda:0"),torch.from_numpy(cv).to("cuda:0")),1)
            fp32=n.fwd(model,ids[:,:-1],am[:,:-1]).float().log_softmax(-1)
            model.bfloat16()
            torch.cuda.empty_cache()
            reference=n.fwd(model,ids[:,:-1],am[:,:-1])
            if not torch.equal(reference,n.fwd(model,ids[:,:-1],am[:,:-1])):
                raise ValueError("Parent native repeat differs")
            with n.restricted.restricted_gates(model,np.ones((2,16,128),bool)):
                if not torch.equal(reference,n.fwd(model,ids[:,:-1],am[:,:-1])):
                    raise ValueError("Parent all-slot identity differs")
            bf16=reference.float().log_softmax(-1)
            precision=n.data.masked_mean(n.old.prediction_metrics(fp32,bf16,ids[:,1:]).cpu().numpy(),cv)
            layer=model.model.layers[9].mlp
            try:
                model.model.layers[9].mlp=n.Zero(layer.gate)
                zero=n.fwd(model,ids[:,:-1],am[:,:-1]).float().log_softmax(-1)
            finally:
                model.model.layers[9].mlp=layer
            positive=n.data.masked_mean(n.old.prediction_metrics(bf16,zero,ids[:,1:]).cpu().numpy(),cv)
            if torch.equal(zero,bf16):
                raise ValueError("Parent zero-layer control failed")
            path=RAW/"cal_native_bf16.npz"
            if path.exists():
                raise ValueError("Refusing to replace parent calibration")
            np.savez_compressed(path,logits=reference.contiguous().view(torch.uint16).cpu().numpy())
            n.write(RESULT/"preflight.json",{"status":"complete","source_sha256":proof(),"FP32_to_BF16_metrics_per_sequence":precision.tolist(),
                    "zero_L9_metrics_per_sequence":positive.tolist(),"fields":list(n.old.METRICS),
                    "raw":{"path":str(path),"sha256":n.sha(path)},"repeat_exact":True,"full_slot_exact":True,"keys_strict":True})
            del fp32,bf16,zero,reference,ids,am,layer
            before=n.old.tensor_hash(model.state_dict())
            before_buffers=n.old.tensor_hash(n.buffers(model))
            values=np.empty((9,64,512,4),np.float32)
            own_keeps=np.empty((64,16,128),bool)
            for start in range(0,64,4):
                budget.check()
                ids=torch.from_numpy(held[start:start+4].astype(np.int64)).to("cuda:0")
                am=torch.cat((torch.ones((len(ids),1),dtype=torch.bool,device="cuda:0"),torch.from_numpy(valid[start:start+4]).to("cuda:0")),1)
                own_keep=n.restricted.prefix_keep(model,ids[:,:128],32)
                own_keeps[start:start+4]=own_keep
                reference=n.fwd(model,ids[:,:-1],am[:,:-1]).float().log_softmax(-1)
                values[0,start:start+4]=n.old.prediction_metrics(reference,reference,ids[:,1:]).cpu().numpy()
                for index,keep in enumerate([own_keep]+[fixed[j,start:start+4] for j in range(5)],start=1):
                    budget.check()
                    with n.restricted.restricted_gates(model,keep):
                        current=n.fwd(model,ids[:,:-1],am[:,:-1]).float().log_softmax(-1)
                    values[index,start:start+4]=n.old.prediction_metrics(reference,current,ids[:,1:]).cpu().numpy()
                    del current
                for index,which in ((7,"routed"),(8,"shared")):
                    budget.check()
                    with v.suppress(model,which):
                        current=n.fwd(model,ids[:,:-1],am[:,:-1]).float().log_softmax(-1)
                    values[index,start:start+4]=n.old.prediction_metrics(reference,current,ids[:,1:]).cpu().numpy()
                    del current
                del ids,am,reference
                n.old.emit("E154_parent_batch",sequences=start+4,peak_GB=torch.cuda.max_memory_allocated()/1e9)
            if n.old.tensor_hash(model.state_dict())!=before or n.old.tensor_hash(n.buffers(model))!=before_buffers:
                raise ValueError("Parent source parameters/buffers changed")
            path=RAW/"metrics.npz"
            if path.exists():
                raise ValueError("Refusing to replace parent raw")
            suffix=valid&(np.arange(512)[None,:]>=127)
            np.savez_compressed(path,metrics=values,valid=valid,suffix_valid=suffix,own_prefix_masks=own_keeps,
                                conditions=np.array(CONDITIONS),fields=np.array(n.old.METRICS))
            n.write(RESULT/"manifest.json",{"experiment":"E154","status":"complete","source_sha256":proof(),
                    "plan_sha256":n.sha(RESULT/"plan.json"),"asset_manifest_sha256":n.sha(RESULT/"asset_manifest.json"),
                    "raw":{"path":str(path),"sha256":n.sha(path),"size_bytes":path.stat().st_size},
                    "controls":{"native_cal_repeat_exact":True,"all_slot_native_exact":True,"zero_L9_changes_prediction":True,
                                "inherited_masks_exact":True,"source_parameters_buffers_unchanged":True},
                    "source_parameter_hash":before,"source_buffer_hash":before_buffers,"physical_gpu":physical,
                    "visible_device_uuid":str(torch.cuda.get_device_properties(0).uuid),"peak_allocated_bytes":torch.cuda.max_memory_allocated(),
                    "scope":"Declared public parent, nine fixed interventions, old language inputs and two sealed descendants; no training."})
    finally:
        if lock is not None:
            lock.close()
    return {"status":"complete"}


if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode",choices=("self-test","prepare","evaluate"))
    p.add_argument("--physical-gpu",type=int,default=0)
    args=p.parse_args()
    torch.set_num_threads(4)
    result=self_test() if args.mode=="self-test" else prepare() if args.mode=="prepare" else evaluate(args.physical_gpu)
    print(json.dumps(result,indent=2),flush=True)
