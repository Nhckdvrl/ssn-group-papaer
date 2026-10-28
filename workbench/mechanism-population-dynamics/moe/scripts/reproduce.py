"""One CPU entrypoint for the completed E158--E162 result spine.

Never trains or evaluates a model. Older frozen experiment drivers remain intact.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

WB=Path(__file__).resolve().parents[2]
RESULTS={'E158':'e158/whole_path','E159':'e159','E160':'e160/retry_1','E161':'e161','E162':'e162'}


def commands(experiment,action):
    r='moe/results/'+RESULTS[experiment];python=sys.executable
    stats={
        'E158':[['moe/scripts/e158_whole_analyze.py','--analyze']],
        'E159':[['moe/scripts/e159_analyze.py','--analyze']],
        'E160':[['moe/scripts/e160_retry.py','analyze','--physical-gpu','1'],['moe/scripts/e160_natural_effects.py']],
        'E161':[['moe/scripts/e161_analyze.py','--analyze']],
        'E162':[['moe/scripts/e162_analyze.py','--analyze']]}
    verify={
        'E158':[['moe/results/e158_whole_independent_audit/audit.py','--audit','--summary',r+'/summary.json','--output','moe/results/e158_whole_independent_audit/report.json']],
        'E159':[['moe/results/e159_independent_audit/audit.py','--result',r,'--compare-summary',r+'/summary.json','--output','moe/results/e159_independent_audit/report.json']],
        'E160':[['moe/results/e160_independent_audit/audit.py','--audit','--root',r,'--summary',r+'/summary.json','--output',r+'/independent_report.json']],
        'E161':[['moe/results/e161_independent_audit/audit.py','--audit','--summary',r+'/summary.json','--output','moe/results/e161_independent_audit/report.json']],
        'E162':[['moe/results/e162_independent_audit/audit.py','--summary',r+'/summary.json','--output','moe/results/e162_independent_audit/report.json']]}
    plots={
        'E158':[['moe/scripts/e158_whole_plot.py'],['moe/scripts/e158_whole_key_plot.py']],
        'E159':[['moe/scripts/e159_plot.py']],
        'E160':[['moe/scripts/e160_plot.py']],
        'E161':[['moe/scripts/e161_plot.py']],
        'E162':[['moe/scripts/e162_plot.py']]}
    stages={'stats':stats,'verify':verify,'plots':plots}
    chosen=('stats','verify','plots') if action=='all' else (action,)
    return [[python,'-B',*command] for stage in chosen for command in stages[stage][experiment]]


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('experiment',choices=RESULTS)
    p.add_argument('action',choices=('stats','verify','plots','all'),default='all',nargs='?')
    p.add_argument('--show-commands',action='store_true');args=p.parse_args()
    selected=commands(args.experiment,args.action)
    if args.show_commands:
        print(json.dumps(selected,indent=2));return
    path=WB/'moe/results'/RESULTS[args.experiment]/'manifest.json'
    if not path.exists() or json.loads(path.read_text()).get('status')!='complete':
        raise SystemExit('This experiment has no complete result. This entrypoint will not run or download a model.')
    for command in selected:subprocess.run(command,cwd=WB,check=True)
    print(args.experiment+' '+args.action+' complete; no model forward or training was launched')


if __name__=='__main__':main()
