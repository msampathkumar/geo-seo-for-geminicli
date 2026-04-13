#!/usr/bin/env bash
set -euo pipefail

# ============================================================
# GEO-SEO Gemini CLI Tool Uninstaller
# Removes the GEO-first SEO analysis tool components.
# ============================================================

# Note: The CLAUDE_DIR variable might be a remnant if the tool is now managed by Gemini CLI's skill system.
# This script focuses on removing project-specific files installed by the install.sh script.
# It does NOT uninstall the Gemini CLI itself.

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo ""
echo -e "${YELLOW}GEO-SEO Gemini CLI Tool Uninstaller${NC}"
echo ""
echo "This script will remove the GEO-SEO tool's local project files."
echo "It does NOT uninstall the Gemini CLI itself. To uninstall the Gemini CLI, use:"
echo -e "${BLUE}  npm uninstall -g @google/gemini-cli${NC}"
echo ""

# --- Removal Logic ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_DIR="$SCRIPT_DIR"

GEMINI_SKILL_PATH="${HOME}/.gemini/skills/geo"
GEMINI_AGENTS_DIR="${HOME}/.gemini/agents"
GEMINI_SKILLS_DIR="${HOME}/.gemini/skills"

echo -e "${YELLOW}→ Checking for installed GEO-SEO Gemini CLI skill files...${NC}"

REMOVED_COUNT=0

# Remove main skill
if [ -d "$GEMINI_SKILL_PATH" ]; then
    echo -e "${BLUE}  Found main skill at ${GEMINI_SKILL_PATH}. Removing...${NC}"
    rm -rf "$GEMINI_SKILL_PATH"
    echo -e "${GREEN}✓ Removed: ${GEMINI_SKILL_PATH}${NC}"
    REMOVED_COUNT=$((REMOVED_COUNT + 1))
fi

# Remove sub-skills
echo -e "${YELLOW}→ Checking for installed sub-skills...${NC}"
if [ -d "$SOURCE_DIR/skills" ]; then
    for skill_dir in "$SOURCE_DIR/skills"/*/; do
        if [ -d "$skill_dir" ]; then
            skill_name=$(basename "$skill_dir")
            target_dir="${GEMINI_SKILLS_DIR}/${skill_name}"
            if [ -d "$target_dir" ]; then
                rm -rf "$target_dir"
                echo -e "${GREEN}✓ Removed: ${target_dir}${NC}"
                REMOVED_COUNT=$((REMOVED_COUNT + 1))
            fi
        fi
    done
fi

# Remove agents
echo -e "${YELLOW}→ Checking for installed subagents...${NC}"
if [ -d "$SOURCE_DIR/agents" ]; then
    for agent_file in "$SOURCE_DIR/agents/"*.md; do
        if [ -f "$agent_file" ]; then
            agent_name=$(basename "$agent_file")
            target_file="${GEMINI_AGENTS_DIR}/${agent_name}"
            if [ -f "$target_file" ]; then
                rm -f "$target_file"
                echo -e "${GREEN}✓ Removed: ${target_file}${NC}"
                REMOVED_COUNT=$((REMOVED_COUNT + 1))
            fi
        fi
    done
fi

# Check for old Claude-specific directories and provide advice
CLAUDE_DIR_REMNANT="${HOME}/.claude"
if [ -d "$CLAUDE_DIR_REMNANT" ]; then
    echo -e "${YELLOW}→ Found old Claude-specific directory: ${CLAUDE_DIR_REMNANT}${NC}"
    echo -e "${BLUE}  This directory is likely a remnant from previous installations.${NC}"
    echo -e "${BLUE}  If it's no longer needed, you can manually remove it:${NC}"
    echo -e "${BLUE}    rm -rf ${CLAUDE_DIR_REMNANT}${NC}"
fi

if [ "$REMOVED_COUNT" -eq 0 ]; then
    echo -e "${BLUE}→ No GEO-SEO Gemini CLI files found at common locations. No files removed by this script.${NC}"
fi

echo ""
echo -e "${GREEN}Uninstall process finished.${NC}"
echo ""
echo "To remove Python dependencies, if installed globally, you may need to run:"
echo "  pip uninstall beautifulsoup4 requests lxml Pillow validators"
echo ""
