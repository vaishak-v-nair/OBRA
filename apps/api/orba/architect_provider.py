"""One Architect provider, reusing the PM's bounded official SDK transport."""

import hashlib
from pathlib import Path
from typing import Protocol

from orba.architect_schemas import ArchitectureDocument
from orba.pm_provider import GeminiStructuredProvider, ProviderFailure, ProviderResult

PROMPT_VERSION = "architect-v1"
PROMPT = (Path(__file__).parent / "prompts" / "architect_v1.txt").read_text(encoding="utf-8")
PROMPT_HASH = hashlib.sha256(PROMPT.encode()).hexdigest()


def output_schema():
    # Provider grammar hints only. The full strict Pydantic contract is unchanged.
    def project(node):
        if isinstance(node, list):
            return [project(item) for item in node]
        if not isinstance(node, dict):
            return node
        result = {
            key: project(value)
            for key, value in node.items()
            if key
            not in {"default", "title", "maxItems", "minLength", "maxLength", "pattern", "const"}
        }
        if "properties" in node:
            result["properties"] = {
                key: project(value) for key, value in node["properties"].items()
            }
        if "const" in node:
            result["enum"] = [node["const"]]
        return result

    return project(ArchitectureDocument.model_json_schema())


class ArchitectModelProvider(Protocol):
    async def generate(self, snapshot: dict) -> ProviderResult: ...


class GeminiArchitectProvider(GeminiStructuredProvider):
    def __init__(self, settings):
        super().__init__(settings.architect_settings(), prompt=PROMPT, schema_factory=output_schema)

    async def generate(self, snapshot):
        try:
            return await super().generate(snapshot)
        except ProviderFailure as exc:
            message = (
                exc.message.replace("product document", "architecture document")
                .replace("product plan", "architecture")
                .replace("No new plan", "No new architecture")
                .replace("No plan", "No architecture")
                .replace("Plan generation", "Architecture generation")
                .replace("ORBA_PM_MODEL", "ORBA_ARCHITECT_MODEL")
            )
            category = exc.category.replace(
                "pm_not_configured", "architect_not_configured"
            ).replace("pm_invalid_configuration", "architect_invalid_configuration")
            raise ProviderFailure(
                category, message, exc.status, diagnostic=exc.diagnostic, result=exc.result
            ) from None


def request_metrics(config, snapshot):
    return GeminiArchitectProvider(config).metrics(snapshot)
