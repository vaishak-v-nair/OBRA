"""Redact exact ephemeral worker credentials without changing test outcomes."""

import re

WORKER_CREDENTIAL = re.compile(r"orba_wkr_[0-9a-fA-F-]{36}\.[A-Za-z0-9_-]{40,}")


def redact(value: str) -> str:
    return WORKER_CREDENTIAL.sub("<redacted-worker-credential>", value)


class WorkerHeaders(dict):
    def __repr__(self):
        return redact(super().__repr__())


def protect_report(report):
    # Retain normal pytest traceback formatting when no credential is present.
    # Never alter outcome, assertions, test identity, timing or failure status.
    if report.longrepr is not None:
        rendered = str(report.longrepr)
        if WORKER_CREDENTIAL.search(rendered):
            report.longrepr = redact(rendered)
    report.sections = [(name, redact(content)) for name, content in report.sections]
