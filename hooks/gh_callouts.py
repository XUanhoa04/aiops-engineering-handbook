"""
MkDocs hook: convert GitHub-flavored alerts to Material admonitions.

Source markdown stays as:

    > [!NOTE]
    > **KEY IDEA**
    > body...

GitHub continues to render native alerts. At MkDocs build time we rewrite to:

    !!! note "KEY IDEA"
        body...

so the site gets colored callout boxes instead of raw `[!NOTE]` text.
"""

from __future__ import annotations

import re
from typing import Match

# GitHub alert type → Material admonition type
ALERT_MAP = {
    "NOTE": "note",
    "TIP": "tip",
    "IMPORTANT": "important",
    "WARNING": "warning",
    "CAUTION": "warning",
    "DANGER": "danger",
}

# Match a GFM alert block: > [!TYPE] optional title on same line, then > body lines
_ALERT_RE = re.compile(
    r"^> \[!(NOTE|TIP|IMPORTANT|WARNING|CAUTION|DANGER)\][^\n]*\n"
    r"((?:^>.*\n?)*)",
    re.MULTILINE | re.IGNORECASE,
)


def _strip_blockquote_prefix(line: str) -> str:
    if line.startswith("> "):
        return line[2:]
    if line.startswith(">"):
        return line[1:]
    return line


def _convert_block(match: Match[str]) -> str:
    kind = match.group(1).upper()
    adm = ALERT_MAP.get(kind, "note")
    raw_body = match.group(2) or ""

    lines = [_strip_blockquote_prefix(ln) for ln in raw_body.splitlines()]
    # Drop trailing empty lines
    while lines and not lines[-1].strip():
        lines.pop()
    # Drop leading empty lines
    while lines and not lines[0].strip():
        lines.pop(0)

    content = "\n".join(lines).strip()
    title = ""

    # Optional first line as bold title: **Ý TƯỞNG** / **KEY IDEA** / **Why**
    title_m = re.match(r"^\*\*([^*]+)\*\*\s*(?:\n|$)", content)
    if title_m:
        title = title_m.group(1).strip()
        content = content[title_m.end() :].lstrip("\n").strip()

    if not content and title:
        # Title-only callout — keep title as body
        content = title
        title = ""

    # Indent body for admonition (4 spaces)
    if content:
        indented = "\n".join(
            ("    " + line) if line.strip() else "    " for line in content.splitlines()
        )
    else:
        indented = "    "

    if title:
        # Escape quotes in title for attribute string
        safe_title = title.replace('"', "'")
        return f'!!! {adm} "{safe_title}"\n{indented}\n\n'
    return f"!!! {adm}\n{indented}\n\n"


# Soften remaining harsh Mermaid fills at build time (pastel + dark text)
_HARSH_FILLS = {
    "#e94560": "#fecdd3",
    "#ff4444": "#fecaca",
    "#b71c1c": "#fecaca",
    "#e65100": "#ffedd5",
    "#1565c0": "#dbeafe",
    "#2e7d32": "#dcfce7",
    "#4a148c": "#f3e8ff",
    "#0d4f8b": "#dbeafe",
    "#1a1a2e": "#e2e8f0",
    "#533483": "#ede9fe",
}


def _soften_mermaid(markdown: str) -> str:
    def repl(m: re.Match) -> str:
        s = m.group(0)
        for old, new in _HARSH_FILLS.items():
            s = re.sub(re.escape(old), new, s, flags=re.I)
        s = re.sub(r"color:#fff\b", "color:#1e293b", s, flags=re.I)
        s = re.sub(r"color:#ffffff\b", "color:#1e293b", s, flags=re.I)
        return s

    return re.sub(
        r"style\s+\w+\s+fill:#[0-9A-Fa-f]{3,8}(?:,[^\n]*)?",
        repl,
        markdown,
        flags=re.I,
    )


def on_page_markdown(markdown: str, **kwargs) -> str:
    """MkDocs page hook entrypoint."""
    markdown = _soften_mermaid(markdown)
    if "[!" not in markdown:
        return markdown
    return _ALERT_RE.sub(_convert_block, markdown)
