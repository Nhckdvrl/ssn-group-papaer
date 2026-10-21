#!/usr/bin/env python3
"""Render all raw-derived dialogue triples for qualitative review, without judging style."""
import argparse,json
from pathlib import Path
import scope_probe as p
from analyze_baseline import normalized_reply, read_responses


def escape(s):return str(s).replace('|','\\|').replace('\n','<br>')


def main():
    a=argparse.ArgumentParser();a.add_argument('--root',required=True);args=a.parse_args()
    root=Path(args.root);tasks=p.read_jsonl(root/'tasks.jsonl')
    lines=['# E01 全量台词审阅入口','',
           '由原回复机械排版；外层 JSON 围栏可移除，未评分语气。不是独立真人评价。原任务及完整响应以各目录 JSONL 为准。','']
    for folder in sorted(root.iterdir()):
        if not (folder/'responses.jsonl').exists() and not (folder/'responses.jsonl.gz').exists():continue
        responses={r['task_id']:r for r in read_responses(folder)}
        if folder.name.endswith('_recovery'):
            lines += ['## '+folder.name,'','仅对原轮截断项提高预算，以下是额外请求；不覆盖上表。','']
            for task_id,row in responses.items():
                action,utterance=normalized_reply(row.get('raw'))
                lines += [f'- `{task_id}`: {action}: {utterance}', '']
            continue
        lines += ['## '+folder.name,'','| 场景 | Original | Situated | Explicit |','|---|---|---|---|']
        for t in tasks:
            if t['mode']!='original':continue
            prefix=t['task_id'].rsplit('/',1)[0]
            cells=[prefix]
            for mode in ['original','situated','explicit']:
                row=responses.get(prefix+'/'+mode,{})
                action,utterance=normalized_reply(row.get('raw'))
                cells.append(f'{action}: {utterance}' if action else f"无有效输出 ({row.get('finish_reason','missing')})")
            lines.append('| '+' | '.join(escape(x) for x in cells)+' |')
        lines.append('')
    (root/'CASEBOOK.md').write_text('\n'.join(lines)+'\n')

if __name__=='__main__':main()
