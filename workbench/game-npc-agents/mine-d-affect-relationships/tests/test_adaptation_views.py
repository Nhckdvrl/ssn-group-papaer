import copy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from build_adaptation_views import (build, continuity, export_sft, future_readout_ids,
                                    partitions, update_messages, update_target)
from experience_store import ExperienceStore, build_index


def update(book, scene, before='P0', after='P1', old_tracker='(Empty)'):
    return dict(details=dict(book_name=book, character='Ada', scene_index=scene,
                             task='character_state_update'), conversations=[
        dict(from_='system', value='Update Ada after the scene.'),
        dict(from_='human', value='## Scene Scenario\nMeeting\n\n## Scene Interactions\nExperience.\n\n'
             '## Current Profile (State At Scene Start)\n' + before + '\n\n'
             '## Hidden Tracker (State At Scene Start)\n' + old_tracker + '\n\n'
             '## Current Motivation (State At Scene Start)\nHer own goal.'),
        dict(from_='assistant', value=json.dumps(dict(profile_updated=True,
             updated_profile=after, hidden_tracker='new signal', short_description='TARGET_ONLY'))),
    ])


def native(row):
    for turn in row['conversations']:
        turn['from'] = turn.pop('from_')
    return row


class AdaptationViewTests(unittest.TestCase):
    def test_future_labels_cannot_enter_writer_input(self):
        row = native(update('A', 1))
        altered = copy.deepcopy(row)
        altered['conversations'][-1]['value'] = json.dumps(dict(profile_updated=True,
            updated_profile='FUTURE ANSWER', hidden_tracker='PRIVATE TARGET', short_description='new'))
        self.assertEqual(update_messages(row), update_messages(altered))
        self.assertNotEqual(update_target(row), update_target(altered))
        self.assertNotIn('TARGET_ONLY', json.dumps(update_messages(row)))

    def test_complete_book_split_does_not_depend_on_enumeration_or_labels(self):
        policy = dict(observed_books=['A'], partition_salt='fixed', new_test_books=1,
                      new_validation_books=1)
        first = partitions(['A', 'B', 'C', 'D'], policy)
        self.assertEqual(first, partitions(['D', 'B', 'A', 'C'], policy))
        self.assertEqual(first['A'], 'observed_development')
        self.assertEqual(set(first.values()), {'train', 'test', 'validation', 'observed_development'})
        with self.assertRaises(ValueError):
            partitions(['B', 'C', 'D'], policy)

    def test_build_export_and_successor_not_same_scene(self):
        def interaction(scene):
            return dict(details=dict(book_name='A', character='Ada', scene_index=scene,
                                     task='interaction_generation'), conversations=[])
        rows = [native(update('A', 1)), interaction(1),
                native(update('A', 3, before='P1', after='P2', old_tracker='new signal')),
                interaction(3), native(update('B', 1)), native(update('C', 1)), native(update('D', 1))]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, index = root / 'source.json', root / 'index.sqlite'
            source.write_text(json.dumps(rows))
            sha = hashlib.sha256(source.read_bytes()).hexdigest()
            build_index(source, index, 'test-rev', sha)
            store = ExperienceStore(index)
            try:
                readout = future_readout_ids(store, 0)
                self.assertEqual(readout['interaction_ids'], [3])
                self.assertNotIn(1, readout['interaction_ids'])
                self.assertTrue(all(continuity(rows[0], rows[2]).values()))
                self.assertFalse(continuity(rows[0], rows[4])['profile_exact'])
                policy = dict(source_revision='test-rev', source_sha256=sha,
                    observed_books=['A'], partition_salt='fixed', new_test_books=1, new_validation_books=1)
                inv = build(store, policy, root / 'views', 'policy-sha')
                self.assertEqual(inv['n_updates'], 5)
                self.assertEqual(inv['links']['matched_with_next_interaction'], 1)
                result = export_sft(store, root / 'views/episodes.jsonl', 'observed_development', root / 'sft.jsonl')
                self.assertEqual(result['n_rows'], 2)
                exported = [json.loads(line) for line in (root / 'sft.jsonl').read_text().splitlines()]
                self.assertTrue(all('TARGET_ONLY' not in json.dumps(row['messages']) for row in exported))
                self.assertTrue(all('TARGET_ONLY' in row['completion'] for row in exported))
                self.assertEqual(exported[0]['messages'], update_messages(rows[0]))
                with self.assertRaises(FileExistsError):
                    export_sft(store, root / 'views/episodes.jsonl', 'train', root / 'sft.jsonl')
                with (root / 'views/episodes.jsonl').open('a') as handle:
                    handle.write('{}\n')
                with self.assertRaises(ValueError):
                    export_sft(store, root / 'views/episodes.jsonl', 'train', root / 'tampered.jsonl')
            finally:
                store.close()


if __name__ == '__main__':
    unittest.main()
