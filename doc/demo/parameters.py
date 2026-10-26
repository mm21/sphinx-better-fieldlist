"""
Examples of parameters.
"""

from __future__ import annotations

import os


def names_only(path: str, mode: str = "r"):
    """
    Open a file.

    :param path: Path to the file
    :param mode: Mode in which to open it
    """


def explicit_types(timeout, retries, callback):
    """
    Connect to a server.

    :param timeout: Seconds to wait
    :type timeout: float
    :param int retries: Number of attempts
    :param callback: Called once connected
    """


def single(path: str) -> bool:
    """
    Check whether a path exists.

    :param path: Path to check
    """
    return os.path.exists(path)


def multi_paragraph(text: str, width: int = 88):
    """
    Wrap text.

    :param text: Text to wrap.

        Paragraphs are separated by blank lines, which are preserved.
    :param width: Maximum line width; may be:

        - a positive number of characters
        - ``0`` to disable wrapping
    """
