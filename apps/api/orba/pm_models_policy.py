"""Reviewed Gemini configuration, not a router or proof of account availability.

Capabilities reviewed 2026-10-20 against each model's official page and
https://ai.google.dev/gemini-api/docs/generate-content/thinking.
Changing this table requires review/tests and fresh source-bound verification.
"""

from dataclasses import dataclass
from typing import Literal

ThinkingLevel = Literal["minimal", "low", "medium", "high"]


@dataclass(frozen=True)
class ModelPolicy:
    identifier: str
    thinking_levels: tuple[ThinkingLevel, ...]

    @property
    def documentation(self) -> str:
        return f"https://ai.google.dev/gemini-api/docs/models/{self.identifier}"


APPROVED_MODELS = (
    ModelPolicy("gemini-3.8-flash", ("low", "medium", "high")),
    ModelPolicy("gemini-3.6-flash", ("minimal", "low", "medium", "high")),
    ModelPolicy("gemini-3.5-flash-lite", ("minimal", "low", "medium", "high")),
)
MODEL_CONFIGURATION_HELP = (
    "ORBA_PM_MODEL must select gemini-3.8-flash, gemini-3.6-flash or "
    "gemini-3.5-flash-lite (optional models/ prefix). ORBA_PM_THINKING_LEVEL "
    "supports low/medium/high; minimal is supported only by 3.6 and 3.5 Flash-Lite. "
    "No default model, fallback or automatic switch is used."
)


def model_policy(identifier: str | None) -> ModelPolicy | None:
    if not isinstance(identifier, str):
        return None
    name = identifier.removeprefix("models/")
    return next((policy for policy in APPROVED_MODELS if policy.identifier == name), None)


def validate_model_configuration(identifier: str | None, level: str) -> None:
    if level not in {"minimal", "low", "medium", "high"}:
        raise ValueError(MODEL_CONFIGURATION_HELP)
    if identifier is None:
        return  # Missing provider is a supported setup state, never a default model.
    policy = model_policy(identifier)
    if policy is None or level not in policy.thinking_levels:
        raise ValueError(MODEL_CONFIGURATION_HELP)
