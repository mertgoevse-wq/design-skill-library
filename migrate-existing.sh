#!/usr/bin/env bash
# Design Skill Library — Migration der bestehenden auto-geladenen Design-Skills
#
# Ziel: Die bereits in ~/.claude/skills vorhandenen Design-Skills sollen NICHT
# mehr bei jeder Session automatisch in den Kontext geladen werden, aber weiter
# vollstaendig zugaenglich bleiben.
#
# Mechanik: Original wird nach ~/.claude/design-skill-library/skills/<slug>
# verschoben, in ~/.claude/skills/<slug> bleibt ein SYMLINK -> Bibliothek.
# Claude Code folgt Symlinks; durch Entfernen des Symlinks ist alles rueckgaengig.
# Vollstaendige Ruecknahme: ./restore-existing.sh
set -euo pipefail

LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$LIB/skills"
SRC="$HOME/.claude/skills"
BACKUP="$LIB/.backup-originals"
mkdir -p "$DEST" "$BACKUP"

# Skills die Design-Kategorie haben. Alles andere (Android, Karpathy, DevOps)
# bleibt bewusst unangetastet und laeuft weiterhin normal.
MIGRATE=(
  impeccable critique clarify colorize typeset layout adapt audit bolder quieter
  distill polish overdrive delight craft animate general-design-review design-review
  design-analysis design-system dieter-rams-principles
  cognitive-load-conversion empathy-mapping journey-mapping ux-heuristics-review
  ux-personas ux-research-methods ux-storyboard like-wish-what-if feature-prioritization
  low-effort-high-reward persuasive-ux writing-guidelines
  ai-governors ai-identifiers ai-inputs ai-trust-builders ai-tuners ai-wayfinders
  gpt-taste high-end-visual-design minimalist-ui design-taste-frontend
  redesign-existing-projects stitch-design-taste image-to-code
  imagegen-frontend-web imagegen-frontend-mobile brandkit website
  emil-design-eng cosmic-glass-dashboard mobile-app-design
  web-design-guidelines accessibility ui-ux-pro-max
  vercel-react-best-practices vercel-react-view-transitions
  vercel-react-native-skills vercel-composition-patterns
  design-taste-frontend-v1
)

moved=0; already=0; missing=0
declare -a SKIPPED=()

for slug in "${MIGRATE[@]}"; do
  s="$SRC/$slug"
  [[ -e "$s" ]] || { missing=$((missing+1)); continue; }

  # Bereits ein Symlink (vorheriger Lauf) oder bereits in der Bibliothek
  if [[ -L "$s" ]]; then
    target=$(readlink -f "$s")
    if [[ "$target" == "$DEST"/* ]]; then already=$((already+1)); continue; fi
  fi

  # Ziel in der Bibliothek schon belegt?
  if [[ -e "$DEST/$slug" && ! -L "$DEST/$slug" ]]; then
    # Bibliothek hat bereits eine Version -> vorhandene behalten, Original nur sichern
    if [[ ! -e "$BACKUP/$slug" ]]; then
      cp -R "$s" "$BACKUP/$slug"
    fi
    rm -rf "$s"
    ln -s "$DEST/$slug" "$s"
    echo "RELINK $slug  (Bibliothek behalten, Original gesichert)"
    moved=$((moved+1)); continue
  fi

  # Backup anlegen, dann verschieben
  if [[ ! -e "$BACKUP/$slug" ]]; then
    cp -R "$s" "$BACKUP/$slug"
  fi
  rm -rf "$DEST/$slug"
  mv "$s" "$DEST/$slug"
  ln -s "$DEST/$slug" "$s"
  echo "MOVED  $slug"
  moved=$((moved+1))
done

echo
echo "─────────────────────────────────────────"
echo "migriert: $moved   bereits symlinked: $already   nicht vorhanden: $missing"
echo "Backup der Originale: $BACKUP"
