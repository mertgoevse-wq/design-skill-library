#!/usr/bin/env python3
"""Erzeugt ATTRIBUTION.md mit Herkunft und Lizenz jedes kuratierten Skills."""
from __future__ import annotations

import re
import subprocess
from collections import defaultdict
from pathlib import Path

LIB = Path(__file__).resolve().parent
CLONE = LIB / ".tmp-clone"
MANIFESTS = [LIB / "CURATION.tsv", LIB / "CURATION2.tsv"]

URL = {
    "anthropics_skills": "https://github.com/anthropics/skills",
    "anthropics_claude-code": "https://github.com/anthropics/claude-code",
    "anthropics_knowledge-work-plugins": "https://github.com/anthropics/knowledge-work-plugins",
    "vercel-labs_agent-skills": "https://github.com/vercel-labs/agent-skills",
    "pbakaus_impeccable": "https://github.com/pbakaus/impeccable",
    "leonxlnx_taste-skill": "https://github.com/leonxlnx/taste-skill",
    "emilkowalski_skills": "https://github.com/emilkowalski/skills",
    "mattpocock_skills": "https://github.com/mattpocock/skills",
    "nextlevelbuilder_ui-ux-pro-max-skill": "https://github.com/nextlevelbuilder/ui-ux-pro-max-skill",
    "designed-by-ai_skills": "https://github.com/designed-by-ai/skills",
    "ibelick_ui-skills": "https://github.com/ibelick/ui-skills",
    "jakubkrehel_skills": "https://github.com/jakubkrehel/skills",
    "jakubkrehel_oklch-skill": "https://github.com/jakubkrehel/oklch-skill",
    "wondelai_skills": "https://github.com/wondelai/skills",
    "expo_skills": "https://github.com/expo/skills",
    "flutter_agent-plugins": "https://github.com/flutter/agent-plugins",
    "wshobson_agents": "https://github.com/wshobson/agents",
    "addyosmani_web-quality-skills": "https://github.com/addyosmani/web-quality-skills",
    "addyosmani_agent-skills": "https://github.com/addyosmani/agent-skills",
    "google-labs-code_stitch-skills": "https://github.com/google-labs-code/stitch-skills",
    "squirrelscan_skills": "https://github.com/squirrelscan/skills",
    "nutlope_hallmark": "https://github.com/nutlope/hallmark",
    "dammyjay93_interface-design": "https://github.com/dammyjay93/interface-design",
    "conardli_garden-skills": "https://github.com/conardli/garden-skills",
    "sentimony_skills": "https://github.com/sentimony/skills",
    "antfu_skills": "https://github.com/antfu/skills",
    "arvindrk_extract-design-system": "https://github.com/arvindrk/extract-design-system",
    "owl-listener_designer-skills": "https://github.com/owl-listener/designer-skills",
    "julianoczkowski_designer-skills": "https://github.com/julianoczkowski/designer-skills",
    "mengto_skills": "https://github.com/mengto/skills",
    "openai_skills": "https://github.com/openai/skills",
    "figma_mcp-server-guide": "https://github.com/figma/mcp-server-guide",
    "higgsfield-ai_skills": "https://github.com/higgsfield-ai/skills",
    "daniel-dan-conrad_ui-designer-skill": "https://github.com/daniel-dan-conrad/ui-designer-skill",
    "tw93_waza": "https://github.com/tw93/waza",
    "zeke_swiss-design-skill": "https://github.com/zeke/swiss-design-skill",
    "secondsky_claude-skills": "https://github.com/secondsky/claude-skills",
    "jezweb_claude-skills": "https://github.com/jezweb/claude-skills",
    "cline_skills": "https://github.com/cline/skills",
    "samber_cc-skills": "https://github.com/samber/cc-skills",
    "dmmulroy_anti-slop": "https://github.com/dmmulroy/anti-slop",
    "deeflect_mies": "https://github.com/deeflect/mies",
    "iart-ai_motion-design-skills": "https://github.com/iart-ai/motion-design-skills",
    "bergside_awesome-design-skills": "https://github.com/bergside/awesome-design-skills",
    "sanity-io_agent-toolkit": "https://github.com/sanity-io/agent-toolkit",
    "supabase_agent-skills": "https://github.com/supabase/agent-skills",
    "shadcn-ui_ui": "https://github.com/shadcn-ui/ui",
    "alchaincyf_huashu-design": "https://github.com/alchaincyf/huashu-design",
    "wilwaldon_Claude-Code-Frontend-Design-Toolkit": "https://github.com/wilwaldon/Claude-Code-Frontend-Design-Toolkit",
    "pbakaus": "https://github.com/pbakaus",
}

LICENSE_PATTERNS = [
    (re.compile(r"Apache License", re.I), "Apache-2.0"),
    (re.compile(r"MIT License|The MIT License", re.I), "MIT"),
    (re.compile(r"BSD 3-Clause|Redistribution and use in source and binary forms", re.I), "BSD-3-Clause"),
    (re.compile(r"GNU GENERAL PUBLIC LICENSE", re.I), "GPL"),
    (re.compile(r"All rights reserved", re.I), "Proprietär (All rights reserved)"),
]

# Quellen, deren Weiterverbreitung in einem oeffentlichen Sammel-Repo nicht
# belegbar erlaubt ist. Werden aus dem Repo-Snapshot ausgeschlossen.
EXCLUDE_FROM_REPO = {
    "anthropics_skills",
    "anthropics_claude-code",
    "openai_skills",
    "figma_mcp-server-guide",
    "jakubkrehel_oklch-skill",
    "daniel-dan-conrad_ui-designer-skill",
    "sentimony_skills",
    "vercel-labs_agent-skills",
}


def detect_license(repo_dir: str) -> str:
    p = CLONE / repo_dir
    for f in p.glob("LICENSE*"):
        head = f.read_text(encoding="utf-8", errors="replace")[:1200]
        for pat, name in LICENSE_PATTERNS:
            if pat.search(head):
                return name
    return "KEINE LIZENZ IM REPO"


def git_sha(repo_dir: str) -> str:
    try:
        return subprocess.run(
            ["git", "-C", str(CLONE / repo_dir), "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip() or "unbekannt"
    except Exception:
        return "unbekannt"


def main() -> int:
    by_repo: dict[str, list[str]] = defaultdict(list)
    for m in MANIFESTS:
        if not m.is_file():
            continue
        for line in m.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.startswith("#"):
                continue
            f = line.split("\t")
            if len(f) >= 2:
                by_repo[f[1]].append(f[0])

    lines = [
        "# Attribution & Licenses",
        "",
        "Diese Bibliothek besteht aus **third-party Agent Skills** verschiedener Autoren.",
        "Die jeweilige Urheberschaft und Lizenz liegt bei den Original-Autoren.",
        "Dieses Repository bündelt sie lediglich zu einer kuratierten, on-demand nutzbaren Sammlung.",
        "",
        "**Es wird hier keine eigene Lizenz über die Originalinhalte gestellt.**",
        "Jede Skill bleibt unter der Lizenz ihres Ursprungs-Repos. Wer ein Repo weiterverbreiten",
        "will, muss dessen Lizenz beachten — insbesondere bei Einträgen ohne erkennbare Lizenz.",
        "",
        "---",
        "",
        "## Übersicht",
        "",
        "| Quelle | Skills | Lizenz | Commit |",
        "|---|---|---|---|",
    ]

    total = 0
    included_total = 0
    for repo in sorted(by_repo):
        slugs = sorted(by_repo[repo])
        lic = detect_license(repo)
        if repo in EXCLUDE_FROM_REPO or lic in ("KEINE LIZENZ IM REPO", "Proprietär (All rights reserved)"):
            lines.append(
                f"| ~~[{repo}]({URL.get(repo, 'https://github.com/' + repo)})~~ "
                f"| {len(slugs)} | {lic} | *(nicht enthalten)* |"
            )
            continue
        total += len(slugs)
        included_total += len(slugs)
        lines.append(
            f"| [{repo}]({URL.get(repo, 'https://github.com/' + repo)}) "
            f"| {len(slugs)} | {lic} | `{git_sha(repo)}` |"
        )

    lines += [
        "",
        "Zeilen mit *nicht enthalten* stammen aus Quellen ohne erkennbare bzw. restriktive",
        "Lizenz. Ihre Skills bleiben lokal in der Bibliothek verfügbar, werden aber **nicht**",
        "in diesem oeffentlichen Repository weiterverbreitet.",
        "",
    ]

    lines += ["", "---", "", "## Details je Quelle", ""]
    for repo in sorted(by_repo):
        slugs = sorted(by_repo[repo])
        lic = detect_license(repo)
        if repo in EXCLUDE_FROM_REPO or lic in ("KEINE LIZENZ IM REPO", "Proprietär (All rights reserved)"):
            lines += [
                f"### {repo}",
                "",
                f"- **Lizenz:** {lic}",
                "- **Status:** 🚫 nicht in diesem Repo enthalten (lokal weiterhin verfügbar)",
                f"- **Skills ({len(slugs)}):** " + ", ".join(f"`{s}`" for s in slugs),
                "",
            ]
            continue
        lines += [f"### [{repo}]({URL.get(repo, 'https://github.com/' + repo)})", ""]
        lines += [f"- **Lizenz:** {lic}", f"- **Commit:** `{git_sha(repo)}`", f"- **Skills ({len(slugs)}):**", ""]
        for s in slugs:
            lines.append(f"  - `{s}`")
        lines.append("")

    lines += [
        "---",
        "",
        "## Eigene Bestandteile dieses Repositories",
        "",
        "Die folgenden Dateien wurden für dieses Projekt geschrieben und stehen nicht unter",
        "den Lizenzen der Drittanbieter:",
        "",
        "- `install.sh`, `migrate-existing.sh`, `slop-scan.sh`, `build-index.py`, `build-attribution.py`",
        "- `CURATION.tsv`, `CURATION2.tsv` (Auswahlmanifeste)",
        "- `INDEX.md`, `index.json` (generiert)",
        "- `commands/design.md`, `commands/design-skills.md` (Slash-Commands)",
        "- `skills/design-library/SKILL.md` (Router-Skill)",
        "",
    ]

    out = LIB / "ATTRIBUTION.md"
    out.write_text("\n".join(lines), encoding="utf-8")
    excluded = sum(len(v) for k, v in by_repo.items()
                   if k in EXCLUDE_FROM_REPO
                   or detect_license(k) in ("KEINE LIZENZ IM REPO", "Proprietär (All rights reserved)"))
    print(f"OK: ATTRIBUTION.md — {included_total} Skills enthalten, {excluded} ausgelassen "
          f"(Lizenz unklar/restriktiv), {len(by_repo)} Quellen gesamt")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
