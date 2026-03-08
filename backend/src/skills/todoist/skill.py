"""Todoist Skill Implementation (Placeholder).

Framework for the Todoist skill. Actual Todoist API integration
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
TODOIST_INDEX = PromptFragment(
    id="todoist.index",
    kind="index",
    priority=85,
    tokens_hint=12,
    text=_extract_section(_BODY, "Index"),
)

TODOIST_BASE = PromptFragment(
    id="todoist.base",
    kind="base",
    priority=75,
    tokens_hint=45,
    text=_extract_section(_BODY, "Base"),
)

TODOIST_PACK = PromptFragment(
    id="todoist.pack",
    kind="pack",
    priority=65,
    tokens_hint=240,
    text=_extract_section(_BODY, "Pack"),
)


class TodoistSkill(Skill):
    """Todoist skill for household task management."""

    id = "todoist"

    def is_enabled(self) -> bool:
        """Todoist skill is enabled by ENABLE_TODOIST_SKILL env var."""
        return os.getenv("ENABLE_TODOIST_SKILL", "true").lower() == "true"

    def build_patch(
        self, ctx: HouseholdSkillContext, *, mode: str
    ) -> SessionPatch:
        """Build the Todoist patch for a given mode."""
        if mode == "index":
            return SessionPatch(tools=[], prompt_fragments=[TODOIST_INDEX], routers=[])

        if mode == "base":
            # Phase 2: Import Todoist integration and tools
            # from src.integrations.todoist import TODOIST_TOOLS, todoist_router
            # For now, return empty tools and routers (to be implemented)
            tools = []
            routers = []

            # Only expose full tool set when Todoist is connected
            if ctx.todoist_connected:
                # tools = TODOIST_TOOLS
                pass

            return SessionPatch(tools=tools, prompt_fragments=[TODOIST_BASE], routers=routers)

        if mode == "pack":
            return SessionPatch(tools=[], prompt_fragments=[TODOIST_PACK], routers=[])

        raise ValueError(f"Unknown mode: {mode}")
