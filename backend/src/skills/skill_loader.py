"""Parse SKILL.md files: YAML frontmatter + markdown body."""

from __future__ import annotations

from pathlib import Path

import yaml


def parse_skill_md(path: Path | str) -> tuple[dict, str]:
    """Parse a SKILL.md into (frontmatter_dict, body_text).

    If the file starts with ``---``, everything between the first and
    second ``---`` is treated as YAML frontmatter. The rest is the
    markdown body. If no frontmatter delimiter is found, the entire
    content is returned as the body with an empty dict.
    """
    content = Path(path).read_text()
    if content.startswith("---"):
        _, fm_raw, body = content.split("---", 2)
        return yaml.safe_load(fm_raw) or {}, body.strip()
    return {}, content.strip()
