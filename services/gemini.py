"""Gemini Flash API wrapper."""
import os
import logging
from google import genai
from google.genai import types

logger = logging.getLogger("gemini")

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "gemini-3-flash-preview"


async def call_gemini_direct(prompt: str, temperature: float = 0.5) -> str:
    """Call Gemini without search grounding."""
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=4000,
        ),
    )
    return response.text or ""


async def call_gemini_with_search(prompt: str) -> str:
    """Call Gemini WITH Google Search grounding (for stock prices etc.)."""
    response = client.models.generate_content(
        model=MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            tools=[types.Tool(google_search=types.GoogleSearch())],
            temperature=0.5,
            max_output_tokens=4000,
        ),
    )
    return response.text or ""
