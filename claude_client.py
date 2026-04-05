"""
Claude AI client — manages conversations with per-thread memory.
"""

import anthropic
from collections import defaultdict
from config import (
    ANTHROPIC_API_KEY,
    CLAUDE_MODEL,
    CLAUDE_MAX_TOKENS,
    SYSTEM_PROMPT,
    MAX_CONVERSATION_HISTORY,
    CREATIVE_MODEL,
    RESEARCH_MODEL,
    RESEARCH_MAX_TOKENS,
)
import knowledge_base

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

# In-memory conversation store keyed by (channel_id, thread_ts)
# Each value is a list of {"role": ..., "content": ...} dicts.
_conversations: dict[tuple[str, str], list[dict]] = defaultdict(list)


def _trim(history: list[dict]) -> list[dict]:
    """Keep only the most recent messages to stay within context limits."""
    return history[-MAX_CONVERSATION_HISTORY:]


def chat(channel: str, thread_ts: str, user_message: str) -> str:
    """
    Send a user message in the context of a Slack thread and return
    Claude's response. Conversation history is preserved per-thread.
    """
    key = (channel, thread_ts)
    _conversations[key].append({"role": "user", "content": user_message})
    _conversations[key] = _trim(_conversations[key])

    # Load ONLY the condensed client summaries for chat — small and fast
    client_context = knowledge_base.load_section("clients")
    system = SYSTEM_PROMPT
    if client_context:
        system = f"{SYSTEM_PROMPT}\n\n=== CLIENT CONTEXT ===\n{client_context}\n=== END CLIENT CONTEXT ==="

    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            system=system,
            messages=_conversations[key],
        )
        assistant_text = response.content[0].text
        _conversations[key].append({"role": "assistant", "content": assistant_text})
        return assistant_text

    except anthropic.APIError as e:
        # Remove the failed user message so history stays clean
        _conversations[key].pop()
        return f"Sorry, I hit an API error: {e.message}"


def one_shot(prompt: str) -> str:
    """Single-turn request with no memory (used by slash commands)."""
    try:
        response = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=CLAUDE_MAX_TOKENS,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except anthropic.APIError as e:
        return f"Sorry, I hit an API error: {e.message}"


def summarize_messages(messages: list[str]) -> str:
    """Summarize a list of Slack messages into key points."""
    joined = "\n".join(f"- {m}" for m in messages)
    prompt = (
        "Summarize the following Slack conversation into 3-5 bullet points. "
        "Focus on decisions made, action items, and key information.\n\n"
        f"{joined}"
    )
    return one_shot(prompt)


def creative_request(system_prompt: str, context: str, brief: str) -> str:
    """
    Run a creative writing request with a specialized system prompt
    and optional knowledge-base context. Uses higher token limit for
    long-form creative output. Includes A.D.A.P.T.-specific instructions.
    """
    user_message = (
        f"{brief}\n\n"
        "IMPORTANT: Follow the A.D.A.P.T. framework EXACTLY as described in your instructions. "
        "Use the correct section labels (A=Authority Hook, D=Define Enemy, A=Anecdotal Catalyst, "
        "P=Proof & Mechanism, T=Transition & CTA). Write 1:30-3:00 minutes of spoken script. "
        "Sound like a REAL PERSON talking to a friend — use contractions, filler words, vulnerability. "
        "NOT a copywriter. Include the full output format with avatar, emotion, big domino, visual notes, "
        "and QA checklist."
    )
    if context:
        user_message = f"{context}\n\n---\n\nBRIEF: {user_message}"

    try:
        response = client.messages.create(
            model=CREATIVE_MODEL,
            max_tokens=8192,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text
    except anthropic.APIError as e:
        return f"Sorry, I hit an API error: {e.message}"


def long_creative_request(system_prompt: str, context: str, brief: str, max_tokens: int = 16384) -> str:
    """
    Run a long-form creative request (advertorial, listicle, etc.).
    Unlike creative_request(), this does NOT inject A.D.A.P.T.-specific
    instructions — format-specific instructions belong in the system prompt.
    """
    user_message = brief
    if context:
        user_message = f"{context}\n\n---\n\nBRIEF: {brief}"

    try:
        response = client.messages.create(
            model=CREATIVE_MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text
    except anthropic.APIError as e:
        return f"Sorry, I hit an API error: {e.message}"


def research_analysis(system_prompt: str, raw_content: str, instruction: str) -> str:
    """
    Single-turn analysis call for the research pipeline.
    Uses RESEARCH_MODEL (Sonnet) — extraction doesn't need Opus.
    """
    user_message = f"{raw_content}\n\n---\n\nINSTRUCTION: {instruction}"

    try:
        response = client.messages.create(
            model=RESEARCH_MODEL,
            max_tokens=RESEARCH_MAX_TOKENS,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        return response.content[0].text
    except anthropic.APIError as e:
        return f"Research analysis error: {e.message}"
