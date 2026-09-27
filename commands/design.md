---
description: Intelligent design skill router. Picks the best matching skills from a 224-skill on-demand library, loads them, and applies them in parallel where independent. Anti-AI-slop enforced.
argument-hint: <was du designen/kritiseren/optimieren willst>
allowed-tools: Read, Grep, Glob, Bash(python3:*), Bash(ls:*), Bash(cat:*), Edit, Write, MultiEdit, WebFetch, WebSearch, Task
---

# /design — intelligenter Design-Skill-Router

**Auftrag:** $ARGUMENTS

## Schritt 1 — Passende Skills auswählen

Die Bibliothek liegt in `~/.claude/design-skill-library/` und hat **224 Skills**.
Ihre Beschreibungen sind in `index.json` — **lade nicht alle**, sondern wähle gezielt.

Führe das aus:

```bash
python3 - <<'PY'
import json, re, sys
d = json.load(open('/home/mert/.claude/design-skill-library/index.json'))
q = """$ARGUMENTS""".lower()
# Wörter aus dem Auftrag als Suchbegriffe
terms = [t for t in re.findall(r"[a-zäöüß0-9\-]{3,}", q)]
stop = {"der","die","das","und","oder","mit","für","ein","eine","den","dem","des","auf","von","im","zu","ist","soll","ich","wir","bitte","mach","design","designen","skill","skills"}
terms = [t for t in terms if t not in stop]
scores = {}
for s in d["skills"]:
    hay = (s["slug"] + " " + s["description"]).lower()
    sc = sum(hay.count(t) * (3 if t in s["slug"].lower() else 1) for t in terms)
    if sc: scores[s["slug"]] = sc
top = sorted(scores.items(), key=lambda x: -x[1])[:18]
by = {s["slug"]: s for s in d["skills"]}
for slug, sc in top:
    print(f"[{sc:3}] {slug}\n      {by[slug]['description'][:150]}\n      {by[slug]['path']}")
PY
```

## Schritt 2 — Auswahl treffen

Wähle **2 bis 5** Skills. Kriterien:

- **Deckung:** welche Skills decken zusammen die Aufgabe wirklich ab?
- **Keine Redundanz:** wenn zwei Skills dasselbe tun, nur den stärkeren nehmen.
- **Reihenfolge:** erst Foundations (Typografie, Farbe, Layout, Hierarchie), dann
  Ausführung (Build, Motion), dann Prüfung (Review, A11y, QA).
- **Pragmatisch:** ein Task braucht selten 8 Skills. 3 sind oft besser als 8.

Wenn `$ARGUMENTS` leer ist oder sehr allgemein ist, frage **einmal** nach, was gebaut
werden soll, statt raten.

## Schritt 3 — Skills laden

Lies die `path` der gewählten Skills mit `Read`. Liest ein SKILL.md auf `references/`,
`assets/` oder `templates/` verweist, **lies diese Dateien ebenfalls** — sie enthalten
den eigentlichen Regelkatalog.

Beispiel mehrerer Skills:
```
Read  /home/mert/.claude/design-skill-library/skills/<slug>/SKILL.md
Read  /home/mert/.claude/design-skill-library/skills/<slug>/references/<datei>.md
```

## Schritt 4 — Anwenden

**Arbeite die Skills in der oben gewählten Reihenfolge ab.** Wenn Aufgaben unabhängig
voneinander sind, **nutze `Task`, um sie parallel laufen zu lassen** — z. B. ein Task für
"Kritik & A11y-Audit" und parallel ein Task für "Kopie & Konzept", während du selbst
das visuelle Fundament baust. Sage kurz, was parallel läuft.

Vereint die Skills sich widersprechen, gilt diese Präzedenz:
1. **Grundlagen-Skills** (Typografie, Farbe, Layout) schlagen Effekt-Skills.
2. **Anti-Slop-Skills** (`no-ai-design-slop`, `hallmark`, `audit-ai-design-slop`) schlagen
   jeden Stil-Skill.
3. **Zuletzt:** explizite Nutzer-Vorgaben.

## Schritt 5 — Anti-Slop-Check

Diese Regeln sind **verbindlich** und überschreiben jeden Skill, der sie verletzt:

**Verboten:**
- Liquid Glass, Glassmorphism, Neumorphism, Brutalism, Skeuomorphie
- generische AI-Gradienten, Inter-ohne-Gegenstueck, gleichförmige 8px-Raster ohne Absicht
- Stock-Ästhetik: übermäßige Rundungen, Glow,Glass-Flaechen, Pseudo-3D-Buttons
- Inhalt, der nur so tut als wärs eine Marke (generische Buzzwords)

**Erlaubt und erwünscht:**
- klare typografische Hierarchie mit Absicht, echte Rasterstruktur
- OKLCH-basierte, systematische Farbsysteme mit geprüftem Kontrast
- Editorial-Layout, Flatness mit funktionaler Tiefe, ruhige, gezielte Bewegung
- ein erkennbarer Charakter, der nicht austauschbar ist

Prüfe das Ergebnis bei visuellen Aufgaben mit:
```bash
cd ~/.claude/design-skill-library && ./slop-scan.sh
```

## Schritt 6 — Ergebnis

Berichte kurz:
1. Welche Skills geladen wurden und warum genau diese
2. Was umgesetzt wurde
3. Offene Punkte / bewusste Entscheidungen

**Nicht** alle 224 Skills auflisten. Nur die genutzten.
