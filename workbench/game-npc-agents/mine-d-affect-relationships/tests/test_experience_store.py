import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from experience_store import ExperienceStore, build_index, indexed_items, summarize


class ExperienceStoreTests(unittest.TestCase):
    def test_unicode_offsets_preserve_exact_source_at_every_chunk_boundary(self):
        rows = [dict(text='信任🙂, ][\r\n', nested={'x': [1, 2]}), dict(text='é')]
        data = (' \r\n' + json.dumps(rows, ensure_ascii=False, indent=2) + '\r\n').encode()
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.json'
            source.write_bytes(data)
            for chunk in [1, 2, 7, 17, 2**20]:
                found = list(indexed_items(source, chunk))
                self.assertEqual([r[3] for r in found], rows)
                for _, offset, raw, _ in found:
                    self.assertEqual(data[offset:offset + len(raw)], raw)

    def test_rejects_incomplete_array_and_trailing_data(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'source.json'
            for text in ['[{"x":1}', '[{},]', '[{} {}]', '[{}] extra']:
                source.write_text(text)
                with self.assertRaises(ValueError):
                    list(indexed_items(source, 2))

    def test_successor_is_same_book_and_role_not_next_global_scene(self):
        def task(book, role, scene, kind):
            return dict(details=dict(book_name=book, character=role, scene_index=scene, task=kind), conversations=[])
        rows = [task('Book A', 'Ada', 2, 'character_state_update'),
                task('Book B', 'Ada', 3, 'character_state_update'),
                task('Book A', 'Bo', 3, 'character_state_update'),
                task('Book A', 'Ada', 9, 'character_state_update'),
                task('Book A', 'Ada', 2, 'character_motivation_update'),
                task('Book A', 'Ada', 2, 'interaction_generation')]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); source = root / 'source.json'; index = root / 'index.sqlite'
            raw = json.dumps(rows).encode(); source.write_bytes(raw)
            build_index(source, index, 'test-revision', hashlib.sha256(raw).hexdigest())
            store = ExperienceStore(index)
            try:
                self.assertEqual(store.appearance(0)['next_update_id'], 3)
                self.assertIsNone(store.appearance(1)['next_update_id'])
                self.assertEqual(store.appearance(0)['same_appearance_tasks']['character_motivation_update'], [4])
                self.assertEqual(store.get(3), rows[3])
                self.assertEqual(summarize(store)['n_role_timelines'], 3)
                changed = raw.replace(b'Book A', b'Book Z'); source.write_bytes(changed)
                with self.assertRaises(ValueError):
                    store.get(0)
            finally:
                store.close()


if __name__ == '__main__':
    unittest.main()
