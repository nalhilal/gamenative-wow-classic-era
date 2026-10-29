#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Merge only the documented WoW settings into a separate config file."""
import argparse
from pathlib import Path
import re
import sys

SETTINGS = {
    'gxApi': 'D3D11',
    'gxWindow': '1',
    'gxMaximize': '1',
    'gxWindowedResolution': '1560x720',
    'GamePadEnable': '1',
}
LINE = re.compile(r'^\s*SET\s+(\S+)\s+".*"\s*$', re.IGNORECASE)


def merge(text):
    remaining = {k.lower(): (k, v) for k, v in SETTINGS.items()}
    wanted = set(remaining)
    result = []
    for line in text.splitlines():
        match = LINE.match(line)
        key = match.group(1).lower() if match else None
        if key in wanted:
            if key in remaining:
                name, value = remaining.pop(key)
                result.append(f'SET {name} "{value}"')
        else:
            result.append(line)
    result.extend(f'SET {k} "{v}"' for k, v in remaining.values())
    return '\n'.join(result) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.input.resolve() == args.output.resolve():
        parser.error('input and output must differ')
    result = merge(args.input.read_text(encoding='utf-8-sig'))
    # No output of original file contents: they may contain personal settings.
    with args.output.open('x', encoding='utf-8', newline='\n') as output:
        output.write(result)
    print('Wrote merged config to a separate file. Keep the original as your backup.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        sys.exit(str(error))
