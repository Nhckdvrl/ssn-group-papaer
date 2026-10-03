"""Resume the one missing E51 shard directly, then verify before publishing marker."""
import hashlib
import json
from pathlib import Path
from download_network import configure_direct_downloads

ENDPOINT = configure_direct_downloads()
from huggingface_hub import hf_hub_download

ROOT = Path('/data1/xiangding/work/pragmatic-inference-calibration')
MODEL = 'allenai/OLMo-2-1124-13B'
REVISION = '3fefddc1bf18a30e1d9b91000271630718f2aa8b'


def main():
    target = ROOT/'models'/MODEL.split('/')[-1]
    assert not (target/'DOWNLOAD_COMPLETE.json').exists()
    meta = json.loads((ROOT/'data/OLMo-2-1124-13B-mirror-metadata.json').read_text())
    assert meta['sha'] == REVISION and meta['id'] == MODEL
    assets = {x['rfilename']: x for x in meta['siblings']}
    files = sorted(set(json.loads((target/'model.safetensors.index.json').read_text())['weight_map'].values()))
    missing = [f for f in files if not (target/f).exists()]
    assert missing == ['model-00011-of-00012.safetensors'], missing
    verified = []
    for f in files:
        if f in missing:
            continue
        a = assets[f]
        lines = (target/'.cache/huggingface/download'/(f+'.metadata')).read_text().splitlines()
        # Metadata acquired from the official endpoint before switching transport.
        assert lines[0] == REVISION and lines[1] == a['lfs']['sha256']
        assert (target/f).stat().st_size == a['size'] == a['lfs']['size']
        verified.append(f)
    f = missing[0]
    incomplete = list((target/'.cache/huggingface/download').glob('*.'+assets[f]['lfs']['sha256']+'.incomplete'))
    assert len(incomplete) == 1
    old_bytes = incomplete[0].stat().st_size
    print(json.dumps({'direct_only': True, 'endpoint': ENDPOINT, 'resume_bytes': old_bytes,
                      'remaining_bytes': assets[f]['size']-old_bytes}), flush=True)
    path = Path(hf_hub_download(MODEL, f, revision=REVISION, local_dir=target,
                               endpoint=ENDPOINT, token=False))
    assert path.stat().st_size == assets[f]['size']
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8*1024*1024), b''):
            digest.update(chunk)
    assert digest.hexdigest() == assets[f]['lfs']['sha256']
    audit = {'model': MODEL, 'revision': REVISION, 'direct_only': True,
             'endpoint': ENDPOINT, 'resumed_from_bytes': old_bytes,
             'new_weight_bytes': path.stat().st_size-old_bytes,
             'new_shard_sha256': digest.hexdigest(), 'new_shard_verified': f,
             'cached_shard_official_metadata_and_size_verified': verified,
             'all_cached_shards_rehashed': False, 'selected_weight_files': files}
    (ROOT/'data/E51-direct-download-audit.json').write_text(json.dumps(audit, indent=2)+'\n')
    (target/'DOWNLOAD_COMPLETE.json').write_text(json.dumps(audit, indent=2)+'\n')
    print(json.dumps({'complete': True, 'new_weight_bytes': audit['new_weight_bytes']}), flush=True)


if __name__ == '__main__':
    main()
