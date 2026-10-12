"""Regression tests: fixtures, no model weights/GPU/network/real experiment data."""
import ast
import json
from pathlib import Path
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]/'scripts'
sys.path.insert(0, str(SCRIPTS))
from forward_preflight import MODES, require_valid_forward_smoke, unusable_reasons


def good(**changes):
    x = dict(item_id='fixture', answer='a', parse_status='explicit_final_answer',
             output_text='Final Answer [a].', output_tokens=[1, 2],
             stopped=True, capped=False, valid=True, cap=64,
             lower_correct=False, upper_correct=False)
    x.update(changes)
    return x


class ForwardPreflightTests(unittest.TestCase):
    def test_valid_but_incorrect_is_admitted(self):
        # Scientific correctness is deliberately irrelevant to interface admission.
        self.assertEqual(unusable_reasons(good()), [])

    def test_repeated_invalid_still_rejected(self):
        x=good(answer=None,parse_status='UNKNOWN',valid=False,stopped=False,capped=True)
        self.assertEqual(x['output_tokens'],dict(x)['output_tokens'])
        self.assertTrue(unusable_reasons(x))

    def test_capped_final_string_is_not_completion(self):
        self.assertIn('not_stopped',unusable_reasons(good(stopped=False,capped=True)))

    def test_unclosed_thought_is_rejected(self):
        self.assertIn('unclosed_reasoning_tag',unusable_reasons(good(output_text='<think>Final Answer [a]')))

    def test_closed_thought_without_final_is_rejected(self):
        r=good(output_text='<think>Final Answer [a].</think>')
        self.assertIn('no_matching_choice_in_final_text',unusable_reasons(r))

    def test_real_final_after_thought_is_admitted(self):
        r=good(answer='b', output_text='<think>Final Answer [a].</think>Final Answer [b].')
        self.assertEqual(unusable_reasons(r),[])

    def test_parser_final_disagreement_is_rejected(self):
        r=good(answer='a', output_text='Final Answer [b].')
        self.assertIn('no_matching_choice_in_final_text',unusable_reasons(r))

    def test_missing_choice_is_rejected(self):
        self.assertIn('no_valid_choice',unusable_reasons(good(answer=None)))

    def test_empty_output_is_rejected(self):
        self.assertIn('empty_output',unusable_reasons(good(output_text='')))

    def test_missing_cot_is_rejected_and_persisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'smoke.json'
            with self.assertRaises(RuntimeError):
                require_valid_forward_smoke({'FORWARD_DIRECT':[good()]},p)
            self.assertEqual(json.loads(p.read_text())['missing_modes'],['FORWARD_COT'])

    def test_cot_failure_cannot_hide_behind_direct(self):
        with tempfile.TemporaryDirectory() as tmp:
            samples={m:[good()] for m in MODES}
            samples['FORWARD_COT']=[good(stopped=False,capped=True)]
            with self.assertRaises(RuntimeError):
                require_valid_forward_smoke(samples,Path(tmp)/'smoke.json')

    def test_existing_report_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'smoke.json'; samples={m:[good()] for m in MODES}
            require_valid_forward_smoke(samples,p); before=p.read_bytes()
            with self.assertRaises(FileExistsError):require_valid_forward_smoke(samples,p)
            self.assertEqual(before,p.read_bytes())

    def test_report_does_not_admit_by_gold(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'smoke.json'
            report=require_valid_forward_smoke({m:[good()] for m in MODES},p)
            self.assertTrue(report['passed']);self.assertFalse(report['gold_used_for_admission'])
            self.assertNotIn('lower_correct',p.read_text())

    def test_runner_calls_guard_before_full_output(self):
        source=(SCRIPTS/'run_belief_r_credit.py').read_text(); tree=ast.parse(source)
        guards=[n.lineno for n in ast.walk(tree) if isinstance(n,ast.Call)
                and isinstance(n.func,ast.Name) and n.func.id=='require_valid_forward_smoke']
        self.assertEqual(len(guards),1)
        full_output=source[:source.index("with (a.out/'predictions.jsonl').open('w')")].count('\n')+1
        self.assertLess(guards[0],full_output)


if __name__=='__main__':unittest.main()
