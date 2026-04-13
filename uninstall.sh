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
# Assumes files were installed into a structure that might be under ~/.gemini/skills/geo or similar.
# The exact path can vary, so we try common locations.

GEMINI_SKILL_PATH_1="~/.gemini/skills/geo"
GEMINI_SKILL_PATH_2="${HOME}/.gemini/skills/geo" # Explicitly expand home directory

echo -e "${YELLOW}→ Checking for installed GEO-SEO Gemini CLI skill files...${NC}"

REMOVED_COUNT=0

# Attempt to remove from common Gemini CLI skill paths
if [ -d "$GEMINI_SKILL_PATH_1" ]; then
    echo -e "${BLUE}  Found at ${GEMINI_SKILL_PATH_1}. Removing...${NC}"
    rm -rf "$GEMINI_SKILL_PATH_1"
    echo -e "${GREEN}✓ Removed: ${GEMINI_SKILL_PATH_1}${NC}"
    REMOVED_COUNT=$((REMOVED_COUNT + 1))
elif [ -d "$GEMINI_SKILL_PATH_2" ]; then
    echo -e "${BLUE}  Found at ${GEMINI_SKILL_PATH_2}. Removing...${NC}"
    rm -rf "$GEMINI_SKILL_PATH_2"
    echo -e "${GREEN}✓ Removed: ${GEMINI_SKILL_PATH_2}${NC}"
    REMOVED_COUNT=$((REMOVED_COUNT + 1))
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
    echo -e "${BLUE}→ No GEO-SEO Gemini CLI skill files found at common locations. No project files removed by this script.${NC}"
fi

echo ""
echo -e "${GREEN}Uninstall process finished.${NC}"
echo ""
echo "To remove Python dependencies, if installed globally, you may need to run:"
echo "  pip uninstall beautifulsoup4 requests lxml Pillow validators"
echo ""
