"""Repair only T4's 35-word note schema; preserve all old requests and reviews."""
import argparse
import json
from pathlib import Path
import shutil

from audit_paraphrases import PROMPT,validate_t4
from data import sha
from data_v2 import digest


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--destination',type=Path,required=True);ap.add_argument('--data',type=Path,required=True);args=ap.parse_args()
    assert args.source!=args.destination and not args.destination.exists(),'Always preserve the original version'
    protocol=json.loads((args.source/'protocol.json').read_text())
    assert protocol['prompt_sha256']==digest(PROMPT) and protocol['data_sha256']==sha(args.data)
    rows={r['item_id']:r for r in map(json.loads,args.data.read_text().splitlines())}
    args.destination.mkdir(parents=True);(args.destination/'previous-reviews').mkdir()
    shutil.copy2(args.source/'protocol.json',args.destination/'protocol.json')
    ledger=[]
    for request in sorted(args.source.glob('*.request.json')):
        prefix=request.name.removesuffix('.request.json');payload=json.loads(request.read_text())
        shutil.copy2(request,args.destination/request.name)
        previous=args.source/(prefix+'.review.json')
        old=json.loads(previous.read_text()) if previous.exists() else {}
        if previous.exists():shutil.copy2(previous,args.destination/'previous-reviews'/previous.name)
        responses=sorted(args.source.glob(prefix+'.response-t*.json'),key=lambda p:int(p.stem.rsplit('-t',1)[1]))
        for response in responses:shutil.copy2(response,args.destination/response.name)
        if not responses:continue  # Future driver completes an unanswered request normally.
        selected=responses[-1]
        for response in responses:
            if json.loads(response.read_text())['http_status'] not in (429,500,502,503,504):selected=response;break
        report={**old,'request_sha256':sha(request),'status':'failed','previous_schema_status':old.get('status'),
            'schema_revalidation':'T4 prompt always allowed 35 words; old shared validator incorrectly allowed only 20',
            'selected_response_sha256':sha(selected)}
        try:
            response=json.loads(selected.read_text());assert response['http_status']==200
            body=response['body'];assert body.get('stop_reason')=='end_turn'
            text=''.join(c['text'] for c in body['content'] if c['type']=='text').strip()
            if text.startswith('```'):text=text.split('\n',1)[1].rsplit('```',1)[0].strip()
            annotations=json.loads(text)['annotations'];items=json.loads(payload['messages'][0]['content'])['items']
            assert len(annotations)==len(items) and {a['item_id'] for a in annotations}=={r['item_id'] for r in items}
            by_id={a['item_id']:a for a in annotations}
            if prefix.startswith('p3-'):assert all(a.get('rationale') for a in annotations)
            report.update(status='complete',annotations=[validate_t4(by_id[r['item_id']],rows[r['item_id']]) for r in items],
                response_sha256=sha(selected),usage=body.get('usage'))
            report.pop('error',None)
        except Exception as error:report['error']=type(error).__name__+': '+str(error)
        (args.destination/(prefix+'.review.json')).write_text(json.dumps(report,indent=2)+'\n')
        ledger.append(dict(packet=prefix,old_status=old.get('status'),new_status=report['status'],request_sha256=sha(request),response_sha256=sha(selected)))
    (args.destination/'schema-revalidation.json').write_text(json.dumps(dict(source=str(args.source),
        no_new_model_calls=True,no_response_selection_by_labels=True,criterion='Original T4 prompt note limit 35',packets=ledger),indent=2)+'\n')
    print(json.dumps(dict(packets=len(ledger),completed=sum(x['new_status']=='complete' for x in ledger))))


if __name__=='__main__':main()
