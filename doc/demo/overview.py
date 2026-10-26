"""
Example shown on the landing page.
"""

from __future__ import annotations


def fetch(url: str, timeout: float | None = None, *, retries: int = 3) -> bytes:
    """
    Fetch a resource.

    :param url: URL of the resource
    :param timeout: Seconds to wait for a response, or ``None`` to wait indefinitely
    :type timeout: float | None
    :param int retries: Number of attempts before giving up
    :returns: Content of the resource
    :raises TimeoutError: If no response was received in time
    :raises ConnectionError: If the server couldn't be reached
    """
    return b""
