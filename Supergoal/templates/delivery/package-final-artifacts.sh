#!/usr/bin/env bash
# Template: package final SuperGoal artifacts with path safety, secret scan, deterministic ZIP, and self-check manifest.
set -euo pipefail
ROOT="${SUPERGOAL_ROOT:-$(pwd)/.supergoal}"
OUT="$ROOT/out"
mkdir -p "$OUT"
ARCHIVE="$OUT/final-artifacts.zip"
MANIFEST="$OUT/final-artifacts-manifest.json"
python3 - <<'PY' "$ROOT" "$ARCHIVE" "$MANIFEST"
from pathlib import Path
import hashlib, json, re, stat, sys, zipfile
root=Path(sys.argv[1]).resolve(); archive=Path(sys.argv[2]); manifest=Path(sys.argv[3])
patterns=[re.compile(rb'-----BEGIN (?:RSA |OPENSSH |EC |DSA |)?PRIVATE KEY-----'), re.compile(rb'gh[pousr]_[A-Za-z0-9_]{20,}'), re.compile(rb'(?<![A-Za-z0-9])sk-[A-Za-z0-9]{32,}'), re.compile(rb'eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}')]
def fail(code,msg):
    print(f'{code}: {msg}', file=sys.stderr); raise SystemExit(1)
def sha(data): return hashlib.sha256(data).hexdigest()
def shafile(p): return sha(p.read_bytes())
manifest_in=root/'delivery-manifest.json'
if manifest_in.exists():
    data=json.loads(manifest_in.read_text())
    rels=[item['path'] if isinstance(item,dict) else item for item in data.get('items',[])]
else:
    rels=[]
    for p in sorted(root.rglob('*')):
        rel=p.relative_to(root).as_posix()
        if rel.startswith('out/'):
            continue
        rels.append(rel)
files=[]; seen=set()
for rel in rels:
    if rel.startswith('/') or '..' in Path(rel).parts or '\x00' in rel:
        fail('SGV-PACKAGE-PATH-ESCAPE', rel)
    p=root/rel
    try: st=p.lstat()
    except FileNotFoundError: fail('SGV-PACKAGE-MISSING', rel)
    if stat.S_ISDIR(st.st_mode):
        continue
    if stat.S_ISLNK(st.st_mode):
        fail('SGV-PACKAGE-SYMLINK', rel)
    if not stat.S_ISREG(st.st_mode):
        fail('SGV-PACKAGE-SPECIAL-FILE', rel)
    resolved=p.resolve(strict=True)
    if not resolved.is_relative_to(root):
        fail('SGV-PACKAGE-PATH-ESCAPE', rel)
    low=rel.lower()
    if low in seen:
        fail('SGV-PACKAGE-CASE-COLLISION', rel)
    seen.add(low)
    data=p.read_bytes()
    if any(pat.search(data) for pat in patterns):
        fail('SGV-PACKAGE-SECRET', rel)
    files.append((p,rel,data))
records=[{'path':rel,'sha256':sha(data),'bytes':len(data),'mode':'0644'} for p,rel,data in files]
embedded={'manifest_version':'1.0','files':records,'secret_scan':'passed'}
archive.parent.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p,rel,data in files:
        info=zipfile.ZipInfo(rel, date_time=(1980,1,1,0,0,0)); info.external_attr=0o100644<<16; z.writestr(info,data)
    info=zipfile.ZipInfo('MANIFEST.json', date_time=(1980,1,1,0,0,0)); info.external_attr=0o100644<<16; z.writestr(info,json.dumps(embedded,ensure_ascii=False,indent=2,sort_keys=True).encode())
with zipfile.ZipFile(archive) as z:
    names=z.namelist()
    if any(name.startswith('../') or name.startswith('/') for name in names):
        fail('SGV-PACKAGE-ZIP-TRAVERSAL', str(names))
    for rec in records:
        if sha(z.read(rec['path'])) != rec['sha256']:
            fail('SGV-PACKAGE-ZIP-HASH-MISMATCH', rec['path'])
result={'ok':True,'archive':str(archive),'hash':shafile(archive),'files':records,'embedded_manifest':'MANIFEST.json'}
manifest.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n')
print(str(archive)); print(result['hash'])
PY
