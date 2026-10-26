"""
Examples of fields other than parameters.
"""

from __future__ import annotations


def raises(path: str) -> str:
    """
    Read a file.

    :param path: Path to the file
    :raises FileNotFoundError: If the file doesn't exist
    :raises PermissionError: If the file can't be read
    """
    with open(path) as fh:
        return fh.read()


def raises_single(value: str) -> int:
    """
    Parse an integer.

    :param value: Text to parse
    :raises ValueError: If ``value`` isn't an integer
    """
    return int(value)


class Connection:
    """
    Connection to a server.

    :param host: Server to connect to
    :ivar connected: Whether the connection is open
    :vartype connected: bool
    :ivar retries: Number of attempts made
    """

    connected: bool
    retries: int

    def __init__(self, host: str):
        self.connected = False
        self.retries = 0


def returns(values: list[int]) -> list[int]:
    """
    Sort values.

    :param values: Values to sort
    :returns: Sorted copy of ``values``
    :rtype: list[int]
    """
    return sorted(values)
