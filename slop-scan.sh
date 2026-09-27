#!/usr/bin/env bash
# Design Skill Library — Anti-Slop Gate
# Scans every installed skill for banned AI-slop aesthetics.
# Banned: liquid glass, liquid-metal, neumorphism/neomorphic, glassmorphism,
#         brutalism, skeuomorphism, "frosted" glass shells.
# Exit 1 if any skill is flagged.
set -uo pipefail

LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="$LIB/skills"

# name-level bans: whole skill is about a banned aesthetic
NAME_BAN='industrial-brutalist|brutalist-skill|glass-dark-ui|dark-glass|blue-laser-clean-glass|liquid-metal|progressive-blur|glass-dark-mode|high-contrast-skeuomorphic|skeuomorphic-ui|gooey-blob|blue-cloudy-clean-modern'
# content-level bans: banned aesthetic PROMOTED. Lines that explicitly reject it
# ("instead of glassmorphism", "never brutalist") are filtered out first.
BODY_BAN='liquid glass|liquid-glass|neumorph|glassmorphism|brutalist|brutalism|frosted glass'

# lines that NEGATE a banned aesthetic, or list it as an optional variant among many
NEGATION='instead of|rather than|avoid|never |no |not |without|don.t|don\x27t|do not|anti-|or brutalist/ahead of|in place of'

# slugs where the word appears only inside an explicit "pick a tone" list
OPTIONAL_TONE_LIST=('ui-designer')

flag=0
echo "=== Anti-Slop Gate: $DEST ==="
echo

for d in "$DEST"/*/; do
  slug=$(basename "$d")
  [[ -f "$d/SKILL.md" ]] || continue

  if [[ "$slug" =~ $NAME_BAN ]]; then
    echo "BANNED-NAME  $slug"
    flag=1; continue
  fi

  for t in "${OPTIONAL_TONE_LIST[@]}"; do
    [[ "$slug" == "$t" ]] && continue 2
  done

  # only inspect frontmatter description + first 60 lines, not deep references
  hit=$(head -60 "$d/SKILL.md" \
        | grep -Eiv "$NEGATION" \
        | grep -Eio "$BODY_BAN" | sort -u | tr '\n' ',' )
  if [[ -n "$hit" ]]; then
    echo "BANNED-BODY  $slug  -> ${hit%,}"
    flag=1
  fi
done

echo
if (( flag == 1 )); then
  echo "ERGEBNIS: VERSTOESSE GEFUNDEN — Skills oben entfernen oder in CURATION streichen."
  exit 1
fi
echo "ERGEBNIS: sauber — keine verbotene Aesthetik in der Bibliothek."
exit 0
