"""Materialize audited E165 inputs, numerical source closure and metadata, no weights."""
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

WB=Path(__file__).resolve().parents[2]
ROOT=WB/'moe/results/e165'
RAW=Path.home()/'mechpop_cache/e165_mature_olmoe_transport'


def read(p):return json.loads(Path(p).read_text())


def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    plan=read(ROOT/'plan.json');manifest=read(ROOT/'manifest.json');end=read(ROOT/'execution_complete.json')
    if manifest['status']!='complete' or end['status']!='complete' or read(ROOT/'independent_audit.json')['status']!='passed':
        raise ValueError('Completed audited execution required')
    for phase in ('chain','preflight','run'):
        state=read(ROOT/('supervision_'+phase+'.json'))
        if state['status']!='complete' or state['returncode']!=0:raise ValueError('Missing successful durable exit')
    for name in ('plan','manifest','summary','independent_audit'):
        if sha(ROOT/(name+'.json'))!=end[name+'_sha256']:raise ValueError('Scientific artifact changed')
    for name,digest in plan['source_sha256'].items():
        if sha(WB/'moe/scripts'/name)!=digest:raise ValueError('Frozen numerical source changed: '+name)
    if sha(manifest['raw']['path'])!=manifest['raw']['sha256']:raise ValueError('Raw changed')
    commit=subprocess.check_output(['git','rev-parse','--short=8','HEAD'],cwd=WB,text=True).strip()
    target=RAW/('run_metadata_'+commit+'.tar.gz')
    if target.exists() or (ROOT/'artifact_seal.json').exists():raise FileExistsError('Preserve earlier seal')
    entries={}
    for name in (*plan['source_sha256'],'e165_finish.py','e165_stage_local.py','e165_local_adapter.py',
                 'moe_paper_figures.py','seal_e165.py','reproduce.py'):
        entries['repo/moe/scripts/'+name]=WB/'moe/scripts'/name
    for p in ROOT.rglob('*'):
        if p.is_file() and p.suffix in ('.json','.log','.png','.pdf') and p.name!='artifact_seal.json':
            entries['repo/moe/results/e165/'+str(p.relative_to(ROOT))]=p
    for p in RAW.rglob('*'):
        if p.is_file() and p.suffix in ('.npz','.jsonl','.json','.log'):
            entries['raw/'+str(p.relative_to(RAW))]=p
    data=read(plan['data_plan']['path'])
    for key in ('data','source_texts'):
        item=data.get(key)
        if item is not None and isinstance(item,dict) and 'path' in item:
            p=Path(item['path'])
            if sha(p)!=item['sha256']:raise ValueError('Input text changed')
            entries['inputs/'+key+'/'+p.name]=p
    # Tokenization's raw source lives in E164 and is not duplicated by the E165 loader.
    texts=WB/'moe/results/e164/data_plan.json'
    for key in ('texts',):
        item=read(texts)[key];p=Path(item['path'])
        if sha(p)!=item['sha256']:raise ValueError('Original text changed')
        entries['inputs/original_text/'+p.name]=p
    public={}
    for label,model in read(plan['asset_manifest']['path'])['models'].items():
        public[label]={}
        for name,item in model['files'].items():
            if name.endswith('.safetensors'):continue
            p=Path(item['path']).resolve()
            if sha(p)!=item['sha256']:raise ValueError('Public source changed')
            entries['public_source/'+label+'/'+name]=p;public[label][name]=item['sha256']
    for module,item in plan['software']['native_sources'].items():
        p=Path(item['path']).resolve()
        if sha(p)!=item['sha256']:raise ValueError('Installed native source changed')
        entries['native_software/'+module+'.py']=p
    for p in (WB/'moe/paper').rglob('*'):
        if p.is_file() and p.suffix in ('.tex','.pdf','.png','.json'):
            entries['repo/moe/paper/'+str(p.relative_to(WB/'moe/paper'))]=p
    for name in ('README.md','PAPER_SHAPE.md','RESEARCH_DIRECTION.md','ASSETS.md'):
        entries['repo/moe/'+name]=WB/'moe'/name
    for name in ('CLAIMS.md','PAIN_LOG.md','AGENTS.md'):entries['repo/'+name]=WB/name
    for name in ('E165-mature-olmoe-selection-transport.md','E166-gain-matched-property-transport.md'):
        entries['repo/moe/experiments/'+name]=WB/'moe/experiments'/name
    p=WB/'moe/notes/PRIMARY_READING_ARGUMENT_2026-10-29.json';entries['repo/moe/notes/'+p.name]=p
    records={name:{'path':str(p),'sha256':sha(p),'size_bytes':p.stat().st_size} for name,p in entries.items()}
    with tarfile.open(target,'w:gz',dereference=True) as archive:
        for name,p in entries.items():archive.add(p.resolve(),arcname=name,recursive=False)
    with tarfile.open(target,'r:gz') as archive:
        for member in archive:
            if not member.isfile() or member.issym():raise ValueError('Unresolved package link')
            with archive.extractfile(member) as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
            if digest!=records[member.name]['sha256']:raise ValueError('Package SHA mismatch')
    seal={'experiment':'E165','status':'sealed','result_commit':commit,
          'frozen_numerical_commit':plan['numerical_source_commit'],'plan_sha256':sha(ROOT/'plan.json'),
          'summary_sha256':sha(ROOT/'summary.json'),'raw':manifest['raw'],
          'source_result_package':{'path':str(target),'sha256':sha(target),'size_bytes':target.stat().st_size},
          'entries':records,'public_source_materialized_sha256':public,
          'gpu_seconds_registered_timer':end['gpu_seconds'],'model_weights_in_package':False}
    (ROOT/'artifact_seal.json').write_text(json.dumps(seal,indent=2)+'\n')
    print(json.dumps({'status':'sealed','entries':len(entries),'package':seal['source_result_package']}))


if __name__=='__main__':main()
