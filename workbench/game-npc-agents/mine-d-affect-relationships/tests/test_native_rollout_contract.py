import copy
import pathlib
import sys
import unittest

sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'scripts'))
from run_native_rollouts import select_snapshots,uses_adapter


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


if __name__=='__main__':unittest.main()
