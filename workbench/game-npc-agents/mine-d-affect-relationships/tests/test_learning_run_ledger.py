import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from collect_learning_run_ledger import record_file


class LearningRunLedger(unittest.TestCase):
    def test_failed_record_is_not_invented_as_a_returned_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);run=root/'run';run.mkdir()
            (run/'metadata.json').write_text(json.dumps(dict(complete=False,wall_s=None)))
            values=[dict(response='ok',finish_reason='stop',usage=dict(prompt_tokens=3,completion_tokens=2)),
                    dict(response=None,finish_reason='error',usage=dict(prompt_tokens=5,completion_tokens=None))]
            file=run/'raw.jsonl';file.write_text(''.join(json.dumps(v)+'\n' for v in values))
            value=record_file(file,root)
            self.assertEqual(value['records'],2);self.assertEqual(value['returned_records'],1)
            self.assertEqual(value['known_usage'],dict(prompt_tokens=8,completion_tokens=2))
            self.assertEqual(value['missing_usage_fields'],1);self.assertIsNone(value['process_wall_s'])


if __name__=='__main__':unittest.main()
