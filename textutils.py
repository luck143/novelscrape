#!/usr/bin/env python3
"""Shared text-cleaning utilities for NovelScrape.

Single source of truth for clean_text_content — used by combiner.py and
clean_epub_file.py. Do not copy this function into other files.
"""

import re

# Matches censored-swear patterns: 3+ single letters separated by dots,
# e.g. "f.u.c", "f.u.c.k", "s.h.i.t". Requires at least 3 letters so that
# legitimate abbreviations like "e.g" / "i.e" are NOT destroyed.
_CENSORED_PATTERN = re.compile(r'\b(?:[a-zA-Z]\.){2,}[a-zA-Z]\b')
_DOT_PLUS_PATTERN = re.compile(r'\.\+')


def clean_text_content(content):
    """Clean scraped text without damaging legitimate prose.

    Removes:
    1. Censored dotted-letter patterns (f.u.c.k -> f***, at least 3 letters)
    2. Literal ".+" artifacts left by some scrapers
    3. Multiple consecutive spaces
    4. Leading/trailing whitespace on each line
    5. Excessive blank lines (>2 consecutive newlines)

    Preserves normal punctuation: sentence periods, "e.g", "i.e", "Mr." etc.
    """
    content = _CENSORED_PATTERN.sub(
        lambda m: m.group(0).replace('.', ''), content
    )
    content = _DOT_PLUS_PATTERN.sub('', content)
    content = re.sub(r' +', ' ', content)
    lines = [line.strip() for line in content.split('\n')]
    content = '\n'.join(lines)
    content = re.sub(r'\n\n\n+', '\n\n', content)
    return content
