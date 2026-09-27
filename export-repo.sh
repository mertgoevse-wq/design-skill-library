#!/usr/bin/env bash
# Design Skill Library — repo export
#
# The published repository contains ONLY content authored for this project:
# the installer, the selection engine, the manifests, the slash commands and
# the router skill. No third-party skill content is redistributed here —
# install.sh fetches each curated skill from its original GitHub repository.
#
# README.md, LICENSE and .gitignore live in the working tree and are preserved
# across re-exports. .git is never touched.
set -euo pipefail

LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
R="$LIB/.repo"

PRESERVE=(README.md README.de.md LICENSE .gitignore)

STASH="$LIB/.repo-stash"
rm -rf "$STASH"; mkdir -p "$STASH"
for f in "${PRESERVE[@]}"; do
  [[ -f "$R/$f" ]] && cp "$R/$f" "$STASH/" || true
done

echo "→ clearing $R (keeping .git)"
find "$R" -mindepth 1 -maxdepth 1 ! -name '.git' -exec rm -rf {} +
mkdir -p "$R/commands" "$R/skills"
cp -a "$STASH/." "$R/" 2>/dev/null || true
rm -rf "$STASH"

echo "→ copying project files"
for f in CURATION.tsv CURATION2.tsv CURATION3.tsv install.sh select-skills.py \
         slop-scan.sh build-index.py build-attribution.py migrate-existing.sh \
         export-repo.sh auto-update.sh update-on-start.sh ATTRIBUTION.md; do
  [[ -f "$LIB/$f" ]] && cp "$LIB/$f" "$R/"
done
chmod +x "$R"/*.sh 2>/dev/null || true
chmod +x "$R"/*.py 2>/dev/null || true

# Slash commands and the router skill (both authored here)
cp "$HOME/.claude/commands/design.md"            "$R/commands/design.md"            2>/dev/null || true
cp "$HOME/.claude/commands/design-skills.md"     "$R/commands/design-skills.md"     2>/dev/null || true
cp "$HOME/.claude/commands/design-interview.md"  "$R/commands/design-interview.md"  2>/dev/null || true
rm -rf "$R/skills/design-library"
cp -R "$HOME/.claude/skills/design-library" "$R/skills/design-library" 2>/dev/null || true

# Guard: refuse to publish if any third-party SKILL.md slipped in.
# The router skill (skills/design-library/SKILL.md) is ours and allowed.
strays=$(find "$R/skills" -mindepth 2 -name SKILL.md -not -path "*/design-library/*" 2>/dev/null | wc -l)
if (( strays > 0 )); then
  echo "ERROR: $strays foreign SKILL.md files in $R/skills — aborting."
  find "$R/skills" -mindepth 2 -name SKILL.md -not -path "*/design-library/*" | head
  exit 1
fi

echo
echo "project files: $(find "$R" -type f -not -path "*/.git/*" | wc -l)"
echo "skills shipped: $(ls "$R/skills" | wc -l)  (router only — the rest is fetched)"
du -sh "$R" --exclude=.git 2>/dev/null || du -sh "$R"
