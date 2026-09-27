#!/usr/bin/env bash
# Design Skill Library — session-start update hook
#
# Designed for environments without cron or a systemd user bus (WSL, containers).
# Run this from a SessionStart hook; it is a no-op unless the library has not been
# refreshed for 30 days, and it never blocks the session.
#
# Safe by construction:
#   - never fails the session (always exits 0)
#   - never touches the published repo
#   - concurrent runs are prevented with a lock file
#   - silent when up to date
set -uo pipefail

LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STATE="$LIB/.last-update"
INTERVAL_DAYS=30
LOCK="$LIB/.update.lock"
QUIET_WINDOW_SEC=8          # stay silent for the first seconds of a session

# ---- lock ------------------------------------------------------------------
exec 9>"$LOCK" 2>/dev/null || exit 0
if ! flock -n 9 2>/dev/null; then
  exit 0                      # another run holds the lock
fi

# ---- interval check --------------------------------------------------------
now=$(date +%s)
if [[ -f "$STATE" ]]; then
  last=$(cat "$STATE" 2>/dev/null || echo 0)
  age_days=$(( (now - last) / 86400 ))
  (( age_days < INTERVAL_DAYS )) && exit 0
  echo "$last" > "$STATE"       # record the attempt so a failure does not retry hourly
else
  echo "$now" > "$STATE"
fi

# ---- run in the background so the session is not delayed --------------------
(
  sleep "$QUIET_WINDOW_SEC"
  out=$(cd "$LIB" && ./auto-update.sh 2>&1)
  status=$?

  if [[ $status -ne 0 ]]; then
    # Surface problems once, into the session transcript.
    claude mcp list >/dev/null 2>&1 || true
    summary=$(grep -E '^summary' <<< "$out" || echo "update failed")
    echo "design-skill-library: $summary" >> "$LIB/logs/last-failure.txt"
  fi
) >/dev/null 2>&1 &

exit 0
