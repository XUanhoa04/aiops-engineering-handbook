#!/usr/bin/env python3
"""Soft pastel Mermaid styles + collapse implementation code (ch08+) into <details>."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

FILL_MAP = {
    "#e94560": "#fecdd3",
    "#ff4444": "#fecaca",
    "#ff0000": "#fecaca",
    "#b71c1c": "#fecaca",
    "#c62828": "#fecaca",
    "#e65100": "#ffedd5",
    "#ef6c00": "#ffedd5",
    "#f57c00": "#ffedd5",
    "#ff6f00": "#ffedd5",
    "#1565c0": "#dbeafe",
    "#0d47a1": "#dbeafe",
    "#0d4f8b": "#dbeafe",
    "#0277bd": "#e0f2fe",
    "#01579b": "#e0f2fe",
    "#1a237e": "#e0e7ff",
    "#283593": "#e0e7ff",
    "#2e7d32": "#dcfce7",
    "#1b5e20": "#dcfce7",
    "#33691e": "#ecfccb",
    "#4a148c": "#f3e8ff",
    "#6a1b9a": "#f3e8ff",
    "#4a1942": "#fae8ff",
    "#880e4f": "#fce7f3",
    "#311b92": "#ede9fe",
    "#1a1a2e": "#e2e8f0",
    "#16213e": "#e2e8f0",
    "#0f3460": "#dbeafe",
    "#533483": "#ede9fe",
    "#2d3561": "#e0e7ff",
    "#7c3aed": "#ede9fe",
}

IMPL = {
    "python",
    "py",
    "yaml",
    "yml",
    "json",
    "jsonc",
    "bash",
    "sh",
    "shell",
    "go",
    "javascript",
    "js",
    "typescript",
    "ts",
    "sql",
    "promql",
    "logql",
    "hcl",
    "terraform",
    "dockerfile",
    "toml",
    "rust",
    "java",
    "kotlin",
    "powershell",
    "ps1",
    "console",
    "diff",
}


def expand_hex(h: str) -> str:
    h = h.lower()
    if len(h) == 4:
        return "#" + "".join(c * 2 for c in h[1:])
    return h


def soften_styles(text: str) -> str:
    def repl(m: re.Match) -> str:
        s = m.group(0)
        fm = re.search(r"fill:(#[0-9A-Fa-f]{3,8})", s, re.I)
        if not fm:
            return s
        fill = expand_hex(fm.group(1))
        new_fill = FILL_MAP.get(fill)
        if not new_fill:
            try:
                r, g, b = int(fill[1:3], 16), int(fill[3:5], 16), int(fill[5:7], 16)
                if (r + g + b) / 3 < 110:
                    new_fill = "#e2e8f0"
                else:
                    return s
            except Exception:
                return s
        s = re.sub(r"fill:#[0-9A-Fa-f]{3,8}", f"fill:{new_fill}", s, flags=re.I)
        s = re.sub(r"color:#fff\b", "color:#1e293b", s, flags=re.I)
        s = re.sub(r"color:#ffffff\b", "color:#1e293b", s, flags=re.I)
        return s

    return re.sub(
        r"style\s+\w+\s+fill:#[0-9A-Fa-f]{3,8}(?:,[^\n]*)?",
        repl,
        text,
        flags=re.I,
    )


def strip_our_details(text: str) -> str:
    return re.sub(
        r"<details>\s*\n<summary><strong>See the code below.*?</strong></summary>\s*\n+"
        r"(```[\s\S]*?```)\s*\n*</details>\s*",
        r"\1\n\n",
        text,
    )


def wrap_impl_code(text: str, ui: str) -> str:
    text = strip_our_details(text)
    lines = text.replace("\r\n", "\n").split("\n")
    summary = (
        "See the code below — bấm để xem code (đọc concept trước)"
        if ui == "vi"
        else "See the code below — click to expand (read concepts first)"
    )
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            info = line[3:].strip()
            lang = info.split()[0].lower() if info else ""
            start = i
            i += 1
            while i < len(lines) and not re.match(r"^```\s*$", lines[i]):
                i += 1
            if i < len(lines):
                i += 1
            block = lines[start:i]
            if lang in IMPL:
                out.append("<details>")
                out.append(f"<summary><strong>{summary}</strong></summary>")
                out.append("")
                out.extend(block)
                out.append("")
                out.append("</details>")
            else:
                out.extend(block)
            continue
        out.append(line)
        i += 1
    new = "\n".join(out)
    if not new.endswith("\n"):
        new += "\n"
    return new


def chapter_num(path: Path) -> int | None:
    for p in path.parts:
        m = re.match(r"^(\d{2})-", p)
        if m:
            return int(m.group(1))
    return None


def main() -> None:
    n_soft = n_wrap = 0
    for path in sorted(DOCS.rglob("*.md")):
        if path.name in {"extra.css"}:
            continue
        original = path.read_text(encoding="utf-8")
        text = soften_styles(original)
        soft_changed = text != original

        num = chapter_num(path)
        if num is not None and num >= 8:
            ui = "vi" if "vi" in path.parts else "en"
            wrapped = wrap_impl_code(text, ui)
            if wrapped != text:
                n_wrap += 1
            text = wrapped

        if text != original:
            path.write_text(text, encoding="utf-8")
            n_soft += 1
            print(("soft+wrap" if soft_changed else "wrap"), path.relative_to(ROOT))
    print(f"done files_changed={n_soft} wrap_ops={n_wrap}")


if __name__ == "__main__":
    main()
