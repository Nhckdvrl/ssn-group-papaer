"""E51 resume collector: accept only preserved original Base download timeouts."""
import json,subprocess,time
from pathlib import Path
from dense_stage_data import specs,sha
from run_followup_queue import ROOT,PYTHON


def main():
    script=Path(__file__).with_name('summarize_dense_natural.py')
    frozen=sha(script);assert frozen=='b492c53e72ad4a311c2962fbfd560a4ad1190798922c5676711ec97db9ed9563'
    expected=[ROOT/'runs'/('E51-'+task+'-'+m['id'].split('/')[-1])/'config.json' for m in specs(ROOT) for task in ('iqap','circa')]
    output=Path(__file__).resolve().parents[1]/'results/E51-dense-natural-summary.json'
    status=ROOT/'data/E51-resume-collector-status.json';start=time.monotonic()
    while time.monotonic()-start<10800:
        old=json.loads((ROOT/'data/E51-collector-status.json').read_text())
        if old['state']=='complete':
            assert output.exists();status.write_text(json.dumps({'state':'complete','original_collector_succeeded':True}));return 0
        if old['state']=='failed':
            failures=old.get('failures',[])
            assert len(failures)==2 and all(x=='Pinned download missing OLMo-2-1124-13B' for x in failures),old
            complete=sum(p.exists() and json.loads(p.read_text()).get('complete',False) for p in expected)
            state={'state':'waiting','complete_jobs':complete,'expected_jobs':8,'original_failures':failures,'seconds':time.monotonic()-start}
            status.write_text(json.dumps(state,indent=2)+'\n')
            if complete==8:
                assert sha(script)==frozen and not output.exists()
                with (ROOT/'E51-resume-summary.log').open('w') as log:
                    code=subprocess.run([PYTHON,str(script),'--root',str(ROOT),'--experiment','E51','--output',str(output)],stdout=log,stderr=subprocess.STDOUT).returncode
                state.update(state='complete' if code==0 else 'failed',summary_exit_code=code)
                status.write_text(json.dumps(state,indent=2)+'\n');return code
        time.sleep(10)
    status.write_text(json.dumps({'state':'timeout','raw_work_not_terminated':True})+'\n');return 1
if __name__=='__main__':raise SystemExit(main())
