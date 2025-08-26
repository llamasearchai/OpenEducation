from __future__ import annotations
import os
import json
from typing import Any, Dict
import time
import hashlib
from openai import OpenAI
from ratelimit import limits, sleep_and_retry

from ..utils.io import ensure_dir

class OpenAIWrapper:
    def __init__(self, model: str = "gpt-4-turbo", temperature: float = 0.2) -> None:
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable is not set.")
        
        self.client, self.model, self.temperature = OpenAI(), model, temperature
        self.cache_path = "data/cache/llm_responses"
        ensure_dir(self.cache_path)

    @sleep_and_retry
    @limits(calls=10, period=60) # 10 calls per minute
    def complete(self, system: str, user: str, retries: int = 3, delay: int = 5) -> str:
        # Create a unique hash for the request to use as a cache key
        request_string = f"{self.model}-{self.temperature}-{system}-{user}"
        request_hash = hashlib.sha256(request_string.encode('utf-8')).hexdigest()
        cache_file = os.path.join(self.cache_path, f"{request_hash}.json")

        # Check if the response is in the cache
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)["response"]

        for i in range(retries):
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    temperature=self.temperature,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                )
                response_content = resp.choices[0].message.content or ""
                
                # Save the successful response to the cache
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump({"request": request_string, "response": response_content}, f, indent=2)
                
                return response_content
            except Exception as e:
                if i < retries - 1:
                    print(f"API call failed, retrying in {delay} seconds... ({e})")
                    time.sleep(delay)
                    delay *= 2  # Exponential backoff
                else:
                    print(f"API call failed after {retries} retries.")
                    return ""
        return ""  # Should not be reached

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
