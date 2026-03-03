from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from langchain_core.language_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI

Provider = Literal["gemini", "openai", "local_openai_compatible"]


@dataclass
class LLMConfig:
    provider: Provider
    model: str
    api_key: str
    base_url: str | None = None
    temperature: float = 0.1


def build_chat_model(config: LLMConfig) -> BaseChatModel:
    if config.provider == "gemini":
        return ChatGoogleGenerativeAI(
            model=config.model,
            google_api_key=config.api_key,
            temperature=config.temperature,
        )

    if config.provider == "openai":
        return ChatOpenAI(
            model=config.model,
            api_key=config.api_key,
            temperature=config.temperature,
        )

    if config.provider == "local_openai_compatible":
        return ChatOpenAI(
            model=config.model,
            api_key=config.api_key or "local",
            base_url=config.base_url,
            temperature=config.temperature,
        )

    raise ValueError(f"Unsupported provider: {config.provider}")
