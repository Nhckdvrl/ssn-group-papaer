import copy
import contextlib
import json
import pathlib
import sys
import tempfile
from types import SimpleNamespace
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from run_native_rollouts import LocalClient,select_snapshots,uses_adapter
from score_native_rollouts import parse_native_score,has_character_state


class NativeRolloutContract(unittest.TestCase):
    def test_world_never_receives_trained_character_adapter(self):
        for system in ['base','update_sft','multitask_sft']:
            for task in ['character_update','interaction_gen','scene_cast']:
                self.assertFalse(uses_adapter(system,'world',task))
        self.assertTrue(uses_adapter('update_sft','character','character_update'))
        self.assertFalse(uses_adapter('update_sft','character','interaction_gen'))
        self.assertTrue(uses_adapter('multitask_sft','character','interaction_gen'))

    def test_no_future_reference_in_simulator_input(self):
        row=dict(book_name='book',scene_index=3,world_state={},character_states={},previous_scene=None,
                 ground_truth_scenes=['FUTURE_SECRET'],tag='answer')
        before=copy.deepcopy(row);selected=select_snapshots([row])
        self.assertNotIn('FUTURE_SECRET',str(selected))
        self.assertNotIn('tag',selected[0]['input'])
        self.assertEqual(row,before)

    def test_native_judge_requires_evidence_points(self):
        self.assertIsNone(parse_native_score('{"score":100}'))
        self.assertIsNone(parse_native_score('{"merits":[{"points":true}],"demerits":[]}'))
        self.assertEqual(parse_native_score('{"merits":[{"points":8}],"demerits":[{"points":-3}]}')['score'],55)

    def test_untracked_cast_has_no_profile_evolution_target(self):
        self.assertFalse(has_character_state(dict(initial_profile='',profile_history=[])))
        self.assertFalse(has_character_state(dict(profile_history=[{'profile':''}])))
        self.assertTrue(has_character_state(dict(initial_profile='prior outlook',profile_history=[])))
        self.assertTrue(has_character_state(dict(initial_profile='',profile_history=[{'profile':'observed state'}])))

    def test_generation_failure_keeps_request_and_error(self):
        class IDs:
            shape=(1,3)
            def __getitem__(self,key):return self
            def tolist(self):return [1,2,3]
        class Inputs(dict):
            def to(self,device):return self
        class Model:
            def generate(self,**kwargs):raise RuntimeError('simulated OOM')
        with tempfile.TemporaryDirectory() as folder:
            backend=SimpleNamespace(system='base',started=0,max_seconds=float('inf'),
                tokenizer=SimpleNamespace(apply_chat_template=lambda *a,**k:Inputs(input_ids=IDs()),pad_token_id=0),
                model=Model(),has_adapter=False,torch=SimpleNamespace(inference_mode=contextlib.nullcontext),
                calls=0,snapshot_index=4,raw=pathlib.Path(folder)/'raw.jsonl')
            client=LocalClient(backend,'world');client.task_name='scene_cast'
            with self.assertRaisesRegex(RuntimeError,'simulated OOM'):client.chat([{'role':'user','content':'test'}])
            self.assertEqual(backend.calls,1)
            self.assertEqual(len((pathlib.Path(folder)/'requests.jsonl').read_text().splitlines()),1)
            raw=json.loads(backend.raw.read_text())
            self.assertEqual(raw['finish_reason'],'error')
            self.assertIsNone(raw['usage']['completion_tokens'])
            self.assertEqual(raw['prompt_token_ids'],[1,2,3])


if __name__=='__main__':unittest.main()
