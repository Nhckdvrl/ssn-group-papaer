"""H2 B1 source features, with a one-time node-local raw-data copy."""
import argparse
import hashlib
import shutil
import time
from pathlib import Path
import numpy as np
import torch
import intact_published_control_v3 as a
import fixed_controller_model as m
from experience_transfer_control_audit import ROOT, read, save, sha


@torch.inference_mode()
def run(task):
    a.setup()
    source_bank = ROOT/f'20261005-E14-fixed-controller-experience-{task}'
    assert read(source_bank/'complete.json')['n'] == 1632
    out = ROOT/f'20261005-E14-fixed-controller-features-{task}'
    assert not out.exists()
    out.mkdir()
    shutil.copy2(__file__,out/'used.py')
    try:
        local = Path('/tmp/latent-wm-data')/f'E14-fixed-controller-{task}'
        assert not local.exists()
        stage_start = time.monotonic()
        shutil.copytree(source_bank,local)
        stage_time = time.monotonic()-stage_start
        source_cfg, cfg = read(source_bank/'config.json'),read(local/'config.json')
        assert source_cfg == cfg and sha(local/'rows.json') == sha(source_bank/'rows.json')
        rows, proposals = read(local/'rows.json'),read(local/'candidates.json')
        assert cfg['candidates_sha256'] == sha(local/'candidates.json') and cfg['memory_images_sha256'] == sha(local/'memory_images.npy')
        memory = np.load(local/'memory_images.npy')
        original_bank = Path(cfg['source_bank'])
        ledger = read(original_bank/'ledger.json')
        goal_images = [np.load(original_bank/f'goal_{j:03d}.npy') for j in range(48)]
        net,processor,source = a.source(task,'cuda')
        assert source == cfg['source']
        original = a.state_hash(net.state_dict())
        cache,values = {},{k:[] for k in ['z','goal','previous','commands','complete_macro','frozen','anchor','candidate','method','steps','initial_success','native_success']}

        def encode(image):
            key = hashlib.sha256(image.tobytes()).hexdigest()
            if key not in cache:
                cache[key] = net.encode(dict(pixels=a.pixels(image[None,None],'cuda')))['emb'][0,0].cpu().numpy()
            return cache[key].copy()

        for index,row in enumerate(rows):
            j,c,method = row['anchor'],row['candidate'],row['method']
            path = local/f'trace_{j:03d}_c{c:02d}_{method}.npz'
            assert row['trace_sha256'] == sha(path)
            with np.load(path) as raw:
                assert raw['commands'].shape == (25,2) and raw['observations'].shape == (6,224,224,3)
                z = np.asarray([encode(image) for image in raw['observations']])
                mid = proposals[j]['memory_ids'][c]
                assert mid == row['memory_id']
                query_image = goal_images[j] if mid == -1 else memory[mid]
                goal = encode(query_image)
                previous = processor.scaler.transform(np.asarray(ledger[j]['warm_actions'][-5:],dtype=np.float32)).reshape(10).astype(np.float32)
                commands = processor.scaler.transform(raw['commands']).reshape(5,10).astype(np.float32)
                args = [torch.from_numpy(v[None]).cuda() for v in [z[0],goal,previous]]
                predicted,imagined_commands = m.option(net,net,None,*args,method)
                if index == 0:
                    actual_plan = net.get_action(a.info(raw['observations'][0],query_image,ledger[j]['warm_actions'],processor,'cuda'),horizon=5)
                    assert torch.equal(actual_plan,imagined_commands)
                    assert np.array_equal(z[0],net.encode(dict(pixels=a.pixels(raw['observations'][:1,None],'cuda')))['emb'][0,0].cpu().numpy())
                    cpu,_,cpu_source = a.source(task,'cpu')
                    assert cpu_source == source
                    cpu_z = cpu.encode(dict(pixels=a.pixels(raw['observations'][:1,None],'cpu')))['emb'][0,0].numpy()
                    np.testing.assert_allclose(z[0],cpu_z,atol=2e-4,rtol=1e-5)
                    del cpu
                for key,v in [('z',z),('goal',goal),('previous',previous),('commands',commands),('complete_macro',np.ones(5,bool)),('frozen',np.concatenate([z[:1],predicted[0].cpu().numpy()])),('anchor',j),('candidate',c),('method',m.METHODS.index(method)),('steps',25),('initial_success',row['initial_success']),('native_success',row['native_success_anytime'])]:
                    values[key].append(v)
            if index%136==135:
                print('H2 fixed physical feature cache',task,index+1,'/1632',flush=True)
        assert original == a.state_hash(net.state_dict())
        path = out/'features.npz'
        np.savez_compressed(path,**{k:np.asarray(v) for k,v in values.items()})
        save(out/'config.json',dict(task=task,source=source,source_bank=str(source_bank),source_config_sha256=sha(source_bank/'config.json'),source_rows_sha256=sha(source_bank/'rows.json'),script_sha256=sha(__file__),option_helper_sha256=sha(m.__file__),actor_helper_sha256=sha(a.__file__),features_sha256=sha(path),train_anchors=m.TRAIN,held_anchors=m.HELD,rows=1632,unique_B1_images=len(cache),stage_seconds=stage_time,stage_bytes=sum(p.stat().st_size for p in local.iterdir() if p.is_file()),local_stage=str(local),hardware=torch.cuda.get_device_name(),preflight=dict(passed=True,B1_visual_exact=True,source_open_plan_exact=True,CPU_CUDA_original_visual_tolerance=True),scope='All five actual physical prefixes and issued macros; no artificial absorption labels. TRAIN/HELD balanced near/far; node-local raw stage, compact shared feature cache only.'))
        save(out/'complete.json',dict(completed=True,n=1632,encoder_unchanged=True))
    except Exception as error:
        save(out/'failure.json',dict(type=type(error).__name__,message=str(error)))
        raise


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--task',choices=['tworoom','pusht'],required=True)
    run(p.parse_args().task)
