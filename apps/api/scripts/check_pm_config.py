"""Offline by default. --check-model makes one read-only GET, never generation."""

import argparse
import asyncio
import json

from pydantic import ValidationError

from orba.config import Settings
from orba.pm_models_policy import MODEL_CONFIGURATION_HELP
from orba.pm_readiness import ProviderReadiness, check_model, configuration_readiness


def main(argv=None):
    parser = argparse.ArgumentParser(
        description=__doc__,
        epilog=MODEL_CONFIGURATION_HELP
        + " ORBA_PM_MAX_INPUT_BYTES bounds prompt+canonical schema+snapshot UTF8 content "
        "(8192-96000, default48000), not billed tokens. Invalid configured Settings can "
        "prevent API startup; use this offline check before restarting.",
    )
    parser.add_argument(
        "--check-model",
        action="store_true",
        help="Explicitly check model metadata (one GET, no generation). Exit0 only for ready_for_attempt; other states2. Default is offline configured0/missing1; invalid settings2.",
    )
    args = parser.parse_args(argv)
    try:
        config = Settings()
    except ValidationError:
        # ValidationError text/errors can contain secret-bearing input values.
        print(
            ProviderReadiness(
                status="invalid_configuration",
                operation="model_metadata" if args.check_model else "configuration",
                message="Local settings are invalid. "
                + MODEL_CONFIGURATION_HELP
                + " Review numeric limits and origin settings server-side; no provider request was sent.",
            ).model_dump_json()
        )
        return 2
    report = (
        asyncio.run(check_model(config)) if args.check_model else configuration_readiness(config)
    )
    value = report.model_dump(mode="json") | {"model": config.pm_model}
    if not config.pm_configured:
        value.update(
            verdict="BLOCKED",
            missing=[
                name
                for name, present in [
                    (
                        "GEMINI_API_KEY or ORBA_PM_API_KEY",
                        bool(config.pm_api_key and config.pm_api_key.get_secret_value()),
                    ),
                    ("ORBA_PM_MODEL", bool(config.pm_model)),
                ]
                if not present
            ],
        )
    print(json.dumps(value))
    if args.check_model:
        return 0 if report.status == "ready_for_attempt" else 2
    return (0 if config.pm_configured else 1) if report.status != "invalid_configuration" else 2


if __name__ == "__main__":
    raise SystemExit(main())
