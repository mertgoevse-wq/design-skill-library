<div align="center">

# Design Skill Library

**321 curated design agent skills.<br>Loaded on demand, orchestrated autonomously.**

[Quick start](#quick-start) · [`/design`](#design--the-autonomous-orchestrator) · [`/design-interview`](#design-interview--for-non-designers) · [Anti-slop](#anti-slop-gate) · [Deutsch](README.de.md)

</div>

---

<div align="center">

| | |
|---|---|
| **Skills** | 321 |
| **Sources** | 74 repositories |
| **Context at startup** | 1 description, not 321 |
| **Vendored content** | none — fetched at install |

</div>

---

## The problem

Installing design skills the normal way puts every description in your context at
session start, whether you need it or not.

This library inverts that. The skills sit in a directory no agent scans. A single
`/design` command reads the task, decides what kind of work it is, loads the right
skills, and builds.

```
Context at startup:  1 skill description        (not 321)
Loaded per task:     2–5 skills, on demand     (~21 KB)
```

> This repository contains **no third-party skill content**. `install.sh` fetches each
> curated skill from its own GitHub repository at install time.

---

## Quick start

```bash
git clone https://github.com/mertgoevse-wq/design-skill-library
cd design-skill-library

./install.sh                               # all 321 skills (~30 MB)
./install.sh gsap-core interface-design    # or only what you need
python3 build-index.py                     # generate the index
```

Register the commands and the router:

```bash
cp commands/*.md ~/.claude/commands/
cp -R skills/design-library ~/.claude/skills/
```

**Freebuff and other agents without slash commands** — `./sync-freebuff.sh` writes the
same three commands into `~/.agents/skills/` as skills. Opt-in, because that directory is
auto-scanned: `--remove` undoes it.

---

## `/design` — the autonomous orchestrator

```
/design build a 3d game hero with shader effects and a HUD
/design redesign our analytics dashboard, dense data, dark mode --n=8
/design onboarding flow for a banking app --style=trustworthy
/design a landing page for a coffee subscription --deep
/design make me an app                            # vague → guided interview
```

You describe the outcome. The orchestrator does the rest.

| step | what happens |
|---|---|
| **Classify** | determines the domains: `ui` `ux` `visual` `motion` `3d` `game` `dataviz` `mobile` `a11y` `review` `marketing` `code` |
| **Select** | scores all 321 skills, caps per category, sizes 2–3 per domain |
| **Load** | reads each `SKILL.md` **and** the `references/` it points to |
| **Execute** | foundations alone first, then build + motion + data/3D **in parallel**, verification last |
| **Enforce** | anti-slop rules, overriding any skill that conflicts |

It writes real code — components, shaders, styles, motion. Not a plan.

### Flags

| flag | effect |
|---|---|
| `--n=<count>` | how many skills to load (default: auto, max 12) |
| `--domain=a,b` | force the domain list |
| `--style=<name>` | force a visual direction |
| `--fast` | single pass, no subagents |
| `--deep` | force a large selection |
| `--interview` | run the guided interview first |

### Selection engine

Works on its own:

```bash
python3 select-skills.py "pricing page for a saas" --n=6
python3 select-skills.py "3d hero" --domain=3d,motion --style=atmospheric
python3 select-skills.py --selftest        # 11 cases
```

Weighted word-boundary matching, so "photographer" does not trigger the chart domain
and "apple" does not trigger the app domain. Industry modifiers — `fintech`,
`ecommerce`, `healthcare`, `education`, `enterprise`, `portfolio` — inform selection
without competing for a primary domain slot.

---

## `/design-interview` — for non-designers

When you cannot name a look, this asks in plain language and offers named directions
matched to your project type.

```
/design-interview a small shop for handmade ceramics
```

| project type | directions offered |
|---|---|
| SaaS / dashboard | `quiet-professional` · `dense-data` · `friendly-approachable` |
| Marketing site | `editorial-bold` · `minimal-calm` · `expressive-motion` |
| Consumer app | `warm-human` · `swift-functional` · `playful` |
| Game | `high-energy` · `atmospheric` · `retro-analog` |
| Portfolio | `showcase` · `type-led` · `experimental` |
| Shop | `trustworthy` · `premium` · `bargain-loud` |

Two rounds maximum, no design vocabulary. Skippable — the orchestrator picks a
defensible default, says which, and continues.

---

## `/design-skills` — library management

```
/design-skills list              overview + what is symlinked
/design-skills search motion     find by term
/design-skills select <task>     run the selection engine
/design-skills enable polish     always auto-load
/design-skills disable polish    back to on-demand
/design-skills slop              run the anti-slop gate
/design-skills rebuild           reinstall and regenerate
```

---

## Anti-slop gate

The library is deliberately free of current AI-design clichés. `slop-scan.sh` enforces
it and **exits 1** on violation.

**Forbidden** — Liquid Glass · Glassmorphism · Neumorphism · Brutalism · Skeuomorphism ·
frosted-glass shells · generic AI gradients · undifferentiated uniform spacing · stock
3D buttons · interchangeable buzzword copy.

**Expected** — intentional type hierarchy · a real grid · a systematic colour system
(prefer OKLCH) with checked contrast · flat surfaces with functional depth · motion that
earns its place · one detail that could not appear in any other project.

The gate distinguishes **mention** from **promotion**:

```
"Avoid glassmorphism"                        → passes
"Styles: glassmorphism, brutalism, neumorphism" → fails
```

Skills the gate rejects are disabled, not deleted — each keeps its content with a
`WHY-DISABLED.md` and a reactivation snippet.

---

## What's in the library

Curated from 74 upstream repositories across three waves.

| category | n | covers |
|---|---:|---|
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

A skill qualified on at least one of: a **concrete checkable rule set** rather than
motivational prose; real traction; a **gap others did not fill**; no duplicate of
impeccable, taste-skill or ui-ux-pro-max.

Deliberately excluded: prompt collections without substance, marketing buzzword skills,
and every skill of a banned aesthetic.

---

## Keeping it current

```bash
./auto-update.sh              # refresh from source, gate + selftest, rebuild index
./auto-update.sh --check      # report only
./release.sh                  # stage, verify, tag, publish
./release.sh --dry-run        # show what would happen
```

`release.sh` refuses to publish unless the anti-slop gate passes, the self-test passes,
the index builds, and no third-party content has slipped into the repo.

**Scheduling.** Where cron or a systemd user bus exists, schedule `auto-update.sh`
directly. Elsewhere, use the session-start hook — a no-op unless 30 days have passed,
and it never blocks or fails a session:

```jsonc
// ~/.claude/settings.json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{ "type": "command", "command": "/path/to/update-on-start.sh" }]
    }]
  }
}
```

---

## Files

```
CURATION.tsv / 2 / 3     the catalogue — 262 curated entries across three waves
install.sh               fetch curated skills from their source repos
select-skills.py         selection engine, with --selftest
slop-scan.sh             anti-slop gate
sync-freebuff.sh         expose commands to agents without slash commands
auto-update.sh           refresh + gate + selftest + index
update-on-start.sh       session-start wrapper for cron-less environments
release.sh               stage, verify, tag, publish
build-index.py           generate INDEX.md + index.json
build-attribution.py     generate ATTRIBUTION.md
migrate-existing.sh      move existing skills into the library
commands/                design, design-interview, design-skills
skills/design-library/   router skill
```

`INDEX.md` and `index.json` are generated locally and not committed — they exist only
after you install the skills.

Development notes, architecture decisions and the migration record live in a separate
**private** repository. This repo ships the tool.

---

## Licensing

This repository contains **only files authored for this project** — the installer, the
selection engine, the manifests, the slash commands and the router skill. Those are
covered by the `LICENSE` here.

The design skills themselves are **not redistributed here**. `install.sh` fetches each
from its original repository, where its own licence and copyright apply. Sources and
commit hashes: **[ATTRIBUTION.md](ATTRIBUTION.md)**. Check the licence there before
using a skill commercially.

Skills whose upstream repository states no licence, or restricts redistribution, are
excluded from the manifests entirely. They remain usable locally if you already have
them, but `install.sh` will not fetch them.
