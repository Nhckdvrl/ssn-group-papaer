#!/usr/bin/env python3
"""Index native EvolvingWorld tasks by complete character appearances, without inference.

The source remains authoritative. This index contains offsets, hashes and links,
not rewritten scenes, psychological labels, model prompts, or a new test split.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3


def indexed_items(path, chunk_chars=2**20):
    """Yield (row_id, UTF-8 byte offset, exact bytes, object) from a JSON array."""
    decoder = json.JSONDecoder()
    buffer, position, row_id = '', 0, 0
    state = 'start'
    with Path(path).open(encoding='utf-8', newline='') as source:
        eof = False
        while True:
            if not eof:
                chunk = source.read(chunk_chars)
                eof = not chunk
                buffer += chunk
            while True:
                whitespace = len(buffer) - len(buffer.lstrip())
                position += len(buffer[:whitespace].encode('utf-8'))
                buffer = buffer[whitespace:]
                if not buffer:
                    break
                if state == 'start':
                    if buffer[0] != '[':
                        raise ValueError('Expected a JSON array')
                    state = 'first'
                elif state in ('first', 'next'):
                    if state == 'first' and buffer[0] == ']':
                        state = 'done'
                    else:
                        try:
                            item, end = decoder.raw_decode(buffer)
                        except json.JSONDecodeError:
                            if eof:
                                raise ValueError('Incomplete or malformed source item') from None
                            break
                        if not isinstance(item, dict):
                            raise ValueError('Native task must be an object')
                        raw = buffer[:end].encode('utf-8')
                        yield row_id, position, raw, item
                        row_id += 1
                        position += len(raw)
                        buffer = buffer[end:]
                        state = 'separator'
                        continue
                elif state == 'separator':
                    if buffer[0] == ',':
                        state = 'next'
                    elif buffer[0] == ']':
                        state = 'done'
                    else:
                        raise ValueError('Expected comma or end of array')
                else:
                    raise ValueError('Data after source array')
                position += 1
                buffer = buffer[1:]
            if eof:
                if state != 'done' or buffer.strip():
                    raise ValueError('Incomplete source array')
                return


def file_sha(path):
    with Path(path).open('rb') as source:
        return hashlib.file_digest(source, 'sha256').hexdigest()


def build_index(source, destination, revision, expected_sha):
    source, destination = Path(source).resolve(), Path(destination)
    if destination.exists():
        raise FileExistsError('Preserve the existing index; use a new destination')
    partial = destination.with_suffix(destination.suffix + '.partial')
    if partial.exists():
        raise FileExistsError('An incomplete build exists; inspect before retrying')
    destination.parent.mkdir(parents=True, exist_ok=True)
    source_stat = source.stat()
    counts, books = Counter(), set()
    with sqlite3.connect(partial) as db:
        db.executescript('''
            CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE records (
                row_id INTEGER PRIMARY KEY, book TEXT NOT NULL, role TEXT,
                scene INTEGER NOT NULL, task TEXT NOT NULL, segment INTEGER,
                offset INTEGER NOT NULL, length INTEGER NOT NULL, sha256 TEXT NOT NULL
            );
        ''')
        for row_id, offset, raw, item in indexed_items(source):
            detail = item['details']
            scene = detail['scene_index']
            if type(scene) is not int:
                raise ValueError(f'Non-integer scene index at source row {row_id}')
            book, task = detail['book_name'], detail['task']
            db.execute('INSERT INTO records VALUES (?,?,?,?,?,?,?,?,?)', (
                row_id, book, detail.get('character'), scene, task,
                detail.get('segment_start'), offset, len(raw),
                hashlib.sha256(raw).hexdigest(),
            ))
            counts[task] += 1
            books.add(book)
        actual_sha = file_sha(source)
        if actual_sha != expected_sha:
            raise ValueError('Source hash differs from the registered release')
        if source.stat().st_size != source_stat.st_size or source.stat().st_mtime_ns != source_stat.st_mtime_ns:
            raise ValueError('Source changed during indexing')
        db.executescript('''
            CREATE INDEX appearance ON records (book,role,scene,task,segment);
            CREATE UNIQUE INDEX unique_update ON records(book,role,scene)
                WHERE task='character_state_update';
            CREATE VIEW updates AS SELECT row_id,book,role,scene,
                LEAD(row_id) OVER (PARTITION BY book,role ORDER BY scene) AS next_update_id
                FROM records WHERE task='character_state_update';
        ''')
        metadata = dict(schema_version=1, source_path=str(source), source_revision=revision,
                        source_sha256=actual_sha, source_bytes=source_stat.st_size,
                        source_mtime_ns=source_stat.st_mtime_ns, n_rows=sum(counts.values()),
                        n_books=len(books), task_counts=dict(counts),
                        scope='Published training records only; original native tasks and source split retained.')
        db.executemany('INSERT INTO metadata VALUES (?,?)', [(k, json.dumps(v, ensure_ascii=False)) for k, v in metadata.items()])
        db.commit()
        integrity = db.execute('PRAGMA integrity_check').fetchone()[0]
        if integrity != 'ok':
            raise ValueError(integrity)
    db.close()
    partial.rename(destination)
    return metadata


class ExperienceStore:
    """Read exact source tasks and metadata-only links; no source text is duplicated."""

    def __init__(self, index, source=None):
        self.db = sqlite3.connect(Path(index).resolve().as_uri() + '?mode=ro', uri=True)
        self.db.row_factory = sqlite3.Row
        self.metadata = {r['key']: json.loads(r['value']) for r in self.db.execute('SELECT * FROM metadata')}
        self.source = Path(source or self.metadata['source_path'])
        if self.source.stat().st_size != self.metadata['source_bytes']:
            raise ValueError('Source size differs from index')

    def close(self):
        self.db.close()

    def get(self, row_id):
        row = self.db.execute('SELECT * FROM records WHERE row_id=?', (row_id,)).fetchone()
        if row is None:
            raise KeyError(row_id)
        with self.source.open('rb') as stream:
            stream.seek(row['offset'])
            raw = stream.read(row['length'])
        if hashlib.sha256(raw).hexdigest() != row['sha256']:
            raise ValueError(f'Source bytes changed at row {row_id}')
        return json.loads(raw)

    def appearance(self, update_id):
        """Return source IDs for this appearance and the next appearance of the same role.

        Future IDs are provenance links, not authorized current model inputs.
        get() returns original conversations including supervision; adapters must
        keep assistant targets and future material separate from inference inputs.
        """
        row = self.db.execute('SELECT * FROM updates WHERE row_id=?', (update_id,)).fetchone()
        if row is None:
            raise KeyError(update_id)
        tasks = {}
        for item in self.db.execute('SELECT row_id,task FROM records WHERE book=? AND role=? AND scene=? ORDER BY segment,row_id', (row['book'], row['role'], row['scene'])):
            tasks.setdefault(item['task'], []).append(item['row_id'])
        return dict(update_id=update_id, book=row['book'], role=row['role'], scene=row['scene'],
                    same_appearance_tasks=tasks, next_update_id=row['next_update_id'])

    def verify_all(self):
        """Check every exact byte span and metadata key against the native source."""
        count = 0
        with self.source.open('rb') as stream:
            for row in self.db.execute('SELECT * FROM records ORDER BY row_id'):
                stream.seek(row['offset'])
                raw = stream.read(row['length'])
                if hashlib.sha256(raw).hexdigest() != row['sha256']:
                    raise ValueError(f'Source bytes changed at row {row["row_id"]}')
                detail = json.loads(raw)['details']
                original = (detail['book_name'], detail.get('character'), detail['scene_index'],
                            detail['task'], detail.get('segment_start'))
                indexed = tuple(row[k] for k in ['book', 'role', 'scene', 'task', 'segment'])
                if original != indexed:
                    raise ValueError(f'Metadata mismatch at row {row["row_id"]}')
                count += 1
        if count != self.metadata['n_rows'] or file_sha(self.source) != self.metadata['source_sha256']:
            raise ValueError('Source or index coverage changed')
        return count


def summarize(store):
    db = store.db
    result = dict(store.metadata)
    result['n_role_timelines'] = db.execute('SELECT COUNT(*) FROM (SELECT DISTINCT book,role FROM updates)').fetchone()[0]
    result['n_successor_links'] = db.execute('SELECT COUNT(*) FROM updates WHERE next_update_id IS NOT NULL').fetchone()[0]
    coverage = {}
    for task in ['character_motivation_update', 'interaction_generation']:
        coverage[task] = db.execute('''SELECT COUNT(*) FROM updates u WHERE EXISTS
            (SELECT 1 FROM records r WHERE r.book=u.book AND r.role=u.role AND r.scene=u.scene AND r.task=?)''', (task,)).fetchone()[0]
    result['update_appearances_with_task'] = coverage
    result['successor_links_with_next_interaction'] = db.execute('''
        SELECT COUNT(*) FROM updates u JOIN updates n ON n.row_id=u.next_update_id
        WHERE EXISTS (SELECT 1 FROM records r WHERE r.book=n.book AND r.role=n.role
            AND r.scene=n.scene AND r.task='interaction_generation')
    ''').fetchone()[0]
    result['note'] = ('Source availability, not semantic correctness or independent experimental samples. '
                      'Successors follow numeric scene_index within this training-file namespace; '
                      'canonical narrative chronology and cross-file scene ID equivalence are not certified. '
                      'Narrator-like entries are retained, not certified as NPCs.')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index', required=True)
    parser.add_argument('--source')
    parser.add_argument('--build', action='store_true')
    parser.add_argument('--revision')
    parser.add_argument('--expected-sha256')
    parser.add_argument('--verify', action='store_true', help='Read and verify every original record')
    parser.add_argument('--out', required=True)
    args = parser.parse_args()
    if args.build:
        if not all([args.source, args.revision, args.expected_sha256]):
            parser.error('--build requires --source, --revision and --expected-sha256')
        build_index(args.source, args.index, args.revision, args.expected_sha256)
    store = ExperienceStore(args.index, args.source)
    try:
        result = summarize(store)
        if args.verify:
            result['verified_source_row_spans'] = store.verify_all()
        result['index_sha256'] = file_sha(args.index)
        result['index_bytes'] = Path(args.index).stat().st_size
        result['inventory_script_sha256'] = file_sha(__file__)
    finally:
        store.close()
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
