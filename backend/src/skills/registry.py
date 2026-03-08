"""Household Skill Registry and Aggregation.

Auto-discovers skills by scanning src/skills/*/SKILL.md at startup.
Aggregates tools, prompts, and routers for household operations.
"""

from __future__ import annotations

import importlib
import logging
import os
from pathlib import Path
from typing import Any

from .skill_loader import parse_skill_md
from .types import HouseholdSkillContext, MarkdownSkill, Skill

logger = logging.getLogger(__name__)

_SKILLS_DIR = Path(__file__).parent


def _load_all_skills() -> list[Skill]:
    """Auto-discover skills by scanning for SKILL.md files.

    For each ``src/skills/<name>/SKILL.md``:
    - If a companion ``skill.py`` exists with a Skill class, import and
      instantiate it (e.g. CalendarSkill with tools/routers).
    - Otherwise, create a MarkdownSkill (instructions-only, no tools).
    """
    skills: list[Skill] = []

    for skill_md_path in sorted(_SKILLS_DIR.glob("*/SKILL.md")):
        folder = skill_md_path.parent
        skill_id = folder.name

        try:
            meta, body = parse_skill_md(skill_md_path)
        except Exception as e:
            logger.warning(f"Skipping skill {skill_id}: failed to parse SKILL.md: {e}")
            continue

        # Check for companion skill.py with a Skill class
        skill_py = folder / "skill.py"
        if skill_py.exists():
            try:
                module = importlib.import_module(f"src.skills.{skill_id}.skill")
                # Find the first class that has is_enabled and build_patch
                for attr_name in dir(module):
                    cls = getattr(module, attr_name)
                    if (
                        isinstance(cls, type)
                        and hasattr(cls, "is_enabled")
                        and hasattr(cls, "build_patch")
                        and cls is not MarkdownSkill
                        and cls is not Skill
                    ):
                        skills.append(cls())
                        logger.info(
                            f"Loaded skill {skill_id} from {skill_id}/skill.py ({cls.__name__})"
                        )
                        break
                else:
                    # No Skill class found in skill.py — treat as markdown-only
                    skills.append(MarkdownSkill(skill_id, meta, body))
                    logger.info(
                        f"Loaded skill {skill_id} as MarkdownSkill (skill.py has no Skill class)"
                    )
            except Exception as e:
                logger.warning(f"Skipping skill {skill_id}: failed to import skill.py: {e}")
                continue
        else:
            # No skill.py — instructions-only skill
            skills.append(MarkdownSkill(skill_id, meta, body))
            logger.info(f"Loaded skill {skill_id} as MarkdownSkill (instructions-only)")

    return skills


def get_enabled_skills() -> list[Skill]:
    """Return enabled skills."""
    skills = [s for s in _load_all_skills() if s.is_enabled()]
    names = ", ".join(getattr(s, "id", type(s).__name__) for s in skills)
    logger.info(f"Enabled skills: {len(skills)} ({names})")
    return skills


def get_enabled_skill_routers() -> list[Any]:
    """Return FastAPI routers for enabled skills."""
    routers: list[Any] = []
    ctx = HouseholdSkillContext(household_id="default", user_id="default")
    for skill in get_enabled_skills():
        patch = skill.build_patch(ctx, mode="base")
        routers.extend(patch.routers)
    logger.info(f"Skill routers: {len(routers)}")
    return routers


def get_enabled_skill_tools(
    ctx: HouseholdSkillContext | None = None,
) -> list[dict[str, Any]]:
    """Return OpenAI function schemas for enabled skills."""
    if ctx is None:
        ctx = HouseholdSkillContext(household_id="default", user_id="default")
    tools: list[dict[str, Any]] = []
    for skill in get_enabled_skills():
        patch = skill.build_patch(ctx, mode="base")
        tools.extend(patch.tools)
    logger.info(f"Skill tools: {len(tools)} for household={ctx.household_id}, user={ctx.user_id}")
    return tools


def get_enabled_skill_prompt_sections(*, ctx: HouseholdSkillContext) -> list[str]:
    """Return skill-related prompt sections for household conversations.

    Aggregates index, base, and pack fragments from enabled skills.
    Respects token budget to avoid prompt inflation.
    """
    enabled = get_enabled_skills()
    if not enabled:
        return []

    budget_tokens = int(os.getenv("SKILLS_PROMPT_BUDGET_TOKENS", "350"))

    index_frags: list = []
    base_frags: list = []
    pack_frags: list = []

    for skill in enabled:
        index_frags.extend(skill.build_patch(ctx, mode="index").prompt_fragments)
        base_frags.extend(skill.build_patch(ctx, mode="base").prompt_fragments)
        # Include pack fragments for detailed household knowledge
        pack_frags.extend(skill.build_patch(ctx, mode="pack").prompt_fragments)

    # Simple token budget: sort by priority, take top tokens
    all_frags = index_frags + base_frags + pack_frags
    selected = sorted(all_frags, key=lambda f: -f.priority)[
        : max(1, budget_tokens // 25)
    ]  # rough estimate

    # Always present a tiny capability index for the model.
    index_lines = [f"- {f.text.strip()}" for f in selected if f.kind == "index"]
    sections: list[str] = []
    if index_lines:
        sections.append(
            """# Household Skills (Capabilities)

These are the household's available capabilities:
"""
            + "\n".join(index_lines)
        )

    # Then add any base/pack behavioral rules selected.
    for frag in selected:
        if frag.kind in ("base", "pack"):
            sections.append(frag.text.strip())

    return sections
