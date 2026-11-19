#!/usr/bin/env python3
"""Remove junk content from scraped novel files."""

import os
import shutil
from pathlib import Path


def clean_content(content):
    """Remove everything from 'Comments' onwards."""
    idx = content.find('\nComments\n')
    if idx == -1:
        idx = content.find('Comments\n')
    if idx == -1:
        idx = content.find('\nComments')
    if idx == -1:
        idx = content.find('Comments')

    if idx != -1:
        return content[:idx].rstrip() + '\n'
    return content


directory = Path('downloads/eternal-cultivation-of-alchemy')
backup_dir = directory.parent / f"{directory.name}_backup"

# Create backup
if backup_dir.exists():
    shutil.rmtree(backup_dir)
shutil.copytree(directory, backup_dir)

txt_files = sorted(directory.glob('*.txt'))
print(f"Processing {len(txt_files)} files...")

cleaned = 0
for filepath in txt_files:
    try:
        original = filepath.read_text(encoding='utf-8')
        cleaned_text = clean_content(original)

        if len(cleaned_text) != len(original):
            filepath.write_text(cleaned_text, encoding='utf-8')
            cleaned += 1
            if cleaned % 100 == 0:
                print(f"Cleaned {cleaned}...")
    except Exception as e:
        print(f"Error {filepath.name}: {e}")

print(f"\nDone! Cleaned {cleaned} files.")
print(f"Backup: {backup_dir}")