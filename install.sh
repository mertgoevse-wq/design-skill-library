#!/usr/bin/env bash
# Design Skill Library — Installer
# Kopiert die kuratierten Skills aus .tmp-clone/ nach skills/<slug>/
# Idempotent: überschreibt Symlinks, aber lässt echten Inhalt unangetastet.
set -euo pipefail

LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLONE="$LIB/.tmp-clone"
# Both manifests: wave 1 (CURATION.tsv) and wave 2 (CURATION2.tsv)
MANIFESTS=("$LIB/CURATION.tsv" "$LIB/CURATION2.tsv")
DEST="$LIB/skills"

mkdir -p "$DEST"
ok=0; skip=0; fail=0
declare -a FAILED=()

for MANIFEST in "${MANIFESTS[@]}"; do
[[ -f "$MANIFEST" ]] || continue
while IFS=$'\t' read -r slug repo path category installs origin; do
  [[ -z "${slug:-}" || "$slug" == \#* ]] && continue
  src="$CLONE/$repo/$path"
  dst="$DEST/$slug"

  if [[ ! -d "$src" ]]; then
    echo "MISS  $slug  (nicht gefunden: $repo/$path)"
    fail=$((fail+1)); FAILED+=("$slug"); continue
  fi
  if [[ ! -f "$src/SKILL.md" ]]; then
    echo "NOSKILL $slug  ($repo/$path hat keine SKILL.md)"
    fail=$((fail+1)); FAILED+=("$slug"); continue
  fi

  # Wenn Ziel ein Symlink ist (migrierter Skill): Auflösen und durch echten Inhalt ersetzen
  if [[ -L "$dst" ]]; then
    rm "$dst"
  elif [[ -d "$dst" && -n "$(ls -A "$dst" 2>/dev/null)" ]]; then
    echo "KEEP  $slug  (Ziel hat bereits echten Inhalt, übersprungen)"
    skip=$((skip+1)); continue
  fi

  cp -R "$src" "$dst" 2>/dev/null
  if [[ ! -f "$dst/SKILL.md" ]]; then
    echo "BROKEN $slug  (Kopie unvollständig)"
    rm -rf "$dst"; fail=$((fail+1)); FAILED+=("$slug"); continue
  fi
  echo "OK    $slug  <- $repo/$path"
  ok=$((ok+1))
done < "$MANIFEST"
done

echo
echo "─────────────────────────────────────────"
echo "installiert: $ok   übersprungen: $skip   fehlgeschlagen: $fail"
if (( fail > 0 )); then
  printf 'fehlend: %s\n' "${FAILED[*]}"
fi
