"""Execution placement for the unchanged ICES operation and analysis protocols."""
from pathlib import Path
import json,time
_MODELS={}
_RESIDENCY={}
REVISIONS={'Qwen3-8B':'b968826d9c46dd6066d109eabc6255188de91218',
 'Qwen3-32B':'9216db5781bf21249d130ec9da846c4624c16137',
 'Llama-3.1-8B':'1f47e50cdbe801ad8a5174156ec3a0655108fb9f',
 'Llama-3.1-70B':'beb678ba5bd7eb1aafeffa01e2a2b3b5e93d1dd3'}
def scale_revision(path):return REVISIONS[Path(path).name]
def scale_num_devices(model):
    values=set(model.hf_device_map.values())
    assert all(isinstance(x,int) for x in values),values
    return len(values)
def load_scale_model(path):
    import torch
    from transformers import AutoModelForCausalLM
    name=Path(path).name;scale_revision(path)
    # Full FP32 weights/caches/GEMMs, matching the parent scientific protocols.
    # Every engine keeps the inherited full-token/cached and self .001 floor.
    torch.backends.cuda.matmul.allow_tf32=False
    n=torch.cuda.device_count();expected=4 if '70B' in name else 2 if '32B' in name else 1
    assert n==expected,(name,n,expected)
    if path not in _MODELS:
        _RESIDENCY[path]={'started_at':time.time(),'num_devices':n}
        memory={i:torch.cuda.get_device_properties(i).total_memory-10*2**30 for i in range(n)}
        memory['cpu']=0
        model=AutoModelForCausalLM.from_pretrained(path,local_files_only=True,dtype=torch.float32,
            device_map='balanced' if n>1 else {'':0},max_memory=memory,attn_implementation='eager').eval()
        model.requires_grad_(False)
        assert scale_num_devices(model)==n
        assert all(p.dtype==torch.float32 and p.device.type=='cuda' and not p.requires_grad for p in model.parameters())
        _MODELS[path]=model
    return _MODELS[path]
