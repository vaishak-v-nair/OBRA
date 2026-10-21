"""Bounded monotonic diagnostics. No inputs, credentials or provider bodies."""

import logging
from contextlib import contextmanager
from time import monotonic

logger = logging.getLogger("uvicorn.error.orba.pm_timing")


class RunTiming:
    def __init__(self):
        self.started = monotonic()
        self.run_id = None
        self.durations = {}

    @contextmanager
    def measure(self, stage):
        start = monotonic()
        try:
            yield
        finally:
            self.durations[stage] = round(max(0, monotonic() - start) * 1000, 3)

    def diagnostic(self, existing=None):
        return dict(existing or {}) | {
            "timing_version": 1,
            "attempt": 1,  # A new explicit request has its own run/UUID; no automatic retries.
            "timing_boundary": "before_terminal_commit",
            "elapsed_ms": round(max(0, monotonic() - self.started) * 1000, 3),
            "stages_ms": dict(self.durations),
        }

    def event(self, stage, state, category=None, provider_status=None):
        phase = {
            "admission_commit_acknowledged": "admission_transaction",
            "running_commit_acknowledged": "running_transaction",
            "provider_response_received": "provider_call",
            "output_validated": "validation",
            "publication_commit_acknowledged": "persistence_transaction",
        }.get(stage)
        logger.info(
            "pm_timing run_id=%s stage=%s elapsed_ms=%.3f stage_duration_ms=%s attempt=1 final_state=%s "
            "error_category=%s provider_http_status=%s",
            self.run_id or "-",
            stage,
            max(0, monotonic() - self.started) * 1000,
            self.durations.get(phase, "-"),
            state,
            category or "-",
            provider_status or "-",
        )
