"""A single destructive-test boundary shared by all test and live verification entrypoints."""

from sqlalchemy.engine import make_url


def guard_test_url(url: str):
    parsed = make_url(url)
    if (
        parsed.drivername != "postgresql+psycopg"
        or parsed.host not in {"127.0.0.1", "localhost", "::1"}
        or parsed.port != 54330
        or parsed.database != "orba_test"
        or parsed.username != "orba_test"
    ):
        raise RuntimeError(
            "Refusing test mutation: require loopback:54330 with orba_test database and role."
        )
    return parsed
