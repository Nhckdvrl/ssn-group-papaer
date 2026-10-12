"""CPU-only validation of native forward smoke outputs, without inspecting gold.

This checks measurement usability, not model capability or scientific promise.
A failed smoke is persisted before aborting. Never overwrite a prior report.
"""
from __future__ import annotations
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

MODES = ('FORWARD_DIRECT', 'FORWARD_COT')


def unusable_reasons(record: Mapping[str, Any]) -> list[str]:
    reasons: list[str] = []
    if record.get('stopped') is not True:
        reasons.append('not_stopped')
    if record.get('capped') is not False:
        reasons.append('capped_or_missing_cap_status')
    if record.get('valid') is not True or record.get('answer') not in ('a', 'b', 'c'):
        reasons.append('no_valid_choice')
    if record.get('parse_status') not in ('explicit_final_answer', 'bare_choice'):
        reasons.append('unsupported_parse_status')
    text = record.get('output_text')
    if not isinstance(text, str) or not text.strip():
        reasons.append('empty_output')
    elif any(text.lower().count('<'+tag+'>') > text.lower().count('</'+tag+'>')
             for tag in ('think', 'analysis')):
        reasons.append('unclosed_reasoning_tag')
    else:
        # The historical parser can pick a choice inside a reasoning block.
        # Only validate the suffix after the last visible closing reasoning tag.
        closes = list(re.finditer(r'</(?:think|analysis)>', text, flags=re.I))
        final = text[closes[-1].end():] if closes else text
        choices = re.findall(r'final\s*answer\s*[:：]?\s*\[?\s*([abc])\b', final, flags=re.I)
        bare = re.fullmatch(r'\s*\[?([abc])\]?\s*[.。]?\s*', final, flags=re.I)
        choice = choices[-1].lower() if choices else bare.group(1).lower() if bare else None
        if choice is None or choice != record.get('answer'):
            reasons.append('no_matching_choice_in_final_text')
    return reasons


def require_valid_forward_smoke(
    samples: Mapping[str, Sequence[Mapping[str, Any]]], report_path: Path,
) -> dict[str, Any]:
    """Check all registered modes on a predetermined, gold-independent sample.

    Does not inspect correctness, change budgets/prompts, or retry until success.
    A passing tiny smoke is NOT a guarantee of whole-dataset validity.
    """
    missing = [mode for mode in MODES if not samples.get(mode)]
    checks = []
    keep = ('item_id', 'answer', 'parse_status', 'stopped', 'capped', 'valid',
            'prompt_sha256', 'prompt_tokens', 'cap', 'output_text', 'output_tokens')
    for mode in MODES:
        for record in samples.get(mode, ()):
            checks.append({'mode': mode, 'reasons': unusable_reasons(record),
                           'output': {k: record.get(k) for k in keep}})
    report = {'schema_version': 1, 'required_modes': list(MODES),
              'missing_modes': missing, 'checks': checks,
              'passed': not missing and all(not x['reasons'] for x in checks),
              'gold_used_for_admission': False,
              'scope': 'Interface smoke only; no capability or whole-run certification.'}
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with report_path.open('x', encoding='utf-8') as stream:
        json.dump(report, stream, ensure_ascii=False, indent=2)
        stream.write('\n')
    if not report['passed']:
        raise RuntimeError(f'Native forward interface is not usable; retained smoke: {report_path}')
    return report
