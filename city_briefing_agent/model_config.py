"""Centralized model selection.

Reads LLM_PROVIDER from the environment and returns the right model
configuration for every agent in the project. This lets you switch
between Gemini, Claude, and local Ollama models by editing one line
in .env instead of editing every agent file.

Also exposes USE_NESTED_AGENTS — a hint to agent.py about whether
the chosen model can reliably handle the nested specialist pattern
(cloud models = yes, local models = no, use flat tool architecture).
"""

import os
from typing import Union

# Lazy import LiteLlm only when needed — keeps the module importable
# even if litellm isn't installed and you're only using Gemini.
_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower().strip()


def get_model() -> Union[str, object]:
    """Return the model parameter for LlmAgent based on LLM_PROVIDER.

    Supported values for LLM_PROVIDER (set in .env):
        gemini       → gemini-2.5-flash (default)
        gemini-lite  → gemini-2.5-flash-lite (lower-cost cloud option)
        claude       → anthropic/claude-haiku-4-5 via LiteLLM
        claude-sonnet→ anthropic/claude-sonnet-4-6 via LiteLLM
        ollama       → ollama_chat/qwen2.5:7b via LiteLLM (smaller local)
        ollama-14b   → ollama_chat/qwen2.5:14b via LiteLLM (recommended for GPU)
        ollama-32b   → ollama_chat/qwen2.5:32b via LiteLLM (high quality)
    """
    if _PROVIDER == "gemini":
        return "gemini-2.5-flash"

    if _PROVIDER == "gemini-lite":
        return "gemini-2.5-flash-lite"

    # Everything below needs LiteLlm — import it here so users on
    # gemini-only setups don't need litellm installed.
    from google.adk.models.lite_llm import LiteLlm

    if _PROVIDER == "claude":
        return LiteLlm(model="anthropic/claude-haiku-4-5")

    if _PROVIDER == "claude-sonnet":
        return LiteLlm(model="anthropic/claude-sonnet-4-6")

    if _PROVIDER == "ollama":
        return LiteLlm(model="ollama_chat/qwen2.5:7b")

    if _PROVIDER == "ollama-14b":
        return LiteLlm(model="ollama_chat/qwen2.5:14b")

    if _PROVIDER == "ollama-32b":
        return LiteLlm(model="ollama_chat/qwen2.5:32b")

    raise ValueError(
        f"Unknown LLM_PROVIDER: {_PROVIDER!r}. "
        f"Set one of: gemini, gemini-lite, claude, claude-sonnet, "
        f"ollama, ollama-14b, ollama-32b in your .env file."
    )


# Architecture hint: cloud models handle the nested specialist pattern
# well; small local models do better with flat (tools directly on root).
# 14B+ local models can usually handle nested too.
USE_NESTED_AGENTS = _PROVIDER in {
    "gemini",
    "gemini-lite",
    "claude",
    "claude-sonnet",
    "ollama-14b",
    "ollama-32b",
}


# Print which configuration is active — handy for debugging when you
# forget what's in .env. Comment out if you find it noisy.
print(f"[model_config] LLM_PROVIDER={_PROVIDER!r} "
      f"USE_NESTED_AGENTS={USE_NESTED_AGENTS}")
