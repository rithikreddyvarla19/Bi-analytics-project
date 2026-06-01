"""LLM provider abstractions."""

from __future__ import annotations

import os
import re
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class GenerationResult:
    text: str
    model: str
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


class LLMProvider(Protocol):
    model_name: str

    def generate(self, prompt: str) -> GenerationResult:
        """Generate an answer for a rendered prompt."""


class LocalTemplateLLM:
    """Deterministic local model for development, tests, and smoke checks."""

    model_name = "local-template-llm"

    def generate(self, prompt: str) -> GenerationResult:
        question = self._extract_section(prompt, "Question")
        context = self._extract_context(prompt)
        sentences = re.split(r"(?<=[.!?])\s+", context)
        question_terms = set(re.findall(r"[a-zA-Z]{4,}", question.lower()))
        ranked = sorted(
            (sentence.strip() for sentence in sentences if sentence.strip()),
            key=lambda sentence: len(question_terms.intersection(set(re.findall(r"[a-zA-Z]{4,}", sentence.lower())))),
            reverse=True,
        )
        answer_sentences = ranked[:2] if ranked else ["The available sources do not contain enough information."]
        answer = " ".join(answer_sentences)
        if "[S" not in answer and context:
            answer = f"{answer} [S1]"
        return GenerationResult(text=answer, model=self.model_name)

    @staticmethod
    def _extract_section(prompt: str, name: str) -> str:
        match = re.search(rf"{name}:\s*(.*?)(?:\n\n[A-Z][A-Za-z ]+:|\Z)", prompt, re.DOTALL)
        return match.group(1).strip() if match else ""

    @staticmethod
    def _extract_context(prompt: str) -> str:
        for label in ("Context", "Evidence"):
            match = re.search(rf"{label}:\s*(.*?)(?:\n\nAnswer:|\Z)", prompt, re.DOTALL)
            if match:
                return match.group(1).strip()
        return ""


class OpenAIChatLLM:
    """OpenAI chat-completions provider."""

    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.0,
        api_key: str | None = None,
    ) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - optional production dependency
            raise RuntimeError("Install openai to use OpenAI chat models.") from exc

        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model_name = model
        self.temperature = temperature

    def generate(self, prompt: str) -> GenerationResult:
        response = self.client.chat.completions.create(
            model=self.model_name,
            temperature=self.temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        usage = response.usage
        return GenerationResult(
            text=response.choices[0].message.content or "",
            model=self.model_name,
            prompt_tokens=getattr(usage, "prompt_tokens", None),
            completion_tokens=getattr(usage, "completion_tokens", None),
        )


class HuggingFaceLLM:
    """Text-generation provider backed by HuggingFace Transformers."""

    def __init__(
        self,
        model_name: str = "google/flan-t5-base",
        max_new_tokens: int = 256,
        device: int = -1,
    ) -> None:
        try:
            from transformers import pipeline
        except ImportError as exc:  # pragma: no cover - optional production dependency
            raise RuntimeError("Install transformers to use HuggingFace generation.") from exc

        self.pipeline = pipeline("text2text-generation", model=model_name, device=device)
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens

    def generate(self, prompt: str) -> GenerationResult:
        output = self.pipeline(prompt, max_new_tokens=self.max_new_tokens, do_sample=False)
        text = output[0]["generated_text"] if output else ""
        return GenerationResult(text=text, model=self.model_name)


def get_llm_provider(provider: str | None = None, **kwargs: object) -> LLMProvider:
    selected = (provider or os.getenv("LLM_PROVIDER") or "local").lower()
    if selected == "openai":
        return OpenAIChatLLM(**kwargs)
    if selected in {"huggingface", "hf", "transformers"}:
        return HuggingFaceLLM(**kwargs)
    if selected == "local":
        return LocalTemplateLLM()
    raise ValueError(f"Unsupported LLM provider: {selected}")
