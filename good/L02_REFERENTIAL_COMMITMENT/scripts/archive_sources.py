"""Archive named research sources without overwriting bytes; stdlib only."""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import io
import tarfile
import zipfile
from pathlib import Path
import urllib.error
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def acquire(item):
    dest = ROOT / item['path']
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        raise FileExistsError(dest)
    record = dict(item, retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
    try:
        with urllib.request.urlopen(item['url'], timeout=40) as response:
            data = response.read()
            record.update(http_status=response.status, final_url=response.url,
                          content_type=response.headers.get('Content-Type'))
    except urllib.error.HTTPError as error:
        data = error.read()
        record.update(http_status=error.code, error=str(error))
    except Exception as error:
        record['error'] = str(error)
        return record
    with dest.open('xb') as handle:
        handle.write(data)
    record.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest())
    record['transport_ok'] = record['http_status'] == 200
    kind = item.get('expected_kind', 'pdf' if item['path'].endswith('.pdf') else 'unspecified')
    record['expected_kind'] = kind
    record['payload_format_valid'] = None
    if kind == 'pdf':
        record['payload_format_valid'] = data.startswith(b'%PDF')
    elif kind == 'archive':
        try:
            if zipfile.is_zipfile(io.BytesIO(data)):
                with zipfile.ZipFile(io.BytesIO(data)) as archive:
                    record['archive_members'] = archive.namelist()
            else:
                with tarfile.open(fileobj=io.BytesIO(data)) as archive:
                    record['archive_members'] = archive.getnames()
            record['payload_format_valid'] = True
        except (tarfile.TarError, zipfile.BadZipFile):
            record['payload_format_valid'] = False
    record['research_source_identity_verified'] = False
    return record


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('spec', type=Path)
    parser.add_argument('manifest', type=Path)
    args = parser.parse_args()
    if args.manifest.exists():
        raise FileExistsError(args.manifest)
    items = json.loads(args.spec.read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        records = list(pool.map(acquire, items))
    args.manifest.write_text(json.dumps(records, indent=2) + '\n')
    for record in records:
        print(record['path'], record.get('http_status'), record.get('bytes'), record.get('error', ''))
