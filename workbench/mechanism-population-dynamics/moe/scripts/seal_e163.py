"""Seal completed E163 raw, numerical sources and real public source files.

No large model weights are copied. Tar entries are checked byte for byte;
Hugging Face symlinks are resolved before inclusion, so the archived source
remains usable without the original cache's symlink targets.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

WB=Path(__file__).resolve().parents[2]
ROOT=WB/'moe/results/e163'
RAW=Path.home()/'mechpop_cache/e163_message_geometry'


def sha(path):
    with Path(path).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def read(path):return json.loads(Path(path).read_text())


def main():
    manifest=read(ROOT/'manifest.json');plan=read(ROOT/'plan.json');audit=read(ROOT/'independent_audit.json')
    if manifest['status']!='complete' or audit['status']!='passed':raise ValueError('Complete audited E163 required')
    if read(ROOT/'supervision_CPU_finish.json')['status']!='complete':raise ValueError('CPU finisher must have a durable successful exit')
    if manifest['plan_sha256']!=sha(ROOT/'plan.json') or manifest['summary_sha256']!=sha(ROOT/'summary.json'):
        raise ValueError('Sealed scientific inputs changed')
    for name,expected in plan['source_sha256'].items():
        if sha(WB/'moe/scripts'/name)!=expected:raise ValueError('Frozen source changed '+name)
    commit=subprocess.check_output(['git','rev-parse','--short=8','HEAD'],cwd=WB,text=True).strip()
    target=RAW/('run_metadata_'+commit+'.tar.gz')
    if target.exists() or (ROOT/'artifact_seal.json').exists():raise FileExistsError('Preserve the previous package')
    entries={}
    for name in (*plan['source_sha256'],'e163_plot.py','e163_finish.py','seal_e163.py','reproduce.py','e163_cpu_priority.py'):
        entries['repo/moe/scripts/'+name]=WB/'moe/scripts'/name
    for path in ROOT.rglob('*'):
        if path.is_file() and path.suffix in ('.json','.log','.png','.pdf') and not path.name.endswith('.tmp'):
            entries['repo/moe/results/e163/'+str(path.relative_to(ROOT))]=path
    for name in ('README.md','PAPER_SHAPE.md','RESEARCH_DIRECTION.md','ASSETS.md'):
        entries['repo/moe/'+name]=WB/'moe'/name
    entries['repo/moe/experiments/E163-native-message-geometry-and-reuse.md']=WB/'moe/experiments/E163-native-message-geometry-and-reuse.md'
    for name in ('CLAIMS.md','PAIN_LOG.md','AGENTS.md'):
        entries['repo/'+name]=WB/name
    for path in RAW.glob('*.npz'):entries['raw/'+path.name]=path
    for path in (RAW/'attempt_1_KL_reduction').rglob('*'):
        if path.is_file() and path.suffix in ('.py','.npz','.json'):
            entries['raw/attempt_1_KL_reduction/'+str(path.relative_to(RAW/'attempt_1_KL_reduction'))]=path
    assets=read(WB/'moe/results/e150/asset_manifest.json')['models']
    source={'P':read(WB/'moe/results/e154/asset_manifest.json')['model'],
            'A':assets['StdMoE_1b14b_1T'],'B':assets['StdMoE_1b14b_1T_EmoAnnealed'],'F':plan['F_asset']}
    public={}
    for label,model in source.items():
        public[label]={}
        for name,proof in model['files'].items():
            if not (name.endswith('.py') or name in ('config.json','model.safetensors.index.json')):continue
            path=Path(proof['path']).resolve()
            if not path.is_file() or sha(path)!=proof['sha256']:raise ValueError('Public native source changed')
            arc='public_source/'+label+'/'+name;entries[arc]=path;public[label][name]=proof['sha256']
    records={name:{'path':str(path),'sha256':sha(path),'size_bytes':path.stat().st_size} for name,path in entries.items()}
    with tarfile.open(target,'w:gz',dereference=True) as archive:
        for name,path in entries.items():archive.add(path.resolve(),arcname=name,recursive=False)
    with tarfile.open(target,'r:gz') as archive:
        for item in archive:
            if not item.isfile() or item.issym():raise AssertionError('Archive contains a nonmaterialized source')
            with archive.extractfile(item) as stream:actual=hashlib.file_digest(stream,'sha256').hexdigest()
            if actual!=records[item.name]['sha256']:raise AssertionError('Archive entry changed '+item.name)
    seal={'experiment':'E163','status':'sealed','result_commit':commit,'frozen_numerical_commit':plan.get('numerical_source_commit','19f6f3a5'),
          'plan_sha256':sha(ROOT/'plan.json'),'summary_sha256':sha(ROOT/'summary.json'),
          'source_result_package':{'path':str(target),'sha256':sha(target),'size_bytes':target.stat().st_size},
          'entries':records,'public_source_materialized_sha256':public,
          'raw':manifest['raw'],'gpu_seconds':manifest['gpu_seconds'],
          'large_model_weights_duplicated':False,'canonical_public_models_retained':True,
          'CPU_A100_attempt_retained':True,'source_dependencies_included':True}
    (ROOT/'artifact_seal.json').write_text(json.dumps(seal,indent=2)+'\n')
    print(json.dumps({'status':'sealed','package':seal['source_result_package'],'entries':len(entries)},indent=2))


if __name__=='__main__':main()
