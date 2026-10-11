"""Parser integrity tests; artificial error fixtures are not research data."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from corpus import Corpus


class ReleasedCorpusTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        config = json.loads((ROOT / 'experiments/E000_data_audit/protocol.json').read_text())
        cls.c = Corpus(ROOT / config['source'])
        cls.rows, cls.issues, cls.frames = cls.c.inventory()
        cls.by_id = {r['id']: r for r in cls.rows}

    def test_published_ni_counts_exclude_auxiliary_frames(self):
        self.assertEqual(len(self.c.sentences), 438)
        self.assertEqual(sum(self.frames.values()), 1370)
        self.assertEqual(sum(r['interpretation'] == 'DNI' for r in self.rows), 303)
        self.assertEqual(sum(r['interpretation'] == 'INI' for r in self.rows), 277)

    def test_ini_does_not_become_unanswerable(self):
        row = self.by_id['s393_f3_e2']
        self.assertEqual(row['interpretation'], 'INI')
        self.assertTrue(row['source_link_present'])
        self.assertEqual(row['source_link']['text'], 'my room')
        self.assertIsNone(row['specific_filler_licensed'])
        self.assertEqual(row['link_sentence_offsets'], [-1])

    def test_dni_without_link_remains_dni(self):
        rows = [r for r in self.rows if r['interpretation'] == 'DNI' and not r['source_link_present']]
        self.assertEqual(len(rows), 58)
        self.assertTrue(all(r['specific_filler_licensed'] is None for r in rows))

    def test_all_released_graph_references_resolve(self):
        self.assertEqual(self.issues, [])
        self.assertEqual(self.c.graph_audit(), [])

    def test_uncertainty_is_retained(self):
        self.assertIn('Uncertain_Interpretation', self.by_id['s286_f1229595859.77616_e1']['flags'])
        self.assertEqual(sum('Uncertain_Interpretation' in r['flags'] for r in self.rows), 6)

    def test_splitword_parts_preserve_parent_and_surface_order(self):
        self.assertEqual(len(self.c.parts), 24)
        self.assertEqual(self.c.parts['s2_17_s0'], 's2_17')
        self.assertEqual(self.c.span(['s2_17_s2', 's2_17_s0'])['text'], 'slate coloured')

    def test_invalid_node_cannot_become_empty_gold(self):
        with self.assertRaisesRegex(ValueError, 'Missing graph node'):
            self.c.span(['not_a_released_node'])

    def test_cycle_is_rejected(self):
        # A software-only malformed graph fixture.
        with tempfile.TemporaryDirectory(dir=ROOT / 'tests') as d:
            p = Path(d) / 'bad.xml'
            p.write_text('<corpus><body><s id="s1"><graph><terminals><t id="s1_0" word="x"/></terminals>'
                         '<nonterminals><nt id="n"><edge idref="n"/></nt></nonterminals></graph></s></body></corpus>')
            with self.assertRaisesRegex(ValueError, 'Graph cycle'):
                Corpus(p).leaves('n')


if __name__ == '__main__':
    unittest.main()
