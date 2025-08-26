from __future__ import annotations

import json
from typing import Any, Dict

from openai import OpenAI


class OpenAIWrapper:
    def __init__(self, model: str = "gpt-4.1", temperature: float = 0.2) -> None:
        self.client, self.model, self.temperature = OpenAI(), model, temperature

    def complete(self, system: str, user: str) -> str:
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
            )
            return resp.choices[0].message.content or ""
        except Exception:
            return ""

    def json_structured(self, system: str, user: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                temperature=self.temperature,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                response_format={"type": "json_object"},
            )
            content = resp.choices[0].message.content or "{}"
            return json.loads(content)
        except Exception:
            return {}
