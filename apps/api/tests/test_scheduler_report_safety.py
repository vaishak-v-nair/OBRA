"""Exact credential redaction preserves real pytest failures and useful evidence."""

from types import SimpleNamespace
from uuid import uuid4

from tests.report_safety import WorkerHeaders, protect_report, redact


def test_worker_headers_keep_actual_authorization_but_redact_rendering():
    token = f"orba_wkr_{uuid4()}." + "a" * 43  # Isolated string, never a credential.
    headers = WorkerHeaders(Authorization="Bearer " + token)
    assert headers["Authorization"] == "Bearer " + token
    assert token not in repr(headers)
    assert "<redacted-worker-credential>" in repr(headers)


def test_failed_pytest_report_remains_failed_after_exact_credential_redaction():
    token = f"orba_wkr_{uuid4()}." + "b" * 43
    report = SimpleNamespace(
        outcome="failed",
        longrepr=f"E assert 201 == 503\nheaders={{'Authorization': 'Bearer {token}'}}",
        sections=[("Captured stdout call", f"rejected {token}; exit_code=1")],
        nodeid="actual_failure",
    )
    protect_report(report)
    assert report.outcome == "failed" and report.nodeid == "actual_failure"
    assert "assert 201 == 503" in report.longrepr
    assert token not in report.longrepr
    assert "exit_code=1" in report.sections[0][1]
    assert token not in report.sections[0][1]


def test_ordinary_diagnostics_and_identifiers_remain_unchanged():
    text = f"run_id={uuid4()}; snapshot_sha256={'c' * 64}; HTTP 503; failed"
    assert redact(text) == text
    report = SimpleNamespace(outcome="passed", longrepr=None, sections=[])
    protect_report(report)
    assert report.outcome == "passed" and report.longrepr is None
