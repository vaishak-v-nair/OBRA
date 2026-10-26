"""Isolated incorrect assertion: an expired claim must NOT publish a lease.

Run explicitly; real PostgreSQL fixture/API. Expected underlying pytest exit1.
Never part of the mandatory passing suite or an executor success record.
"""

from tests.scheduler_support import ready
from tests.test_scheduler_credential_races import blocked_until_expiry


def test_rejected_expired_claim_is_not_successful_publication(client):
    _, run, worker_id, _, _ = ready(client)
    response, _, _ = blocked_until_expiry(client, run, worker_id)
    assert response.status_code == 201, (
        "Deliberately incorrect: actual expired claim must return401."
    )
