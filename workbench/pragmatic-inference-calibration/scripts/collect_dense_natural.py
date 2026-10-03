"""Finite E51 collector: read completed files, fail closed, never update claims."""
import argparse
import json
import subprocess
import time
from pathlib import Path
from dense_stage_data import specs, sha
from run_followup_queue import PYTHON


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,required=True)
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--max-seconds',type=int,default=9500)
    a=ap.parse_args();assert a.max_seconds>0
    summary_script=Path(__file__).with_name('summarize_dense_natural.py')
    frozen_sha=sha(summary_script)
    status=a.root/'data/E51-collector-status.json';started=time.monotonic()
    expected=[a.root/'runs'/('E51-'+task+'-'+m['id'].split('/')[-1])/'config.json'
              for m in specs(a.root) for task in ['iqap','circa']]
    while time.monotonic()-started<a.max_seconds:
        ready=[p for p in expected if p.exists() and json.loads(p.read_text()).get('complete')]
        state={'state':'waiting','complete_jobs':len(ready),'expected_jobs':len(expected),
            'summary_script_sha256':frozen_sha,'seconds':time.monotonic()-started}
        status.write_text(json.dumps(state,indent=2)+'\n')
        queue=a.root/'E51-queue.log'
        if queue.exists():
            for line in queue.read_text().splitlines():
                try:record=json.loads(line)
                except ValueError:continue
                if record.get('failed'):
                    state.update(state='failed',reason='queue reported failure',failures=record['failed'])
                    status.write_text(json.dumps(state,indent=2)+'\n');return 1
        if len(ready)==len(expected):
            assert sha(summary_script)==frozen_sha,'Summary changed while collector was waiting'
            if a.output.exists():
                result=json.loads(a.output.read_text());assert result['full_source_input_score_gate_pass'] and result['experiment']=='E51'
                state.update(state='complete',summary_sha256=sha(a.output),existing_result=True)
                status.write_text(json.dumps(state,indent=2)+'\n');return 0
            with (a.root/'E51-summary.log').open('w') as log:
                code=subprocess.run([PYTHON,str(summary_script),'--root',str(a.root),'--experiment','E51','--output',str(a.output)],
                    stdout=log,stderr=subprocess.STDOUT).returncode
            state.update(state='complete' if code==0 else 'failed',summary_exit_code=code)
            if code==0:state['summary_sha256']=sha(a.output)
            status.write_text(json.dumps(state,indent=2)+'\n');return code
        time.sleep(10)
    status.write_text(json.dumps({'state':'timeout','reason':'finite wait expired; raw work not terminated','expected_jobs':len(expected)},indent=2)+'\n')
    return 1


if __name__=='__main__':raise SystemExit(main())
