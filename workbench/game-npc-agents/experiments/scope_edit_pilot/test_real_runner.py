import unittest
from types import SimpleNamespace
from run_baseline import step_payload, STEP_ENDPOINT
from analyze_baseline import normalized_reply, interval

class RealRunnerTests(unittest.TestCase):
    def test_exact_step_plan_endpoint_and_no_gold(self):
        self.assertEqual(STEP_ENDPOINT,'https://api.stepfun.com/step_plan/v1/chat/completions')
        messages=[{'role':'user','content':'scene'}]
        payload=step_payload(dict(messages=messages,expected_actions=['secret']),SimpleNamespace(max_tokens=4096))
        self.assertEqual(payload['messages'],messages)
        self.assertEqual(set(payload),{'model','messages','temperature','reasoning_effort','max_tokens','stream'})
    def test_outer_fence_only(self):
        raw='{"action_id":"B","utterance":"No."}'
        self.assertEqual(normalized_reply('```json\n'+raw+'\n```'),('B','No.'))
        self.assertEqual(normalized_reply('Answer:\n```json\n'+raw+'\n```'),(None,None))
        self.assertEqual(normalized_reply(raw+'\n'+raw),(None,None))
        self.assertEqual(normalized_reply(None),(None,None))
    def test_cluster_bootstrap_constant(self):
        self.assertEqual(interval([.8,.8,.8,.8]),[.8,.8])

if __name__=='__main__':unittest.main()
