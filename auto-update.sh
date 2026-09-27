#!/usr/bin/env bash
# Design Skill Library — monthly maintenance
#
# 1. refresh every installed skill from its source repo
# 2. run the anti-slop gate
# 3. run the selection-engine self-test
# 4. rebuild the index
# 5. report what changed
#
# Never pushes. Publishing stays a manual step.
#
# Usage:  ./auto-update.sh [--check]   --check reports only, changes nothing
set -uo pipefail

LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOGDIR="$LIB/logs"
mkdir -p "$LOGDIR"
STAMP=$(date +%Y-%m-%d)
LOG="$LOGDIR/update-$STAMP.log"

CHECK=0
[[ "${1:-}" == "--check" ]] && CHECK=1

say() { printf '%s\n' "$*" | tee -a "$LOG"; }
hr()  { say "─────────────────────────────────────────"; }

hr
say "Design Skill Library — update $STAMP"
say "library: $LIB"
hr

before=$(ls "$LIB/skills" 2>/dev/null | wc -l)

# ---- 1. refresh ------------------------------------------------------------
say
say "▸ 1/4  refresh from source"
if (( CHECK )); then
  say "  (--check: skipping fetch)"
  fetch_note="skipped"
else
  fetch_out=$(cd "$LIB" && ./install.sh --update 2>&1)
  echo "$fetch_out" >> "$LOG"
  failed=$(grep -cE '^(MISS|NOREPO|CLONE|BROKEN)' <<< "$fetch_out" || true)
  installed=$(grep -c '^OK' <<< "$fetch_out" || true)
  fetch_note="installed=$installed failed=$failed"
  say "  $fetch_note"
  (( failed > 0 )) && grep -E '^(MISS|NOREPO|CLONE|BROKEN)' <<< "$fetch_out" \
    | head -10 | while read -r l; do say "    $l"; done
fi

# ---- 2. anti-slop gate -----------------------------------------------------
say
say "▸ 2/4  anti-slop gate"
if (cd "$LIB" && ./slop-scan.sh >> "$LOG" 2>&1); then
  say "  PASS — no banned aesthetic"
  gate=PASS
else
  say "  FAIL — violations below"
  (cd "$LIB" && ./slop-scan.sh 2>/dev/null | grep -E 'BEWERBUNG|NAME ' | head -15) | while read -r l; do say "    $l"; done
  gate=FAIL
fi

# ---- 3. selection self-test ------------------------------------------------
say
say "▸ 3/4  selection engine self-test"
if (cd "$LIB" && python3 select-skills.py --selftest >> "$LOG" 2>&1); then
  say "  PASS"
  st=PASS
else
  say "  FAIL — see $LOG"
  (cd "$LIB" && python3 select-skills.py --selftest 2>/dev/null | grep '^FAIL') | while read -r l; do say "    $l"; done
  st=FAIL
fi

# ---- 4. index --------------------------------------------------------------
say
say "▸ 4/4  rebuild index"
if (cd "$LIB" && python3 build-index.py >> "$LOG" 2>&1); then
  after=$(ls "$LIB/skills" | wc -l)
  say "  $after skills indexed"
  if (( after != before )); then
    say "  count changed: $before -> $after"
  fi
else
  say "  FAIL — see $LOG"
  say "  count: $before"
fi

# ---- summary ---------------------------------------------------------------
hr
say "summary  gate=$gate  selftest=$st  fetch=$fetch_note  skills=$before->$after"
if [[ "$gate" == "FAIL" || "$st" == "FAIL" ]]; then
  say "ACTION NEEDED — see $LOG"
  hr
  exit 1
fi
say "all green. review the log, then commit if something changed:"
say "  cd $LIB/.repo && git status"
hr
