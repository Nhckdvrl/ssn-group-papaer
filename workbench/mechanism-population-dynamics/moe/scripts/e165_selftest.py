"""E165 real native CPU controls and independent statistical known answers."""
import copy
import itertools
import json

import numpy as np
import torch
from transformers import OlmoeConfig, OlmoeForCausalLM
from transformers.models.olmoe.modeling_olmoe import OlmoeSparseMoeBlock

import e165_common as c
import e165_core as core
import e165_analyze as author
import e165_verify as independent
import e153_harness as h


@torch.no_grad()
def native(dtype):
    torch.manual_seed(165); torch.set_num_threads(1)
    cfg = OlmoeConfig(vocab_size=48, hidden_size=16, intermediate_size=8,
            num_hidden_layers=2, num_attention_heads=2, num_key_value_heads=2,
            num_experts=4, num_experts_per_tok=2, norm_topk_prob=False,
            pad_token_id=47, eos_token_id=46, max_position_embeddings=64,
            attention_dropout=0.)
    cfg._attn_implementation = 'eager'
    models = [OlmoeForCausalLM(cfg).to(dtype).eval() for _ in range(2)]
    old = core.blocks(models); states = [copy.deepcopy(m.state_dict()) for m in models]
    seqs = [np.array(x) for x in [(1,2,3,4), (1,2,3,5,6), (1,2,3,7), (1,2,3,8,9,10)]]
    ids, mask = h.padded(seqs,47,'cpu')
    refs = [h.score_candidates(model,seqs,3,47) for model in models]
    for case in author.CASES:
        model = core.assemble(models,old,case)
        for name,value in model.state_dict().items():
            src = case[1] if '.mlp.gate.' in name else case[2] if '.mlp.experts.' in name else case[0]
            assert torch.equal(value,states[src][name]),name
        ll,count,first = h.score_candidates(model,seqs,3,47)
        if case in ((0,0,0),(1,1,1)):
            assert np.array_equal(ll,refs[case[0]][0]) and torch.equal(first,refs[case[0]][2])
        with core.RoutingEngine(model) as engine:
            engine.configure(capture=True)
            with core.restricted(model,np.ones((2,4),bool)):
                a,counts,fp = h.score_candidates(model,seqs,3,47)
            trace = tuple(engine.captured)
            assert np.array_equal(a,ll) and torch.equal(fp,first)
            engine.configure(trace=trace)
            b,_,bp = h.score_candidates(model,seqs,3,47)
            assert np.array_equal(a,b) and torch.equal(fp,bp)
            perm=[2,0,3,1]
            engine.configure(trace=core.permute_trace(trace,perm,4))
            other,oc,op = h.score_candidates(model,[seqs[i] for i in perm],3,47)
            assert np.array_equal(other,b[perm]) and np.array_equal(oc,counts[perm]) and torch.equal(op,bp)
        with core.zero_moe(model):
            _,_,zero = h.score_candidates(model,seqs,3,47)
        assert not torch.equal(zero,first)
    core.restore(models,old)
    for m,state in zip(models,states):
        assert all(torch.equal(v,state[k]) for k,v in m.state_dict().items())
        assert c.state(m,'tiny')['hooks']['total_pre']==c.state(m,'tiny')['hooks']['total_post']==0
    for layer in models[0].model.layers:
        layer.mlp.gate.weight.zero_()
    keep,prob,counts=core.greedy(models[0],[np.array([1,2,3]),np.array([4,5])],47,3,2)
    assert np.array_equal(keep,np.tile([True,True,True,False],(2,1)))
    assert np.allclose(prob,.25) and counts==[5,5]
    traces=[]
    for r in range(2):
        model=core.assemble(models,old,(0,0,r))
        with core.RoutingEngine(model) as engine:
            engine.configure(capture=True)
            with core.restricted(model,keep):h.score_candidates(model,seqs,3,47)
            traces.append(tuple(engine.captured))
    assert all(torch.equal(a,b) for a,b in zip(*traces))
    for r in range(2):
        model=core.assemble(models,old,(0,0,r));values=[]
        for trace in traces:
            with core.RoutingEngine(model) as engine:
                engine.configure(trace=trace)
                with core.restricted(model,keep):values.append(h.score_candidates(model,seqs,3,47)[0])
        assert np.array_equal(*values)
    failed=False
    try:
        with core.restricted(model,keep):
            with core.RoutingEngine(model):h.score_candidates(model,seqs,3,47)
    except ValueError as error:
        failed='precede' in str(error)
    assert failed,'Wrong capture/mask order must fail'
    core.restore(models,old)
    # A native block with analytically known expert outputs and routing probabilities.
    small=OlmoeConfig(hidden_size=4,intermediate_size=1,num_experts=2,num_experts_per_tok=1,norm_topk_prob=False)
    block=OlmoeSparseMoeBlock(small).to(dtype).eval()
    block.gate.weight.zero_();block.gate.weight[0,0]=np.log(3.)
    for i,expert in enumerate(block.experts):
        expert.gate_proj.weight.zero_();expert.up_proj.weight.zero_()
        expert.gate_proj.weight[0,0]=1;expert.up_proj.weight[0,0]=1
        expert.down_proj.weight.fill_(i+1)
    x=torch.tensor([[[1.,0.,0.,0.]]],dtype=dtype)
    original=block(x)[0]
    handle=block.gate.register_forward_hook(lambda module,args,out:out[:,[1,0]])
    changed=block(x)[0];handle.remove()
    if dtype==torch.float32:
        expected=.75*float(torch.nn.functional.silu(torch.tensor(1.)))
        assert torch.allclose(original,torch.full_like(original,expected),atol=1e-6)
    assert torch.equal(changed,2*original) and not torch.equal(original,changed)
    return {'dtype':str(dtype),'source_cube_and_native_corners_exact':True,
            'real_route_identity_mask_permutation_and_prefix_exact':True,
            'constant_gate_no_false_route_effect':True,'wrong_hook_order_rejected':True,
            'native_known_answer_before':float(original[0,0,0]),'native_known_answer_after':float(changed[0,0,0])}


def statistics():
    rng=np.random.default_rng(165)
    ll=rng.normal(-4,2,(26,440,4));gold=rng.integers(0,4,440)
    a={'candidate_loglikelihood':ll,'first_answer_token_KL':rng.random((26,440)),
       'subject':np.repeat(np.arange(55),8),'gold':gold,
       'answer_tokens':rng.integers(1,8,(440,4)),'answer_chars':rng.integers(2,35,(440,4)),
       'conditions':np.array(author.CONDITIONS),'natural_LL':np.stack([ll[[0,8]],ll[[7,15]]]),
       'trace_hashes':np.full((2,2,440),'a'*64),'gate0_hashes':np.full((2,2,440),'b'*64)}
    names=['subject_'+str(i) for i in range(55)]
    result=independent.verify(a,author.summarize(a,names),names)
    x=np.zeros((26,440))
    for p in range(2):
        for i,(d,g,e) in enumerate(author.CASES):
            x[p*8+i]=1+2*d+3*g+5*e+7*g*e+11*d*g*e+p*(1+2*e)
    x[16]=4;x[17]=10;x[18]=7;x[19]=13
    values=author.contrasts(x,'true_answer_token_NLL')
    assert np.all(values['full/three_way']==11)
    assert np.all(values['full/G_x_E_other_0']==7)
    assert np.all(values['full/G_x_E_other_1']==18)
    assert np.all(values['full/D_x_MoE_matching_cost']==-5.5)
    assert np.all(values['full/actual_route/interaction']==-7)
    return result


def main():
    checks=[native(dtype) for dtype in (torch.float32,torch.bfloat16)]
    fixture=statistics()
    assert not torch.cuda.is_initialized()
    c.write(c.ROOT/'CPU_tests.json',{'status':'passed','CUDA_initialized':False,'native_controls':checks,
            'independent_statistics_fixture':fixture,'source_sha256':c.proof(),
            'scope':'Synthetic native-interface and scoring controls only; no mature-model prediction results.'})
    print(json.dumps({'status':'passed','native_dtypes':2,'statistics':fixture,'CUDA_initialized':False}))


if __name__=='__main__':main()
