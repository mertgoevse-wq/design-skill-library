# Design Skill Library

**316 kuratierte Design-Agent-Skills für Claude Code und jeden Agent-Skills-kompatiblen
Client — on-demand geladen, autonom orchestriert.**

Installiert man 100+ Design-Skills normal, liegt die Beschreibung jedes einzelnen bei
jedem Session-Start im Kontext — ob du sie brauchst oder nicht. Diese Bibliothek dreht
das um: Die Skills liegen außerhalb jedes Verzeichnisses, das ein Agent scannt, und ein
einziger `/design`-Befehl wählt und lädt genau die passenden für die aktuelle Aufgabe.

```
Kontext beim Start:  1 Skill-Beschreibung
                     statt 316

Skills verfügbar:    316
Quelle:              werden bei der Installation aus den Origin-Repos geholt
```

> Dieses Repository enthält **keine fremden Skill-Inhalte**. `install.sh` holt jeden
> kuratierten Skill direkt aus seinem eigenen GitHub-Repo. Siehe
> [Lizenzierung](#lizenzierung).

---

## Schnellstart

```bash
git clone https://github.com/mertgoevse-wq/design-skill-library
cd design-skill-library
./install.sh                             # alle 316 Skills holen (~30 MB)
./install.sh gsap-core interface-design  # oder nur was du brauchst
python3 build-index.py                   # Index erzeugen
```

Dann die drei Befehlsdateien und den Router-Skill installieren:

```bash
cp commands/*.md ~/.claude/commands/
cp -R skills/design-library ~/.claude/skills/
```

Funktioniert genauso in Codex, Cursor, Gemini CLI und jedem Client, der das
Agent-Skills-Format liest — `skills/` einfach dorthin legen, wo der Client sucht.

---

## `/design` — der autonome Orchestrator

```
/design build a 3d game hero with shader effects and a HUD
/design redesign our analytics dashboard, dense data, dark mode --n=8
/design onboarding flow for a banking app --style=trustworthy
/design a landing page for a coffee subscription --deep
/design make me an app                            # vage -> geführtes Interview
```

Du beschreibst das Ergebnis. Der Orchestrator erledigt den Rest:

1. **Klassifizieren** — welche Domänen die Aufgabe berührt: `ui`, `ux`, `visual`,
   `motion`, `3d`, `game`, `dataviz`, `mobile`, `a11y`, `review`, `marketing`, `code`.
2. **Auswählen** — `select-skills.py` bewertet alle 316 Skills gegen die Aufgabe, achtet
   auf Kategorie-Vielfalt und liefert eine Rangliste. Der Orchestrator überschreibt sie,
   wenn sein eigenes Urteil besser ist.
3. **Laden** — liest jede gewählte `SKILL.md` *und* die darin genannten `references/`.
   Die Referenzen zu überspringen ist der häufigste Fehler bei diesen Skills.
4. **Ausführen** — arbeitet in Spuren. Foundations laufen zuerst allein; Build, Motion
   und Data/3D/Game laufen danach **als parallele Subagenten**; Verifikation zuletzt.
5. **Durchsetzen** — die Anti-Slop-Regeln sind verbindlich und überschreiben jeden
   widersprechenden Skill.

Er schreibt echten Code: Komponenten, Shader, Styles, Motion. Kein Plan.

### Flags

| Flag | Wirkung |
|---|---|
| `--n=<anzahl>` | wie viele Skills geladen werden (Standard: automatisch, 2–3 pro aktiver Domäne, max. 12) |
| `--domain=a,b` | Domänen-Liste erzwingen statt erraten |
| `--style=<name>` | visuelle Richtung erzwingen |
| `--fast` | ein Durchgang, keine Subagenten |
| `--deep` | große Auswahl erzwingen |
| `--interview` | zuerst das geführte Interview |

### Auswahl-Engine

Auch eigenständig nutzbar:

```bash
python3 select-skills.py "pricing page for a SaaS" --n=6
python3 select-skills.py "3d hero" --domain=3d,motion --style=atmospheric
python3 select-skills.py "saas dashboard" --style=dense-data --json
```

Die Domänenerkennung nutzt Wortgrenzen, damit „photographer" nicht die Chart-Domäne
auslöst. Kategorie-Limits verhindern, dass eine Kategorie die Auswahl dominiert.

---

## `/design-interview` — für Leute ohne Designvokabular

Wenn du einen Look nicht benennen kannst, fragt dieses Interview in Alltagssprache und
bietet benannte Richtungen passend zur Projektart an.

```
/design-interview
/design-interview ein kleiner Laden für handgemachte Keramik
```

Maximal zwei Runden. Für SaaS werden `quiet-professional` / `dense-data` /
`friendly-approachable` angeboten, für ein Portfolio `showcase` / `type-led` /
`experimental`, für ein Spiel `high-energy` / `atmospheric` / `retro-analog`. Jede
Richtung ist in einem schlichten Satz ohne Fachjargon erklärt.

Du kannst jederzeit überspringen — der Orchestrator wählt eine vertretbare Vorgabe,
sagt welche und warum, und macht weiter.

---

## `/design-skills` — Bibliotheksverwaltung

```
/design-skills list              Übersicht + was verlinkt ist
/design-skills search motion     Skills nach Begriff suchen
/design-skills select <task>     Auswahl-Engine ausführen
/design-skills enable polish     dauerhaft auto-geladen
/design-skills disable polish    zurück auf on-demand
/design-skills slop              Anti-Slop-Gate ausführen
/design-skills rebuild           neu installieren und Index erzeugen
```

`enable` verlinkt einen Skill nach `~/.claude/skills/` — er lädt ab dann automatisch und
kostet bei jedem Start Kontext. `disable` entfernt nur den Symlink; der Inhalt bleibt in
der Bibliothek und ist über `/design` weiter erreichbar.

---

## Anti-Slop-Gate

Die Bibliothek ist bewusst frei von den aktuellen KI-Design-Klischees.
`slop-scan.sh` erzwingt das und **endet mit exit 1** bei Verstoß.

**Verboten:** Liquid Glass · Glassmorphism · Neumorphism · Brutalism · Skeuomorphie ·
Frosted-Glass-Flächen · generische AI-Gradienten · gleichförmige Abstände ohne Absicht ·
Standard-3D-Buttons · austauschbarer Buzzword-Text.

**Erwartet:** klare typografische Hierarchie · echtes Raster · systematisches
Farbsystem (bevorzugt OKLCH) mit geprüftem Kontrast · flache Flächen mit funktionaler
Tiefe · Bewegung, die ihren Platz verdient · ein Detail, das in keinem anderen Projekt
vorkommen könnte.

Das Gate unterscheidet **Erwähnung** von **Bewerbung**. Ein Skill mit „avoid
glassmorphism" besteht. Ein Skill mit „styles: glassmorphism, brutalism, neumorphism"
scheitert. Verifiziert an vier Testfällen.

Vom Gate deaktivierte Skills liegen lokal in `.disabled-slop/` mit `WHY-DISABLED.md` und
einem Reaktivierungs-Snippet — es wird nichts gelöscht.

---

## Inhalt der Bibliothek

Kuratiert aus **27+ Upstream-Repositories** in drei Wellen.

| Kategorie | Anzahl | Inhalt |
|---|---|---|
| `motion` | 61 | GSAP und ScrollTrigger, Animationsprinzipien, Timing, Playbooks pro Element und Branche |
| `ux` | 25 | Research, Personas, Journeys, Formulare, Onboarding, HCI-Gesetze |
| `review` | 18 | Critique, Audits, Refactoring, Design-Debt |
| `marketing` | 18 | Landing, Pricing, CRO, Copy, Brand, Onboarding |
| `3d` | 16 | Three.js, Shader, R3F, Babylon, WebGL, Postprocessing |
| `mobile` | 15 | iOS, Android, macOS, iPadOS, watchOS, tvOS, visionOS, React Native |
| `visual` | 13 | Brand Kits, Diagramme, Logos, Bild-Richtung |
| `core` | 11 | Anti-Slop-Gates, Interface-Design, Frontend-Craft |
| `design-system` | 11 | Tokens, Komponenten, Theming, Dark Mode, Governance |
| `a11y` | 7 | WCAG 2.2, ARIA, Screenreader, zugängliche Bewegung |
| `layout` | 7 | Grid, Spacing, Editorial, Image-First |
| `process` + `hci` | 12 | Design-Ops, Fitts, Miller, Hick, Doherty, Zeigarnik |
| `figma` | 6 | Design-to-Code, Library-Generierung, SwiftUI-Brücke |
| `foundations` | 5 | Hierarchie, Abstands-Scales, Icons, Schatten |
| `quality` | 5 | Web Vitals, Performance, QA |
| `design-doc` | 5 | DESIGN.md, Figma-Designsysteme |
| `typography` + `color` | 7 | Type-Scales, Paarung, OKLCH, Paletten |
| `dataviz` + `game` + `2d` | 5 | Charts, HUDs, PixiJS |
| `copy` + `research` + `iterate` | 8 | UX-Writing, Empathy Maps, Varianten, Stresstests |

Ein Skill kam hinein, wenn er mindestens eines erfüllt:

- ein konkretes, überprüfbares Regelwerk statt Motivationsprosa
- echte Installationszahlen auf skills.sh oder nennenswerte GitHub-Resonanz
- eine Lücke, die andere nicht füllten — Kritik, Motion-Tiefe, HCI, Research fehlten oft
- kein Duplikat — Überschneidungen mit impeccable, taste-skill und ui-ux-pro-max
  wurden zusammengeführt statt doppelt übernommen

Bewusst **nicht** übernommen: Prompt-Sammlungen ohne technische Substanz,
Marketing-Buzzword-Skills und alle Skills der verbotenen Ästhetiken.

---

## Dateien

```
design-skill-library/
├── CURATION.tsv          Welle 1  — Design, UX, Motion, A11y, Brand
├── CURATION2.tsv         Welle 2  — Anti-Slop, Grids, Motion, Figma, Research
├── CURATION3.tsv         Welle 3  — Motion-Tiefe, 3D/WebGL, Game-UI, Dataviz, Plattformen
├── install.sh            kuratierte Skills aus ihren Quell-Repos holen
├── select-skills.py      Auswahl-Engine
├── slop-scan.sh          Anti-Slop-Gate
├── build-index.py        INDEX.md + index.json erzeugen
├── build-attribution.py  ATTRIBUTION.md erzeugen
├── migrate-existing.sh   bestehende Skills in die Bibliothek überführen
├── export-repo.sh        veröffentlichbaren Snapshot bauen
├── ATTRIBUTION.md        Quellen, Lizenzen, Commit-Hashes
├── commands/
│   ├── design.md             /design
│   ├── design-interview.md   /design-interview
│   └── design-skills.md      /design-skills
└── skills/
    └── design-library/       Router-Skill
```

`INDEX.md` und `index.json` erzeugt `build-index.py` lokal und werden nicht committet —
sie existieren erst, nachdem du die Skills installiert hast.

---

## Lizenzierung

Dieses Repository enthält **nur selbst geschriebene Dateien**: den Installer, die
Auswahl-Engine, die Manifeste, die Slash-Commands und den Router-Skill. Diese fallen
unter die `LICENSE` dieses Repos.

Die Design-Skills selbst werden hier **nicht weiterverbreitet**. `install.sh` holt
jeden aus seinem Origin-Repo, wo dessen eigene Lizenz und dessen Urheberrecht gelten.
Quellen und Commit-Hashes stehen in [ATTRIBUTION.md](ATTRIBUTION.md) — prüf dort die
Lizenz, bevor du einen Skill kommerziell einsetzt.

Skills, deren Upstream-Repo keine Lizenz nennt oder die Weiterverbreitung einschränkt,
sind vollständig aus den Manifesten ausgeschlossen. Sie bleiben lokal nutzbar, wenn du
sie bereits hast, aber `install.sh` holt sie nicht.
