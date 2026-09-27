# Design Skill Library

**166 kuratierte Design-Agent-Skills für Claude Code und jeden OpenAI-Agent-Skills-kompatiblen Client — on-demand statt im Kontext.**

Die Skills in `~/.claude/skills/` werden bei **jeder** Session automatisch geladen. Wer
30 bis 100 Design-Skills parallel installiert hat, zahlt dafür bei jedem Start Kontext,
auch wenn davon nur einer gebraucht wird.

Diese Bibliothek löst das über einen **Router**: die Skills liegen physisch in einem
Verzeichnis, das kein Agent scannt, und werden erst geladen, wenn sie wirklich gebraucht
werden. Ein einziger `/design`-Befehl wählt automatisch die passenden aus.

```
Kontext beim Start:   1 Skill-Beschreibung
                     statt 166
Skills verfügbar:    166 (lokal) / 154 (in diesem Repo)
```

---

## Was drin ist

| Kategorie | Anzahl | Beispiele |
|---|---|---|
| `core` | ~20 | Anti-Slop-Gates, Interface-Design, Frontend-Craft |
| `foundations` | ~10 | Hierarchie, Icons, Shadows, Gestaltungsgesetze |
| `typography` | ~8 | Schriftpaarung, Scales, Web-Typografie, Messbreite |
| `color` | ~9 | OKLCH, Paletten, Farbsysteme, Dark Mode |
| `layout` | ~14 | Grid, Spacing, Editorial, Image-First, Frames |
| `motion` | ~22 | GSAP, Scroll, Microinteractions, HCI-Laws, Apple-Motion |
| `a11y` | ~10 | WCAG 2.2, ARIA, Screenreader, inklusives Design |
| `design-system` | ~14 | Tokens, Components, Theming, Governance, Naming |
| `review` | ~18 | Critique, Audits, Refactoring, Design-Debt |
| `ux` | ~20 | Research, Personas, Journeys, Formulare, Onboarding |
| `figma` | ~7 | Figma→Code, Library-Generierung, SwiftUI-Bridge |
| `mobile` | ~10 | Native iOS/Android, React Native, responsive |
| `marketing` | ~15 | Landingpage, Pricing, Copy, Brand, CRO |
| `quality` | ~5 | Web-Vitals, Performance, QA, Accessibility-Plan |
| `iterate` | ~3 | Varianten bauen, Zustands-Stresstests |

Gebaut aus **27 Quell-Repos** — darunter Anthropic, Vercel, Emil Kowalski, Meng To,
Julien Thibeaut, Jakob Krehel, Addy Osmani, Google Stitch und weitere.
Vollständige Aufstellung mit Commit-Hashes und Lizenzen: **[ATTRIBUTION.md](ATTRIBUTION.md)**.

---

## Nutzung

### `/design <Auftrag>` — der Haupteinstieg

Ein einziger Befehl für alles Designrelevante:

```
/design Landingpage für ein Preisanbieter-Tool bauen
/design Animationen im Onboarding auditieren
/design WCAG-Audit der Checkbox-Gruppe
/design Dashboard mit Farbsystem und Dark Mode
```

Ablauf:

1. **Auswahl** — der Befehl durchsucht `index.json` nach Relevanz und schlägt 2–5 Skills vor
2. **Laden** — nur diese werden per `Read` geladen, inkl. aller `references/`
3. **Anwenden** — Foundations zuerst, dann Ausführung, dann Prüfung
4. **Parallelisieren** — unabhängige Teilaufgaben laufen als parallele Subagenten
5. **Prüfen** — Anti-Slop-Gate läuft mit

Präzedenz bei Widersprüchen: Grundlagen-Skills schlagen Effekt-Skills, Anti-Slop-Skills
schlagen jeden Stil-Skill, Nutzer-Vorgaben schlagen alles.

### `/design-skills <befehl>` — Bibliotheksverwaltung

```
/design-skills list              Übersicht + was symlinked ist
/design-skills search motion     Skills nach Begriff durchsuchen
/design-skills enable polish     dauerhaft auto-geladen machen
/design-skills disable polish    wieder aus dem Auto-Laden nehmen
/design-skills slop              Anti-Slop-Gate ausführen
/design-skills rebuild           Index neu erzeugen
```

`enable` legt einen Symlink in `~/.claude/skills/` an — der Skill ist dann in jeder
Session verfügbar, kostet aber entsprechend Kontext. `disable` entfernt nur den
Symlink; der Inhalt bleibt in der Bibliothek und ist über `/design` weiter nutzbar.

---

## Installation

```bash
git clone https://github.com/mertgoevse-wq/design-skill-library
cd design-skill-library
./install.sh
```

Ohne die geklonten Quell-Repos holt `install.sh` die Skills aus `CURATION.tsv` /
`CURATION2.tsv`. Wer nur den fertigen Snapshot nutzen will, kopiert `skills/` direkt:

```bash
cp -r skills/* ~/.claude/design-skill-library/skills/
python3 build-index.py
```

Für Codex, Cursor, Gemini CLI und alle anderen Clients, die das Agent-Skills-Format
lesen, funktioniert `skills/` genauso — einfach in das jeweilige Skill-Verzeichnis legen.

### Router-Skill

`skills/design-library/SKILL.md` muss in `~/.claude/skills/` liegen, damit der Agent die
Bibliothek kennt. Die Slash-Commands liegen in `~/.claude/commands/`.

---

## Anti-Slop-Gate

Die Sammlung ist bewusst frei von den aktuellen KI-Design-Klischees. `slop-scan.sh`
prüft das automatisch und **fehlschlägt** bei Treffern:

**Verboten:** Liquid Glass · Glassmorphism · Neumorphism · Brutalism · Skeuomorphie ·
Frosted-Glass-Shells · generische AI-Gradienten

**Erlaubt und erwünscht:** klare typografische Hierarchie mit Absicht · echte
Rasterstruktur · OKLCH-Farbsysteme mit geprüftem Kontrast · Editorial-Layout ·
funktionale Tiefe statt Deko · ruhige, gezielte Bewegung · ein erkennbarer Charakter

```bash
./slop-scan.sh    # exit 0 = sauber, exit 1 = Verstoß gefunden
```

`/design` erzwingt dieselben Regeln auch ohne Skript — Anti-Slop-Skills
(`no-ai-design-slop`, `hallmark`, `audit-ai-design-slop`) haben dort Vorrang vor
allen Stil-Skills.

---

## Aufbau

```
design-skill-library/
├── INDEX.md              alle Skills als Tabelle (generiert)
├── index.json            Metadaten für den Router
├── CURATION.tsv          Welle 1 — Auswahlmanifest
├── CURATION2.tsv         Welle 2 — Auswahlmanifest
├── ATTRIBUTION.md        Quellen, Lizenzen, Commits
├── install.sh            Skills aus den Manifesten installieren
├── build-index.py        INDEX.md + index.json erzeugen
├── build-attribution.py  ATTRIBUTION.md erzeugen
├── slop-scan.sh          Anti-Slop-Gate
├── export-repo.sh        veröffentlichbaren Snapshot bauen
├── migrate-existing.sh   Bestands-Skills in die Bibliothek überführen
├── commands/
│   ├── design.md         /design
│   └── design-skills.md  /design-skills
└── skills/
    ├── design-library/   Router-Skill
    └── <slug>/           die einzelnen Skills
```

---

## Auswahlkriterien

Ein Skill kam in die Bibliothek, wenn er mindestens eines erfüllt:

- **Konkretes, überprüfbares Regelwerk** statt Motivationsprosa
- **Bestehende Installationszahlen** auf skills.sh oder ≥1k GitHub-Sterne
- **Füllt eine echte Lücke** — Kritik, Motion, A11y, Research, HCI-Laws fehlten oft
- **Keine Kopie** — Redundanzen zu impeccable, taste-skill und ui-ux-pro-max wurden
  zusammengeführt statt mehrfach übernommen

Bewusst **nicht** übernommen: reine Prompt-Sammlungen ohne technische Substanz,
Marketing-Buzzword-Skills, und alle Skills der ausgeschlossenen Ästhetiken.

---

## Lizenz & Urheberrecht

Diese Bibliothek enthält **fremde** Agent-Skills. Urheberrecht und Lizenz liegen
bei den jeweiligen Autoren — dieses Repository stellt **keine** eigene Lizenz über
diese Inhalte.

Quellen ohne erkennbare bzw. restriktive Lizenz (Anthropic, OpenAI, Figma, Vercel und
weitere) sind **nicht** in diesem Repo enthalten. Sie bleiben lokal in der
privaten Bibliothek nutzbar, werden aber nicht weiterverbreitet.

Details je Quelle und Skill: **[ATTRIBUTION.md](ATTRIBUTION.md)**.

Die Projektdateien (`install.sh`, `build-index.py`, `commands/`, `skills/design-library/`,
die Manifeste) sind neu geschrieben und stehen unter der Lizenz dieses Repositories.
