---
description: Manage the design skill library. List, search, select, enable or disable individual design skills, run the anti-slop gate, rebuild the index, or restore the previous setup.
argument-hint: [list | search <term> | select <task> | enable <slug> | disable <slug> | slop | rebuild | restore]
allowed-tools: Bash(ls:*), Bash(cat:*), Bash(rm:*), Bash(ln:*), Bash(cd:*), Bash(python3:*), Bash(./slop-scan.sh:*), Read, Grep
---

# /design-skills — library management

**Request:** $ARGUMENTS

Library: `~/.claude/design-skill-library/` · 316 skills · on-demand
Index: `~/.claude/design-skill-library/index.json`

## `list` (or empty)

```bash
cd ~/.claude/design-skill-library
python3 build-index.py
echo "--- categories ---"
python3 -c "
import json, collections
d = json.load(open('index.json'))
c = collections.Counter(s.get('category','other') for s in d['skills'])
for k,v in c.most_common(): print(f'{k:16}{v}')
print('TOTAL'.ljust(16), d['count'])
"
echo "--- auto-loaded (symlinks) ---"
ls -la ~/.claude/skills/ | grep '^l' | awk '{print $9, $11}'
```

## `search <term>`

```bash
python3 - <<'PY'
import json
d = json.load(open('/home/mert/.claude/design-skill-library/index.json'))
q = "$ARGUMENTS".lower().split(' ', 1)[-1]
for s in d['skills']:
    if q in s['slug'].lower() or q in s['description'].lower():
        print(f"{s['slug']:34} {s.get('category','other'):12} {s['description'][:88]}")
PY
```

## `select <task>`

Run the selection engine — same thing `/design` uses internally.

```bash
python3 ~/.claude/design-skill-library/select-skills.py "$ARGUMENTS"
```

## `enable <slug>` — always auto-loaded

Creates a symlink in `~/.claude/skills/`. From the next session the skill is available
automatically, and its description costs context at every start.

```bash
slug="$ARGUMENTS".split()[-1]
src="$HOME/.claude/design-skill-library/skills/$slug"
[ -d "$src" ] || { echo "MISSING: $slug"; exit 1; }
ln -sfn "$src" "$HOME/.claude/skills/$slug" && echo "enabled: $slug"
```

## `disable <slug>` — back to on-demand

Removes **only the symlink**. The content stays in the library and remains reachable
through `/design`.

```bash
slug="$ARGUMENTS".split()[-1]
p="$HOME/.claude/skills/$slug"
if [ -L "$p" ]; then rm "$p" && echo "disabled: $slug (content kept in library)"
else echo "$slug is not a symlink — nothing changed"; fi
```

## `slop` — anti-slop gate

```bash
cd ~/.claude/design-skill-library && ./slop-scan.sh
```

Scans every skill for banned aesthetics: Liquid Glass, Glassmorphism, Neumorphism,
Brutalism, Skeuomorphism. Exit 1 on violation.

## `rebuild` — regenerate everything

```bash
cd ~/.claude/design-skill-library
./install.sh && python3 build-index.py && python3 build-attribution.py && ./slop-scan.sh
```

## `restore` — undo the symlink migration

Only when the migration of pre-existing skills should be fully reverted:

```bash
rsync -a ~/.claude/skills.pre-designlib.bak/ ~/.claude/skills/ 2>/dev/null \
  || cp -a ~/.claude/skills.pre-designlib.bak/. ~/.claude/skills/
echo "previous state restored"
```

---

**Note:** `enable`, `disable` and `restore` change filesystem state. Only run them when
explicitly asked.
