from __future__ import annotations

import json
from typing import Any
from urllib import error, request

from gov_writer_agent.config import Settings


class OpenAIResponsesClient:
    def __init__(self, settings: Settings) -> None:
        if not settings.api_key:
            raise ValueError("Missing OPENAI_API_KEY. Please create a .env file first.")
        self.settings = settings

    def generate_text(
        self,
        *,
        instructions: str,
        prompt: str,
        max_output_tokens: int = 4000,
    ) -> str:
        payload = {
            "model": self.settings.model,
            "instructions": instructions,
            "input": prompt,
            "reasoning": {"effort": self.settings.reasoning_effort},
            "max_output_tokens": max_output_tokens,
        }

        response_payload = self._post_json("/responses", payload)
        text = self._extract_text(response_payload).strip()
        if not text:
            raise RuntimeError("The model returned an empty response.")
        return text

    def generate_json(
        self,
        *,
        instructions: str,
        prompt: str,
        max_output_tokens: int = 1200,
    ) -> dict[str, Any]:
        text = self.generate_text(
            instructions=instructions,
            prompt=prompt,
            max_output_tokens=max_output_tokens,
        )
        return self._parse_json_text(text)

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            url=f"{self.settings.base_url}{path}",
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.settings.api_key}",
                "Content-Type": "application/json",
            },
        )

        try:
            with request.urlopen(req) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise RuntimeError(f"OpenAI API request failed: {detail}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"Network error while calling OpenAI API: {exc.reason}") from exc

    def _extract_text(self, payload: dict[str, Any]) -> str:
        direct_text = payload.get("output_text")
        if isinstance(direct_text, str) and direct_text.strip():
            return direct_text

        texts: list[str] = []

        def visit(node: Any) -> None:
            if isinstance(node, dict):
                text_value = node.get("text")
                if isinstance(text_value, str) and text_value.strip():
                    texts.append(text_value)
                for value in node.values():
                    visit(value)
            elif isinstance(node, list):
                for item in node:
                    visit(item)

        visit(payload.get("output", []))
        return "\n".join(texts).strip()

    def _parse_json_text(self, text: str) -> dict[str, Any]:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            if cleaned.startswith("json"):
                cleaned = cleaned[4:].strip()

        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise RuntimeError(f"Model did not return valid JSON: {text}")

        return json.loads(cleaned[start : end + 1])
