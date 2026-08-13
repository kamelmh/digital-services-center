"""HTML escaping utility for DSC generators.

Prevents XSS by escaping user input before inserting into HTML.
All generators should use _esc() on any user-provided text.
"""

import html


def _esc(value, default=""):
    """Escape HTML special characters. Returns default if value is falsy."""
    if value:
        return html.escape(str(value))
    return default


def _esc_blank(value, width=40):
    """Escape value or return dotted blank line."""
    if value:
        return html.escape(str(value))
    return "." * width
