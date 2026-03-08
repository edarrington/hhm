"""Google Drive Skill Implementation (Placeholder).

Framework for the Drive skill. Actual Google Drive API integration
will be implemented in Phase 2.
"""

from __future__ import annotations

import os
from pathlib import Path

from ..skill_loader import parse_skill_md
from ..types import HouseholdSkillContext, PromptFragment, SessionPatch, Skill

# Parse SKILL.md once at import time
_SKILL_MD_PATH = Path(__file__).parent / "SKILL.md"
_META, _BODY = parse_skill_md(_SKILL_MD_PATH)


def _extract_section(body: str, heading: str) -> str:
    """Extract a section from SKILL.md by heading name."""
    marker = f"## {heading}\n"
    start = body.find(marker)
    if start == -1:
        return ""
    start += len(marker)
    # Find next ## heading or end of string
    next_heading = body.find("\n## ", start)
    if next_heading == -1:
        return body[start:].strip()
    return body[start:next_heading].strip()


# Pre-build prompt fragments from SKILL.md sections
DRIVE_INDEX = PromptFragment(
    id="drive.index",
    kind="index",
    priority=80,
    tokens_hint=12,
    text=_extract_section(_BODY, "Index"),
)

DRIVE_BASE = PromptFragment(
    id="drive.base",
    kind="base",
    priority=70,
    tokens_hint=40,
    text=_extract_section(_BODY, "Base"),
)

DRIVE_PACK = PromptFragment(
    id="drive.pack",
    kind="pack",
    priority=60,
    tokens_hint=200,
    text=_extract_section(_BODY, "Pack"),
)


class DriveSkill(Skill):
    """Google Drive skill for household document management."""

    id = "drive"

    def is_enabled(self) -> bool:
        """Drive skill is enabled by ENABLE_DRIVE_SKILL env var."""
        return os.getenv("ENABLE_DRIVE_SKILL", "true").lower() == "true"

    def build_patch(
        self, ctx: HouseholdSkillContext, *, mode: str
    ) -> SessionPatch:
        """Build the Drive patch for a given mode."""
        if mode == "index":
            return SessionPatch(tools=[], prompt_fragments=[DRIVE_INDEX], routers=[])

        if mode == "base":
            # Phase 2: Import Drive integration and tools
            # from src.integrations.drive import DRIVE_TOOLS, drive_router
            # For now, return empty tools and routers (to be implemented)
            tools = []
            routers = []

            # Only expose full tool set when Drive is connected
            if ctx.drive_connected:
                # tools = DRIVE_TOOLS
                pass

            return SessionPatch(tools=tools, prompt_fragments=[DRIVE_BASE], routers=routers)

        if mode == "pack":
            return SessionPatch(tools=[], prompt_fragments=[DRIVE_PACK], routers=[])

        raise ValueError(f"Unknown mode: {mode}")
