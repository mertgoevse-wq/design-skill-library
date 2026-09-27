---
description: Guided plain-language interview that helps non-designers find the right visual direction for their project, per project type, and hands the result to the /design orchestrator.
argument-hint: [what the project is, or leave empty to be asked]
allowed-tools: Read, Bash(python3:*)
---

# /design-interview — find the right design direction

**You said:** $ARGUMENTS

You do not need design vocabulary. Answer in plain language, pick options by
describing how they *feel*, and I will translate that into the right skills and
implementation.

I will ask **at most two rounds**. If you would rather skip it, say so and I will
pick a sensible default and tell you which one.

---

## Round 1 — three questions

Adapt the wording to the project. Drop anything already answered. Keep it short.

**1. What is it, and who uses it?**
One sentence. A tool for engineers reads very differently from a shop for children.

**2. How should it feel?** Offer three named directions, each with a plain
one-liner. Pick from the table for the project type:

| Project type | Directions to offer |
|---|---|
| SaaS / dashboard / admin tool | **quiet-professional** — calm, competent, gets out of the way · **dense-data** — lots of numbers on screen at once, optimised for scanning · **friendly-approachable** — warm, easy, low intimidation |
| Marketing site / landing page | **editorial-bold** — magazine-like, type does the talking · **minimal-calm** — lots of space, very little noise · **expressive-motion** — moves, reacts, rewards attention |
| Consumer app / mobile | **warm-human** — soft, caring, personal · **swift-functional** — fast, obvious, does the job · **playful** — colourful, light-hearted |
| Game / interactive | **high-energy** — loud, fast, competitive · **atmospheric** — moody, immersive, storytelling · **retro-analog** — pixel, 8-bit, terminal |
| Portfolio / studio / agency | **showcase** — the work is the hero · **type-led** — typography carries it · **experimental** — unusual, generative, memorable |
| Shop / e-commerce | **trustworthy** — safe, clear, no surprises · **premium** — restrained, expensive-feeling · **bargain-loud** — bright, urgent, deal-forward |
| Educational / docs | **clear-technical** — precise, scannable · **guided-friendly** — patient, hand-holding · **dense-reference** — everything, searchable, no fluff |

If the project type is unclear, ask instead of offering.

**3. Anything to avoid?**
Colours they dislike, a competitor that looks wrong, a look they have seen too
often. This often matters more than question 2.

---

## Round 2 — only if needed

Confirm the direction by showing what it implies, not by asking about details:

- **One sentence** naming the chosen direction
- **The type feel** — e.g. "large tight headlines, generous line height"
- **The colour approach** — e.g. "warm off-white base, one dark accent"
- **The motion level** — e.g. "restrained: fades and slides, nothing bouncing"
- **What we are deliberately avoiding**

Ask only: *"Does that match what you had in mind, or should I adjust?"*

---

## Then hand over

Once a direction is fixed, continue with the orchestrator:

```
/design <task> --style=<direction> --n=<count>
```

State the direction you settled on and the reasoning in one line, then proceed.
Do not stop after the interview — the point is to get to the work.
