"""E165 path-only loading adapter; frozen model/metric programs are unchanged."""
import argparse
import copy
import json
from pathlib import Path
import socket

import e165_run as run
c=run.c


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('preflight','run'))
    parser.add_argument('--physical-gpu',type=int,default=0);args=parser.parse_args()
    stage=c.read(c.ROOT/'local_staging.json')
    if stage['status']!='complete' or stage['host']!=socket.gethostname():
        raise ValueError('Matching node-local verified source stage required')
    if stage['asset_manifest_sha256']!=c.sha(c.ROOT/'asset_manifest.json'):
        raise ValueError('Durable source registration changed')
    original=c.load_cpu
    def local(labels,assets,expected=None,phase='canonical'):
        if expected is None:raise ValueError('Local adapter requires prior canonical CPU fingerprints')
        proxy=copy.deepcopy(assets)
        for label in labels:
            source=stage['models'][label];proxy['models'][label]['directory']=source['directory']
            for name,old in assets['models'][label]['files'].items():
                new=source['files'][name]
                if new['sha256']!=old['sha256'] or c.sha(new['path'])!=old['sha256']:
                    raise ValueError('Local asset differs from public/durable source')
                proxy['models'][label]['files'][name]['path']=new['path']
        return original(labels,proxy,expected,phase)
    record={'status':'registered','phase':args.mode,'adapter_sha256':c.sha(__file__),
            'local_stage_sha256':c.sha(c.ROOT/'local_staging.json'),'plan_sha256':c.sha(c.ROOT/'plan.json'),
            'scope':'Only file locators changed; exact public bytes and canonical loaded parameter/buffer/hook fingerprints required.'}
    c.write(c.ROOT/('loading_adapter_'+args.mode+'.json'),record)
    c.load_cpu=local
    try:
        run.main();record['status']='complete'
    except BaseException as error:
        record.update(status='failed',error=type(error).__name__+': '+str(error));raise
    finally:
        c.load_cpu=original;c.write(c.ROOT/('loading_adapter_'+args.mode+'.json'),record)


if __name__=='__main__':main()
