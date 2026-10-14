"""E38 numerical qualification of the author's explicitly independent reader.

This is an implementation audit, not a novel readout/control separation claim.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import time


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp-meltingpot-audit'))
    ap.add_argument('--episode',type=Path,default=Path('/home/xiang/.cache/game-npc-research/runs/e38_policy_episode_pilot_v1/correct_s1_full_cooperative_sustainer_w38011'))
    ap.add_argument('--out',type=Path,required=True)
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(args.source))
    import numpy as np
    import torch
    from src.persona.projection import build_conditioning_head
    from src.persona.trajectory_encoder import TrajectoryEncoder,InfoNCEHead
    from src.training.cleanrl_ppo.networks import ActorCritic
    torch.set_num_threads(1);torch.manual_seed(38051);start=time.monotonic()
    data=np.load(args.episode/'native.npz');summary=json.loads((args.episode/'summary.json').read_text())
    cache=torch.load('/home/xiang/.cache/game-npc-research/runs/e38_embedding_qualification/persona_emb_correct_pool.pt',map_location='cpu',weights_only=False)
    ids=cache['ids'];table=cache['embeddings'].float().detach()
    targets=torch.tensor([ids.index(x) for x in summary['persona_ids']])
    candidates=torch.tensor([ids.index(x) for x in ['cooperative_sustainer','selfish_harvester','cautious_observer','aggressive_zapper','reciprocator','explorer','territorial_defender','risk_seeking_raider','cleaner_helper','free_rider']])
    agent=ActorCritic(obs_height=88,obs_width=88,obs_channels=3,num_actions=8,feature_dim=256,
                     conditioning=build_conditioning_head('concat',256,1024))
    reader=TrajectoryEncoder(num_actions=8,traj_dim=64,hidden_dim=128,include_reward=True)
    head=InfoNCEHead(64,1024,temperature=.1)
    optimizer=torch.optim.Adam(list(agent.parameters())+list(reader.parameters())+list(head.parameters()),lr=2.5e-4)
    a=torch.from_numpy(data['actions'][:128]);r=torch.from_numpy(data['rewards'][:128])
    done=torch.zeros_like(r);obs=torch.from_numpy(data['focal_rgb']);persona=table[targets[summary['focal_slot']]].repeat(len(obs),1)
    def model_hash(model):
        h=hashlib.sha256()
        for k,v in model.state_dict().items():h.update(k.encode());h.update(v.numpy().tobytes())
        return h.hexdigest()
    initial_hash=model_hash(agent)
    with torch.no_grad():initial_logits=agent.policy_logits(obs,persona).clone()
    gradients=[];losses=[]
    for _ in range(4):
        loss,stats=head(reader(a,r,done),table,targets,candidate_indices=candidates)
        optimizer.zero_grad(set_to_none=True);(.5*loss).backward()
        gradients.append({'agent_nonzero':sum(p.grad is not None and bool((p.grad!=0).any()) for p in agent.parameters()),
                          'reader_nonzero':sum(p.grad is not None and bool((p.grad!=0).any()) for p in reader.parameters()),
                          'head_nonzero':sum(p.grad is not None and bool((p.grad!=0).any()) for p in head.parameters())})
        torch.nn.utils.clip_grad_norm_(list(reader.parameters())+list(head.parameters()),.5)
        optimizer.step();losses.append(float(loss))
    with torch.no_grad():after_logits=agent.policy_logits(obs,persona)
    assert initial_hash==model_hash(agent) and torch.equal(initial_logits,after_logits)
    action=torch.from_numpy(data['actions'][data['frame_steps'],summary['focal_slot']])
    logp,entropy,value=agent.evaluate(obs,action,persona=persona)
    target=torch.from_numpy(data['rewards'][data['frame_steps'],summary['focal_slot']])
    ppo_fixture=-(logp*(target-target.mean())).mean()+.5*((value-target)**2).mean()-.01*entropy.mean()
    optimizer.zero_grad(set_to_none=True);ppo_fixture.backward()
    positive={name:sum(p.grad is not None and bool((p.grad!=0).any()) for p in module.parameters())
              for name,module in [('actor',agent.actor),('encoder',agent.encoder),('conditioning',agent.conditioning)]}
    assert all(v>0 for v in positive.values())
    result={'source':'root PHASE5 CleanRL; distinct from research CNN-FiLM and Mini-Inzoi',
            'InfoNCE_steps':4,'losses':losses,'gradient_groups':gradients,
            'agent_parameter_hash_before':initial_hash,'agent_parameter_hash_after':model_hash(agent),
            'all_policy_logits_byte_equal':torch.equal(initial_logits,after_logits),
            'positive_PPO_fixture_nonzero_groups':positive,
            'scope':'Author-defined independent reader confirmed numerically; fixture is not trained PHASE5 performance or a novelty claim.',
            'input_native_episode':str(args.episode),'reward_table_frozen':not table.requires_grad,
            'wall_seconds':time.monotonic()-start,'cloud_calls':0,
            'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (args.out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
