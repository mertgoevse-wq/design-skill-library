# Design Skill Library

**316 curated design agent skills for Claude Code and every Agent-Skills-compatible
client — loaded on demand, orchestrated autonomously.**

Installing 100+ design skills the normal way means every one of their descriptions sits
in your context at every session start, whether you need them or not. This library
inverts that: the skills live outside any directory an agent scans, and a single
`/design` command picks and loads the right ones for the task at hand.

```
Context at startup:  1 skill description
                     instead of 316

Skills available:    316
Fetches:             from their original repos, at install time
```

> This repository contains **no third-party skill content**. `install.sh` fetches each
> curated skill directly from its own GitHub repository. See
> [Licensing](#licensing).

---

## Quick start

```bash
git clone https://github.com/mertgoevse-wq/design-skill-library
cd design-skill-library
./install.sh                       # fetch all 316 skills (~30 MB)
./install.sh gsap-core interface-design   # or just what you need
python3 build-index.py             # generate the index
```

Then install the three command files and the router skill:

```bash
cp commands/*.md ~/.claude/commands/
cp -R skills/design-library ~/.claude/skills/
```

Works the same way in Codex, Cursor, Gemini CLI and any other client that reads the
Agent Skills format — put `skills/` wherever that client looks.

---

## `/design` — the autonomous orchestrator

```
/design build a 3d game hero with shader effects and a HUD
/design redesign our analytics dashboard, dense data, dark mode --n=8
/design onboarding flow for a banking app --style=trustworthy
/design a landing page for a coffee subscription --deep
/design make me an app                            # vague -> guided interview
```

You describe the outcome. The orchestrator does the rest:

1. **Classify** — determines which domains the task spans: `ui`, `ux`, `visual`,
   `motion`, `3d`, `game`, `dataviz`, `mobile`, `a11y`, `review`, `marketing`, `code`.
2. **Select** — `select-skills.py` scores all 316 skills against the task, keeps
   category diversity, and returns a ranked shortlist. The orchestrator overrides it
   when its own read is better.
3. **Load** — reads each selected `SKILL.md` *and* the `references/` directories it
   points to. Skipping the references is the most common way these skills get misapplied.
4. **Execute** — works in tracks. Foundations run alone first; build, motion and
   data/3D/game then run **as parallel subagents**; verification runs last.
5. **Enforce** — anti-slop rules are binding and override any skill that conflicts.

It writes real code: components, shaders, styles, motion. Not a plan.

### Flags

| Flag | Effect |
|---|---|
| `--n=<count>` | how many skills to load (default: auto, 2–3 per active domain, max 12) |
| `--domain=a,b` | force the domain list instead of inferring it |
| `--style=<name>` | force a visual direction |
| `--fast` | single pass, no subagents |
| `--deep` | force a large selection |
| `--interview` | run the guided interview first |

### Selection engine

Usable on its own:

```bash
python3 select-skills.py "pricing page for a SaaS" --n=6
python3 select-skills.py "3d hero" --domain=3d,motion --style=atmospheric
python3 select-skills.py "saas dashboard" --style=dense-data --json
```

Domain detection uses word boundaries, so "photographer" does not trigger the chart
domain. Category caps prevent a single category from dominating the shortlist.

---

## `/design-interview` — for non-designers

When you cannot articulate a look, this asks in plain language and offers named
directions matched to your project type.

```
/design-interview
/design-interview a small shop for handmade ceramics
```

Maximum two rounds. For a SaaS it offers `quiet-professional` / `dense-data` /
`friendly-approachable`; for a portfolio `showcase` / `type-led` / `experimental`; for
a game `high-energy` / `atmospheric` / `retro-analog`. Each is described in one plain
sentence with no design vocabulary.

You can always skip it — the orchestrator picks a defensible default, says which one and
why, and continues.

---

## `/design-skills` — library management

```
/design-skills list              overview + what is symlinked
/design-skills search motion     find skills by term
/design-skills select <task>     run the selection engine
/design-skills enable polish     always auto-load this skill
/design-skills disable polish    back to on-demand
/design-skills slop              run the anti-slop gate
/design-skills rebuild           reinstall and regenerate
```

`enable` symlinks a skill into `~/.claude/skills/` so it loads automatically from then on
— and costs context at every startup. `disable` removes only the symlink; the content
stays in the library and remains reachable through `/design`.

---

## Anti-slop gate

The library is deliberately free of current AI-design clichés. `slop-scan.sh` enforces
this and **exits 1** on violation.

**Forbidden:** Liquid Glass · Glassmorphism · Neumorphism · Brutalism · Skeuomorphism ·
frosted-glass shells · generic AI gradients · undifferentiated uniform spacing · stock
3D buttons · interchangeable buzzword copy.

**Expected:** intentional type hierarchy · a real grid · a systematic colour system
(prefer OKLCH) with checked contrast · flat surfaces with functional depth · motion
that earns its place · one detail that could not appear in any other project.

The gate distinguishes **mention** from **promotion**. A skill that says *"avoid
glassmorphism"* passes. A skill offering *"styles: glassmorphism, brutalism,
neumorphism"* fails. Verified against four fixtures.

Skills disabled by this rule sit in `.disabled-slop/` locally with a
`WHY-DISABLED.md` and a reactivation snippet — nothing is deleted.

---

## What is in the library

Curated from **27+ upstream repositories** across three waves.

| Category | Count | Covers |
|---|---|---|
| `motion` | 61 | GSAP and ScrollTrigger, animation principles, timing, per-element and per-industry playbooks |
| `ux` | 25 | research, personas, journeys, forms, onboarding, HCI laws |
| `review` | 18 | critique, audits, refactoring, design debt |
| `marketing` | 18 | landing, pricing, CRO, copy, brand, onboarding |
| `3d` | 16 | Three.js, shaders, R3F, Babylon, WebGL, postprocessing |
| `mobile` | 15 | iOS, Android, macOS, iPadOS, watchOS, tvOS, visionOS, React Native |
| `visual` | 13 | brand kits, diagrams, logos, image direction |
| `core` | 11 | anti-slop gates, interface design, frontend craft |
| `design-system` | 11 | tokens, components, theming, dark mode, governance |
| `a11y` | 7 | WCAG 2.2, ARIA, screen readers, accessible motion |
| `layout` | 7 | grid, spacing, editorial, image-first |
| `process` + `hci` | 12 | design ops, Fitts, Miller, Hick, Doherty, Zeigarnik |
| `figma` | 6 | design-to-code, library generation, SwiftUI bridge |
| `foundations` | 5 | hierarchy, spacing scales, icons, shadows |
| `quality` | 5 | Web Vitals, performance, QA |
| `design-doc` | 5 | DESIGN.md, Figma design systems |
| `typography` + `color` | 7 | type scales, pairing, OKLCH, palettes |
| `dataviz` + `game` + `2d` | 5 | charts, HUDs, PixiJS |
| `copy` + `research` + `iterate` | 8 | UX writing, empathy maps, variants, stress tests |

A skill qualified if it had at least one of:

- a concrete, checkable rule set rather than motivational prose
- real install numbers on skills.sh or notable GitHub traction
- a gap others did not fill — critique, motion depth, HCI, research were often missing
- no duplicate — overlap with impeccable, taste-skill and ui-ux-pro-max was merged
  rather than taken twice

Deliberately **excluded**: prompt collections without technical substance, marketing
buzzword skills, and every skill of the banned aesthetics.

---

## Files

```
design-skill-library/
├── CURATION.tsv          wave 1  — design, UX, motion, A11y, brand
├── CURATION2.tsv         wave 2  — anti-slop, grids, motion, Figma, research
├── CURATION3.tsv         wave 3  — motion depth, 3D/WebGL, game UI, dataviz, platforms
├── install.sh            fetch curated skills from their source repos
├── select-skills.py      selection engine
├── slop-scan.sh          anti-slop gate
├── build-index.py        generate INDEX.md + index.json
├── build-attribution.py  generate ATTRIBUTION.md
├── migrate-existing.sh   move existing skills into the library
├── export-repo.sh        build the publishable snapshot
├── ATTRIBUTION.md        sources, licenses, commit hashes
├── commands/
│   ├── design.md             /design
│   ├── design-interview.md   /design-interview
│   └── design-skills.md      /design-skills
└── skills/
    └── design-library/       router skill
```

`INDEX.md` and `index.json` are generated locally by `build-index.py` and are not
committed — they only exist once you have installed the skills.

---

## Licensing

This repository contains **only files authored for this project**: the installer, the
selection engine, the manifests, the slash commands and the router skill. Those are
covered by the `LICENSE` in this repo.

The design skills themselves are **not redistributed here**. `install.sh` fetches each
one from its original repository, where its own license and copyright apply. Sources and
commit hashes are recorded in [ATTRIBUTION.md](ATTRIBUTION.md) — check the license there
before using a skill commercially.

Skills whose upstream repository states no license, or restricts redistribution, are
excluded from the manifests entirely. They remain usable locally if you already have
them, but `install.sh` will not fetch them.
