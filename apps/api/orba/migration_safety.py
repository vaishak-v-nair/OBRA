"""Local offline-upgrade guard; never an authentication bypass."""

import socket


def require_stopped_api(port: int = 8000):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.5):
            raise RuntimeError(
                "Stop the local API before the Stage02 ownership migration. An old unauthenticated process must not serve the migrated database."
            )
    except OSError:
        return
