#!/usr/bin/env python3
"""Bounded offline verification for one public research repository."""
from pathlib import Path
import hashlib, json, os, subprocess, sys
ROOT=Path(__file__).resolve().parent
REPO=ROOT.parent
if sys.version_info < (3,10) or sys.flags.optimize or os.getenv('PYTHONOPTIMIZE') not in (None,'','0'):
    raise SystemExit('Use Python 3.10+ without optimization; assertions are required.')
checked=0
for line in (REPO/'SHA256SUMS.txt').read_text().splitlines():
    digest,name=line.split('  ',1)
    rel=Path(name)
    if rel.is_absolute() or '..' in rel.parts:
        raise SystemExit('Unsafe manifest path')
    if hashlib.sha256((REPO/rel).read_bytes()).hexdigest()!=digest:
        raise SystemExit('Hash mismatch: '+name)
    checked+=1
script=ROOT/'anna-ticha/verify.py'
result=subprocess.run([sys.executable,str(script)],cwd=script.parent,text=True,capture_output=True)
if result.returncode:
    sys.stderr.write(result.stdout+result.stderr)
    raise SystemExit(result.returncode)
try:
    replay=json.loads(result.stdout)
except json.JSONDecodeError:
    replay={'status':'passed','output':result.stdout.strip()}

print(json.dumps({'status':'passed','topic':'anna-ticha','files_checked':checked,'replay':replay,'limits':['Bounded mechanical replay only; no source-image review or full search rerun.','Coverage is not accuracy; historical truth and priority are not certified.']},ensure_ascii=False,indent=2))
