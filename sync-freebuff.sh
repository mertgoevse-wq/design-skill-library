#!/usr/bin/env bash
# Design Skill Library — expose the commands to agents without slash-command
# support (Freebuff, Codex, anything that only reads Agent Skills).
#
# Writes a SKILL.md per command into ~/.agents/skills/. The body is the command
# file itself, so Claude Code and Freebuff run identical instructions from a
# single source of truth. Re-run after editing any command file.
set -euo pipefail

LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CMD="$HOME/.claude/commands"
DEST="$HOME/.agents/skills"

mkdir -p "$DEST"

sync_one() {
  local name="$1"
  local desc="$2"
  local src="$CMD/$name.md"
  [[ -f "$src" ]] || { echo "FEHLT: $src"; return 1; }
  mkdir -p "$DEST/$name"
  # The command file carries its own frontmatter for Claude Code. Strip it, or the
  # skill would end up with two YAML blocks and the second would read as body text.
  BODY=$(python3 -c '
import re, sys
t = open(sys.argv[1], encoding="utf-8").read()
sys.stdout.write(re.sub(r"\A---\s*\n.*?\n---\s*\n", "", t, flags=re.DOTALL))
' "$src")
  {
    echo "---"
    echo "name: $name"
    echo "description: $desc"
    echo "---"
    echo
    # No extra "# /name" header: the command body already opens with one.
    printf '%s\n' "$BODY"
  } > "$DEST/$name/SKILL.md"
  echo "  synced  $name  ($(wc -l < "$DEST/$name/SKILL.md") Zeilen)"
}

echo "→ synchronisiere nach $DEST"
sync_one "design" "Autonomous design orchestrator. Classifies the task, selects the best matching skills from a 321-skill library, loads them, then builds and verifies using parallel work tracks. Anti-AI-slop enforced. Use for apps, games, websites, dashboards, 3D and marketing pages. Triggers on /design, or any request to design, build, restyle, critique or polish an interface."
sync_one "design-interview" "Guided plain-language interview that helps non-designers find the right visual direction for their project, matched to the project type, then hands the result to the design orchestrator. Use when someone cannot articulate a look they want."
sync_one "design-skills" "Manage the design skill library: list, search, select, enable, disable individual skills, run the anti-slop gate, rebuild the index, or restore the previous setup. Triggers on /design-skills."

echo
echo "→ ~/.agents/skills jetzt:"
for d in "$DEST"/design "$DEST"/design-interview "$DEST"/design-skills; do
  [ -d "$d" ] && echo "  $(basename "$d")"
done    # Sanity: frontmatter must parse and the body must match the command file
python3 - <<'PY'
import pathlib, re, sys
home = pathlib.Path.home()
bad = 0
for p in sorted(home.joinpath(".agents/skills").glob("design*/SKILL.md")):
    name = p.parent.name
    t = p.read_text(encoding="utf-8")
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", t, re.DOTALL)
    if not m:
        print(f"  FEHLER: kein Frontmatter in {name}"); bad += 1; continue
    fm = m.group(1)
    nm = re.search(r"^name:\s*(.+)$", fm, re.M)
    ds = re.search(r"^description:\s*(.+)$", fm, re.M)
    if not nm or not ds:
        print(f"  FEHLER: name/description fehlt in {name}"); bad += 1; continue
    # No second YAML frontmatter: it would be read as body text. A '---' later in
    # the body is a markdown rule, which is fine.
    rest = t[m.end():]
    if re.match(r"\s*---\s*\n(?:[A-Za-z_-]+:)", rest):
        print(f"  FEHLER: zweites Frontmatter in {name}"); bad += 1; continue
    # body must equal the command file minus its own frontmatter
    cmd = home.joinpath(".claude/commands", f"{name}.md").read_text()
    want = re.sub(r"\A---\s*\n.*?\n---\s*\n", "", cmd, flags=re.DOTALL).strip()
    got = t[m.end():].strip()
    if want != got:
        print(f"  FEHLER: Inhalt weicht ab in {name}"); bad += 1; continue
    print(f"  ok  {name:18} frontmatter + {len(got.splitlines())} Zeilen, inhaltsgleich")
sys.exit(1 if bad else 0)
PY
