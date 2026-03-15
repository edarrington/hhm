"""Tyrone Voice Skill — Claude-powered household voice assistant."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, Callable, Optional

import anthropic
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..skill_loader import parse_skill_md
from ..types import HouseholdSkillContext, PromptFragment, SessionPatch, Skill

logger = logging.getLogger(__name__)

_SKILL_MD_PATH = Path(__file__).parent / "SKILL.md"
_META, _BODY = parse_skill_md(_SKILL_MD_PATH)

SYSTEM_PROMPT = """You are Tyrone, the voice assistant for Happy House Manager — Erick and Jewel Darrington's household AI.

You help them manage their calendar, tasks, home life, and daily plans.

You have access to:
- Their open Todoist tasks (listed in context with IDs)
- Their upcoming Google Calendar events (listed in context)
- Their unread emails (listed in context with IDs and sender/subject)
- Tools to create calendar events, add/complete tasks, and read full email content

Rules:
- Respond in 1-2 sentences maximum. Be brief. Voice responses must be short.
- Be direct and warm. Never formal or corporate.
- NEVER say: "Certainly!", "Absolutely!", "Great question!", "I'd be happy to help!", "Is there anything else?"
- Natural openers: "Yeah,", "Sure,", "Got it,", "On it,", "Let me think,"
- When you complete a tool action, confirm briefly: "Done, added that." or "Marked it done."
- Sound human. Use contractions. Be brief.
- When asked about emails, use the unread email list in context. If they want more detail, use read_email.
- When summarizing emails, list who they're from and the subject — keep it short.
- If you genuinely don't have the info, say so plainly: "Not sure about that."
- You know both Erick and Jewel. Refer to them by name when relevant."""

SERVER_TOOLS = [
    {
        "type": "web_search_20260209",
        "name": "web_search",
    },
]

USER_TOOLS = [
    {
        "name": "create_calendar_event",
        "description": "Create a new event on the household Google Calendar.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Event title"},
                "start": {"type": "string", "description": "Start datetime in ISO 8601, e.g. 2026-03-10T14:00:00"},
                "end": {"type": "string", "description": "End datetime in ISO 8601, e.g. 2026-03-10T15:00:00"},
                "description": {"type": "string", "description": "Optional event description"},
            },
            "required": ["title", "start", "end"],
        },
    },
    {
        "name": "create_todoist_task",
        "description": "Add a new task to Todoist.",
        "input_schema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "Task content/title"},
                "due_string": {"type": "string", "description": "Due date in natural language, e.g. 'today', 'tomorrow', 'next Monday'"},
            },
            "required": ["content"],
        },
    },
    {
        "name": "complete_todoist_task",
        "description": "Mark an existing Todoist task as complete using its ID from context.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "The ID of the task to mark complete"},
            },
            "required": ["task_id"],
        },
    },
    {
        "name": "read_email",
        "description": "Read the full content of a specific email using its ID from context.",
        "input_schema": {
            "type": "object",
            "properties": {
                "message_id": {"type": "string", "description": "The email message ID from context"},
            },
            "required": ["message_id"],
        },
    },
]


class ChatRequest(BaseModel):
    transcript: str
    history: list[dict[str, str]] = []
    context: str = ""
    user_name: str = "Erick"


class ChatResponse(BaseModel):
    response: str


async def voice_chat(
    transcript: str,
    history: list[dict[str, str]],
    context: str,
    user_name: str,
    execute_tool: Optional[Callable] = None,
) -> str:
    """Send a voice transcript to Claude with optional tool support."""
    from src.config import get_settings
    settings = get_settings()

    if not settings.anthropic_api_key:
        return "Anthropic API key not configured."

    client = anthropic.AsyncAnthropic(api_key=settings.anthropic_api_key)

    system = SYSTEM_PROMPT
    if context:
        system += f"\n\nCurrent context for {user_name}:\n{context}"

    messages: list[dict[str, Any]] = []
    for msg in history[-6:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": transcript})

    try:
        response = await client.messages.create(
            model=settings.voice_model,
            max_tokens=200,
            system=system,
            tools=SERVER_TOOLS + (USER_TOOLS if execute_tool else []),
            messages=messages,
        )

        # Handle tool calls
        if response.stop_reason == "tool_use" and execute_tool:
            messages.append({"role": "assistant", "content": response.content})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    logger.info(f"Tyrone calling tool: {block.name} with {block.input}")
                    tool_result = await execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": tool_result,
                    })

            messages.append({"role": "user", "content": tool_results})

            followup = await client.messages.create(
                model=settings.voice_model,
                max_tokens=150,
                system=system,
                messages=messages,
            )
            for block in followup.content:
                if block.type == "text":
                    return block.text
            return "Done."

        for block in response.content:
            if block.type == "text":
                return block.text
        return ""

    except anthropic.APIError as e:
        logger.error(f"Anthropic API error: {e}")
        return "I ran into an issue. Try again in a moment."
    except Exception as e:
        logger.error(f"Tyrone error: {e}")
        return "Give me a second — just hit a snag. Try again."


def _make_router() -> APIRouter:
    router = APIRouter(prefix="/voice", tags=["voice"])

    @router.post("/chat", response_model=ChatResponse)
    async def chat(req: ChatRequest):
        reply = await voice_chat(
            transcript=req.transcript,
            history=req.history,
            context=req.context,
            user_name=req.user_name,
        )
        return ChatResponse(response=reply)

    return router


def _extract_section(body: str, heading: str) -> str:
    marker = f"## {heading}\n"
    start = body.find(marker)
    if start == -1:
        return ""
    start += len(marker)
    next_heading = body.find("\n## ", start)
    if next_heading == -1:
        return body[start:].strip()
    return body[start:next_heading].strip()


VOICE_INDEX = PromptFragment(
    id="voice.index",
    kind="index",
    priority=90,
    tokens_hint=12,
    text=_extract_section(_BODY, "Index"),
)

VOICE_BASE = PromptFragment(
    id="voice.base",
    kind="base",
    priority=80,
    tokens_hint=60,
    text=_extract_section(_BODY, "Base"),
)

VOICE_PACK = PromptFragment(
    id="voice.pack",
    kind="pack",
    priority=70,
    tokens_hint=80,
    text=_extract_section(_BODY, "Pack"),
)


class VoiceSkill(Skill):
    """Tyrone voice assistant skill powered by Claude."""

    id = "voice"

    def is_enabled(self) -> bool:
        return os.getenv("ENABLE_VOICE_SKILL", "true").lower() == "true"

    def build_patch(self, ctx: HouseholdSkillContext, *, mode: str) -> SessionPatch:
        if mode == "index":
            return SessionPatch(tools=[], prompt_fragments=[VOICE_INDEX], routers=[])

        if mode == "base":
            return SessionPatch(
                tools=[],
                prompt_fragments=[VOICE_BASE],
                routers=[_make_router()],
            )

        if mode == "pack":
            return SessionPatch(tools=[], prompt_fragments=[VOICE_PACK], routers=[])

        raise ValueError(f"Unknown mode: {mode}")
