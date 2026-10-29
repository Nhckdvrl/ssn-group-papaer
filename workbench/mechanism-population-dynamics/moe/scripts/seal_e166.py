"""Seal complete two-family gain evidence and original references as real files."""
import hashlib
import json
from pathlib import Path
import subprocess
import tarfile

WB=Path(__file__).resolve().parents[2]
ROOT=WB/'moe/results/e166'
RAW=Path.home()/'mechpop_cache/e166_gain_transport'


def read(p):return json.loads(Path(p).read_text())


def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def main():
    plan=read(ROOT/'plan.json');end=read(ROOT/'execution_complete.json');audit=read(ROOT/'independent_audit.json')
    if end['status']!='complete' or audit['status']!='passed' or end['plan_sha256']!=sha(ROOT/'plan.json'):
        raise ValueError('Completed, audited two-family result required')
    if sha(ROOT/'independent_audit.json')!=end['independent_audit_sha256']:raise ValueError('Audit changed')
    supervision=end.get('supervision',{phase:'supervision_'+phase+'.json' for phase in ('chain','emo','olmoe')})
    for name in supervision.values():
        s=read(ROOT/name)
        if s['status']!='complete' or s['returncode']!=0:raise ValueError('Successful terminal exit missing')
    for f in ('emo','olmoe'):
        for kind in ('manifest','summary'):
            if sha(ROOT/(f+'_'+kind+'.json'))!=end[kind+'_sha256'][f]:raise ValueError('Scientific artifact changed')
    for name,digest in plan['source_sha256'].items():
        if sha(WB/'moe/scripts'/name)!=digest:raise ValueError('Frozen numerical program changed')
    commit=subprocess.check_output(['git','rev-parse','--short=8','HEAD'],cwd=WB,text=True).strip()
    target=RAW/('run_metadata_'+commit+'.tar.gz')
    if target.exists() or (ROOT/'artifact_seal.json').exists():raise FileExistsError('Preserve previous package')
    entries={}
    def verified(item,name):
        p=Path(item['path']).resolve()
        if sha(p)!=item['sha256']:raise ValueError('Pinned bytes changed: '+name)
        entries[name]=p
    for name in (*plan['source_sha256'],'seal_e166.py','moe_paper_figures.py','reproduce.py',
                 'e166_stage_emo.py','e166_emo_local.py','e166_resume.py'):
        entries['repo/moe/scripts/'+name]=WB/'moe/scripts'/name
    for p in ROOT.rglob('*'):
        if p.is_file() and p.suffix in ('.json','.log') and p.name!='artifact_seal.json':
            entries['repo/moe/results/e166/'+str(p.relative_to(ROOT))]=p
    for p in RAW.rglob('*'):
        if p.is_file() and p.suffix in ('.npz','.json','.log'):
            entries['raw/'+str(p.relative_to(RAW))]=p
    for family,spec in plan['families'].items():
        for key in ('input','selectors','reference','previous_plan','previous_manifest'):
            verified(spec[key],'inputs/'+family+'/'+key+'/'+Path(spec[key]['path']).name)
        prior=read(spec['previous_plan']['path'])
        if family=='emo':
            for label,files in prior['public_source_files'].items():
                for name,item in files.items():verified(item,'public_source/emo/'+label+'/'+name)
            for label,record in spec['source_records'].items():
                if 'calibration' in record:verified(record['calibration'],'inputs/emo/'+label+'_calibration.npz')
        else:
            assets=read(spec['asset_manifest']['path'])
            verified(spec['asset_manifest'],'public_source/olmoe/asset_manifest.json')
            for label,model in assets['models'].items():
                for name,item in model['files'].items():
                    if not name.endswith('.safetensors'):verified(item,'public_source/olmoe/'+label+'/'+name)
    for module,item in plan['software']['native_sources'].items():verified(item,'native_software/'+module+'.py')
    data=read(WB/'moe/results/e164/data_plan.json');verified(data['texts'],'inputs/original_text/questions.jsonl')
    for p in (WB/'moe/paper').rglob('*'):
        if p.is_file() and p.suffix in ('.tex','.pdf','.png','.json'):
            entries['repo/moe/paper/'+str(p.relative_to(WB/'moe/paper'))]=p
    for name in ('README.md','PAPER_SHAPE.md','RESEARCH_DIRECTION.md','ASSETS.md'):
        entries['repo/moe/'+name]=WB/'moe'/name
    for name in ('CLAIMS.md','PAIN_LOG.md','AGENTS.md'):entries['repo/'+name]=WB/name
    p=WB/'moe/experiments/E166-gain-matched-property-transport.md';entries['repo/moe/experiments/'+p.name]=p
    p=WB/'moe/notes/PRIMARY_READING_ARGUMENT_2026-10-29.json';entries['repo/moe/notes/'+p.name]=p
    entries['repo/library/SELECTABLE_COMPUTATION_AND_HISTORY_2026-10-29.md']=WB.parents[1]/'library/themes/moe-routing/SELECTABLE_COMPUTATION_AND_HISTORY_2026-10-29.md'
    records={name:{'path':str(p),'sha256':sha(p),'size_bytes':p.stat().st_size} for name,p in entries.items()}
    with tarfile.open(target,'w:gz',dereference=True) as archive:
        for name,p in entries.items():archive.add(p.resolve(),arcname=name,recursive=False)
    with tarfile.open(target,'r:gz') as archive:
        for member in archive:
            if not member.isfile() or member.issym():raise ValueError('Unresolved source link')
            with archive.extractfile(member) as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
            if digest!=records[member.name]['sha256']:raise ValueError('Archive entry changed')
    seal={'experiment':'E166','status':'sealed','result_commit':commit,
          'frozen_numerical_commit':plan['numerical_source_commit'],'plan_sha256':sha(ROOT/'plan.json'),
          'source_result_package':{'path':str(target),'sha256':sha(target),'size_bytes':target.stat().st_size},
          'entries':records,'gpu_seconds_registered_timer':end['gpu_seconds'],
          'model_weights_in_package':False,'inherited_references_preserved':True}
    (ROOT/'artifact_seal.json').write_text(json.dumps(seal,indent=2)+'\n')
    print(json.dumps({'status':'sealed','package':seal['source_result_package'],'entries':len(entries)}))


if __name__=='__main__':main()
