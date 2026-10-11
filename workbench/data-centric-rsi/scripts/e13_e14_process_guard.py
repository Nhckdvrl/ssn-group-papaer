"""Track launched descendants across vLLM setproctitle/environment rewriting.

Roots are authenticated by immutable Popen PID/start-tick launch records. Live
ancestry extends ownership; durable PID/start-tick records survive reparenting.
Only the selected closeout attempt is observed. No GPU work is launched.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import signal
import time


def utc(): return dt.datetime.now(dt.timezone.utc).isoformat()
def write(p, value):
    tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(value,indent=2)+chr(10));tmp.replace(p)


def processes():
    result={}
    for p in Path('/proc').iterdir():
        if not p.name.isdigit():continue
        try:
            row=(p/'stat').read_text().rsplit(')',1)[1].split()
            if row[0]!='Z':result[int(p.name)]={'pid':int(p.name),'ppid':int(row[1]),'start_ticks':row[19]}
        except (FileNotFoundError,PermissionError,ProcessLookupError):pass
    return result


def discover(m, known, table):
    root=table.get(m['pid'])
    if root and root['start_ticks']==m['start_ticks']:known[str(root['pid'])]=root
    while True:
        before=len(known)
        live={int(pid) for pid,r in known.items() if pid.isdigit() and int(pid) in table and table[int(pid)]['start_ticks']==r['start_ticks']}
        for pid,r in table.items():
            if r['ppid'] in live:known[str(pid)]=r
        if len(known)==before:break
    return [r for pid,r in known.items() if int(pid) in table and table[int(pid)]['start_ticks']==r['start_ticks']]


def watch(base):
    started=time.time()
    while time.time()-started < 10*3600:
        table=processes()
        for path in base.glob('*/launch.json'):
            m=json.loads(path.read_text()); directory=path.parent
            audit=directory/'descendant_guard.json'
            if audit.exists():result=json.loads(audit.read_text())
            else:result={'launch_pid':m['pid'],'launch_start_ticks':m['start_ticks'],'token':m['token'],'known':{},'first_observed_utc':utc()}
            active=discover(m,result['known'],table)
            owner=table.get(m['owner_pid'])
            owner_alive=owner and owner['start_ticks']==m['owner_ticks']
            end=dt.datetime.fromisoformat(m['started_utc']).timestamp()+m['cap_seconds']
            stop=(directory/'cleanup.json').exists() or not owner_alive or time.time()>=end
            if stop and active:
                result.setdefault('stop_started_utc',utc())
                age=time.time()-dt.datetime.fromisoformat(result['stop_started_utc']).timestamp()
                sig=signal.SIGKILL if age>20 else signal.SIGTERM
                for r in active:
                    current=processes().get(r['pid'])
                    if current and current['start_ticks']==r['start_ticks']:
                        try:os.kill(r['pid'],sig)
                        except ProcessLookupError:pass
            result.update(last_observed_utc=utc(),active_pids=[r['pid'] for r in active],stop_requested=bool(stop))
            if stop and not active:
                result.setdefault('all_descendants_exited_utc',utc()); result['cleanup_complete']=True
            write(audit,result)
        time.sleep(2)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',type=Path,required=True)
    watch(p.parse_args().base)
