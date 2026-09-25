"""
AI Assistant module.

Uses Groq's free-tier API (OpenAI-compatible chat completions) to turn a
plain-English admin instruction like:

    "Move Sarah to seat B4"
    "Unassign John from his seat"
    "Put Alex next to the window on seat C2"

into a structured JSON action:

    {"employee": "Sarah", "action": "assign", "seat": "B4"}

Get a free API key at https://console.groq.com/keys (no credit card required).
Set it as the GROQ_API_KEY environment variable.
"""

import os
import json
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "openai/gpt-oss-20b"  # fast + free on Groq

SYSTEM_PROMPT = """You are a backend assistant for an office seating system.
Given an admin's natural-language instruction, extract the intended action
and reply with ONLY valid JSON (no markdown, no commentary) in this exact
shape:

{"employee": "<employee name mentioned>", "action": "assign" | "unassign", "seat": "<seat label or null>"}

Rules:
- "action" is "unassign" if the instruction removes/clears/frees a seat.
- "action" is "assign" if the instruction places/moves/puts an employee in a seat.
- "seat" must be null when action is "unassign".
- If no seat label is given for an assign action, set seat to null.
- Only output the JSON object, nothing else.
"""


class AIAssistantError(Exception):
    pass


def interpret_prompt(prompt: str) -> dict:
    """Send the admin's prompt to Groq and return the parsed action dict."""
    if not GROQ_API_KEY:
        raise AIAssistantError(
            "GROQ_API_KEY is not set. Get a free key at "
            "https://console.groq.com/keys and add it to your .env file."
        )

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        resp = requests.post(GROQ_URL, headers=headers, json=payload, timeout=20)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise AIAssistantError(f"AI request failed: {e}")

    data = resp.json()
    try:
        content = data["choices"][0]["message"]["content"]
        action = json.loads(content)
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        raise AIAssistantError(f"Could not parse AI response: {e}")

    if "employee" not in action or "action" not in action:
        raise AIAssistantError("AI response missing required fields.")

    return action
