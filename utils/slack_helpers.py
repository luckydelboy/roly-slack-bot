"""
Slack utility functions — message splitting, progress posting, long messages.
"""

import logging

logger = logging.getLogger(__name__)

MAX_SLACK_LENGTH = 3900  # Slack limit is ~4000, leave margin


def split_message(text: str, max_len: int = MAX_SLACK_LENGTH) -> list[str]:
    """Split a long message at section boundaries to respect Slack's char limit."""
    if len(text) <= max_len:
        return [text]

    chunks = []
    current = ""

    # Try splitting on double-newline (section breaks) first
    sections = text.split("\n\n")

    for section in sections:
        candidate = f"{current}\n\n{section}" if current else section

        if len(candidate) <= max_len:
            current = candidate
        else:
            # Current chunk is full — save it
            if current:
                chunks.append(current.strip())

            # If this single section exceeds the limit, split on single newlines
            if len(section) > max_len:
                lines = section.split("\n")
                current = ""
                for line in lines:
                    line_candidate = f"{current}\n{line}" if current else line
                    if len(line_candidate) <= max_len:
                        current = line_candidate
                    else:
                        if current:
                            chunks.append(current.strip())
                        current = line[:max_len]
            else:
                current = section

    if current.strip():
        chunks.append(current.strip())

    return chunks if chunks else [text[:max_len]]


def post_long_message(client, channel: str, thread_ts: str, text: str):
    """Post a long message as multiple chunks in a Slack thread."""
    chunks = split_message(text)
    total = len(chunks)

    for i, chunk in enumerate(chunks):
        prefix = f"*({i + 1}/{total})*\n" if total > 1 else ""
        client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=f"{prefix}{chunk}",
        )


def post_progress(client, channel: str, thread_ts: str, emoji: str, message: str):
    """Post a short progress update in a Slack thread."""
    client.chat_postMessage(
        channel=channel,
        thread_ts=thread_ts,
        text=f":{emoji}: {message}",
    )
