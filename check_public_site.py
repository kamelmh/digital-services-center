#!/usr/bin/env python3
"""Dependency-free guard for the public GitHub Pages artifact (Guide S4)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

SENSITIVE_RE = re.compile(r"(\.env(\.|$)|\.db$|\.sqlite|\.pem$|\.key$|keys)", re.IGNORECASE)
# Also match literal substrings db/env/pem/keys as filenames; SENSITIVE_RE covers common cases.
SENSITIVE_SUBSTRINGS = (".env", ".pem", ".key", ".db", ".sqlite")
SENSITIVE_KEYWORDS = ("keys", "credentials", "secrets")

CREDENTIAL_PATTERNS = [
    (re.compile(r"sk-[A-Za-z0-9]{20,}"), "sk-"),
    (re.compile(r"gsk_[A-Za-z0-9]{20,}"), "gsk_"),
    (re.compile(r"AKIA[0-9A-Z]{16}"), "AKIA"),
    (re.compile(r"postgresql://\S+"), "postgresql://"),
    (re.compile(r"JWT_SECRET"), "JWT_SECRET"),
]

# Text extensions to scan; other files are still checked for filenames/symlinks.
TEXT_EXTS = {".html", ".htm", ".css", ".js", ".json", ".md", ".txt", ".yml", ".yaml", ".xml", ".svg", ".csv", ".toml", ".ini", ".cfg"}


def is_sensitive_filename(p: Path) -> str | None:
    name = p.name.lower()
    # direct substring checks for guide keywords
    for sub in SENSITIVE_SUBSTRINGS:
        if sub in name:
            return f"sensitive filename contains '{sub}'"
    for kw in SENSITIVE_KEYWORDS:
        if kw in name:
            return f"sensitive filename contains '{kw}'"
    if SENSITIVE_RE.search(name):
        return "sensitive filename pattern"
    return None


def scan(root: Path) -> list[str]:
    errors: list[str] = []
    if not root.exists():
        return [f"path not found: {root}"]
    for p in root.rglob("*"):
        # symlink check (file or dir)
        try:
            if p.is_symlink():
                errors.append(f"symlink: {p}")
                continue
        except OSError as e:
            errors.append(f"symlink check failed {p}: {e}")
            continue
        if p.is_dir():
            continue
        reason = is_sensitive_filename(p)
        if reason:
            errors.append(f"sensitive file: {p} ({reason})")
        # credential scan for text-ish files
        if p.suffix.lower() in TEXT_EXTS or p.suffix == "":
            try:
                if p.stat().st_size > 2_000_000:
                    continue
            except OSError:
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="strict")
            except (UnicodeDecodeError, OSError):
                continue
            for pat, label in CREDENTIAL_PATTERNS:
                if pat.search(text):
                    # report first match per file/pattern
                    for i, line in enumerate(text.splitlines(), 1):
                        if pat.search(line):
                            snippet = line.strip()[:160]
                            errors.append(f"credential pattern '{label}' in {p}:{i}: {snippet}")
                            break
        else:
            # still scan small text-like files with known ext
            if p.suffix.lower() in {".html", ".css", ".js"}:
                pass
    return errors


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs")
    errs = scan(root)
    if errs:
        print("check_public_site: FAIL", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"check_public_site: OK ({root})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
