"""Google Earth Engine initialization for AGROINTEL AI.

Project is registered for non-commercial use. Credentials themselves
live in ~/.config/earthengine/credentials (created by `ee.Authenticate()`,
run once per machine) — nothing secret is stored in this repo.
"""

from __future__ import annotations

import os

import ee

EE_PROJECT_ID = "nasa-space-apps-513601"

_initialized = False


def init() -> None:
    """Initialize Earth Engine once per process.

    Also works around a common macOS python.org install issue where
    Python's SSL module can't find the system certificate store,
    which otherwise breaks Earth Engine's HTTPS calls.
    """
    global _initialized
    if _initialized:
        return

    if "SSL_CERT_FILE" not in os.environ:
        try:
            import certifi

            os.environ["SSL_CERT_FILE"] = certifi.where()
        except ImportError:
            pass

    ee.Initialize(project=EE_PROJECT_ID)
    _initialized = True
