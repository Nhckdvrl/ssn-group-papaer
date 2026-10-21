#!/usr/bin/env python3
"""E01 descriptive analysis. Preserve strict scores; separately accept a lone JSON fence."""
import argparse
import itertools
import json
import re
from collections import Counter
from pathlib import Path
import scope_probe as p
import v11_probe as v


def normalized_reply(raw):
    """Only remove a complete outer Markdown fence, never search prose for an answer."""
    strict = p.parse_reply(raw)
    if strict[0] is not None or not isinstance(raw, str):
        return strict
    match = re.fullmatch(r'\s*```(?:json)?\s*\n(.*?)\n```\s*', raw, flags=re.S)
    return p.parse_reply(match.group(1)) if match else (None, None)


def interval(values):
    """Enumerate all n^n story bootstrap draws; descriptive only for this convenience set."""
    values = list(values)
    means = sorted(sum(x)/len(x) for x in itertools.product(values, repeat=len(values)))
    return [means[int(.025*(len(means)-1))], means[int(.975*(len(means)-1))]]


def analyze(tasks, responses):
    strict = v.evaluate(tasks, responses)
    normalized = []
    for row in responses:
        action, utterance = normalized_reply(row.get('raw'))
        normalized.append(dict(row, action_id=action, utterance=utterance))
    score = v.evaluate(tasks, normalized)
    detail = score['details']
    stories = sorted({t['story_id'] for t in tasks})
    summary = {}
    for mode in ['original','situated','explicit']:
        block = [r for r in detail if r['mode']==mode]
        by_story = {s:sum(r['author_intent_agreement'] for r in block if r['story_id']==s)/
                       sum(r['story_id']==s for r in block) for s in stories}
        pairs = [r for r in score['paired_comparisons'] if r['mode']==mode]
        pressure = [r for r in score['pressure_pairs'] if r['mode']==mode]
        summary[mode] = dict(score['synthetic_oracle_by_mode'][mode],
            strict_valid_action=strict['synthetic_oracle_by_mode'][mode]['n_valid_action'],
            strict_oracle_match=strict['synthetic_oracle_by_mode'][mode]['n_action_oracle_match'],
            by_story=by_story, descriptive_story_bootstrap95=interval(by_story.values()),
            pressure=dict(n_pairs=len(pressure),action_flips=sum(r['action_changed'] is True for r in pressure),
                          base_matches=sum(r['base_oracle_match'] for r in pressure),
                          pressure_matches=sum(r['pressure_oracle_match'] for r in pressure)),
            original_conditioned={scope:dict(
                eligible=sum(r['reference_before_correct'] for r in pairs if r['scope']==scope),
                after_match=sum(r['paired_correct'] for r in pairs if r['scope']==scope),
                observed_changes=sum(r['observed_action_changed'] for r in pairs if r['scope']==scope))
                for scope in ['change','preserve']})
        for scope in ['change','preserve']:
            bucket=[r for r in block if r['scope']==scope]
            summary[mode][scope]=dict(n=len(bucket),matches=sum(r['author_intent_agreement'] for r in bucket))
    diff={s:summary['explicit']['by_story'][s]-summary['situated']['by_story'][s] for s in stories}
    usage=Counter()
    for r in responses:
        for key,value in r.get('usage',{}).items():
            if isinstance(value,(int,float)):usage[key]+=value
    result=dict(n_responses=len(responses),n_stories=len(stories),
        normalization='POST-HOC mechanical outer JSON fence removal only; strict track preserved',
        inference_warning='Four developer stories, dependent pressure twins, no population inference or seed variance estimate',
        decision_identifiable_accuracy=None,n_certified_situated=score['n_certified_situated'],
        modes=summary,explicit_minus_situated=dict(by_story=diff,mean=sum(diff.values())/len(diff),
                                                descriptive_story_bootstrap95=interval(diff.values())),
        usage=dict(usage), finish_reasons=dict(Counter(r.get('finish_reason') for r in responses)),
        mismatches=[r for r in detail if not r['author_intent_agreement']],
        strict_score=strict,normalized_score=score)
    return result,normalized


def main():
    a=argparse.ArgumentParser();a.add_argument('--tasks',required=True);a.add_argument('--run',required=True)
    args=a.parse_args();run=Path(args.run)
    result,normalized=analyze(p.read_jsonl(args.tasks),p.read_jsonl(run/'responses.jsonl'))
    (run/'analysis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    # Compact text plus audit flags; full transport/generation provenance stays in responses.
    p.write_jsonl(run/'outputs.jsonl',[{k:r.get(k) for k in
        ['task_id','raw','action_id','utterance','finish_reason','usage','error']} for r in normalized])
    print(json.dumps({k:result[k] for k in ['n_responses','n_stories','modes','explicit_minus_situated','usage','finish_reasons']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
