import json
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from run_contrast_calibration import parse


class ContrastCalibrationTests(unittest.TestCase):
    def test_invented_evidence_is_retained_but_not_supported(self):
        body=dict(response_1='She accepts the invitation.',response_2='She refuses the invitation.')
        value=dict(observable_contrast=True,mapping='A1_B2',quotes=[dict(response=1,quote='She accepts the invitation.'),dict(response=2,quote='She burns the letter.')],reason='test')
        result=parse(json.dumps(value),body)
        self.assertIsNotNone(result)
        self.assertFalse(result['quotes_supported'])

    def test_identical_responses_can_be_underdetermined(self):
        body=dict(response_1='I will wait here.',response_2='I will wait here.')
        result=parse(json.dumps(dict(observable_contrast=False,mapping='underdetermined',quotes=[],reason='same response')),body)
        self.assertEqual(result['mapping'],'underdetermined')
        self.assertTrue(result['quotes_supported'])


if __name__=='__main__':unittest.main()
