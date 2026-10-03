"""Finite E57 collector: all jobs and audits required, no claim updates."""
import json
import subprocess
import time
from pathlib import Path
from exposure_data import ROOT,specs,sha

PY='/data1/xiangding/env/pragmatic-inference-calibration/bin/python'


def main():
    script=Path(__file__).with_name('summarize_exposure.py')
    frozen={p.name:sha(p) for p in (script,Path(__file__).with_name('exposure_data.py'),
        Path(__file__).with_name('run_exposure.py'),Path(__file__).with_name('run_exposure_r2.py'))}
    status=ROOT/'data/E57-collector-status.json'
    output=Path(__file__).resolve().parents[1]/'results/E57-exposure-summary.json'
    expected=[]
    for m in specs(ROOT):
        cp=m['id'].split('/')[-1]
        expected.append(ROOT/'runs'/('E57-exposure-'+('r2-' if 'Qwen3-' in cp else '')+cp)/'config.json')
    start=time.monotonic()
    while time.monotonic()-start<18000:
        complete=[p for p in expected if p.exists() and json.loads(p.read_text()).get('complete')]
        state={'state':'waiting','complete_jobs':len(complete),'expected_jobs':8,
            'seconds':time.monotonic()-start,'frozen_scripts':frozen}
        status.write_text(json.dumps(state,indent=2)+'\n')
        if len(complete)==8:
            assert all(sha(script.with_name(n))==v for n,v in frozen.items())
            assert not output.exists()
            with (ROOT/'E57-summary.log').open('w') as log:
                code=subprocess.run([PY,str(script)],stdout=log,stderr=subprocess.STDOUT).returncode
            state.update(state='complete' if code==0 else 'failed',summary_exit_code=code)
            if code==0:state['summary_sha256']=sha(output)
            status.write_text(json.dumps(state,indent=2)+'\n');return code
        time.sleep(10)
    status.write_text(json.dumps({'state':'timeout','expected_jobs':8,
        'reason':'finite wait expired; raw jobs not terminated'},indent=2)+'\n')
    return 1


if __name__=='__main__':raise SystemExit(main())
