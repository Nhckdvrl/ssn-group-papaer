#!/usr/bin/env python3
"""E82 isolated Java server + two native actors, no model entrypoint."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import time
import uuid
from zipfile import ZipFile

WB = Path(__file__).resolve().parents[1]
CACHE = Path('/home/xiang/.cache/game-npc-research')
REPO = CACHE/'sources/mindcraft-paper-repro'
ZIP = CACHE/'assets/minecollab/server_data.zip'
PIN = 'e85ef660171feb81290888c0fb615335f1c7a029'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--port',type=int,default=55982)
    ap.add_argument('--report',type=Path,default=WB/'results/E82_native_cooperation_baseline.json')
    ap.add_argument('--prior-result',type=Path)
    ap.add_argument('--resume-server-dir',type=Path)
    ap.add_argument('--resume-state',type=Path)
    ap.add_argument('--native-composition',action='store_true')
    args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=False)
    if args.native_composition:
        assert args.resume_state and args.resume_server_dir,'Native composition must resume preserved state'
    started=time.monotonic();server=None
    result={'experiment':'E82','inference_api_calls':0,'gpu_hours':0,'port':args.port,
            'source_repo':str(REPO),'source_pin':PIN,'server_zip':str(ZIP),
            'server_zip_sha256':sha(ZIP),'server_zip_bytes':ZIP.stat().st_size,
            'task_id':'multiagent_crafting_bookshelf_full_plan_requires_ctable__depth_0',
            'scope':'Author native physical feasibility witness, not an LLM experiment or success-rate estimate.'}
    assert subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()==PIN
    assert result['server_zip_sha256']=='7a16e9b634d34c0b1c8eb7684a204f2441e9c0111ca700177fceb0b6a3567f40'
    manifest=REPO/'.e82-native-deps/package.json'
    lock=REPO/'.e82-native-deps/package-lock.json'
    result['native_dependency_manifest']=json.loads(manifest.read_text())
    result['native_dependency_lock_sha256']=sha(lock)
    result['resolved_minecraft_data']=json.loads((REPO/'.e82-native-deps/node_modules/minecraft-data/package.json').read_text())['version']
    if args.prior_result:
        prior=json.loads(args.prior_result.read_text())
        result['prior_attempt']={'artifact':str(args.prior_result),'sha256':sha(args.prior_result),
            'actor_exit_code':prior.get('actor_exit_code'),'wall_seconds':prior.get('wall_seconds'),
            'exception':prior.get('episode',{}).get('exception','').split('\n',1)[0][:180],
            'earlier_attempt':prior.get('prior_attempt'),
            'interpretation':('Bootstrap only: operator incorrectly narrowed author minecraft-data ^3.78.0 to 3.78.0; restore declared source semver range.'
                if prior.get('episode',{}).get('exception') else 'Native failure retained; continuation uses the same saved world/inventories, with no reset or item creation. See current continuation_mode for the explicitly distinct native skill composition.')}
    result['continuation_mode']='POST-HOC native discard/pickup/craft composition' if args.native_composition else 'Original giveToPlayer helper'
    with socket.socket() as probe:probe.bind(('127.0.0.1',args.port))
    node_modules=REPO/'node_modules';local=REPO/'.e82-native-deps/node_modules'
    if not node_modules.exists():node_modules.symlink_to(local,target_is_directory=True)
    assert (node_modules/'mineflayer').exists(),'Native local dependencies not installed'
    server_dir=args.resume_server_dir or args.out/'server_data'
    if not args.resume_server_dir:
        with ZipFile(ZIP) as archive:
            for info in archive.infolist():
                if info.filename.startswith('server_data/'):
                    assert '..' not in Path(info.filename).parts
                    archive.extract(info,args.out)
    else:
        assert args.resume_state and args.resume_state.exists()
        result['resume_server_dir']=str(server_dir)
        result['resume_state']=str(args.resume_state)
        result['resume_state_sha256']=sha(args.resume_state)
    properties=server_dir/'server.properties'
    replacements={'server-ip':'127.0.0.1','server-port':str(args.port),'level-name':'Forest'}
    properties.write_text('\n'.join(
        f'{line.split("=",1)[0]}={replacements[line.split("=",1)[0]]}'
        if '=' in line and line.split('=',1)[0] in replacements else line
        for line in properties.read_text().splitlines())+'\n')
    # Original evaluator gives operator permissions for exact task initialization.
    ops=[]
    for name in ['andy','jill']:
        offline=uuid.UUID(bytes=hashlib.md5(('OfflinePlayer:'+name).encode()).digest(),version=3)
        ops.append({'uuid':str(offline),'name':name,'level':4,'bypassesPlayerLimit':False})
    (server_dir/'ops.json').write_text(json.dumps(ops,indent=2))
    result['source_files_sha256']={str(p.relative_to(REPO)):sha(p) for p in [
        REPO/'src/agent/library/skills.js',REPO/'src/agent/tasks/tasks.js',
        REPO/'tasks/crafting_tasks/test_tasks/2_agent.json']}
    result['initialization_adapter']='Isolated copy: bind localhost/unique port, original Forest world, offline ops for exact author inventory initialization; no changes to recipe, native source or world assets.'
    env={k:v for k,v in os.environ.items() if not any(t in k.upper() for t in ['API_KEY','AUTH_TOKEN','ANTHROPIC','OPENAI'])}
    env['CUDA_VISIBLE_DEVICES']=''
    log_path=args.out/'server.log'
    try:
        with log_path.open('w') as log:
            server=subprocess.Popen(['java','-Xms512M','-Xmx2G','-XX:ActiveProcessorCount=2','-jar','server.jar','nogui'],
                cwd=server_dir,stdin=subprocess.PIPE,stdout=log,stderr=subprocess.STDOUT,text=True,env=env,start_new_session=True)
        result['java_pid']=server.pid
        (args.out/'owned_pids.json').write_text(json.dumps({'java_pid':server.pid,'port':args.port}))
        deadline=time.monotonic()+120
        while time.monotonic()<deadline:
            if server.poll() is not None:raise RuntimeError('Original Java server exited; see server.log')
            if 'Done (' in log_path.read_text(errors='replace'):break
            time.sleep(.25)
        else:raise RuntimeError('Original Java server startup exceeded 120 CPU seconds')
        result['server_startup_seconds']=time.monotonic()-started
        node_log=args.out/'native_actor.log'
        with node_log.open('w') as log:
            command=['node',str(WB/'scripts/minecraft_native_cooperation.mjs'),str(REPO),str(args.out/'episode'),str(args.port)]
            if args.resume_state:command.append(str(args.resume_state))
            if args.native_composition:command.append('native-composition')
            actor=subprocess.run(command,
                cwd=REPO,stdout=log,stderr=subprocess.STDOUT,env=env,timeout=190)
        result['actor_exit_code']=actor.returncode
        summary=args.out/'episode/summary.json'
        if summary.exists():
            episode=json.loads(summary.read_text())
            result['episode']={k:v for k,v in episode.items() if k not in ['initial','before_craft','final','stages']}
            if result['episode'].get('exception'):
                result['episode']['exception']=result['episode']['exception'].split('\n',1)[0][:300]
                result['episode']['full_exception_artifact']=str(summary)
            result['initial_inventory']=[x['inventory'] for x in episode.get('initial',{}).get('roles',[])]
            result['final_inventory']=[x['inventory'] for x in episode.get('final',{}).get('roles',[])]
            result['validator_before']=[x['author_validator'] for x in episode.get('initial',{}).get('roles',[])]
            result['validator_final']=[x['author_validator'] for x in episode.get('final',{}).get('roles',[])]
            result['transfer_stages']=episode.get('stages',[])
        else:result['exception']='Native actor process did not produce an episode summary; see native_actor.log'
    except Exception as exc:
        result['exception']=f'{type(exc).__name__}: {exc}'
    finally:
        if server and server.poll() is None:
            try:
                server.stdin.write('stop\n');server.stdin.flush();server.wait(timeout=30)
                result['server_shutdown']='owned PID stopped via Minecraft console'
            except Exception:
                server.terminate()
                try:server.wait(timeout=10)
                except subprocess.TimeoutExpired:server.kill();server.wait()
                result['server_shutdown']='owned PID only terminated after console stop timeout'
        result['wall_seconds']=time.monotonic()-started
        result['raw_artifact_dir']=str(args.out)
        result['artifacts_sha256']={str(p):sha(p) for p in [log_path,args.out/'native_actor.log',args.out/'episode/native_events.jsonl'] if p.exists()}
        args.report.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k in ['experiment','exception','actor_exit_code',
            'initial_inventory','final_inventory','validator_final','server_startup_seconds','server_shutdown','wall_seconds','raw_artifact_dir']},ensure_ascii=False),flush=True)


if __name__=='__main__':main()
