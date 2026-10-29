#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Fetch only the pinned public runtime/addon packages; never install them."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def fetch(item, destination, verify_only=False, opener=urllib.request.urlopen):
    destination = Path(destination)
    name = item['filename']
    if Path(name).name != name or '/' in name or '\\' in name:
        raise ValueError('unsafe component filename')
    target = destination / name
    if target.is_symlink():
        raise ValueError('refusing a symlink destination')
    if target.exists():
        if sha256(target) != item['sha256']:
            raise ValueError(f'{name}: existing file checksum mismatch; move it aside and retry')
        print(f'verified {name}')
        return target
    if verify_only:
        raise ValueError(f'{name}: missing')
    if not item['url'].startswith('https://'):
        raise ValueError('component download must use HTTPS')
    destination.mkdir(parents=True, exist_ok=True)
    partial = target.with_name(name + '.part')
    # Exclusive creation avoids clobbering another process or following a symlink.
    try:
        with partial.open('xb') as out:
            request = urllib.request.Request(item['url'], headers={'User-Agent': 'gamenative-wow-classic-era/1'})
            with opener(request, timeout=60) as source:
                for block in iter(lambda: source.read(1024 * 1024), b''):
                    out.write(block)
        if sha256(partial) != item['sha256']:
            raise ValueError(f'{name}: downloaded checksum mismatch')
        if target.exists():
            raise ValueError(f'{name}: destination appeared during download')
        partial.rename(target)
    except FileExistsError:
        raise ValueError(f'{name}: .part already exists; remove the stale partial file and retry')
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    print(f'downloaded and verified {name}')
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', type=Path, required=True)
    parser.add_argument('--verify-only', action='store_true')
    args = parser.parse_args()
    items = json.loads((ROOT / 'components/manifest.json').read_text())['components']
    for item in items:
        fetch(item, args.dest, args.verify_only)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        sys.exit(str(error))
