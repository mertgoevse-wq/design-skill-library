#!/usr/bin/env python3
"""Design Skill Library — Index-Generator.

Liest alle Skills in skills/ und erzeugt:
  INDEX.md   — kompakte Markdown-Tabelle (wird vom /design-Befehl gelesen)
  index.json — maschinenlesbar mit Metadaten fuer den Router
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parent
SKILLS = LIB / "skills"
BANNED_CATEGORIES: set[str] = set()

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    m = FM_RE.match(text)
    if not m:
        return {}
    out: dict = {}
    block = m.group(1)
    # einfache scalar keys; YAML-Listen/verschachteltes werden ignoriert
    for line in block.splitlines():
        mm = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if not mm:
            continue
        key, val = mm.group(1), mm.group(2).strip()
        if val in ("|", ">", "|-", ">-"):
            continue
        val = val.strip('"').strip("'")
        out[key] = val
    return out


def desc_from_body(text: str) -> str:
    """Fallback: erster nicht-leerer Absatz nach dem Frontmatter."""
    body = FM_RE.sub("", text).strip()
    for para in body.split("\n\n"):
        p = " ".join(para.split())
        if len(p) > 40 and not p.startswith("#"):
            return p[:300]
    return ""


def main() -> int:
    if not SKILLS.is_dir():
        print(f"FEHLER: {SKILLS} existiert nicht", file=sys.stderr)
        return 1

    rows = []
    for d in sorted(SKILLS.iterdir()):
        md = d / "SKILL.md"
        if not d.is_dir() or not md.is_file():
            continue
        text = md.read_text(encoding="utf-8", errors="replace")
        fm = parse_frontmatter(text)
        desc = fm.get("description") or desc_from_body(text)
        # erste Zeile einer aus mehrzeiligem YAML-Description
        desc = " ".join(desc.split())
        name = fm.get("name") or d.name
        category = fm.get("category", "")
        rows.append(
            {
                "slug": d.name,
                "name": name,
                "description": desc[:400],
                "category": category,
                "path": str(md),
            }
        )

    if not rows:
        print("FEHLER: keine Skills gefunden", file=sys.stderr)
        return 1

    # ---- index.json ----
    (LIB / "index.json").write_text(
        json.dumps({"count": len(rows), "skills": rows}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # ---- INDEX.md ----
    lines = [
        "# Design Skill Library — Index",
        "",
        f"{len(rows)} Skills, on-demand ladbar. Generiert von `build-index.py`.",
        "",
        "| slug | description |",
        "|---|---|",
    ]
    for r in rows:
        desc = r["description"].replace("|", "\\|")
        if len(desc) > 150:
            desc = desc[:147] + "..."
        lines.append(f"| `{r['slug']}` | {desc} |")
    lines.append("")
    (LIB / "INDEX.md").write_text("\n".join(lines), encoding="utf-8")

    print(f"OK: {len(rows)} Skills indexiert -> INDEX.md + index.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
