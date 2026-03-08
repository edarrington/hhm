"""HHM Skill Framework Types.

Adapted from Cogneon's types.py for household-aware operations.
Skills define tools, prompts, and routing for household capabilities.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class HouseholdSkillContext:
    """Runtime context for household skill enablement.
    
    Includes household_id and user_id for multi-user operations,
    plus connection state (whether integrations are enabled).
    """

    household_id: str
    user_id: str
    calendar_connected: bool | None = None
    gmail_connected: bool | None = None
    drive_connected: bool | None = None
    todoist_connected: bool | None = None


@dataclass(frozen=True)
class PromptFragment:
    """A small prompt fragment with a declared token cost.
    
    Skills contribute multiple fragments across index, base, and pack modes.
    """

    id: str
    text: str
    tokens_hint: int
    priority: int
    kind: str  # "index" | "base" | "pack"


@dataclass(frozen=True)
class SessionPatch:
    """A patch to the AI session configuration.
    
    Aggregates tools, prompts, and FastAPI routers from a skill.
    """

    tools: list[dict[str, Any]]
    prompt_fragments: list[PromptFragment]
    routers: list[Any]


class Skill(Protocol):
    """Protocol that all household skills must implement."""

    id: str

    def is_enabled(self) -> bool:
        """Return True if the skill is enabled by environment/config."""

    def build_patch(
        self, ctx: HouseholdSkillContext, *, mode: str
    ) -> SessionPatch:
        """Build a patch for a given mode (index/base/pack)."""


class MarkdownSkill:
    """A skill defined entirely by a SKILL.md file (no Python code).
    
    Instructions-only: provides prompt fragments but no tools or routers.
    Useful for behavioral guidance without backend implementation.
    """

    def __init__(self, skill_id: str, meta: dict, body: str) -> None:
        self.id = skill_id
        self._meta = meta
        self._body = body

    def is_enabled(self) -> bool:
        """Check if skill is enabled via environment variable."""
        env_var = self._meta.get("enabled_by")
        if not env_var:
            return True
        return os.getenv(env_var, "false").lower() == "true"

    def build_patch(
        self, ctx: HouseholdSkillContext, *, mode: str
    ) -> SessionPatch:
        """Return prompt fragments for the requested mode."""
        _ = ctx
        priority = self._meta.get("priority", 50)
        tokens_hint = self._meta.get("tokens_hint", 100)

        if mode == "index":
            desc = self._meta.get("description", self.id)
            frag = PromptFragment(
                id=f"{self.id}.index",
                kind="index",
                priority=priority,
                tokens_hint=12,
                text=desc,
            )
            return SessionPatch(tools=[], prompt_fragments=[frag], routers=[])

        if mode in ("base", "pack"):
            frag = PromptFragment(
                id=f"{self.id}.{mode}",
                kind=mode,
                priority=priority,
                tokens_hint=tokens_hint,
                text=self._body,
            )
            return SessionPatch(tools=[], prompt_fragments=[frag], routers=[])

        raise ValueError(f"Unknown mode: {mode}")
