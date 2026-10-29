"""CPU native known-proportion, identity, zero and inferential known answers."""
import copy
import json
import numpy as np
import torch
from transformers import OlmoeConfig,OlmoeForCausalLM
import e156_loading as loading
import e166_common as c
import e166_core as core
import e166_run as run
import e166_analyze as author
import e166_verify as independent
import e153_harness as h
import e165_core as old
from e164_routing import RoutingEngine
import e151_native as removal


@torch.no_grad()
def native(family,dtype):
    shared=family=='emo';torch.manual_seed(166)
    if shared:cfg_class,model_class,_=loading._classes('P',complete=False)
    else:cfg_class,model_class=OlmoeConfig,OlmoeForCausalLM
    cfg=cfg_class(vocab_size=48,hidden_size=16,intermediate_size=8,num_hidden_layers=2,
            num_attention_heads=2,num_key_value_heads=2,num_experts=4,num_experts_per_tok=2,
            num_shared_experts=1 if shared else 0,norm_topk_prob=False,
            pad_token_id=47,eos_token_id=46,max_position_embeddings=64,attention_dropout=0.)
    cfg._attn_implementation='sdpa' if shared else 'eager'
    parent=model_class(cfg).to(dtype).eval().requires_grad_(False);donor=copy.deepcopy(parent)
    for layer in donor.model.layers:
        for expert in (layer.mlp.experts[:-1] if shared else layer.mlp.experts):expert.down_proj.weight.mul_(2)
    models=[parent,donor];blocks=old.blocks(models);states=[copy.deepcopy(m.state_dict()) for m in models]
    seqs=[np.array(x) for x in [(1,2,3,4),(1,2,3,5,6),(1,2,3,7),(1,2,3,8,9,10)]]
    ids,mask=h.padded(seqs,47,'cpu');baseline=parent(input_ids=ids,attention_mask=mask,use_cache=False).logits
    with core.EnergyCalibration(parent,blocks[1],shared) as observer:
        observed=parent(input_ids=ids,attention_mask=mask,use_cache=False).logits
        assert torch.equal(observed,baseline),'Observer must preserve native output'
        cal=observer.result()
    assert np.array_equal(cal['gain'],[2.,2.]),cal
    assert np.allclose(cal['cosine'],1,atol=1e-6)
    native=h.score_candidates(parent,seqs,3,47)
    with core.gains(parent,np.ones(2),shared):
        unit=h.score_candidates(parent,seqs,3,47)
        assert np.array_equal(unit[0],native[0]) and torch.equal(unit[2],native[2])
    with core.gains(parent,np.zeros(2),shared):zero=h.score_candidates(parent,seqs,3,47)
    with (removal.suppress(parent,'routed') if shared else old.zero_moe(parent)):
        oracle=h.score_candidates(parent,seqs,3,47)
    assert np.array_equal(zero[0],oracle[0]) and torch.equal(zero[2],oracle[2]) and not torch.equal(zero[2],native[2])
    keep=np.tile([True,False,True,True],(2,1))
    for policy in range(2):
        model=run.assemble(models,blocks,0,shared)
        with RoutingEngine(model) as engine:
            engine.configure(capture=True)
            if policy:
                with run.restricted(model,keep,shared):h.score_candidates(model,seqs,3,47)
            else:h.score_candidates(model,seqs,3,47)
            trace=tuple(engine.captured)
        outputs=[]
        for r in (1,2):
            model=run.assemble(models,blocks,int(r==1),shared)
            with run.ExitStack() as stack:
                engine=stack.enter_context(RoutingEngine(model));engine.configure(trace=trace)
                if policy:stack.enter_context(run.restricted(model,keep,shared))
                if r==2:stack.enter_context(core.gains(model,cal['gain'],shared))
                outputs.append(h.score_candidates(model,seqs,3,47))
        assert np.array_equal(outputs[0][0],outputs[1][0]) and torch.equal(outputs[0][2],outputs[1][2]),'Known 2P donor must equal GainP'
    old.restore(models,blocks)
    for model,state in zip(models,states):
        assert all(torch.equal(v,state[k]) for k,v in model.state_dict().items())
        assert old.hook_fingerprint(model)['total_post']==old.hook_fingerprint(model)['total_pre']==0
    return {'family':family,'dtype':str(dtype),'calibrated_gain':[float(v) for v in cal['gain']],
            'known_proportional_donor_predictions_exact':True,'unit_and_zero_native_oracles_exact':True,
            'observer_and_source_readonly_exact':True,'pool_fixed_route_multitoken_causal_scoring':True}


def fixture(family):
    rng=np.random.default_rng(166);n=len(author.cases(family))
    a={'candidate_loglikelihood':rng.normal(-4,2,(n,440,4)),'gold':rng.integers(0,4,440),
       'answer_tokens':rng.integers(1,8,(440,4)),'answer_chars':rng.integers(2,30,(440,4)),
       'subject':np.repeat(np.arange(55),8),'conditions':np.array(author.conditions(family)),
       'first_answer_token_KL':rng.random((n,440)),'trace_hashes':np.full((2,440),'x'*64)}
    names=['s'+str(i) for i in range(55)]
    report=independent.verify(a,author.summarize(a,names,family),names,family)
    if family=='emo':
        x=np.array([np.full(440,1+2*r+3*p+5*s+7*r*s+11*r*p) for r,p,s in author.cases(family)])
        out=author.contrasts(x,family,'true_answer_token_NLL')
        assert np.all(out['full/S_role/donor_minus_P']==7)
        assert np.all(out['pool/S0/donor_minus_P']==20)
        assert np.all(out['mask_damage/S1/donor_minus_P']==11)
    return report


def main():
    torch.set_num_threads(1)
    controls=[native(f,d) for f in ('emo','olmoe') for d in (torch.float32,torch.bfloat16)]
    fixtures={f:fixture(f) for f in ('emo','olmoe')}
    assert not torch.cuda.is_initialized()
    c.write(c.ROOT/'CPU_tests.json',{'status':'passed','native_controls':controls,
            'independent_statistics_fixture':fixtures,'source_sha256':c.proof(),'CUDA_initialized':False})
    print(json.dumps({'status':'passed','controls':controls,'statistics':fixtures}))


if __name__=='__main__':main()
