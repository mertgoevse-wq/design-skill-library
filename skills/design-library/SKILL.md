---
name: design-library
description: On-demand access to a 224-skill design library (UI/UX, typography, color, motion, accessibility, design systems, Figma, anti-AI-slop). Use when the user asks for a design skill by name, wants to search or browse design skills, or when UI/UX/design work should pull in the right expert skill. Triggers on "design skill", "design library", "ui skill", "ux skill", "/design", or any request to design, critique, review, polish or refine an interface.
---

# Design Skill Library — Router

Eine kuratierte Bibliothek von **224 Design-Skills**, die **on demand** geladen werden.
Die Beschreibungen aller Skills liegen in `index.json` und werden **nicht** automatisch
in den Kontext geladen. Lade nur die, die du wirklich brauchst.

## Speicherort

```
~/.claude/design-skill-library/
├── index.json        ← Metadaten aller 224 Skills (slug, description, path)
├── INDEX.md          ← dieselben Daten als Markdown-Tabelle
├── skills/<slug>/    ← die eigentlichen Skills (SKILL.md + Referenzen)
├── CURATION.tsv      ← Welle 1 Manifest
├── CURATION2.tsv     ← Welle 2 Manifest
├── slop-scan.sh      ← Anti-Slop-Gate
└── build-index.py    ← Index neu erzeugen
```

## Wie du einen Skill findest

Nutze `index.json`. Beispiel mit grep:

```bash
# nach einem Begriff suchen
grep -i -o '"slug": "[^"]*"' ~/.claude/design-skill-library/index.json
# oder mit python, um Relevanz zu sortieren
python3 - <<'PY'
import json, re
d = json.load(open('/home/mert/.claude/design-skill-library/index.json'))
q = ['motion', 'animation']
hits = [s for s in d['skills'] if any(t in s['slug'] + ' ' + s['description'].lower() for t in q)]
for s in hits[:15]:
    print(f"{s['slug']:38} {s['description'][:90]}")
PY
```

## Wie du einen Skill lädst

`Read` die angegebene `path` aus `index.json`. Bei Skills mit Referenzordnern
(z. B. `*/references/`, `*/assets/`) **auch diese lesen**, wenn SKILL.md darauf verweist.

## Kategorien in der Bibliothek

| Kategorie | Wofür |
|---|---|
| `core` | Grundlagen:anti-slop, Interface-Design, Frontend-Craft |
| `foundations` | Typografie, Farbe, Hierarchie, Shadows, Icons |
| `typography` | Schriftpaarung, Scales, Web-Typografie |
| `color` | Paletten, OKLCH, Farbsysteme, Theme-Mode |
| `layout` | Grid, Spacing, Editorial, Image-First |
| `motion` | Animation, GSAP, Scroll, Microinteractions, HCI-Laws |
| `a11y` | WCAG, ARIA, Screenreader, inklusives Design |
| `design-system` | Tokens, Components, Theming, Governance |
| `review` | Critique, Audits, Refactoring, Debt |
| `ux` | Research, Personas, Journeys, HCI, Onboarding |
| `figma` | Figma→Code, Design-Generierung, Libraries |
| `mobile` | Native iOS/Android, React Native, responsive |
| `marketing` | Landingpage, Pricing, Copy, Brand, CRO |
| `quality` | Web-Vitals, Performance, QA |
| `iterate` | Varianten bauen, Stress-Tests |

## Anti-Slop-Regeln (verbindlich)

Diese Bibliothek ist bewusst **free von** Liquid Glass, Glassmorphism, Neumorphism,
Brutalism und Skeuomorphism. Bei Design-Arbeit gilt:

- **Verboten:** Liquid Glass, Glassmorphism, Neumorphismus, Brutalismus, Skeuomorphie,
  generische "AI-Look"-Gradienten, Inter/gleiche Systemfonts ohne Kontrastidee.
- **Erlaubt und bevorzugt:** klare Typografie-Hierarchie, echte Raster, bewusste
  Farbsysteme (OKLCH), Editorial-Layouts, reduzierte Elevation, funktionale Bewegung.
- Vor Abschluss einer Design-Aufgabe: `./slop-scan.sh` prüfen, falls Visuals involved sind.

Bereits deaktiviert und aus dem aktiven Set entfernt: `industrial-brutalist-ui`,
`cosmic-glass-dashboard` (liegen in `.disabled-slop/`).

## Skills mit Sonderstatus

Einige Skills in `~/.claude/skills/` sind **Symlinks** in diese Bibliothek. Sie
tauchen deshalb normal im Skill-Tool auf, kosten aber keinen extra Speicher:

```bash
ls -la ~/.claude/skills/ | grep '^l'   # alle verlinkten Skills
```

Um einen davon dauerhaft aus dem Auto-Laden zu nehmen, Symlink löschen — der Inhalt
bleibt in der Bibliothek erhalten.
