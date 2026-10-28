"""Run a frozen experiment with a durable exit record and a wall-time limit.

Launch this supervisor with nohup and redirected stdin/stdout. It does not import
the experiment or alter its arguments, model state, ledger, or numerical code.
"""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import signal
import subprocess
import time


def utc():
    return dt.datetime.now(dt.timezone.utc).isoformat()


def write(path, value):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(json.dumps(value, indent=2) + '\n')
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--status', type=Path, required=True)
    parser.add_argument('--log', type=Path, required=True)
    parser.add_argument('--cwd', type=Path, required=True)
    parser.add_argument('--timeout', type=float, required=True)
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    if not command or args.timeout <= 0:
        parser.error('a command and a positive timeout are required')
    if args.status.exists() or args.log.exists():
        raise FileExistsError('Refusing to overwrite a prior supervision record')
    args.status.parent.mkdir(parents=True, exist_ok=True)
    args.log.parent.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    state = {'command': command, 'cwd': str(args.cwd), 'supervisor_pid': os.getpid(),
             'started_utc': utc(), 'timeout_seconds': args.timeout, 'status': 'starting'}
    write(args.status, state)
    with args.log.open('x') as log:
        proc = subprocess.Popen(command, cwd=args.cwd, stdin=subprocess.DEVNULL,
                                stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        state.update(child_pid=proc.pid, status='running')
        timed_out = False
        while proc.poll() is None:
            state.update(heartbeat_utc=utc(), elapsed_seconds=time.monotonic() - start)
            write(args.status, state)
            if state['elapsed_seconds'] >= args.timeout:
                timed_out = True
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=30)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait()
                break
            try:
                proc.wait(timeout=min(15, max(.1, args.timeout-state['elapsed_seconds'])))
            except subprocess.TimeoutExpired:
                pass
        state.update(status='complete' if proc.returncode == 0 else 'failed',
                     returncode=proc.returncode, timed_out=timed_out,
                     ended_utc=utc(), elapsed_seconds=time.monotonic()-start)
        write(args.status, state)
    return 0 if proc.returncode == 0 else 1


if __name__ == '__main__':
    raise SystemExit(main())
