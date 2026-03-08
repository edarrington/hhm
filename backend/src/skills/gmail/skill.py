"""Google Gmail Skill Implementation (Placeholder).

Framework for the Gmail skill. Actual Google Gmail API integration
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
GMAIL_INDEX = PromptFragment(
    id="gmail.index",
    kind="index",
    priority=85,
    tokens_hint=12,
    text=_extract_section(_BODY, "Index"),
)

GMAIL_BASE = PromptFragment(
    id="gmail.base",
    kind="base",
    priority=75,
    tokens_hint=40,
    text=_extract_section(_BODY, "Base"),
)

GMAIL_PACK = PromptFragment(
    id="gmail.pack",
    kind="pack",
    priority=65,
    tokens_hint=220,
    text=_extract_section(_BODY, "Pack"),
)


class GmailSkill(Skill):
    """Google Gmail skill for household email management."""

    id = "gmail"

    def is_enabled(self) -> bool:
        """Gmail skill is enabled by ENABLE_GMAIL_SKILL env var."""
        return os.getenv("ENABLE_GMAIL_SKILL", "true").lower() == "true"

    def build_patch(
        self, ctx: HouseholdSkillContext, *, mode: str
    ) -> SessionPatch:
        """Build the Gmail patch for a given mode."""
        if mode == "index":
            return SessionPatch(tools=[], prompt_fragments=[GMAIL_INDEX], routers=[])

        if mode == "base":
            # Phase 2: Import Gmail integration and tools
            # from src.integrations.gmail import GMAIL_TOOLS, gmail_router
            # For now, return empty tools and routers (to be implemented)
            tools = []
            routers = []

            # Only expose full tool set when Gmail is connected
            if ctx.gmail_connected:
                # tools = GMAIL_TOOLS
                pass

            return SessionPatch(tools=tools, prompt_fragments=[GMAIL_BASE], routers=routers)

        if mode == "pack":
            return SessionPatch(tools=[], prompt_fragments=[GMAIL_PACK], routers=[])

        raise ValueError(f"Unknown mode: {mode}")
