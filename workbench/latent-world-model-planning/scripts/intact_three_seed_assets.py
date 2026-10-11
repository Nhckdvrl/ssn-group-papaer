"""Retrieve immutable extra published seeds; never overwrite existing assets."""
import hashlib
import json
import shutil
import tarfile
from pathlib import Path
from huggingface_hub import hf_hub_download

WB=Path(__file__).resolve().parents[1]
ROOT=Path('/home/xiang/.cache/latent-wm-results')
HF=Path('/home/xiang/.cache/huggingface/latent-wm-derived')
REVISION='0430df6fcda1b0516d5747ded58acb72ceb1e6e7'


def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as stream:
        for block in iter(lambda:stream.read(8<<20),b''):h.update(block)
    return h.hexdigest()


def save(path,value):
    path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n')


def main():
    out=ROOT/'20261005-E01-intact-three-seed-assets'
    assert not out.exists()
    out.mkdir()
    shutil.copy2(__file__,out/'used.py')
    manifest_path=WB/'vendor/intact-jepa/checkpoints/PAPER_E5_GOAL_MANIFEST.json'
    manifest=json.loads(manifest_path.read_text())
    old=json.loads((ROOT/'20261005-E01-intact-published-assets/complete.json').read_text())
    records=[dict(v,train_seed=0) for v in old['records']]
    save(out/'requested.json',dict(train_seeds=[0,42,3072],tasks=['tworoom','pusht'],revision=REVISION,
         manifest_sha256=sha(manifest_path),script_sha256=sha(__file__)))
    archives=[]
    try:
        for training in manifest['training_seeds']:
            seed=training['seed']
            if seed==0:
                for record in records:
                    assert sha(record['path'])==record['sha256'] and Path(record['path']).stat().st_size==record['bytes']
                continue
            assert seed in [42,3072]
            archive=Path(hf_hub_download('INTACT-JEPA/INTACT',training['asset'],revision=REVISION,
                         cache_dir='/home/xiang/.cache/huggingface/hub'))
            archives.append(dict(seed=seed,path=str(archive),sha256=sha(archive),bytes=archive.stat().st_size))
            target=HF/f'intact-e5-goal-seed{seed}'
            assert not target.exists()
            target.mkdir()
            with tarfile.open(archive) as tar:
                for shard in training['shards']:
                    task=shard['task']
                    if task not in ['tworoom','pusht']:continue
                    member=tar.getmember(shard['path'])
                    assert member.isfile() and member.size==shard['bytes']
                    weight=target/f'{task}.pt'
                    with tar.extractfile(member) as src,weight.open('wb') as dst:shutil.copyfileobj(src,dst)
                    assert weight.stat().st_size==shard['bytes'] and sha(weight)==shard['sha256']
                    parent=target/f'recovery_delta_full_{task}_s{seed}'
                    parent.mkdir()
                    for name in ['config.json','config.yaml','multitask_metadata_epoch_5.json']:
                        m=tar.getmember(str(Path(shard['path']).parent/name))
                        assert m.isfile() and m.size<1<<20
                        with tar.extractfile(m) as src,(parent/name).open('wb') as dst:shutil.copyfileobj(src,dst)
                    meta=json.loads((parent/'multitask_metadata_epoch_5.json').read_text())
                    assert (meta['epoch'],meta['seed'],meta['task'],meta['shared_state_sha256'])==(5,seed,task,training['shared_state_sha256'])
                    records.append(dict(task=task,train_seed=seed,path=str(weight),sha256=shard['sha256'],bytes=shard['bytes']))
                    save(out/'records.json',records)
                    print('Immutable published shard',seed,task,'SHA/meta PASS',flush=True)
            save(out/'archives.json',archives)
        assert len(records)==6
        save(out/'complete.json',dict(completed=True,records=records,archives=archives,resolved_revision=REVISION,
            vendor_commit=old['vendor_commit'],manifest_sha256=sha(manifest_path)))
    except Exception as error:
        save(out/'failure.json',dict(type=type(error).__name__,message=str(error)))
        raise


if __name__=='__main__':main()
