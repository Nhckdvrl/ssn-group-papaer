"""E166 EMO loader locator override; original FP32->CPU BF16 program unchanged."""
import json
import socket
import e166_run as run
import e156_loading as loader
c=run.c


def main():
    stage=c.read(c.ROOT/'emo_local_staging.json');plan=c.checked_plan()
    if stage['status']!='complete' or stage['host']!=socket.gethostname() or stage['plan_sha256']!=c.sha(c.ROOT/'plan.json'):
        raise ValueError('Matching verified node stage required')
    original=loader._classes
    def local(label,*,complete):
        cfg,cls,durable=original(label,complete=complete)
        root=stage['models'][label]
        for name,item in root['files'].items():
            if c.sha(item['path'])!=item['sha256']:raise ValueError('Staged bytes changed')
        from pathlib import Path
        return cfg,cls,Path(root['directory'])
    record={'status':'registered','adapter_sha256':c.sha(__file__),'stage_sha256':c.sha(c.ROOT/'emo_local_staging.json'),
            'plan_sha256':c.sha(c.ROOT/'plan.json'),'frozen_source_sha256':plan['source_sha256'],
            'scope':'Only checkpoint directory changes; native class, kwargs, CPU FP32 conversion, buffers and exact historical guards unchanged.'}
    c.write(c.ROOT/'emo_loading_adapter.json',record);loader._classes=local
    try:run.main();record['status']='complete'
    except BaseException as error:record.update(status='failed',error=str(error));raise
    finally:loader._classes=original;c.write(c.ROOT/'emo_loading_adapter.json',record)


if __name__=='__main__':main()
