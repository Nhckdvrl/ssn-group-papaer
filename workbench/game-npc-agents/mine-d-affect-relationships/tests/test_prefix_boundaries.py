import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_prefix_memory import pack_prefix

class PrefixBoundaryTests(unittest.TestCase):
 def test_query_forces_boundary_before_future_text(self):
  blocks=pack_prefix([(1,'early\n'),(2,'current\n'),(3,'future\n')],[2,3],100)
  self.assertEqual([b['checkpoint'] for b in blocks],[2,3]);self.assertEqual([s['unit'] for s in blocks[0]['segments']],[1,2]);self.assertNotIn('future',''.join(s['text'] for s in blocks[0]['segments']))
 def test_long_line_is_preserved_and_checkpoint_waits_for_whole_unit(self):
  text='角色abc\n'+'z'*19;blocks=pack_prefix([(1,text),(2,'end')],[1,2],8)
  self.assertEqual(''.join(s['text'] for b in blocks for s in b['segments'] if s['unit']==1),text)
  snapshots=[b for b in blocks if b['checkpoint']==1];self.assertEqual(len(snapshots),1);self.assertEqual(snapshots[0]['segments'][-1]['end_char'],len(text))
 def test_exact_limit_and_adjacent_query_units(self):
  blocks=pack_prefix([(1,'12345678'),(2,'next')],[1,2],8)
  self.assertEqual([b['checkpoint'] for b in blocks],[1,2]);self.assertEqual([b['completed_through_unit'] for b in blocks],[1,2])
if __name__=='__main__':unittest.main()
