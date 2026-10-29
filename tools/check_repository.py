#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Check public documentation links, component pins and publication boundaries."""
import json
from pathlib import Path
import re
import subprocess
import sys
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ['README.md', 'LICENSE', 'ATTRIBUTION.md', 'THIRD_PARTY_NOTICES.md',
            'docs/installation.md', 'docs/game-files.md', 'docs/display.md',
            'docs/controls.md', 'docs/troubleshooting.md', 'docs/technical-background.md',
            'docs/validation.md', 'docs/file-inventory.md', 'components/SHA256SUMS',
            'configs/Config.wtf', 'configs/gamenative-settings.json',
            'configs/controller-commands.txt', 'LICENSES/MIT.txt',
            'LICENSES/GPL-3.0.txt', 'LICENSES/CC-BY-4.0.txt']
FORBIDDEN_SUFFIXES = {'.apk', '.wcp', '.zip', '.gz', '.exe', '.dll', '.so', '.db', '.sqlite', '.png', '.jpg'}


def public_files():
    result = subprocess.run(['git', '-C', str(ROOT), 'ls-files', '--cached', '--others', '--exclude-standard'], capture_output=True, text=True)
    if result.returncode == 0:
        return sorted({ROOT / name for name in result.stdout.splitlines() if name})
    return sorted(p for p in ROOT.rglob('*') if p.is_file() and not any(
        part in {'.git', 'downloads', 'private', 'staging', '__pycache__'} for part in p.relative_to(ROOT).parts))


def check():
    errors = []
    for name in REQUIRED:
        if not (ROOT / name).is_file():
            errors.append(f'missing {name}')
    manifest = json.loads((ROOT / 'components/manifest.json').read_text())
    items = manifest['components']
    expected = ''.join(f'{i["sha256"]}  {i["filename"]}\n' for i in items)
    if (ROOT / 'components/SHA256SUMS').read_text() != expected:
        errors.append('SHA256SUMS differs from manifest')
    if len({x['id'] for x in items}) != len(items) or len({x['filename'] for x in items}) != len(items):
        errors.append('duplicate manifest entries')
    for item in items:
        if not re.fullmatch(r'[a-f0-9]{64}', item['sha256']) or not item['url'].startswith('https://'):
            errors.append(f'invalid pin: {item["id"]}')
    commands = (ROOT / 'configs/controller-commands.txt').read_text().splitlines()
    for line in commands:
        if line.startswith('/') and len(line) > 255:
            errors.append(f'controller command exceeds 255 characters ({len(line)})')
        if line and not line.startswith(('#', '/')):
            errors.append('unrecognized controller command line')
    for path in public_files():
        relative = path.relative_to(ROOT)
        if path.suffix.lower() in FORBIDDEN_SUFFIXES or any(part in {'Account', 'debug_reports', 'private', 'downloads', 'staging'} for part in relative.parts):
            errors.append(f'forbidden public artifact: {relative}')
        if path.is_symlink():
            errors.append(f'symlink in public tree: {relative}')
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeError:
            errors.append(f'non-text artifact: {relative}')
            continue
        patterns = [r'/Users/[A-Za-z0-9_.-]+/', r'192\.168\.\d+\.\d+',
                    r'CUSTOM_GAME_\d+', r'R5CX\w+',
                    r'(?im)^SET\s+(?:accountName|accountList)\s+"[^"\n]+"']
        if any(re.search(p, text) for p in patterns):
            errors.append(f'possible private identifier: {relative}')
        if path.suffix == '.md':
            for link in re.findall(r'\]\(([^)]+)\)', text):
                target = link.split('#', 1)[0]
                if not target or re.match(r'^[a-zA-Z][\w+.-]*:', target):
                    continue
                if not (path.parent / unquote(target)).exists():
                    errors.append(f'broken local link in {relative}: {link}')
    return errors


if __name__ == '__main__':
    failures = check()
    if failures:
        print('\n'.join(failures), file=sys.stderr)
        sys.exit(1)
    print('Repository checks passed: pins, local links, command lengths and public artifact boundaries.')
