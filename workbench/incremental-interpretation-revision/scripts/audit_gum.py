"""Cache pinned natural news/fiction with existing referential annotations, no inference."""
import argparse
import collections
import concurrent.futures
import hashlib
import json
from pathlib import Path
import requests
from data import CACHE,sha


def audit(directory):
    revision=json.loads((directory/'revision.json').read_text())['sha']
    index=json.loads((directory/'dep-file-index.json').read_text())
    # All files from these two genres; never select by model predictions.
    files=[r for r in index if r['type']=='file' and r['name'].startswith(('GUM_news_','GUM_fiction_')) and r['name'].endswith('.conllu')]
    assert files and len({r['name'] for r in files})==len(files)
    target=directory/'dep';target.mkdir(exist_ok=True)
    def download(row):
        url=f'https://raw.githubusercontent.com/amir-zeldes/gum/{revision}/dep/{row["name"]}'
        path=target/row['name']
        if not path.exists():
            with requests.Session() as session:
                session.trust_env=False;response=session.get(url,timeout=45);response.raise_for_status();body=response.content
            blob=hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest();assert blob==row['sha']
            path.write_bytes(body)
        body=path.read_bytes();assert hashlib.sha1(b'blob '+str(len(body)).encode()+b'\0'+body).hexdigest()==row['sha']
        text=body.decode();tokens=[line.split('\t') for line in text.splitlines() if line and not line.startswith('#') and line.split('\t')[0].isdigit()]
        assert all(len(t)==10 for t in tokens)
        return dict(filename=row['name'],source_url=url,git_blob_sha1=row['sha'],sha256=sha(path),bytes=len(body),
                    genre='news' if row['name'].startswith('GUM_news_') else 'fiction',tokens=len(tokens),sentences=sum(line.startswith('# sent_id = ') for line in text.splitlines()),
                    upos=dict(collections.Counter(t[3] for t in tokens)),dependency_relations=dict(collections.Counter(t[7] for t in tokens)),
                    entity_annotated_tokens=sum('Entity=' in t[9] for t in tokens),
                    metadata=[line for line in text.splitlines() if line.startswith('#') and ('source' in line.lower() or 'newdoc' in line.lower())],
                    raw_text_license='CC-BY-2.5' if row['name'].startswith('GUM_news_') else 'CC-BY-NC-SA-3.0',annotations_license='CC-BY-4.0')
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:results=list(executor.map(download,files))
    results.sort(key=lambda r:r['filename'])
    report=dict(source='amir-zeldes/gum',revision=revision,proxy_used=False,selection='all news and fiction dep files at pinned revision; no score selection',
                license_sha256=sha(directory/'LICENSE.md'),file_index_sha256=sha(directory/'dep-file-index.json'),files=results,
                totals=dict(documents=len(results),bytes=sum(r['bytes'] for r in results),tokens=sum(r['tokens'] for r in results),sentences=sum(r['sentences'] for r in results),
                            genres=dict(collections.Counter(r['genre'] for r in results))),
                limitations='Natural reference/coreference/information-status annotations are assets; no event-role semantic gold adopted and no model inference. Original text licenses differ by genre; raw stays cache.')
    (directory/'audit.json').write_text(json.dumps(report,indent=2)+'\n');return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--directory',type=Path,default=CACHE/'upstream/gum-audit');p.add_argument('--out',type=Path,required=True);a=p.parse_args()
    result=audit(a.directory);a.out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['totals'],indent=2))
