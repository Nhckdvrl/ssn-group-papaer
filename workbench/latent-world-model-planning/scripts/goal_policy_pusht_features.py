"""Frozen published PushT observation features, first86 fact episodes only."""
import json
import shutil
from pathlib import Path
import h5py
import numpy as np
import torch
import effect_transfer as t
from fixed_data_train_seed import normalized_pixels,state_hash
from experience_transfer_control_audit import ROOT,WB,read,save,sha


@torch.inference_mode()
def main():
    out=Path('/tmp/latent-wm-data/E14-goalpolicy-pusht-RELEASED-frozen-features')
    durable=ROOT/'20261005-E14-goalpolicy-pusht-RELEASED-features'
    assert not out.exists() and not durable.exists();out.mkdir(parents=True);shutil.copy2(__file__,out/'used.py')
    try:
        model,cfg,mean,std,norm_sha=t.load_source('cuda');model.eval().requires_grad_(False)
        initial=state_hash(model.state_dict());dataset=Path('/tmp/latent-wm-data/pusht_expert_train.h5')
        fresh={v['episode'] for v in read(ROOT/'20261005-E20-pusht-fresh-control-bank48/ledger.json')}
        episodes=list(range(86));assert not set(episodes)&fresh
        encoded=[];actions=[];ids=[];layout=[];rows=0;checks=[]
        with h5py.File(dataset,'r') as f:
            lens=f['ep_len'][:];offsets=f['ep_offset'][:];assert len(lens)>=86 and f['pixels'].shape[1:]==(224,224,3)
            action_key='actions' if 'actions' in f else 'action'
            for episode in episodes:
                start=int(offsets[episode]);length=int(lens[episode]);stop=start+length
                assert length>=2 and stop<=len(f['pixels'])
                layout.append(dict(episode=episode,source_row=start,cache_row=rows,frames=length));rows+=length
                act=np.asarray(f[action_key][start:stop]);assert act.shape==(length,2)
                actions.append(act);ids.append(np.full(length,episode,np.int64))
                for begin in range(start,stop,64):
                    images=np.asarray(f['pixels'][begin:min(begin+64,stop)]);x=normalized_pixels(images,'cuda')
                    y=model.projector(model.encoder(x,interpolate_pos_encoding=True).last_hidden_state[:,0])
                    assert y.shape==(len(x),192) and torch.isfinite(y).all()
                    if begin==start and episode in [0,43,85]:
                        native=model.encode({'pixels':x[:,None]})['emb'][:,0]
                        assert torch.equal(native,y)
                        singles=model.projector(model.encoder(x[:1],interpolate_pos_encoding=True).last_hidden_state[:,0])
                        assert torch.allclose(singles,y[:1],atol=2e-4,rtol=1e-5)
                        checks.append(dict(episode=episode,native_encode_exact=True,batch_subset_error=float((singles-y[:1]).abs().max())))
                    encoded.append(y.cpu().numpy())
                print('Push goal-policy encoded fact episode',episode,rows,flush=True)
        assert initial==state_hash(model.state_dict())
        values=dict(features=np.concatenate(encoded),actions=np.concatenate(actions),episode_ids=np.concatenate(ids))
        assert values['features'].shape==(rows,192)
        for key,value in values.items():np.save(out/f'{key}.npy',value)
        save(out/'config.json',dict(task='pusht',geometry='RELEASED',source_checkpoint=str(t.SOURCE),source_sha256=t.SOURCE_SHA,model_config=cfg,frozen_model_sha256=initial,dataset_node_local_path=str(dataset),dataset_sha256='not rehashed during export; referenced pinned existing local HDF asset',layout=layout,training_episodes=episodes,excluded_fresh_eval_episodes=sorted(fresh),pixel_normalization='original224 RGB /255 ImageNet, FP32 frozen encoder/projector',action_coordinates='original raw physical, no standardization',unused_cem_action_normalization_sha256=norm_sha,array_sha256={key:sha(out/f'{key}.npy') for key in values},native_controls=checks,script_sha256=sha(__file__),source_loader_sha256=sha(t.__file__),hardware=torch.cuda.get_device_name(),scope='Head training episode exclusion only; released encoder pretraining overlap unknown. No hidden states, eval-goal/outcome labels, or simulator interaction in features.'))
        save(out/'complete.json',dict(completed=True,episodes=86,frames=rows,frozen_model_unchanged=True));shutil.copytree(out,durable)
    except Exception as error:
        save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));shutil.copytree(out,durable);raise


if __name__=='__main__':torch.set_num_threads(4);main()
