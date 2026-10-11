"""G3 bounded 860-episode Push fact cache, preserving existing first86 exactly."""
import shutil
from pathlib import Path
import h5py
import numpy as np
import torch
import effect_transfer as t
import goal_policy_pusht_adapter as a
import goal_policy_baseline as g
from fixed_data_train_seed import normalized_pixels,state_hash


@torch.inference_mode()
def main():
    out=Path('/tmp/latent-wm-data/E14-goalpolicy-pusht-860-frozen-features')
    durable=g.ROOT/'20261005-E14-goalpolicy-pusht-860-features'
    assert not out.exists() and not durable.exists();out.mkdir();shutil.copy2(__file__,out/'used.py')
    try:
        z,raw,ep,_,_,_,meta=a.load('RELEASED',0)
        model,cfg,mean,std,norm=t.load_source('cuda');model.eval().requires_grad_(False);initial=state_hash(model.state_dict())
        assert initial==meta['frozen_model_sha256'] and t.SOURCE_SHA==meta['source_sha256']
        excluded=set(meta['excluded_fresh_eval_episodes']);values=[z];actions=[raw];ids=[ep];layout=list(meta['layout']);rows=len(z);checks=[]
        source=Path(meta['dataset_node_local_path'])
        with h5py.File(source,'r') as f:
            lens=f['ep_len'][:];offsets=f['ep_offset'][:]
            assert len(lens)==18685 and f['pixels'].shape==(2336736,224,224,3)
            added=[e for e in range(86,len(lens)) if e not in excluded][:774];assert len(added)==774
            episodes=list(range(86))+added;assert len(set(episodes))==860 and not set(episodes)&excluded
            g.save(out/'selection.json',dict(training_episodes=episodes,excluded_fresh_eval_episodes=sorted(excluded),selection='first86 retained; append smallest eligible774',source_head_feature_sha256=g.sha(a.CACHE/'features.npy')))
            key='action' if 'action' in f else 'actions'
            for e in added:
                start=int(offsets[e]);length=int(lens[e]);stop=start+length
                assert length>=2 and stop<=len(f['pixels'])
                act=np.asarray(f[key][start:stop]);assert act.shape==(length,2)
                layout.append(dict(episode=e,source_row=start,cache_row=rows,frames=length));rows+=length
                actions.append(act);ids.append(np.full(length,e,np.int64))
                for begin in range(start,stop,64):
                    pixels=np.asarray(f['pixels'][begin:min(begin+64,stop)]);x=normalized_pixels(pixels,'cuda')
                    y=model.projector(model.encoder(x,interpolate_pos_encoding=True).last_hidden_state[:,0])
                    assert y.shape==(len(x),192) and torch.isfinite(y).all()
                    if e in [added[0],added[len(added)//2],added[-1]] and begin==start:
                        native=model.encode({'pixels':x[:,None]})['emb'][:,0]
                        assert torch.equal(native,y);checks.append(dict(episode=e,native_encode_exact=True))
                    values.append(y.cpu().numpy())
                if len(layout)%25==0:print('Push coverage fact encode',len(layout),rows,flush=True)
        assert state_hash(model.state_dict())==initial
        arrays=dict(features=np.concatenate(values),actions=np.concatenate(actions),episode_ids=np.concatenate(ids))
        assert arrays['features'].shape==(rows,192) and np.array_equal(arrays['features'][:len(z)],z)
        assert np.array_equal(arrays['actions'][:len(raw)],raw,equal_nan=True) and np.array_equal(arrays['episode_ids'][:len(ep)],ep)
        for key,value in arrays.items():np.save(out/f'{key}.npy',value)
        g.save(out/'config.json',dict(task='pusht',training_episodes=episodes,excluded_fresh_eval_episodes=sorted(excluded),layout=layout,source_checkpoint=str(t.SOURCE),source_sha256=t.SOURCE_SHA,frozen_model_sha256=initial,original86_feature_metadata=meta,dataset_node_local_path=str(source),dataset_sha256='not rehashed during export',source_episode_count=18685,source_frame_count=2336736,first86_subset_exact=True,array_sha256={key:g.sha(out/f'{key}.npy') for key in arrays},native_controls=checks,script_sha256=g.sha(__file__),source_loader_sha256=g.sha(t.__file__),hardware=torch.cuda.get_device_name(),scope='860 selected fact episodes, not full HDF or published encoder training replication. Original86 cached rows copied bit-exact; only appended facts encoded. Head training excludes fresh48source, published phi pretrain split unknown. No evaluation goals, physical states or outcomes in cache.'))
        g.save(out/'complete.json',dict(completed=True,episodes=860,frames=rows,frozen_model_unchanged=True));shutil.copytree(out,durable)
        print('Push coverage feature cache',rows,'frames DONE',flush=True)
    except Exception as error:g.save(out/'failure.json',dict(type=type(error).__name__,message=str(error)));shutil.copytree(out,durable);raise


if __name__=='__main__':torch.set_num_threads(4);main()
