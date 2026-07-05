#!/usr/bin/env bash
# Template: send the required SuperGoal planning review pack as native files with strict receipt reuse.
set -euo pipefail
ROOT="${SUPERGOAL_ROOT:-$(pwd)/.supergoal}"
OUT="$ROOT/out"
mkdir -p "$OUT"
TARGET="${SUPERGOAL_DELIVERY_TARGET:?set SUPERGOAL_DELIVERY_TARGET}"
FORCE="${SUPERGOAL_FORCE_RESEND:-0}"
FILES=("$ROOT/THINKING.md" "$ROOT/LOOP_DESIGN.md" "$ROOT/ROADMAP.md" "$ROOT/LAUNCH_GOAL.md")
if [[ -s "$ROOT/RESEARCH.md" ]]; then FILES+=("$ROOT/RESEARCH.md"); fi
for f in "${FILES[@]}"; do [[ -s "$f" ]] || { echo "missing review file: $f" >&2; exit 2; }; done
RECEIPT="$OUT/review-md-files-delivery-receipt.json"
HASHES=$(python3 - <<'PY' "${FILES[@]}"
import hashlib,json,sys,os
print(json.dumps({os.path.basename(p): hashlib.sha256(open(p,'rb').read()).hexdigest() for p in sys.argv[1:]}, sort_keys=True))
PY
)
if [[ -f "$RECEIPT" && "$FORCE" != "1" ]] && python3 - <<'PY' "$RECEIPT" "$TARGET" "$HASHES"
import json,sys
path,target,hashes=sys.argv[1:]
try:
    r=json.load(open(path)); h=json.loads(hashes)
    req={'ok','sent','kind','pack_version','target','files','hashes','message_ids'}
    assert not (req-set(r)), 'missing fields'
    assert r['ok'] is True and r['sent'] is True
    assert r['kind']=='review-md-files' and r['pack_version']=='review_pack_v2'
    assert r['target']==target and r['hashes']==h
    assert sorted(r['files'])==sorted(h)
    assert isinstance(r['message_ids'], list) and len(r['message_ids'])==len(r['files']) and all(str(x).strip() for x in r['message_ids'])
except Exception as e:
    print(f'receipt reuse rejected: {e}', file=sys.stderr); raise SystemExit(1)
PY
then
  echo "review files already sent for target+hash"
  exit 0
fi
TRANSPORT_SEND_FILE() {
  file="$1"
  [[ -n "${SUPERGOAL_TRANSPORT_SEND_FILE_CMD:-}" ]] || {
    echo "no real SUPERGOAL_TRANSPORT_SEND_FILE_CMD configured; refusing to mint a fake delivery receipt" >&2
    exit 3
  }
  SUPERGOAL_SEND_TARGET="$TARGET" SUPERGOAL_SEND_FILE="$file" bash -lc "$SUPERGOAL_TRANSPORT_SEND_FILE_CMD"
}
MESSAGE_IDS=()
for f in "${FILES[@]}"; do
  msg_id="$(TRANSPORT_SEND_FILE "$f")"
  [[ -n "$msg_id" ]] || { echo "transport returned empty message id for $f" >&2; exit 4; }
  MESSAGE_IDS+=("$msg_id")
done
python3 - <<'PY' "$RECEIPT" "$TARGET" "$HASHES" "${MESSAGE_IDS[@]}"
import json,sys,datetime
path,target,hashes,*message_ids=sys.argv[1:]
h=json.loads(hashes)
json.dump({'ok':True,'sent':True,'kind':'review-md-files','pack_version':'review_pack_v2','target':target,'files':sorted(h.keys()),'hashes':h,'message_ids':message_ids,'sent_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}, open(path,'w'), ensure_ascii=False, indent=2, sort_keys=True)
PY
