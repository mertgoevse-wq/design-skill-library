#!/usr/bin/env python3
"""Design Skill Library — skill selection engine.

Scores every skill in index.json against a task and returns a ranked shortlist,
grouped by category, sized by how many domains are active.

  select-skills.py "build a pricing page" [--n=6] [--domains=ui,visual]
  select-skills.py "banking app onboarding" --industry=fintech --style=trustworthy
  select-skills.py --selftest          run the built-in test suite

Not a black box: the orchestrator reads the shortlist and overrides it when
the ranking does not match its own read of the task.
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

# --------------------------------------------------------------------- domains
# Cues are (phrase, weight). Multi-word phrases carry more signal than single
# words. Matching is word-boundary based, so "photographer" never triggers
# "graph" and "animated" never triggers "animation".
DOMAIN_CUES: dict[str, tuple[tuple[str, int], ...]] = {
    "code": (
        ("build", 2), ("implement", 2), ("code", 1), ("write", 1),
        ("component", 1), ("scaffold", 2), ("create", 1), ("develop", 1),
        ("integrate", 1), ("migrate", 1), ("ship", 1), ("prototype", 2),
        ("functional", 1), ("feature", 1), ("backend", 1), ("api", 1),
    ),
    "ui": (
        ("ui", 2), ("screen", 2), ("component", 1), ("layout", 2),
        ("button", 2), ("form", 1), ("card", 1), ("modal", 2),
        ("dashboard", 2), ("panel", 2), ("table", 1), ("state", 1),
        ("empty state", 3), ("redesign", 2), ("settings", 2), ("sidebar", 2),
        ("toolbar", 2), ("grid", 1), ("interface", 2), ("widget", 2),
        ("navigation", 1), ("menu", 1), ("dialog", 2), ("popover", 2),
    ),
    "ux": (
        ("flow", 2), ("onboarding", 3), ("wizard", 2), ("signup", 2),
        ("sign up", 3), ("checkout", 2), ("journey", 2),
        ("information architecture", 4), ("persona", 2), ("search", 1),
        ("usability", 2), ("workflow", 1), ("activation", 2),
        ("retention", 2), ("churn", 2), ("first run", 3), ("tutorial", 1),
    ),
    "visual": (
        ("style", 2), ("look", 2), ("aesthetic", 3), ("brand", 2),
        ("colour", 2), ("color", 2), ("typography", 3), ("palette", 3),
        ("theme", 2), ("identity", 2), ("logo", 2), ("visual", 1),
        ("dark mode", 3), ("light mode", 3), ("hierarchy", 2),
        ("spacing", 2), ("contrast", 1), ("premium", 2), ("editorial", 3),
        ("elegant", 1), ("refined", 1), ("vibrant", 1), ("muted", 1),
        ("minimalist", 2), ("minimal", 1), ("swiss", 2), ("image-led", 3),
        ("hero", 1), ("type-led", 3), ("font", 2), ("scale", 1),
    ),
    "motion": (
        ("animation", 2), ("animate", 2), ("motion", 2), ("transition", 2),
        ("scroll", 2), ("gsap", 3), ("micro-interaction", 3),
        ("easing", 3), ("parallax", 3), ("timing", 2), ("framer", 2),
        ("scrolltrigger", 3), ("pinning", 3), ("scrub", 2), ("reveal", 1),
        ("stagger", 2), ("tween", 2), ("spring", 2), ("hover", 1),
        ("cursor", 1), ("transition", 2), ("ken burns", 3), ("entrance", 1),
        ("exit animation", 3), ("skeleton", 2), ("spinner", 2),
    ),
    "3d": (
        ("3d", 3), ("webgl", 3), ("three.js", 3), ("threejs", 3),
        ("shader", 3), ("canvas", 2), ("spline", 2), ("babylon", 2),
        ("webgpu", 3), ("globe", 2), ("particle", 2), ("texture", 2),
        ("lighting", 2), ("postprocessing", 3), ("gltf", 2), ("vr", 2),
        ("ar", 1), ("voxel", 2), ("terrain", 2),
    ),
    "game": (
        ("game", 3), ("hud", 3), ("player", 2), ("gameplay", 3),
        ("level", 1), ("score", 1), ("sprite", 2), ("gamepad", 2),
        ("arcade", 3), ("rpg", 3), ("enemy", 2), ("inventory", 1),
        ("game loop", 3), ("multiplayer", 2), ("quest", 1),
    ),
    "dataviz": (
        ("chart", 3), ("graph", 2), ("metric", 2), ("visualisation", 3),
        ("visualization", 3), ("plot", 2), ("analytics", 2), ("kpi", 3),
        ("statistic", 2), ("series", 1), ("sparkline", 3), ("data table", 3),
        ("reporting", 1), ("insight", 1), ("timeseries", 2), ("bar chart", 3),
        ("line chart", 3), ("pie chart", 3), ("histogram", 2),
        ("heat map", 2), ("scatter", 2), ("axis", 1), ("legend", 1),
        ("tooltip", 1), ("data table", 3), ("dashboard data", 3),
    ),
    "mobile": (
        ("mobile", 3), ("ios", 2), ("android", 2), ("phone", 2),
        ("react native", 3), ("expo", 2), ("tablet", 2), ("responsive", 2),
        ("touch", 1), ("app store", 3), ("handoff", 1), ("watchos", 2),
        ("tvos", 2), ("visionos", 2), ("macos", 2), ("ipados", 2),
        ("gesture", 1), ("haptic", 2), ("app", 1),
    ),
    "a11y": (
        ("accessibility", 3), ("a11y", 3), ("wcag", 3), ("screen reader", 3),
        ("aria", 2), ("keyboard", 2), ("contrast", 1), ("inclusive", 2),
        ("focus state", 3), ("accessible", 3), ("colour blind", 3),
        ("color blind", 3), ("reduced motion", 3), ("screenreader", 3),
        ("assistive", 3), ("tab order", 3), ("focus ring", 3),
        ("alt text", 3), ("legibility", 2), ("old users", 2),
    ),
    "review": (
        ("review", 2), ("critique", 3), ("audit", 2), ("improve", 2),
        ("polish", 2), ("refactor", 2), ("fix", 1), ("optimise", 2),
        ("optimize", 2), ("check", 1), ("deslop", 3), ("feedback", 2),
        ("teardown", 2), ("improve ui", 3),
    ),
    "marketing": (
        ("landing", 3), ("marketing", 3), ("conversion", 3), ("pricing", 2),
        ("copy", 2), ("positioning", 2), ("cta", 2), ("seo", 2),
        ("waitlist", 2), ("sales", 1), ("testimonial", 2),
        ("hero section", 2), ("subscribe", 2), ("subscription", 2),
        ("ecommerce", 3), ("e-commerce", 3), ("newsletter", 2),
        ("campaign", 1), ("brand voice", 3), ("messaging", 2),
        ("launch page", 3), ("sales page", 3), ("case study", 2),
    ),
    # Business/product domains, detected from the project type
    "ecommerce": (
        ("shop", 2), ("store", 2), ("product page", 3), ("cart", 2),
        ("checkout", 2), ("product listing", 3), ("sku", 2),
        ("merchandise", 2), ("b2c", 2), ("retail", 2),
    ),
    "fintech": (
        ("banking", 3), ("bank", 2), ("fintech", 3), ("payment", 2),
        ("payments", 2), ("investment", 2), ("trading", 2),
        ("wallet", 2), ("transaction", 2), ("insurance", 2),
        ("invoice", 2), ("account balance", 3), ("transfer", 1),
    ),
    "healthcare": (
        ("healthcare", 3), ("health", 2), ("medical", 3), ("clinical", 3),
        ("patient", 3), ("clinic", 2), ("telehealth", 3), ("diagnosis", 2),
        ("prescription", 2), ("wellness", 1), ("therapy", 2),
    ),
    "education": (
        ("education", 3), ("learning", 2), ("course", 2), ("lesson", 2),
        ("tutorial", 1), ("student", 2), ("teacher", 2), ("e-learning", 3),
        ("training platform", 3), ("curriculum", 2), ("quiz", 2),
    ),
    "enterprise": (
        ("enterprise", 3), ("internal tool", 4), ("admin panel", 3),
        ("b2b", 2), ("crm", 2), ("erp", 2), ("workflow tool", 3),
        ("back office", 3), ("operations", 1), ("compliance", 1),
        ("admin", 2), ("internal", 2), ("dashboard for", 3),
        ("support agent", 3), ("backoffice", 3), ("operations tool", 3),
        ("staff", 1), ("role-based", 3), ("permission", 1),
    ),
    "portfolio": (
        ("portfolio", 3), ("personal site", 2), ("showcase", 2),
        ("case study", 2), ("photographer", 2), ("designer portfolio", 3),
        ("artist", 1), ("studio", 1), ("my work", 2),
    ),
}

# What each domain needs covered, and the skills that best do it.
DOMAIN_ROLE: dict[str, tuple[str, tuple[str, ...]]] = {
    "code":      ("build", ("frontend-ui-engineering", "web-component-design", "tailwindcss")),
    "ui":        ("build", ("interface-design", "baseline-ui", "ui-designer", "craft")),
    "ux":        ("plan",  ("ux-heuristics", "information-architecture", "design-flow",
                            "onboarding-design", "anecdote")),
    "visual":    ("foundation", ("better-typography", "color-system", "visual-hierarchy",
                                  "dark-mode-design", "typography-scale", "spacing-system",
                                  "readable-measure")),
    "motion":    ("build", ("animation-systems", "anim-web-motion-design", "gsap-core",
                             "anim-universal-patterns", "anim-universal-timing")),
    "3d":        ("build", ("threejs-webgl", "web3d-integration-patterns", "threejs-shaders")),
    "game":      ("build", ("game-ui-design", "anim-game-development")),
    "dataviz":   ("build", ("data-viz", "ai-data-viz", "anim-data-visualization")),
    "mobile":    ("build", ("responsive-design", "mobile-native", "design-mobile-apps")),
    "a11y":      ("verify",("accessibility", "wcag-web-a11y", "anim-accessible-motion",
                             "accessibility-audit")),
    "review":    ("verify",("interface-review", "critique-visual-hierarchy",
                             "design-debt-audit", "hallmark", "no-ai-design-slop")),
    "marketing": ("build", ("landing-page", "cro-methodology", "better-writing",
                             "pricing-page", "storybrand-messaging")),
    "ecommerce": ("build", ("product-proof-saas", "cro-methodology")),
    "fintech":   ("build", ("trust-reliability", "anim-trust-reliability")),
    "healthcare":("build", ("anim-accessible-motion",)),
    "education": ("build", ("anim-professionalism",)),
    "enterprise":("build", ("anim-enterprise-industry",)),
    "portfolio": ("build", ("editorial-portfolio-chapters", "ui-variant")),
}

# Visual style -> keywords that bias tasteful matches.
STYLE_CUES: dict[str, tuple[str, ...]] = {
    "quiet-professional":    ("clean", "restrained", "muted", "subtle", "corporate", "b2b", "saas"),
    "dense-data":            ("dense", "data", "table", "analytics", "kpi", "metrics"),
    "friendly-approachable": ("friendly", "warm", "rounded", "playful", "consumer", "onboarding"),
    "editorial-bold":        ("editorial", "magazine", "bold", "typographic", "print"),
    "minimal-calm":          ("minimal", "calm", "quiet", "simple", "spacious"),
    "expressive-motion":     ("expressive", "cinematic", "dramatic", "award", "scroll-driven"),
    "warm-human":            ("warm", "human", "organic", "soft", "care"),
    "swift-functional":      ("fast", "swift", "functional", "utility", "tool"),
    "playful":               ("fun", "colourful", "kids", "toylike"),
    "high-energy":           ("loud", "competitive", "hype", "neon"),
    "atmospheric":           ("moody", "immersive", "story", "world"),
    "retro-analog":          ("retro", "analog", "vintage", "8bit", "pixel", "crt", "terminal"),
    "showcase":              ("gallery", "work"),
    "type-led":              ("typography", "lettering", "kinetic", "variable"),
    "experimental":          ("generative", "unusual", "unconventional"),
    "trustworthy":           ("trust", "secure", "guarantee", "reliable"),
    "premium":               ("luxury", "high-end", "boutique", "refined"),
    "bargain-loud":          ("discount", "sale", "deal", "urgent", "value"),
}

# Compound words that must not fire a cue.
FALSE_FRIENDS: dict[str, tuple[str, ...]] = {
    "graph":     ("photographer", "graphics", "graphic", "paragraph", "autograph", "telegraph"),
    "app":       ("application form", "apple", "appendix", "appeal", "happen"),
    "ar":        ("card", "car", "bar", "far", "star", "start", "share", "year", "clear",
                  "prepare", "are", "part", "mar", "tar", "par", "war", "jar", "var", "map"),
    "ui":        ("build", "guide", "quiet", "quick", "suit", "fruit", "require"),
    "3d":        ("3ds",),
    "cd":        (),
}

STOP = {
    "der", "die", "das", "und", "oder", "mit", "für", "fuer", "ein", "eine", "einen",
    "den", "dem", "des", "auf", "von", "im", "zu", "ist", "soll", "sollen", "ich", "wir",
    "bitte", "mach", "mache", "design", "designen", "skill", "skills", "mal", "einfach",
    "gut", "schön", "schoen", "schicke", "noch", "wie", "was", "warum", "eine", "the",
    "and", "for", "with", "this", "that", "make", "create", "please", "can", "you",
    "should", "would", "have", "has", "need", "want", "into", "from", "eine", "auch",
    "soll", "können", "kann", "dann", "jetzt", "hier", "diese", "dieser", "dieses",
}

# Skills that must never be auto-selected: they promote banned aesthetics.
EXCLUDE_SLUGS = {
    "industrial-brutalist-ui", "brutalist-skill", "cosmic-glass-dashboard",
    "glass-dark-ui", "dark-glass", "neumorphism", "skeuomorphic-ui",
    "design-taste-frontend",  # promotes "Liquid Glass Refraction"
    "ui-ux-pro-max",          # lists glassmorphism/brutalism/neumorphism as styles
}

# Industry domains are modifiers, not primary domains.
SECONDARY = {"ecommerce", "fintech", "healthcare", "education", "enterprise", "portfolio"}


def _norm(text: str) -> str:
    return " " + re.sub(r"\s+", " ", text.lower().strip()) + " "


def cue_hits(low: str, cues: tuple[tuple[str, int], ...]) -> int:
    total = 0
    for phrase, weight in cues:
        if " " in phrase:
            if phrase in low:
                total += weight + 1          # multi-word: slightly stronger
            continue
        # single word -> boundary match, minus false friends
        if re.search(rf"\b{re.escape(phrase)}\b", low):
            pad = low
            skip = False
            for bad in FALSE_FRIENDS.get(phrase, ()):
                if re.search(rf"\b{re.escape(bad)}\b", pad):
                    skip = True
                    break
            if not skip:
                total += weight
    return total


def detect_domains(text: str, forced: str | None) -> list[str]:
    if forced:
        doms = [d.strip() for d in forced.split(",") if d.strip()]
        return [d for d in doms if d in DOMAIN_CUES] or ["ui", "visual"]
    low = _norm(text)
    hits: list[tuple[str, int]] = []
    for dom, cues in DOMAIN_CUES.items():
        s = cue_hits(low, cues)
        if s:
            hits.append((dom, s))
    if not hits:
        return ["ui", "visual"]
    hits.sort(key=lambda x: -x[1])
    top = hits[0][1]
    primary = [d for d, s in hits
               if d not in SECONDARY and s >= max(1, top * 0.34)]
    # secondary domains ride along if they scored at all
    secondary = [d for d, s in hits if d in SECONDARY and s >= 2]
    out = (primary or [hits[0][0]])[:6]
    for d in secondary:
        if d not in out and len(out) < 8:
            out.append(d)
    return out


def detect_industries(text: str, forced: str | None) -> list[str]:
    if forced:
        return [i.strip() for i in forced.split(",") if i.strip() in SECONDARY]
    low = _norm(text)
    out = []
    for dom in SECONDARY:
        if cue_hits(low, DOMAIN_CUES[dom]) >= 2:
            out.append(dom)
    return out


def tokens(*parts) -> list[str]:
    out: list[str] = []
    for p in parts:
        if not p:
            continue
        text = " ".join(p) if isinstance(p, (tuple, list)) else str(p)
        for t in re.findall(r"[a-z0-9äöüß\-.]{3,}", text.lower()):
            if t not in STOP and t not in out:
                out.append(t)
    return out


def score_skill(sl: dict, task_toks, domains, style_toks) -> float:
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
    for d in domains:
        for phrase, _w in DOMAIN_CUES.get(d, ()):
            if " " in phrase:
                if phrase in slug or phrase in desc:
                    score += 4
            elif phrase in slug:
                score += 3
            elif phrase in desc:
                score += 1
    if cat in domains:
        score += 6
    return score


def coverage_bonus(sl: dict, domains) -> float:
    slug = sl["slug"]
    best = 0.0
    for d in domains:
        role, exemplars = DOMAIN_ROLE.get(d, (None, ()))
        if role and slug in exemplars:
            best = max(best, 25.0)
    return best


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("task", nargs="*")
    ap.add_argument("--n", type=int, default=0)
    ap.add_argument("--domains", default="")
    ap.add_argument("--domain", default="")
    ap.add_argument("--industry", default="")
    ap.add_argument("--style", default="")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    task = " ".join(a.task)
    if not task and not a.domain:
        print('usage: select-skills.py "<task>" [--n=N] [--domains=a,b] '
              '[--industry=x] [--style=NAME] [--json]\n'
              '       select-skills.py --selftest', file=sys.stderr)
        return 2
    if not INDEX.is_file():
        print(f"ERROR: {INDEX} missing — run build-index.py", file=sys.stderr)
        return 1

    data = json.loads(INDEX.read_text(encoding="utf-8"))
    skills = [s for s in data["skills"] if s["slug"] not in EXCLUDE_SLUGS]
    skipped = len(data["skills"]) - len(skills)

    forced = a.domains or a.domain or None
    domains = detect_domains(task, forced)
    industries = detect_industries(task, a.industry)
    for ind in industries:
        if ind not in domains:
            domains.append(ind)
    tt = tokens(task)
    st = tokens(STYLE_CUES.get(a.style, ()))

    scored = []
    for sl in skills:
        base = score_skill(sl, tt, domains, st)
        if base <= 0:
            continue
        scored.append((base + coverage_bonus(sl, domains), sl))
    scored.sort(key=lambda x: -x[0])

    want = a.n if a.n > 0 else max(4, min(12, len(domains) * 3))

    picked, per_cat = [], defaultdict(int)
    for sc, sl in scored:
        c = sl.get("category", "other")
        if per_cat[c] >= 3:
            continue
        picked.append((sc, sl))
        per_cat[c] += 1
        if len(picked) >= want:
            break
    chosen = {sl["slug"] for _, sl in picked}
    for sc, sl in scored:
        if len(picked) >= want:
            break
        if sl["slug"] in chosen:
            continue
        picked.append((sc, sl))
        chosen.add(sl["slug"])
    picked = picked[:want]

    if a.json:
        print(json.dumps({
            "task": task, "domains": domains, "industries": industries,
            "style": a.style or None, "count": len(picked),
            "excluded_banned": skipped,
            "skills": [{"slug": s["slug"], "score": round(sc, 1),
                        "category": s.get("category"), "path": s["path"],
                        "description": s["description"][:150]} for sc, s in picked],
        }, indent=2, ensure_ascii=False))
        return 0

    print(f"task:      {task}")
    print(f"domains:   {', '.join(domains)}")
    if industries:
        print(f"industries:{', '.join(industries)}")
    if a.style:
        print(f"style:     {a.style}")
    print(f"library:   {data['count']} skills ({skipped} banned excluded) "
          f"->  selecting {len(picked)}")
    print()
    for sc, sl in picked:
        desc = sl["description"]
        if len(desc) > 105:
            desc = desc[:102] + "..."
        print(f"[{sc:6.1f}] {sl['slug']:32} {sl.get('category','other'):12} {desc}")
    print()
    print("paths:")
    for _, sl in picked:
        print(f"  {sl['path']}")
    return 0


# ------------------------------------------------------------------ self-test
CASES = [
    # (task, must-include domains, must-contain slug)
    ("build a 3d game with shader effects and a HUD",        {"3d", "game"},       "game-ui-design"),
    ("redesign our saas analytics dashboard, dense data",    {"ui", "dataviz"},    "data-viz"),
    ("onboarding flow for a mobile banking app",             {"ux", "fintech"},    None),
    ("scroll hero with parallax and gsap pinning",           {"motion"},            "gsap-core"),
    ("portfolio site for a photographer, type-led",          {"visual"},            None),
    ("dark mode theme for a healthcare patient portal, accessible", {"a11y", "healthcare"}, None),
    ("pricing page for a saas, high converting",              {"marketing"},         "pricing-page"),
    ("accessibility audit of our checkout",                   {"a11y"},              "accessibility"),
    ("e-commerce product page for a shop",                    {"ecommerce"},         None),
    ("graph the sales numbers over time",                     {"dataviz"},           None),
    ("internal admin tool for support agents",                {"enterprise"},        None),
]


def selftest() -> int:
    low = Path(__file__).resolve().parent
    idx = low / "index.json"
    if not idx.is_file():
        print(f"ERROR: {idx} missing", file=sys.stderr)
        return 1
    data = json.loads(idx.read_text(encoding="utf-8"))
    have = {s["slug"] for s in data["skills"]}

    # A partial install cannot satisfy the ranking cases. Say so once, up front,
    # instead of reporting a wall of failures that look like engine bugs.
    expected_slugs = {s for _, _, s in CASES if s}
    absent = sorted(expected_slugs - have)
    partial = len(absent) > 0

    fails = 0
    for task, want_doms, want_slug in CASES:
        doms = set(detect_domains(task, None))
        inds = set(detect_industries(task, None))
        combined = doms | inds
        missing = want_doms - combined
        status = "ok " if not missing else "FAIL"
        if missing:
            fails += 1
        extra = ""
        if want_slug:
            if want_slug not in have:
                status = "skip"
                extra = f"  | {want_slug} not installed"
            else:
                scored = []
                for sl in data["skills"]:
                    if sl["slug"] in EXCLUDE_SLUGS:
                        continue
                    s = score_skill(sl, tokens(task), list(combined), [])
                    s += coverage_bonus(sl, list(combined))
                    if s > 0:
                        scored.append((s, sl))
                scored.sort(key=lambda x: -x[0])
                top = [sl["slug"] for _, sl in scored[:8]]
                if want_slug not in top:
                    fails += 1
                    extra = f"  | {want_slug} not in top8: {top[:5]}"
                    status = "FAIL"
                else:
                    extra = f"  | {want_slug} in top8"
        print(f"{status}  {task[:46]:46} -> {','.join(sorted(combined))}{extra}")

    print()
    if partial:
        print(f"note: {len(absent)} expected skill(s) not installed: {', '.join(absent)}")
        print("      those cases are skipped, not failed. run './install.sh' for a full set.")
        print()
    print(f"selftest: {'PASS' if fails == 0 else f'{fails} FAILURES'}")
    return 0 if fails == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
