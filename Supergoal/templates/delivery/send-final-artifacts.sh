#!/usr/bin/env bash
# Template: send packaged final artifacts and write a strict blocking receipt.
set -euo pipefail
ROOT="${SUPERGOAL_ROOT:-$(pwd)/.supergoal}"
OUT="$ROOT/out"
TARGET="${SUPERGOAL_DELIVERY_TARGET:?set SUPERGOAL_DELIVERY_TARGET}"
ARCHIVE="${1:-$OUT/final-artifacts.zip}"
[[ -s "$ARCHIVE" ]] || { echo "missing archive: $ARCHIVE" >&2; exit 2; }
HASH="$(sha256sum "$ARCHIVE" | cut -d' ' -f1)"
RECEIPT="$OUT/final-artifacts-delivery-receipt.json"
FORCE="${SUPERGOAL_FORCE_RESEND:-0}"
if [[ -f "$RECEIPT" && "$FORCE" != "1" ]] && python3 - <<'PY' "$RECEIPT" "$TARGET" "$ARCHIVE" "$HASH"
import json,sys
path,target,archive,hash_=sys.argv[1:]
try:
    r=json.load(open(path))
    req={'ok','sent','kind','target','archive','hash','message_id'}
    assert not (req-set(r)), 'missing fields'
    assert r['ok'] is True and r['sent'] is True
    assert r['kind']=='final-artifacts'
    assert r['target']==target and r['archive']==archive and r['hash']==hash_
    assert str(r['message_id']).strip()
except Exception as e:
    print(f'receipt reuse rejected: {e}', file=sys.stderr); raise SystemExit(1)
PY
then
  echo "final artifacts already sent for target+hash"
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
MESSAGE_ID="$(TRANSPORT_SEND_FILE "$ARCHIVE")"
[[ -n "$MESSAGE_ID" ]] || { echo "transport returned empty message id" >&2; exit 4; }
python3 - <<'PY' "$RECEIPT" "$TARGET" "$ARCHIVE" "$HASH" "$MESSAGE_ID"
import json,sys,datetime
path,target,archive,hash_,message_id=sys.argv[1:]
json.dump({'ok':True,'sent':True,'kind':'final-artifacts','target':target,'archive':archive,'hash':hash_,'message_id':message_id,'sent_at':datetime.datetime.now(datetime.timezone.utc).isoformat()}, open(path,'w'), ensure_ascii=False, indent=2, sort_keys=True)
PY
