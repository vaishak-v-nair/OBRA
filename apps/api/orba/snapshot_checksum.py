"""Shared canonical checksum without loading API services or a model SDK."""

import hashlib

from orba.pm_schemas import canonical


def checksum(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()
