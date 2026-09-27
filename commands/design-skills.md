---
description: Manage the design skill library. List, search, enable or disable individual design skills, check the anti-slop gate, or rebuild the index.
argument-hint: [list | search <term> | enable <slug> | disable <slug> | slop | rebuild]
allowed-tools: Bash(ls:*), Bash(cat:*), Bash(rm:*), Bash(ln:*), Bash(cd:*), Bash(python3:*), Bash(chmod:*), Read, Grep
---

# /design-skills — Bibliothek verwalten

**Anfrage:** $ARGUMENTS

Bibliothek: `~/.claude/design-skill-library/` · 224 Skills · on-demand
Index: `~/.claude/design-skill-library/index.json`

## `list` (oder leer)

Kurze Übersicht: Anzahl pro Kategorie, plus alle Skills, die **symlinked** also
automatisch geladen werden.

```bash
cd ~/.claude/design-skill-library
python3 build-index.py
echo "--- auto-geladen (Symlinks) ---"
ls -la ~/.claude/skills/ | grep '^l' | awk '{print $9, $11, $12}'
```

## `search <term>`

```bash
python3 - <<'PY'
import json, sys
d = json.load(open('/home/mert/.claude/design-skill-library/index.json'))
q = "$ARGUMENTS".lower().split(' ', 1)[-1]
for s in d['skills']:
    if q in s['slug'].lower() or q in s['description'].lower():
        print(f"{s['slug']:38} {s['description'][:100]}")
PY
```

## `enable <slug>` — dauerhaft auto-geladen

Legt einen Symlink in `~/.claude/skills/` an. Ab der nächsten Session ist der Skill
automatisch verfügbar **und** kostet dann Kontext bei jedem Start.

```bash
slug="$ARGUMENTS".split()[-1]
src="$HOME/.claude/design-skill-library/skills/$slug"
[ -d "$src" ] || { echo "FEHLT: $slug"; exit 1; }
ln -sfn "$src" "$HOME/.claude/skills/$slug" && echo "aktiviert: $slug"
```

## `disable <slug>` — wieder aus dem Auto-Laden nehmen

Entfernt **nur den Symlink**. Der Inhalt bleibt in der Bibliothek und ist über
`/design` weiterhin on-demand nutzbar.

```bash
slug="$ARGUMENTS".split()[-1]
p="$HOME/.claude/skills/$slug"
if [ -L "$p" ]; then rm "$p" && echo "deaktiviert: $slug (Inhalt bleibt in Bibliothek)"
else echo "$slug ist kein Symlink — nichts geändert"; fi
```

## `slop` — Anti-Slop-Gate

```bash
cd ~/.claude/design-skill-library && ./slop-scan.sh
```

Prüft die gesamte Bibliothek auf die verbotenen Ästhetiken: Liquid Glass, Glassmorphism,
Neumorphism, Brutalism, Skeuomorphie.

## `rebuild` — Index neu erzeugen

```bash
cd ~/.claude/design-skill-library
./install.sh && python3 build-index.py && ./slop-scan.sh
```

## `restore` — Migration vollständig zurücknehmen

Nur falls die Symlink-Migration der Bestands-Skills rückgängig gemacht werden soll:

```bash
rsync -a ~/.claude/skills.pre-designlib.bak/ ~/.claude/skills/
echo "Bestand wiederhergestellt"
```

---

**Wichtig:** Befehle in diesem File ändern Dateisystemzustand. Führe `disable` und
`restore` nur aus, wenn sie explizit angefordert wurden.
