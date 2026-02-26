from __future__ import annotations

from typing import List, Dict, Any

import requests

# Local Qwen model server, running on Raspberry Pi with llama.cpp
QWEN_API_URL = "http://127.0.0.1:9000/v1/chat/completions"
# Model name here is just a label, llama.cpp usually not very strict
QWEN_MODEL_NAME = "qwen3-0.6b"


def call_qwen_chat(
    messages: List[Dict[str, str]],
    temperature: float = 0.3,
    max_tokens: int = 512,
) -> str:
    """
    Call local Qwen model with simple chat API.

    messages example:
    [
      {"role": "system", "content": "..."},
      {"role": "user", "content": "..."},
    ]

    This function is small wrapper: send JSON, get back text.
    """
    payload: Dict[str, Any] = {
        "model": QWEN_MODEL_NAME,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    # Call local HTTP endpoint, not any cloud API
    resp = requests.post(QWEN_API_URL, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    # Typical /v1/chat/completions style
    choices = data.get("choices") or []
    if not choices:
        return "[Qwen] no response from model, maybe something wrong"

    message = choices[0].get("message") or {}
    content = message.get("content", "")
    return str(content).strip()