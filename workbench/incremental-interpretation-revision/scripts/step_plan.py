"""Direct Step Plan transport with process-shared eight-request limit."""
import contextlib
import fcntl
import os
from pathlib import Path
import time
import requests
MODEL='step-5-preview'
MESSAGES='https://api.stepfun.com/step_plan/v1/messages'
CHAT='https://api.stepfun.com/step_plan/v1/chat/completions'
KEY_PATH=Path('/data1/xiangding/.config/ssn-research/stepfun.key')
SLOT_PATH=Path('/data1/xiangding/work/incremental-interpretation-revision/step-plan-slots')
@contextlib.contextmanager
def slot():
    SLOT_PATH.mkdir(exist_ok=True)
    files=[(SLOT_PATH/str(i)).open('a') for i in range(8)];held=None
    try:
        blocking_slot=os.environ.get('STEP_PLAN_BLOCKING_SLOT')
        if blocking_slot is not None:
            index=int(blocking_slot);assert 0<=index<8
            held=files[index];fcntl.flock(held,fcntl.LOCK_EX)
        while held is None:
            for f in files:
                try:
                    fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);held=f;break
                except BlockingIOError:pass
            if held is None:time.sleep(.5)
        yield
    finally:
        if held is not None:fcntl.flock(held,fcntl.LOCK_UN)
        for f in files:f.close()
def post(endpoint,payload,timeout=(20,900)):
    assert endpoint in (MESSAGES,CHAT),'Only Step Plan endpoints authorized'
    assert payload['model']==MODEL
    secret=os.environ.get('STEPFUN_API_KEY') or KEY_PATH.read_text().strip()
    with slot(),requests.Session() as session:
        session.trust_env=False
        return session.post(endpoint,headers={'Authorization':'Bearer '+secret},json=payload,timeout=timeout)
