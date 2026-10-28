"""Briefly prioritize F CPU I/O, then always resume the registered PAB job.

Never starts a model, changes sources, holds a GPU, or selects conditions.
The wait ends on F CPU readiness/failure or after 20 minutes. Exact PID/PGID
and absence of any GPU ledger are required before pausing PAB.
"""
import json
import os
from pathlib import Path
import signal
import time

ROOT=Path(__file__).resolve().parents[1]/'results/e163'


def read(path):return json.loads(Path(path).read_text())


def write(state):
    path=ROOT/'CPU_IO_priority.json';tmp=path.with_suffix('.tmp')
    tmp.write_text(json.dumps(state,indent=2)+'\n');os.replace(tmp,path)


def main():
    pid=read(ROOT/'supervision_PAB.json')['child_pid']
    command=Path('/proc',str(pid),'cmdline').read_bytes().replace(b'\x00',b' ').decode()
    if '--group PAB --physical-gpu 2' not in command or 'e163_run.py run' not in command or os.getpgid(pid)!=pid:
        raise ValueError('PAB exact process identity differs')
    if (ROOT/'budget_PAB.json').exists() or (ROOT/'CPU_readiness_F.json').exists():
        raise ValueError('Only initial CPU preparation may be prioritized')
    if (ROOT/'CPU_IO_priority.json').exists():raise FileExistsError('Keep previous scheduling record')
    start=time.monotonic();state={'status':'CPU_IO_priority','host':os.uname().nodename,'PAB_pid':pid,
        'PAB_command':command,'started_UTC':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
        'maximum_seconds':1200,'GPU_reserved_by_scheduler':False,'scientific_conditions_changed':False}
    stopped=False
    try:
        os.killpg(pid,signal.SIGSTOP);stopped=True;write(state)
        while time.monotonic()-start<1200:
            if (ROOT/'CPU_readiness_F.json').exists():state['reason']='F CPU readiness reached';break
            if read(ROOT/'supervision_F.json')['status'] in ('failed','complete'):
                state['reason']='F supervision terminal';break
            state['elapsed_seconds']=time.monotonic()-start;write(state);time.sleep(10)
        else:state['reason']='20-minute priority bound reached'
    finally:
        if stopped:
            # Retain PID identity before signaling the original process group.
            current=Path('/proc',str(pid),'cmdline').read_bytes().replace(b'\x00',b' ').decode()
            if current!=command or os.getpgid(pid)!=pid:raise ValueError('PID changed before resume')
            os.killpg(pid,signal.SIGCONT)
        state.update(status='resumed',elapsed_seconds=time.monotonic()-start,
                     ended_UTC=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()))
        write(state)


if __name__=='__main__':main()
