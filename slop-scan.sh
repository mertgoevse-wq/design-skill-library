#!/usr/bin/env bash
# Design Skill Library — Anti-Slop Gate
#
# Prüft die gesamte Bibliothek auf die verbotenen AI-Slop-Aesthetiken:
#   Liquid Glass, Glassmorphism, Neumorphism, Brutalism, Skeuomorphie
#
# Unterscheidet zwei Faelle:
#   ERWAHNUNG  — der Skill lehnt die Aesthetik ab ("instead of glassmorphism",
#                "glassmorphism is dated")  -> erlaubt
#   BEWERBUNG  — der Skill bietet sie als Option an ("Styles: glassmorphism,
#                brutalism, ...")           -> Verstoß
#
# Exit 0 = sauber, Exit 1 = mindestens ein Verstoess.
set -uo pipefail

LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEST="${1:-$LIB/skills}"

# ---- 1. Namentliche Verbote: der Skill IST die verbotene Aesthetik ----
NAME_BAN='industrial-brutalist|brutalist-skill|brutalism|glass-dark-ui|dark-glass|glass-dark-mode|blue-laser-clean-glass|liquid-metal|liquid-glass|progressive-blur|high-contrast-skeuomorphic|skeuomorphic-ui|glassmorphism|neumorphism|neomorphic|cosmic-glass'

# ---- 2. Begriffe, die in der Bibliothek nicht vorkommen duerfen ----
TERM_BAN='liquid glass|liquid-glass|glassmorphism|neumorph|neomorphic|brutalist|brutalism|skeuomorph|frosted glass'

# ---- 3. Zeilen, die eine Aesthetik ABLEHNEN -> kein Verstoß ----
NEGATION='instead of|rather than|avoid|avoiding|never |no |not |without|do ?n.t|dont|anti-|anti slop|keeps? being (fashionable|dated)|trendy|trend-driven|dated|feels? dated|outdated|hierarchie|out of fashion|werden|vermeiden'

# ---- 4. Muster fuer BEWERBUNG: Aesthetik als waehlbare Option ----
PROMOTION='styles?:|themes?:|moods?:|aesthetic?s?:|options?:|variants?:|pick (a|one|your|the)|choose|select|supports?|including|use (it|them|these)|apply (a|the|it)|such as|e\.g\.|or (brutalism|glassmorphism|neumorphism|skeuomorph)'

# ---- 5. Manuell bestaetigte Sonderfaelle ----
# slug -> Begruendung. "ok" heisst: geprueft, das Vorkommen ist harmlos.
ALLOWLIST=(
  "ui-designer|Ton-Liste in einem Brainstorm-Schritt, keine Stil-Vorlage"
  "dieter-rams-principles|nennt Glassmorphism explizit als Ueberhol-Meilenstein"
  "editorial-tech|verbietet Glassmorphism ausdruecklich"
  "hallmark|anti-slop-Gate, verhindert die Aesthetiken"
  "no-ai-design-slop|anti-slop-Gate"
  "audit-ai-design-slop|anti-slop-Audit"
)

allowed_for() {
  local slug="$1" entry
  for entry in "${ALLOWLIST[@]}"; do
    [[ "${entry%%|*}" == "$slug" ]] && return 0
  done
  return 1
}

flag=0
checked=0
declare -a VIOLATIONS=()

echo "=== Anti-Slop Gate: $DEST ==="
echo

for d in "$DEST"/*/; do
  [[ -d "$d" ]] || continue
  slug=$(basename "$d")
  [[ -f "$d/SKILL.md" ]] || continue
  checked=$((checked + 1))

  # 1) Namensverbot
  if [[ "$slug" =~ $NAME_BAN ]]; then
    VIOLATIONS+=("NAME    $slug  — Skill ist selbst eine verbotene Aesthetik")
    flag=1; continue
  fi

  allowed_for "$slug" && continue

  # Frontmatter-Description + erste 80 Zeilen; Referenzordner nicht
  body=$(head -80 "$d/SKILL.md")

  # 2a) Vorkommen insgesamt (fuer die Meldung)
  terms=$(printf '%s' "$body" | grep -Eio "$TERM_BAN" | sort -u | tr '\n' ',' | sed 's/,$//')
  [[ -z "$terms" ]] && continue

  # 2b) davon beworbene Zeilen: Begriff UND Bewerbungsmuster, aber KEINE Ablehnung
  promo=$(printf '%s' "$body" \
          | grep -Ei "$TERM_BAN" \
          | grep -Ei "$PROMOTION" \
          | grep -Eiv "$NEGATION" \
          | head -3)

  if [[ -n "$promo" ]]; then
    VIOLATIONS+=("BEWERBUNG $slug  -> $terms")
    flag=1
  else
    VIOLATIONS+=("ERWAHNUNG $slug  -> $terms  (nur ablehnend, ok)")
  fi
done

echo "geprueft: $checked Skills"
echo
if (( flag == 1 )); then
  for v in "${VIOLATIONS[@]}"; do
    [[ "$v" == ERWAHNUNG* ]] || echo "  $v"
  done
  echo
  echo "ERGEBNIS: VERSTOESSE GEFUNDEN."
  echo "  -> Skills aus der Bibliothek nehmen (nach .disabled-slop/)"
  echo "  -> oder Eintraege in CURATION*.tsv streichen"
  exit 1
fi

# Erwaehnungen nur melden, wenn welche da sind
mentions=$(printf '%s\n' "${VIOLATIONS[@]+"${VIOLATIONS[@]}"}" | grep '^ERWAHNUNG' || true)
if [[ -n "$mentions" ]]; then
  echo "Nur ablehnende Erwaehnungen (kein Handlungsbedarf):"
  printf '%s\n' "$mentions" | sed 's/^/  /'
  echo
fi
echo "ERGEBNIS: sauber — keine verbotene Aesthetik in der Bibliothek."
exit 0
