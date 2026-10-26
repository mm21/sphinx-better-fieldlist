"""
Example rendered by each documentation generator.
"""

from __future__ import annotations


def resize(width: int, height: int | None = None, *, keep_ratio: bool = True) -> bool:
    """
    Resize the image.

    :param width: New width in pixels
    :param height: New height in pixels, or ``None`` to derive it from ``width``
    :param keep_ratio: Whether to preserve the aspect ratio
    :returns: Whether the image was changed
    """
    return True
