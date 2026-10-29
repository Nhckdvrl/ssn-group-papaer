"""Resume only the CPU-interrupted family, preserving the complete OLMoE matrix."""
import argparse
import json
import os
import subprocess
import sys
import e166_common as c


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--physical-gpu',type=int,default=1);args=parser.parse_args()
    plan=c.checked_plan();old=c.read(c.ROOT/'supervision_emo.json');interruption=c.read(c.ROOT/'CPU_NFS_interruption.json')
    if old['status']!='failed' or old['returncode']!=-15 or interruption['GPU_attempts_for_emo']!=0:
        raise ValueError('Registered CPU-only interruption required')
    olmoe=c.read(c.ROOT/'olmoe_manifest.json');original=c.read(c.ROOT/'supervision_olmoe.json')
    if olmoe['status']!='complete' or original['status']!='complete' or original['returncode']!=0:
        raise ValueError('Complete original OLMoE source matrix required')
    if c.sha(olmoe['raw']['path'])!=olmoe['raw']['sha256']:raise ValueError('Preserved OLMoE raw changed')
    if any((c.RAW/'emo'/name).exists() for name in ('calibration.npz','scores.npz','partial_scores.npz')):
        raise FileExistsError('No previous EMO calibration or scores may be overwritten')
    status=c.ROOT/'supervision_emo_resume.json'
    subprocess.run([sys.executable,'-B',str(c.SCRIPTS/'supervised_process.py'),'--status',str(status),
         '--log',str(c.ROOT/'run_emo_resume.log'),'--cwd',str(c.WB),'--timeout','28800','--',sys.executable,'-B','-u',
         str(c.SCRIPTS/'e166_emo_local.py'),'emo','--physical-gpu',str(args.physical_gpu)],cwd=c.WB,check=True)
    state=c.read(status)
    if state['status']!='complete' or state['returncode']!=0:raise ValueError('Recovered family not complete')
    env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
    for name in ('e166_analyze.py','e166_verify.py'):
        subprocess.run([sys.executable,'-B',str(c.SCRIPTS/name)],cwd=c.WB,env=env,check=True)
    seconds=sum(row['gpu_seconds'] for row in c.read(c.ROOT/'budget.json')['attempts'])
    if seconds>plan['gpu_limit_seconds'] or c.read(c.ROOT/'independent_audit.json')['status']!='passed':raise ValueError('Invalid result package')
    c.write(c.ROOT/'execution_complete.json',{'experiment':'E166','status':'complete',
            'numerical_source_commit':plan['numerical_source_commit'],'gpu_seconds':seconds,
            'plan_sha256':c.sha(c.ROOT/'plan.json'),'independent_audit_sha256':c.sha(c.ROOT/'independent_audit.json'),
            'manifest_sha256':{f:c.sha(c.ROOT/(f+'_manifest.json')) for f in ('emo','olmoe')},
            'summary_sha256':{f:c.sha(c.ROOT/(f+'_summary.json')) for f in ('emo','olmoe')},
            'CPU_only_interruption':c.record(c.ROOT/'CPU_NFS_interruption.json'),
            'supervision':{'olmoe':'supervision_olmoe.json','emo':'supervision_emo_resume.json','chain':'supervision_resume_chain.json'},
            'resource_adapter_sha256':c.sha(c.SCRIPTS/'e166_emo_local.py'),'resume_sha256':c.sha(__file__),
            'new_training':0,'no_automatic_followup':True})
    print(json.dumps({'status':'complete','GPU_seconds':seconds}),flush=True)


if __name__=='__main__':main()
