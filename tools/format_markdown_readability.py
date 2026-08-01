"""Split dense Markdown prose into readable paragraphs without touching syntax blocks.

The formatter is intentionally conservative: it only rewrites top-level prose blocks
that exceed the configured size and contain usable sentence boundaries. Code fences,
tables, lists, headings, blockquotes, HTML, images, and indented content are preserved.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


SPECIAL_PREFIXES = ("#", ">", "|", "- ", "* ", "+ ", "    ", "<", "![", "---")
SENTENCE_END = re.compile(r"(?<=[.!?…])(?:[\"”’')\]]*)\s+(?=[A-ZÀ-Ỹ0-9*`])")
STANDALONE_SUBHEAD = re.compile(r"^\*\*[^*]+\*\*[:：]?\s*$")


def is_special(line: str) -> bool:
    stripped = line.lstrip()
    return (
        not line.strip()
        or line.startswith(SPECIAL_PREFIXES)
        or bool(re.match(r"^[-*+]\s", stripped))
        or bool(re.match(r"^\d+[.)]\s", stripped))
        or bool(STANDALONE_SUBHEAD.match(stripped))
    )


def split_prose(lines: list[str], target: int, maximum: int) -> list[str]:
    text = " ".join(line.strip() for line in lines)
    if len(text) <= maximum:
        return lines

    sentences = SENTENCE_END.split(text)
    if len(sentences) < 2:
        return lines

    chunks: list[str] = []
    current = ""
    for sentence in sentences:
        candidate = f"{current} {sentence}".strip()
        if current and len(candidate) > target:
            chunks.append(current)
            current = sentence
        else:
            current = candidate
    if current:
        chunks.append(current)

    if len(chunks) < 2:
        return lines
    return [line for index, chunk in enumerate(chunks) for line in (("" if index else None), chunk) if line is not None]


def format_markdown(content: str, target: int, maximum: int) -> tuple[str, int]:
    source = content.splitlines()
    output: list[str] = []
    paragraph: list[str] = []
    in_fence = False
    changes = 0

    def flush() -> None:
        nonlocal changes
        if not paragraph:
            return
        formatted = split_prose(paragraph, target, maximum)
        if formatted != paragraph:
            changes += 1
        output.extend(formatted)
        paragraph.clear()

    for line in source:
        if line.startswith(("```", "~~~")):
            flush()
            in_fence = not in_fence
            output.append(line)
            continue
        if in_fence or is_special(line):
            flush()
            output.append(line)
            continue
        paragraph.append(line)
    flush()

    spaced: list[str] = []
    for index, line in enumerate(output):
        is_subhead = bool(STANDALONE_SUBHEAD.match(line))
        if is_subhead and spaced and spaced[-1].strip():
            spaced.append("")
            changes += 1
        spaced.append(line)
        if is_subhead and index + 1 < len(output) and output[index + 1].strip():
            spaced.append("")
            changes += 1

    suffix = "\n" if content.endswith("\n") else ""
    return "\n".join(spaced) + suffix, changes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--target", type=int, default=390)
    parser.add_argument("--maximum", type=int, default=580)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    total = 0
    for path in args.paths:
        original = path.read_text(encoding="utf-8")
        formatted, changes = format_markdown(original, args.target, args.maximum)
        total += changes
        if changes and args.apply:
            path.write_text(formatted, encoding="utf-8", newline="\n")
        print(f"{path}: {changes} readability edit(s)")
    print(f"Total: {total} readability edit(s){' applied' if args.apply else ' found'}")


if __name__ == "__main__":
    main()
