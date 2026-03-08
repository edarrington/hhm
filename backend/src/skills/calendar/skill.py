"""Google Calendar Skill Implementation (Placeholder).

This is a framework for the calendar skill. Actual Google Calendar API
integration will be implemented in Phase 2.
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
CALENDAR_INDEX = PromptFragment(
    id="calendar.index",
    kind="index",
    priority=90,
    tokens_hint=12,
    text=_extract_section(_BODY, "Index"),
)

CALENDAR_BASE = PromptFragment(
    id="calendar.base",
    kind="base",
    priority=80,
    tokens_hint=45,
    text=_extract_section(_BODY, "Base"),
)

CALENDAR_PACK = PromptFragment(
    id="calendar.pack",
    kind="pack",
    priority=70,
    tokens_hint=260,
    text=_extract_section(_BODY, "Pack"),
)


class CalendarSkill(Skill):
    """Google Calendar skill for household event management."""

    id = "calendar"

    def is_enabled(self) -> bool:
        """Calendar skill is enabled by ENABLE_CALENDAR_SKILL env var."""
        return os.getenv("ENABLE_CALENDAR_SKILL", "true").lower() == "true"

    def build_patch(
        self, ctx: HouseholdSkillContext, *, mode: str
    ) -> SessionPatch:
        """Build the calendar patch for a given mode."""
        if mode == "index":
            return SessionPatch(tools=[], prompt_fragments=[CALENDAR_INDEX], routers=[])

        if mode == "base":
            # Phase 2: Import calendar integration and tools
            # from src.integrations.calendar import CALENDAR_TOOLS, calendar_router
            # For now, return empty tools and routers (to be implemented)
            tools = []
            routers = []

            # Only expose full tool set when calendar is connected
            if ctx.calendar_connected:
                # tools = CALENDAR_TOOLS
                pass

            return SessionPatch(tools=tools, prompt_fragments=[CALENDAR_BASE], routers=routers)

        if mode == "pack":
            return SessionPatch(tools=[], prompt_fragments=[CALENDAR_PACK], routers=[])

        raise ValueError(f"Unknown mode: {mode}")
