#!/usr/bin/env python3
"""Design Skill Library — skill selection engine.

Scores every skill in index.json against a task description and returns a
ranked shortlist, grouped by category, sized by how many domains are active.

Usage:
  select-skills.py "build a pricing page" [--n=6] [--domains=ui,visual,a11y]
  select-skills.py "3d hero for a game" --domain=3d --style=atmospheric

Not a black box: the orchestrator reads the shortlist and overrides it when
the ranking does not match its read of the task.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

LIB = Path(__file__).resolve().parent
INDEX = LIB / "index.json"

# ---------------------------------------------------------------- domain cues
DOMAIN_CUES: dict[str, tuple[str, ...]] = {
    "code":     ("build", "implement", "code", "write", "component", "scaffold", "create",
                 "develop", "integrate", "migrate", "ship"),
    "ui":       ("ui", "screen", "component", "layout", "button", "form", "card", "modal",
                 "dashboard", "panel", "table", "state", "empty state", "redesign",
                 "settings", "sidebar", "nav", "toolbar", "command palette", "grid"),
    "ux":       ("flow", "onboarding", "wizard", "signup", "checkout", "navigation",
                 "information architecture", "journey", "persona", "search",
                 "usability", "workflow"),
    "visual":   ("style", "look", "aesthetic", "brand", "colour", "color", "typography",
                 "palette", "theme", "identity", "logo", "visual", "dark mode",
                 "light mode", "hierarchy", "spacing", "contrast", "premium",
                 "editorial", "elegant", "refined", "vibrant", "muted", "minimalist",
                 "swiss", "grid layout", "image-led", "hero"),
    "motion":   ("animation", "animate", "motion", "transition", "scroll", "gsap",
                 "micro-interaction", "easing", "parallax", "timing", "framer",
                 "scrolltrigger", "pinning", "scrub", "reveal", "stagger", "tween",
                 "spring", "hover", "cursor"),
    "3d":       ("3d", "webgl", "three.js", "threejs", "shader", "canvas", "spline",
                 "babylon", "webgpu", "globe", "particle", "texture", "lighting"),
    "game":     ("game", "hud", "player", "gameplay", "level", "score", "sprite",
                 "gamepad", "arcade", "rpg", "enemy", "inventory"),
    "dataviz":  ("chart", "graph", "metric", "visualisation", "visualization", "plot",
                 "analytics", "kpi", "statistic", "series", "sparkline", "data table",
                 "reporting", "insight", "timeseries", "bar chart", "line chart"),
    "mobile":   ("mobile", "ios", "android", "phone", "react native", "expo", "tablet",
                 "responsive", "touch", "app store", "handoff"),
    "a11y":     ("accessibility", "a11y", "wcag", "screen reader", "aria", "keyboard",
                 "contrast", "inclusive", "focus state"),
    "review":   ("review", "critique", "audit", "improve", "polish", "refactor", "fix",
                 "optimise", "optimize", "check", "deslop"),
    "marketing": ("landing", "marketing", "conversion", "pricing", "copy", "positioning",
                  "cta", "seo", "waitlist", "sales", "testimonial", "hero section",
                  "subscribe", "subscription", "ecommerce", "e-commerce", "checkout",
                  "signup", "newsletter", "campaign", "brand voice", "messaging"),
}

# What each domain needs before it is properly covered.
DOMAIN_ROLE: dict[str, tuple[str, tuple[str, ...]]] = {
    "code":     ("build",      ("implement", "frontend-ui-engineering", "web-component-design")),
    "ui":       ("build",      ("interface-design", "baseline-ui", "ui-designer", "craft")),
    "ux":       ("plan",       ("ux-heuristics", "information-architecture", "design-flow")),
    "visual":   ("foundation", ("better-typography", "color-system", "visual-hierarchy",
                                "dark-mode-design", "typography-scale", "spacing-system")),
    "motion":   ("build",      ("animation-systems", "anim-web-motion-design", "gsap-core",
                                "anim-universal-patterns")),
    "3d":       ("build",      ("threejs-webgl", "web3d-integration-patterns", "threejs-shaders")),
    "game":     ("build",      ("game-ui-design", "anim-game-development")),
    "dataviz":  ("build",      ("data-viz", "ai-data-viz", "anim-data-visualization")),
    "mobile":   ("build",      ("responsive-design", "mobile-native", "design-mobile-apps")),
    "a11y":     ("verify",     ("accessibility", "wcag-web-a11y", "anim-accessible-motion",
                                "accessibility-audit")),
    "review":   ("verify",     ("interface-review", "critique-visual-hierarchy",
                                "design-debt-audit", "hallmark")),
    "marketing":("build",      ("landing-page", "cro-methodology", "better-writing",
                                "pricing-page", "storybrand-messaging")),
}

# Visual style -> extra keyword weight, so a style narrows tasteful matches.
STYLE_CUES: dict[str, tuple[str, ...]] = {
    "quiet-professional": ("clean", "restrained", "muted", "subtle", "corporate", "b2b", "saas"),
    "dense-data":         ("dense", "data", "table", "dashboard", "analytics", "kpi", "metrics"),
    "friendly-approachable": ("friendly", "warm", "rounded", "playful", "consumer", "onboarding"),
    "editorial-bold":     ("editorial", "magazine", "bold", "typographic", "print", "manifesto"),
    "minimal-calm":       ("minimal", "calm", "quiet", "simple", "spacious", "zen"),
    "expressive-motion":  ("expressive", "motion", "cinematic", "dramatic", "award", "scroll-driven"),
    "warm-human":         ("warm", "human", "organic", "soft", "care", "health"),
    "swift-functional":   ("fast", "swift", "functional", "utility", "tool", "productivity"),
    "playful":            ("playful", "fun", "colourful", "kids", "game", "toylike"),
    "high-energy":        ("high-energy", "fast", "arcade", "action", "competitive", "hype"),
    "atmospheric":        ("atmospheric", "moody", "immersive", "cinematic", "story", "world"),
    "retro-analog":       ("retro", "analog", "vintage", "8bit", "pixel", "crt", "terminal"),
    "showcase":           ("portfolio", "showcase", "gallery", "work", "case study", "creative"),
    "type-led":           ("type", "typography", "lettering", "kinetic", "variable"),
    "experimental":       ("experimental", "generative", "unusual", "unconventional", "lab"),
    "trustworthy":        ("trust", "secure", "banking", "insurance", "medical", "guarantee"),
    "premium":            ("premium", "luxury", "high-end", "refined", "boutique"),
    "bargain-loud":       ("discount", "sale", "deal", "bold", "urgent", "value"),
}

STOP = {
    "der", "die", "das", "und", "oder", "mit", "für", "fuer", "ein", "eine", "einen",
    "den", "dem", "des", "auf", "von", "im", "zu", "ist", "soll", "sollen", "ich", "wir",
    "bitte", "mach", "mache", "design", "designen", "skill", "skills", "bitte", "mal",
    "einfach", "gut", "schön", "schoen", "schicke", "noch", "wie", "was", "warum", "eine",
    "the", "and", "for", "with", "this", "that", "make", "build", "create", "please",
    "can", "you", "should", "would", "have", "has", "need", "want", "into", "from",
}


def tokens(*parts: str | tuple[str, ...]) -> list[str]:
    """Accepts a string or a tuple of cues; returns deduped lowercase tokens."""
    out: list[str] = []
    for p in parts:
        if not p:
            continue
        text = " ".join(p) if isinstance(p, (tuple, list)) else str(p)
        for t in re.findall(r"[a-z0-9äöüß\-.]{3,}", text.lower()):
            if t not in STOP and t not in out:
                out.append(t)
    return out


def detect_domains(text: str, forced: str | None) -> list[str]:
    if forced:
        return [d.strip() for d in forced.split(",") if d.strip()]
    low = " " + text.lower() + " "
    hits: list[tuple[str, int]] = []
    for dom, cues in DOMAIN_CUES.items():
        score = 0
        for c in cues:
            # Multiword cues match literally. Single words match on word
            # boundaries, so "photographer" does not trigger "graph".
            if " " in c:
                if c in low:
                    score += 2
            elif re.search(rf"\b{re.escape(c)}\b", low):
                score += 1
        if score:
            hits.append((dom, score))
    if not hits:
        return ["ui", "visual"]
    hits.sort(key=lambda x: -x[1])
    # keep domains that scored at least a third of the best
    top = hits[0][1]
    return [d for d, s in hits if s >= max(1, top * 0.34)][:6]


def score_skill(sl: dict, task_toks: list[str], domains: list[str],
                style_toks: list[str]) -> float:
    slug = sl["slug"].lower()
    desc = sl["description"].lower()
    cat = sl.get("category", "other")
    score = 0.0

    for t in task_toks:
        if t in slug:
            score += 12
        n = desc.count(t)
        if n:
            score += min(n, 3) * 2.0
    for t in style_toks:
        if t in slug:
            score += 6
        if t in desc:
            score += 1.5

    # domain/category affinity
    for d in domains:
        for cue in DOMAIN_CUES.get(d, ()):
            if cue in slug or cue in desc:
                score += 4
    if cat in domains:
        score += 6
    return score


def coverage_bonus(sl: dict, domains: list[str]) -> float:
    """Reward skills that fill a known role for an active, uncovered domain."""
    slug = sl["slug"]
    for d in domains:
        role, exemplars = DOMAIN_ROLE.get(d, (None, ()))
        if role and any(slug == e for e in exemplars):
            return 25.0
    return 0.0


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("task", nargs="*")
    ap.add_argument("--n", type=int, default=0, help="number of skills; 0 = auto")
    ap.add_argument("--domains", default="")
    ap.add_argument("--domain", default="")
    ap.add_argument("--style", default="")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    task = " ".join(a.task)
    if not task and not a.domain:
        print("usage: select-skills.py \"<task>\" [--n=N] [--domains=a,b] [--style=NAME]",
              file=sys.stderr)
        return 2
    if not INDEX.is_file():
        print(f"ERROR: {INDEX} missing — run build-index.py", file=sys.stderr)
        return 1

    data = json.loads(INDEX.read_text(encoding="utf-8"))
    skills = data["skills"]
    forced = a.domains or a.domain or None
    domains = detect_domains(task, forced)
    tt = tokens(task)
    st = tokens(STYLE_CUES.get(a.style, ()))

    scored: list[tuple[float, dict]] = []
    for sl in skills:
        base = score_skill(sl, tt, domains, st)
        if base <= 0:
            continue
        scored.append((base + coverage_bonus(sl, domains), sl))
    scored.sort(key=lambda x: -x[0])

    if a.n > 0:
        want = a.n
    else:
        # roughly 2-3 per domain, at least 4, at most 12
        want = max(4, min(12, len(domains) * 3))

    # keep category diversity: at most 3 per category in the final pick
    picked: list[tuple[float, dict]] = []
    per_cat: dict[str, int] = defaultdict(int)
    cap = 3
    for sc, sl in scored:
        c = sl.get("category", "other")
        if per_cat[c] >= cap:
            continue
        picked.append((sc, sl))
        per_cat[c] += 1
        if len(picked) >= want:
            break
    # relax the cap if we did not reach the target
    for sc, sl in scored:
        if len(picked) >= want:
            break
        if sl in [p[1] for p in picked]:
            continue
        picked.append((sc, sl))
    picked = picked[:want]

    if a.json:
        print(json.dumps({
            "task": task,
            "domains": domains,
            "style": a.style or None,
            "count": len(picked),
            "skills": [{"slug": s["slug"], "score": round(sc, 1),
                        "category": s.get("category"), "path": s["path"],
                        "description": s["description"][:150]} for sc, s in picked],
        }, indent=2, ensure_ascii=False))
        return 0

    print(f"task:    {task}")
    print(f"domains: {', '.join(domains)}")
    if a.style:
        print(f"style:   {a.style}")
    print(f"library: {data['count']} skills  ->  selecting {len(picked)}")
    print()

    for sc, sl in picked:
        desc = sl["description"]
        if len(desc) > 110:
            desc = desc[:107] + "..."
        print(f"[{sc:6.1f}] {sl['slug']:34} {sl.get('category','other'):12} {desc}")
    print()
    print("paths:")
    for _, sl in picked:
        print(f"  {sl['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
