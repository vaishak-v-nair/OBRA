"""Offline readiness by default. Explicit --check-model allows one metadata GET only."""

import argparse
import asyncio
import json

from pydantic import ValidationError

from orba.config import Settings
from orba.pm_readiness import check_model, configuration_readiness


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check-model",
        action="store_true",
        help="One bounded official SDK model metadata GET; never generation or proof of generation.",
    )
    args = parser.parse_args(argv)
    try:
        config = Settings().architect_settings()
    except ValidationError:
        print(
            json.dumps(
                {
                    "agent": "architect",
                    "status": "invalid_configuration",
                    "message": "Check Architect model/thinking, numeric bounds and local origin configuration. No request was sent.",
                }
            )
        )
        return 2
    report = (
        asyncio.run(check_model(config)) if args.check_model else configuration_readiness(config)
    )
    value = report.model_dump(mode="json") | {
        "agent": "architect",
        "model": config.pm_model,
        "generation_verified": False,
    }
    if not config.pm_configured:
        value.update(
            verdict="BLOCKED",
            message="Set ORBA_ARCHITECT_MODEL and a server-only Gemini credential. Readiness is not generation evidence.",
        )
    print(json.dumps(value))
    return (
        (0 if report.status == "ready_for_attempt" else 2)
        if args.check_model
        else (0 if config.pm_configured else 1)
    )


if __name__ == "__main__":
    raise SystemExit(main())
