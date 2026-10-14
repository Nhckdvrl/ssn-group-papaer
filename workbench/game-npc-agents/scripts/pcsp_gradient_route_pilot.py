#!/usr/bin/env python3
"""E25 original trainer; consistency-target gradient route control only."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import sys
import time


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,default=Path('/home/xiang/.cache/game-npc-research/sources/pcsp'))
    ap.add_argument('--embeddings',type=Path,default=Path('/home/xiang/.cache/game-npc-research/runs/e23_embedding_context/proper_pool.npy'))
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--route',choices=['full','no_consist','readout_only'],required=True)
    ap.add_argument('--iterations',type=int,default=1)
    ap.add_argument('--seed',type=int,default=42)
    ap.add_argument('--device',choices=['cpu','cuda'],default='cuda')
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    sys.path.insert(0,str(args.source/'research'))
    import numpy as np
    import torch
    from src.env.mini_inzoi import PersonaConfig
    from src.env.mini_inzoi_v3_large import MiniInzoiV3LargeEnv,N_AGENTS
    from src.env.v3_constants import OBS_DIM_V3_LARGE,N_ACTIONS_V3
    from src.training.pcsp_trainer import PCSPActorCritic,TrajectoryEncoder,PCSPTrainer,PCSPConfig
    torch.set_num_threads(1)
    torch.manual_seed(args.seed);np.random.seed(args.seed);random.seed(args.seed)
    if torch.cuda.is_available():torch.cuda.manual_seed_all(args.seed)
    torch.backends.cudnn.deterministic=True
    torch.backends.cudnn.benchmark=False
    torch.backends.cuda.matmul.allow_tf32=False
    torch.backends.cudnn.allow_tf32=False
    dump=lambda name,obj:(args.out/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
    records=json.loads((args.source/'research/data/personas/train_400_v3.json').read_text())
    embeddings=np.load(args.embeddings).astype(np.float32)
    train_emb=embeddings[[int(r['id'])-1 for r in records]]
    vectors=[torch.from_numpy(e).unsqueeze(0) for e in train_emb]
    rng=np.random.default_rng(args.seed)
    def sampler():
        chosen=rng.choice(len(records),N_AGENTS,replace=False)
        return [PersonaConfig.from_dict(records[i]) for i in chosen], {
            f'agent_{j}':{'e_llm':vectors[i]} for j,i in enumerate(chosen)}
    def factory(personas):return MiniInzoiV3LargeEnv(personas=personas,max_steps=200)

    class RoutedTrainer(PCSPTrainer):
        def _consistency_loss(self,trajectories):
            if args.route!='readout_only':return super()._consistency_loss(trajectories)
            hook=self.policy.persona_proj.register_forward_hook(lambda module,inputs,output:output.detach())
            try:return super()._consistency_loss(trajectories)
            finally:hook.remove()

    cfg=PCSPConfig(seed=args.seed)
    if args.route=='no_consist':cfg.lambda_consistency=0.
    policy=PCSPActorCritic(OBS_DIM_V3_LARGE,N_ACTIONS_V3)
    reader=TrajectoryEncoder(OBS_DIM_V3_LARGE,N_ACTIONS_V3)
    trainer=RoutedTrainer(policy,reader,cfg,args.device)
    def param_hash(module):
        h=hashlib.sha256()
        for key,value in module.state_dict().items():h.update(key.encode());h.update(value.detach().cpu().numpy().tobytes())
        return h.hexdigest()
    initial=param_hash(policy)
    dump('manifest.json',{'source_sha':'5420f7b4fa0fdb6110e131402af9f5386ce2d0cf',
        'harness_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'route':args.route,
        'iterations':args.iterations,'seed':args.seed,'device':args.device,'initial_policy_hash':initial,
        'cfg':vars(cfg),'encoder_array_sha256':hashlib.sha256(args.embeddings.read_bytes()).hexdigest(),
        'world_or_reward_changed':False,'cloud_calls':0})
    start=time.monotonic();all_e=torch.from_numpy(train_emb).to(trainer.device)
    for iteration in range(args.iterations):
        trainer.iteration=iteration
        before=time.monotonic()
        transitions,rewards,trajectories=trainer.collect_rollout(factory,sampler,cfg.n_episodes_per_iter)
        if iteration==0:
            loss=trainer._consistency_loss(trajectories)
            audit=trainer.attributable_gradient_norms(loss)
            if args.route=='readout_only':
                assert audit['persona_projection']==audit['actor']==audit['critic']==0
                assert audit['trajectory_encoder']>0
            elif args.route=='full':assert audit['persona_projection']>0 and audit['trajectory_encoder']>0
            dump('gradient_gate.json',audit)
            # Actual first native episodes are retained, rather than a tensor
            # fixture being presented as trained behavioral evidence.
            np.savez_compressed(args.out/'first_rollout.npz',
                obs=np.asarray([t['obs'] for t in transitions],dtype=np.float32),
                actions=np.asarray([t['action'] for t in transitions],dtype=np.int64),
                rewards=np.asarray([t['reward'] for t in transitions],dtype=np.float32))
        stats=trainer.update(transitions,trajectories,all_e)
        row={'iteration':iteration,'mean_ep_reward':float(np.mean(rewards)),'n_transitions':len(transitions),
            'iteration_seconds':time.monotonic()-before,**stats}
        trainer.metrics.append(row)
        with (args.out/'metrics.jsonl').open('a') as trace:trace.write(json.dumps(row)+'\n')
        print(json.dumps(row),flush=True)
    torch.save(policy.state_dict(),args.out/'policy.pt')
    torch.save(reader.state_dict(),args.out/'traj_encoder.pt')
    torch.save({'policy_optimizer':trainer.optimizer.state_dict(),'reader_optimizer':trainer.traj_optimizer.state_dict(),
        'torch_cpu_rng':torch.get_rng_state(),'torch_cuda_rng':torch.cuda.get_rng_state_all() if torch.cuda.is_available() else [],
        'sampler_rng':rng.bit_generator.state,'numpy_rng':np.random.get_state(),'python_rng':random.getstate()},args.out/'training_state.pt')
    dump('summary.json',{'route':args.route,'iterations':args.iterations,'initial_policy_hash':initial,
        'final_policy_hash':param_hash(policy),'final_reader_hash':param_hash(reader),'final_metric':trainer.metrics[-1],
        'wall_seconds':time.monotonic()-start,'world_or_reward_changed':False,'cloud_calls':0,'scientific_increment':0})


if __name__=='__main__':main()
