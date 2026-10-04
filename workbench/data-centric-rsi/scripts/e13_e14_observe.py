"""Archive scheduling transitions to account for preflight and parallel wait costs."""
import argparse
import datetime as dt
import json
from pathlib import Path
import time


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--state',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();last=None
    with a.out.open('x') as f:
        while True:
            s=json.loads(a.state.read_text())
            r={'observed_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'status':s['status'],
               'active':s['active'],'completed_names':[x['name'] for x in s['runs']]}
            signature=json.dumps([r['status'],r['active'],r['completed_names']],sort_keys=True)
            if signature!=last:
                f.write(json.dumps(r)+chr(10));f.flush();last=signature
            if s.get('finished_utc'):break
            time.sleep(5)

if __name__=='__main__':main()
