"""Claude Sonnet API wrapper for high-stakes tasks."""
import os
import logging
from anthropic import Anthropic

logger = logging.getLogger("claude")

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
MODEL = "claude-sonnet-4-6"

# Personal context — load from config/context.md or override via env var.
# See config/context.md.example for the structure.
def _load_system_prompt() -> str:
    env_prompt = os.environ.get("BRAIN_SYSTEM_PROMPT")
    if env_prompt:
        return env_prompt
    try:
        from pathlib import Path
        ctx_path = Path(__file__).parent.parent / "config" / "context.md"
        if ctx_path.exists():
            return ctx_path.read_text(encoding="utf-8")
    except Exception as e:
        logger.warning("Could not load context.md: %s", e)
    return (
        "You are a personal AI assistant. Communicate clearly and directly. "
        "Adjust tone based on the relationship (formal vs. informal) when drafting messages."
    )

SYSTEM_PROMPT = _load_system_prompt()


async def call_claude(prompt: str, history: str = "") -> str:
    """Call Claude Sonnet for high-stakes tasks."""
    messages = []
    if history:
        messages.append({"role": "user", "content": f"Conversation history:\n{history}"})
        messages.append({"role": "assistant", "content": "Got it, I have the context."})
    messages.append({"role": "user", "content": prompt})

    response = client.messages.create(
        model=MODEL,
        max_tokens=4000,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    return response.content[0].text
