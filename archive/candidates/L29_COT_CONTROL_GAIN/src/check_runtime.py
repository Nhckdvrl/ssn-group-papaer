"""CPU-only architecture/API smoke test; random weights are not research evidence."""
import torch
from transformers import Olmo3Config,Olmo3ForCausalLM

torch.set_num_threads(2); torch.manual_seed(29)
c=Olmo3Config(vocab_size=64,hidden_size=32,intermediate_size=64,num_hidden_layers=4,num_attention_heads=4,num_key_value_heads=4,max_position_embeddings=256,sliding_window=128,layer_types=['sliding_attention']*3+['full_attention'],eos_token_id=2,pad_token_id=0)
m=Olmo3ForCausalLM(c).eval()
x=torch.tensor([[10,11,12,13,14,15]])
with torch.inference_mode():
    out=m(x,labels=x,use_cache=False)
    loss=torch.nn.functional.cross_entropy(out.logits[0,:-1].float(),x[0,1:])
    assert torch.allclose(out.loss,loss,atol=1e-6)
    single=m.generate(x,attention_mask=torch.ones_like(x),max_new_tokens=4,do_sample=False,use_cache=True)
    padded=torch.tensor([[0,0,10,11,12,13,14,15],[16,17,18,19,20,21,22,23]])
    batch=m.generate(padded,attention_mask=padded.ne(0),max_new_tokens=4,do_sample=False,use_cache=True)
    assert torch.equal(single[0,-4:],batch[0,-4:]),(single,batch)
print('CPU API smoke passed: shifted NLL alignment; left-padding cached generation; Olmo3 SDPA. No trained-model evidence.')
