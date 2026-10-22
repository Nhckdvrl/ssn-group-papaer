import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_adaptation_pipeline import completed_requests,write


class AdaptationResumeTests(unittest.TestCase):
    def run_folder(self,path,rows):
        path.mkdir()
        (path/'metadata.json').write_text(json.dumps(dict(complete=False,args=dict(checkpoint='fixed',max_tokens=100,adapter=None,temperature=0,seed=0,batch_size=4))))
        write(path/'responses.jsonl',rows)
        return path

    def test_saved_attempt_is_retained_and_only_absent_ids_remain(self):
        tasks={str(i):dict(task_id=str(i),messages=[dict(role='user',content=str(i))]) for i in range(3)}
        rows=[dict(tasks['0'],response='saved',finish_reason='length')]
        with tempfile.TemporaryDirectory() as d:
            folder=self.run_folder(Path(d)/'attempt',rows)
            known=completed_requests([folder],tasks,'fixed',100,None)
            self.assertEqual(known['0']['response'],'saved')
            self.assertEqual(set(tasks)-set(known),{'1','2'})
            # A length-ended generation is a completed attempt, not an absent request.
            self.assertEqual(known['0']['finish_reason'],'length')

    def test_changed_prompt_or_duplicate_record_cannot_be_reused(self):
        task=dict(task_id='1',messages=[dict(role='user',content='original')])
        with tempfile.TemporaryDirectory() as d:
            a=self.run_folder(Path(d)/'first',[dict(task,response='text')])
            b=self.run_folder(Path(d)/'second',[dict(task,response='different')])
            with self.assertRaises(ValueError):completed_requests([a,b],{'1':task},'fixed',100,None)
            changed=dict(task,messages=[dict(role='user',content='changed')])
            with self.assertRaises(ValueError):completed_requests([a],{'1':changed},'fixed',100,None)


if __name__=='__main__':unittest.main()
