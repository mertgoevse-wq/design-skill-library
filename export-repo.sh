#!/usr/bin/env bash
# Design Skill Library — Repo-Export
#
# Erzeugt .repo/ mit ausschliesslich Inhalten, deren Weiterverbreitung belegbar
# erlaubt ist. Skills aus Quellen ohne erkennbare bzw. restriktive Lizenz
# bleiben lokal in der Bibliothek, werden aber nicht veroeffentlicht.
set -euo pipefail

LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
R="$LIB/.repo"

echo "→ ermittle lizenzierte Skills …"
ALLOW="$LIB/.allowlist.tsv"
python3 - "$LIB" > "$ALLOW" <<'PY'
import re, sys
from pathlib import Path
lib = Path(sys.argv[1])
EXCLUDE = {
    "anthropics_skills", "anthropics_claude-code", "openai_skills",
    "figma_mcp-server-guide", "jakubkrehel_oklch-skill",
    "daniel-dan-conrad_ui-designer-skill", "sentimony_skills",
    "vercel-labs_agent-skills",
}
PERMISSIVE = ("Apache License", "MIT License", "The MIT License", "BSD")
rows = []
for mf in ("CURATION.tsv", "CURATION2.tsv"):
    p = lib / mf
    if not p.is_file():
        continue
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        f = line.split("\t")
        if len(f) < 2 or f[1] in EXCLUDE:
            continue
        repo = lib / ".tmp-clone" / f[1]
        if not repo.is_dir():
            continue
        ok = False
        for lf in repo.glob("LICENSE*"):
            head = lf.read_text(errors="replace")[:1200]
            if any(re.search(pat, head, re.I) for pat in PERMISSIVE):
                ok = True
        if ok:
            rows.append(f"{f[0]}\t{f[1]}")
print("\n".join(rows))
PY
echo "  $(wc -l < "$ALLOW") Skills erlaubt"

echo "→ staging nach $R"
# README/LICENSE/.gitignore liegen dauerhaft in $R und werden beim Re-Export
# gesichert, damit sie nicht verloren gehen. .git wird NIEMALS angefasst:
# das Arbeitsverzeichnis ist selbst das geklonte Repo.
STASH="$LIB/.repo-stash"
rm -rf "$STASH"; mkdir -p "$STASH"
for f in README.md LICENSE .gitignore; do
  [[ -f "$R/$f" ]] && cp "$R/$f" "$STASH/" || true
done

# Inhalt loeschen statt Verzeichnis entfernen -> .git bleibt erhalten
find "$R" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +
mkdir -p "$R/skills" "$R/commands"
cp -a "$STASH/." "$R/"
rm -rf "$STASH"

for f in CURATION.tsv CURATION2.tsv ATTRIBUTION.md install.sh slop-scan.sh \
         build-index.py build-attribution.py migrate-existing.sh export-repo.sh; do
  [[ -f "$LIB/$f" ]] && cp "$LIB/$f" "$R/"
done
chmod +x "$R"/*.sh 2>/dev/null || true

cp "$HOME/.claude/commands/design.md"         "$R/commands/design.md"         2>/dev/null || true
cp "$HOME/.claude/commands/design-skills.md" "$R/commands/design-skills.md" 2>/dev/null || true
cp -R "$HOME/.claude/skills/design-library"  "$R/skills/design-library"     2>/dev/null || true

echo "→ kopiere Skills …"
count=0
while IFS=$'\t' read -r slug repo; do
  [[ -z "${slug:-}" ]] && continue
  src="$LIB/skills/$slug"
  [[ -d "$src" ]] || continue
  rm -rf "$R/skills/$slug"
  cp -R "$src" "$R/skills/$slug"
  count=$((count + 1))
done < "$ALLOW"
rm -f "$ALLOW"

# Index ueber den fertigen Snapshot erzeugen (nicht die lokale Gesamtversion)
(cd "$R" && python3 build-index.py) || echo "WARNUNG: Index-Erzeugung fehlgeschlagen"

echo
echo "Skills im Repo-Snapshot: $count"
du -sh "$R"
