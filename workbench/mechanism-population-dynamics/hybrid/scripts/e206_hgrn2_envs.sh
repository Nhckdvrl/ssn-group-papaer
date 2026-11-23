#!/usr/bin/env bash
# E206 HGRN2: try fla 0.2.2 and 0.6.0 (copies of the tf4.57 env); NLL check on 5 EWT passages, CPU-light, GPU 3 when free.
B=/tmp/xiang_e194
export UV_CACHE_DIR=$B/uv/cache UV_PYTHON_INSTALL_DIR=$B/uv/python UV_NO_CONFIG=1 PYTHONNOUSERSITE=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1
for v in 0.2.2 0.6.0; do
  E=/tmp/xiang_e206_fla$v/env
  [ -x $E/bin/python ] || { mkdir -p /tmp/xiang_e206_fla$v; cp -a /tmp/xiang_e199/env $E; }
  $B/uv/uv-x86_64-unknown-linux-gnu/uv pip install -q --python $E/bin/python "flash-linear-attention==$v" 2>&1 | tail -n 2
  $E/bin/python -c "import fla, transformers; print('ENV', fla.__version__, transformers.__version__)" 2>&1 | tail -n 1
  until [ "$(nvidia-smi -i 3 --query-gpu=memory.used --format=csv,noheader,nounits)" -lt 1000 ]; do sleep 60; done
  CUDA_VISIBLE_DEVICES=3 $E/bin/python -I - <<'PY' 2>&1 | grep -E "NLL|Error|error" | tail -n 3
import json, torch, fla.models  # noqa
from transformers import AutoModelForCausalLM, AutoTokenizer
for name in ("fla_hgrn2", "fla_gla"):
    d = f"/tmp/xiang_hyb/models/{name}"
    tok = AutoTokenizer.from_pretrained("/tmp/xiang_hyb/models/fla_transformer")
    m = AutoModelForCausalLM.from_pretrained(d, torch_dtype=torch.bfloat16).cuda().eval()
    P = json.load(open("/tmp/xiang_e194/passages.json"))["passages"][:5]
    tot = n = 0
    for p in P:
        ids = [tok.bos_token_id] + tok(p["text"], add_special_tokens=False)["input_ids"][:511]
        x = torch.tensor([ids], device="cuda")
        with torch.no_grad():
            lp = m(input_ids=x).logits[0, :-1].float().log_softmax(-1)
        tot += -lp.gather(1, x[0, 1:, None]).sum().item(); n += x.shape[1] - 1
    print("NLL", name, round(tot / n, 3))
PY
done
echo HGRN2_ENVS_DONE
