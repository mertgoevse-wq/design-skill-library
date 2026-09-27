#!/usr/bin/env bash
# Design Skill Library — installer
#
# Fetches the curated skills directly from their original GitHub repositories
# using sparse checkout. Nothing third-party is redistributed here: the library
# pulls each skill from its own source at install time.
#
# Usage:
#   ./install.sh                 # install every curated skill
#   ./install.sh gsap-core web3d # install specific slugs only
#   ./install.sh --update        # re-fetch the skills that are already installed
#
# Idempotent: existing real content is never overwritten without --update.
set -euo pipefail

LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CLONE="$LIB/.sources"
DEST="$LIB/skills"
MANIFESTS=("$LIB/CURATION.tsv" "$LIB/CURATION2.tsv" "$LIB/CURATION3.tsv")

UPDATE=0
SELECTED=()
for arg in "$@"; do
  case "$arg" in
    --update) UPDATE=1 ;;
    -*) echo "unknown flag: $arg" >&2; exit 2 ;;
    *)  SELECTED+=("$arg") ;;
  esac
done

mkdir -p "$DEST" "$CLONE"

# Repo key -> GitHub slug. Derived from the manifest's repo directory name.
repo_slug() {
  local d="$1"
  d="${d#_}"
  # names use '_' as the path separator; the owner/repo split is the last one
  case "$d" in
    anthropics_*)            echo "anthropics/skills" ;;
    vercel-labs_*)           echo "vercel-labs/agent-skills" ;;
    openai_*)                echo "openai/skills" ;;
    figma_*)                 echo "figma/mcp-server-guide" ;;
    pbakaus_*)               echo "pbakaus/impeccable" ;;
    leonxlnx_*)              echo "leonxlnx/taste-skill" ;;
    emilkowalski_*)          echo "emilkowalski/skills" ;;
    mattpocock_*)            echo "mattpocock/skills" ;;
    nextlevelbuilder_*)      echo "nextlevelbuilder/ui-ux-pro-max-skill" ;;
    designed-by-ai_*)        echo "designed-by-ai/skills" ;;
    ibelick_*)               echo "ibelick/ui-skills" ;;
    jakubkrehel_oklch-skill) echo "jakubkrehel/oklch-skill" ;;
    jakubkrehel_*)           echo "jakubkrehel/skills" ;;
    wondelai_*)              echo "wondelai/skills" ;;
    expo_*)                  echo "expo/skills" ;;
    flutter_*)               echo "flutter/agent-plugins" ;;
    wshobson_*)              echo "wshobson/agents" ;;
    addyosmani_web-quality-skills) echo "addyosmani/web-quality-skills" ;;
    addyosmani_*)            echo "addyosmani/agent-skills" ;;
    google-labs-code_*)      echo "google-labs-code/stitch-skills" ;;
    squirrelscan_*)          echo "squirrelscan/skills" ;;
    nutlope_*)               echo "nutlope/hallmark" ;;
    dammyjay93_*)            echo "dammyjay93/interface-design" ;;
    conardli_*)              echo "conardli/garden-skills" ;;
    sentimony_*)             echo "sentimony/skills" ;;
    antfu_*)                 echo "antfu/skills" ;;
    arvindrk_*)              echo "arvindrk/extract-design-system" ;;
    owl-listener_*)          echo "owl-listener/designer-skills" ;;
    julianoczkowski_*)       echo "julianoczkowski/designer-skills" ;;
    mengto_*)                echo "mengto/skills" ;;
    higgsfield-ai_*)         echo "higgsfield-ai/skills" ;;
    daniel-dan-conrad_*)     echo "daniel-dan-conrad/ui-designer-skill" ;;
    tw93_*)                  echo "tw93/waza" ;;
    zeke_*)                  echo "zeke/swiss-design-skill" ;;
    secondsky_*)             echo "secondsky/claude-skills" ;;
    jezweb_*)                echo "jezweb/claude-skills" ;;
    cline_*)                 echo "cline/skills" ;;
    samber_cc-skills)        echo "samber/cc-skills" ;;
    dmmulroy_*)              echo "dmmulroy/anti-slop" ;;
    deeflect_*)              echo "deeflect/mies" ;;
    iart-ai_web-animation-skills) echo "iart-ai/web-animation-skills" ;;
    iart-ai_*)               echo "iart-ai/motion-design-skills" ;;
    bergside_*)              echo "bergside/awesome-design-skills" ;;
    sanity-io_*)             echo "sanity-io/agent-toolkit" ;;
    supabase_*)              echo "supabase/agent-skills" ;;
    shadcn-ui_*)             echo "shadcn-ui/ui" ;;
    alchaincyf_*)            echo "alchaincyf/huashu-design" ;;
    wilwaldon_*)             echo "wilwaldon/Claude-Code-Frontend-Design-Toolkit" ;;
    freshtechbro_*)          echo "freshtechbro/claudedesignskills" ;;
    devmartinese_*)          echo "devmartinese/awwwards-animations-skill" ;;
    cloudai-x_*)             echo "cloudai-x/threejs-skills" ;;
    greensock_*)             echo "greensock/gsap-skills" ;;
    affaan-m_*)              echo "affaan-m/ecc" ;;
    patricio0312rev_*)       echo "patricio0312rev/skills" ;;
    delphi-ai_*)             echo "delphi-ai/animate-skill" ;;
    pixijs_*)                echo "pixijs/pixijs-skills" ;;
    omer-metin_*)            echo "omer-metin/skills-for-antigravity" ;;
    majidmanzarpour_*)       echo "majidmanzarpour/threejs-game-skills" ;;
    aladicf_*)               echo "aladicf/better-web-ui" ;;
    ryanthedev_*)            echo "ryanthedev/design-for-ai" ;;
    dylantarre_*)            echo "dylantarre/animation-principles" ;;
    dembrandt_*)             echo "dembrandt/dembrandt-skills" ;;
    rknall_*)                echo "rknall/claude-skills" ;;
    resciencelab_*)          echo "resciencelab/opc-skills" ;;
    jimliu_*)                echo "jimliu/baoyu-skills" ;;
    ehmo_*)                  echo "ehmo/platform-design-skills" ;;
    petekp_*)                echo "petekp/agent-skills" ;;
    cursor_*)                echo "cursor/plugins" ;;
    hyperb1iss_*)            echo "hyperb1iss/hyperskills" ;;
    syncfusion_*)            echo "syncfusion/react-ui-components-skills" ;;
    alirezarezvani_*)        echo "alirezarezvani/claude-skills" ;;
    coreyhaines31_*)         echo "coreyhaines31/marketingskills" ;;
    *) echo "" ;;
  esac
}

# Sparse-checkout a repo once, then reuse the cache.
ensure_repo() {
  local dir="$1" slug="$2" key
  key="$(echo "$slug" | tr '/' '_')"
  if [[ -d "$CLONE/$key/.git" ]]; then return 0; fi
  echo "  fetch $slug"
  git clone --depth 1 --filter=blob:none --sparse -q \
    "https://github.com/$slug.git" "$CLONE/$key" 2>/dev/null || return 1
  return 0
}

want() {
  local slug="$1"
  (( ${#SELECTED[@]} == 0 )) && return 0
  local s
  for s in "${SELECTED[@]}"; do [[ "$s" == "$slug" ]] && return 0; done
  return 1
}

ok=0; skip=0; fail=0; repos=0
declare -a FAILED=()

for MANIFEST in "${MANIFESTS[@]}"; do
  [[ -f "$MANIFEST" ]] || continue
  while IFS=$'\t' read -r slug repo path category installs origin; do
    [[ -z "${slug:-}" || "$slug" == \#* ]] && continue
    want "$slug" || continue

    dst="$DEST/$slug"
    [[ -e "$dst" || -L "$dst" ]] && (( UPDATE == 0 )) && { skip=$((skip+1)); continue; }

    gh_slug="$(repo_slug "$repo")"
    if [[ -z "$gh_slug" ]]; then
      echo "NOREPO $slug  (no source mapping for '$repo')"
      fail=$((fail+1)); FAILED+=("$slug"); continue
    fi

    if ! ensure_repo "$repo" "$gh_slug"; then
      echo "CLONE  $slug  (could not clone $gh_slug)"
      fail=$((fail+1)); FAILED+=("$slug"); continue
    fi
    repos=$((repos + 1))

    key="$(echo "$gh_slug" | tr '/' '_')"
    ( cd "$CLONE/$key" && git sparse-checkout set --no-cone "$path" 2>/dev/null ) || true

    src="$CLONE/$key/$path"
    if [[ ! -f "$src/SKILL.md" ]]; then
      # fall back to a full checkout for repos that ignore sparse patterns
      ( cd "$CLONE/$key" && git sparse-checkout disable 2>/dev/null ) || true
      src="$CLONE/$key/$path"
    fi
    if [[ ! -f "$src/SKILL.md" ]]; then
      echo "MISS   $slug  (not at $gh_slug/$path)"
      fail=$((fail+1)); FAILED+=("$slug"); continue
    fi

    rm -rf "$dst"
    cp -R "$src" "$dst" 2>/dev/null || true
    if [[ ! -f "$dst/SKILL.md" ]]; then
      rm -rf "$dst"
      echo "BROKEN $slug"
      fail=$((fail+1)); FAILED+=("$slug"); continue
    fi
    echo "OK     $slug  <- $gh_slug/$path"
    ok=$((ok+1))
  done < "$MANIFEST"
done

echo
echo "─────────────────────────────────────────"
echo "installed: $ok   already present: $skip   failed: $fail"
(( fail > 0 )) && printf 'failed: %s\n' "${FAILED[*]}"
exit 0
