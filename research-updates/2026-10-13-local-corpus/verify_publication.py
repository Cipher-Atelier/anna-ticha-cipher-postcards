#!/usr/bin/env python3
"""Verify this text publication without importing any historical science code."""
import ast
import csv
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import sys

PRIVATE = re.compile(r'/(?:Users|home)/[^\s"<>]+|[A-Za-z]:\\Users\\|(?:thread_id|conversation_id|accountLinkId)\s*["\s:]+[a-zA-Z0-9_-]{8,}|data:[i]mage/|-----BEGIN (?:RSA |OPENSSH )?PRIVATE KEY|\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b', re.I)

def verify(root):
    manifest = json.loads((root / 'PUBLICATION_MANIFEST.json').read_text())
    expected = {'PUBLICATION_MANIFEST.json'}
    for record in manifest['files']:
        name = record['path']
        path = PurePosixPath(name)
        assert not path.is_absolute() and '..' not in path.parts and '\\' not in name, 'unsafe path'
        target = root / name
        assert all(not p.is_symlink() for p in [target, *target.parents]), 'symlink'
        data = target.read_bytes()
        assert len(data) == record['bytes'], 'byte count: ' + name
        assert hashlib.sha256(data).hexdigest() == record['sha256'], 'SHA mismatch: ' + name
        text = data.decode('utf-8')
        assert not PRIVATE.search(text), 'privacy pattern: ' + name
        assert target.suffix.lower() in {'.json', '.csv', '.txt', '.md', '.py'}, 'format'
        if target.suffix == '.json':
            json.loads(text)
        elif target.suffix == '.csv':
            list(csv.reader(io.StringIO(text)))
        elif target.suffix == '.py':
            ast.parse(text)
        expected.add(name)
    actual = {str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
    assert actual == expected, 'unexpected/missing files'
    assert not PRIVATE.search((root / 'PUBLICATION_MANIFEST.json').read_text()), 'manifest privacy'
    records = {r['path']: r for r in manifest['files']}
    members = json.loads((root / 'archive-members.json').read_text())
    for member in members:
        assert member['disposition'] and member['archive_member_sha256'] and member['uncompressed_bytes'] >= 0
        if member['published_path']:
            assert records[member['published_path']]['sha256'] == member['published_sha256'] == member['archive_member_sha256'], 'member export mismatch'
    return {'status': 'PASS', 'files': len(records), 'archive_members': len(members), 'bytes': sum(r['bytes'] for r in records.values()), 'scope': 'publication bytes, safe paths, privacy patterns and text syntax only'}

if __name__ == '__main__':
    try:
        print(json.dumps(verify(Path(__file__).resolve().parent), sort_keys=True))
    except Exception as exc:
        print(json.dumps({'status': 'FAIL', 'error': str(exc)}, sort_keys=True))
        sys.exit(1)
