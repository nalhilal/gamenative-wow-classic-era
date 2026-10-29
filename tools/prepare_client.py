#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""Stage matching Classic Era Windows ARM64 binaries from Blizzard metadata.

Adapted from jaredgei/wow-forever-android tools/download_wow_arm64.py,
revision 7e81372b2d1176035572e149a6b18ca6857d40cc (GPL-3.0).
Changes by nalhilal: explicit Era selection, CLI, bounded/checked parsing and
downloads, staging-only output, dry-run, path checks and tests.
See LICENSES/GPL-3.0.txt and ATTRIBUTION.md. No game data is distributed here.
"""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import struct
import sys
import urllib.error
import urllib.request
import zlib

PRODUCT = 'wow_classic_era'
FLAVOR = '_classic_era_'
LIMIT = 512 * 1024 * 1024
KEY = re.compile(r'^[0-9a-f]{32}$')


def md5(data):
    return hashlib.md5(data).hexdigest()


def verify_arm64_pe(data):
    if len(data) < 64 or data[:2] != b'MZ':
        raise ValueError('main executable is not a PE file')
    offset = int.from_bytes(data[60:64], 'little')
    if offset + 6 > len(data) or data[offset:offset + 4] != b'PE\0\0':
        raise ValueError('main executable has an invalid PE header')
    if int.from_bytes(data[offset + 4:offset + 6], 'little') != 0xaa64:
        raise ValueError('main executable is not native ARM64 (PE machine 0xaa64)')


def active_row(path):
    lines = Path(path).read_text(encoding='utf-8-sig').splitlines()
    if not lines:
        raise ValueError('empty .build.info')
    header = [h.split('!')[0] for h in lines[0].split('|')]
    if len(header) != len(set(header)):
        raise ValueError('duplicate .build.info columns')
    rows = [dict(zip(header, line.split('|'))) for line in lines[1:] if line.strip()]
    matches = [r for r in rows if r.get('Active') == '1' and r.get('Product') == PRODUCT]
    if len(matches) != 1:
        raise ValueError('expected exactly one active wow_classic_era row; update/install Classic Era in Battle.net')
    row = matches[0]
    for name in ('Build Key', 'CDN Key'):
        if not KEY.fullmatch(row.get(name, '')):
            raise ValueError(f'invalid {name}')
    if row.get('CDN Path') != 'tpr/wow':
        raise ValueError('unsupported CDN path')
    return row


def safe_name(name):
    name = name.replace('\\', '/')
    p = PurePosixPath(name)
    if not name or p.is_absolute() or any(x in ('', '.', '..') for x in name.split('/')):
        raise ValueError('unsafe install-manifest path')
    if any(':' in x or any(ord(c) < 32 for c in x) for x in p.parts):
        raise ValueError('unsafe install-manifest path')
    if p.parts[0].startswith('_') and p.parts[0] != FLAVOR:
        raise ValueError('unexpected game flavor in install manifest')
    return p


def read_config(text):
    return {k.strip(): v.strip().split() for k, v in
            (line.split('=', 1) for line in text.splitlines()
             if '=' in line and not line.lstrip().startswith('#'))}


def decode_chunk(chunk):
    if not chunk:
        raise ValueError('empty BLTE chunk')
    mode, body = chunk[:1], chunk[1:]
    if mode == b'N':
        return body
    if mode == b'Z':
        decoder = zlib.decompressobj()
        result = decoder.decompress(body, LIMIT + 1)
        if len(result) > LIMIT or not decoder.eof:
            raise ValueError('oversize or incomplete zlib chunk')
        return result
    # Nested/encrypted forms are deliberately unsupported instead of guessed.
    raise ValueError(f'unsupported BLTE mode {mode!r}')


def blte_decode(data):
    if len(data) < 9 or data[:4] != b'BLTE':
        raise ValueError('invalid BLTE header')
    header_size = struct.unpack('>I', data[4:8])[0]
    if header_size == 0:
        return decode_chunk(data[8:])
    if len(data) < 12 or data[8] != 0x0f:
        raise ValueError('invalid BLTE table')
    count = int.from_bytes(data[9:12], 'big')
    if header_size != 12 + count * 24 or header_size > len(data):
        raise ValueError('invalid BLTE table size')
    out = bytearray()
    offset = header_size
    for i in range(count):
        pos = 12 + i * 24
        comp, decomp = struct.unpack('>II', data[pos:pos + 8])
        if not comp or offset + comp > len(data) or len(out) + decomp > LIMIT:
            raise ValueError('invalid BLTE chunk size')
        chunk = data[offset:offset + comp]
        if hashlib.md5(chunk).digest() != data[pos + 8:pos + 24]:
            raise ValueError('BLTE chunk checksum mismatch')
        decoded = decode_chunk(chunk)
        if len(decoded) != decomp:
            raise ValueError('BLTE decoded size mismatch')
        out.extend(decoded)
        offset += comp
    if offset != len(data):
        raise ValueError('unexpected trailing BLTE data')
    return bytes(out)


def parse_install(data):
    if len(data) < 10 or data[:2] != b'IN' or data[3] != 16:
        raise ValueError('invalid install manifest')
    tag_count, entry_count = struct.unpack('>HI', data[4:10])
    mask_len = (entry_count + 7) // 8
    if entry_count > 1000000:
        raise ValueError('too many install entries')
    pos, tags = 10, {}
    for _ in range(tag_count):
        end = data.index(b'\0', pos)
        name = data[pos:end].decode('utf-8')
        pos = end + 3
        if pos + mask_len > len(data):
            raise ValueError('truncated install tag')
        tags[name] = data[pos:pos + mask_len]
        pos += mask_len
    entries = []
    for i in range(entry_count):
        end = data.index(b'\0', pos)
        name = data[pos:end].decode('utf-8')
        pos = end + 1
        if pos + 20 > len(data):
            raise ValueError('truncated install entry')
        ckey = data[pos:pos + 16].hex()
        size = int.from_bytes(data[pos + 16:pos + 20], 'big')
        pos += 20
        entry_tags = {t for t, m in tags.items() if m[i // 8] & (0x80 >> (i % 8))}
        entries.append((name, ckey, size, entry_tags))
    return entries


def select_files(entries):
    files = {}
    seen = set()
    for name, ckey, size, tags in entries:
        if not {'Windows', 'arm64'} <= tags or 'x86_64' in tags:
            continue
        p = safe_name(name)
        if p.suffix.lower() not in ('.exe', '.dll'):
            continue
        # Install-manifest paths are relative to the selected product folder,
        # including nested Utils paths, not the shared WoW installation root.
        if p.parts[0] != FLAVOR:
            p = PurePosixPath(FLAVOR) / p
        # Blizzard uses both UTILS and Utils in the same Windows manifest.
        # Merge that directory on case-sensitive Android/Unix staging volumes.
        p = PurePosixPath(*(('Utils' if i == 1 and part.casefold() == 'utils' else part)
                            for i, part in enumerate(p.parts)))
        normalized = str(p)
        if normalized.casefold() in seen:
            raise ValueError('duplicate or case-colliding ARM64 paths')
        seen.add(normalized.casefold())
        files[normalized] = (ckey, size)
    if f'{FLAVOR}/WowClassic-arm64.exe'.casefold() not in seen:
        raise ValueError('no Classic Era Windows ARM64 executable in this build')
    return files


def ckeys_to_ekeys(data, wanted):
    if len(data) < 22 or data[:2] != b'EN' or data[3:5] != b'\x10\x10':
        raise ValueError('unsupported encoding manifest')
    page_size = int.from_bytes(data[5:7], 'big') * 1024
    page_count = int.from_bytes(data[9:13], 'big')
    start = 22 + int.from_bytes(data[18:22], 'big') + page_count * 32
    if not page_size or start + page_count * page_size > len(data):
        raise ValueError('truncated encoding manifest')
    found = {}
    for page in range(page_count):
        pos = start + page * page_size
        end = pos + page_size
        while pos < end:
            count = data[pos]
            if not count:
                break
            if pos + 22 + count * 16 > end:
                raise ValueError('truncated encoding entry')
            ckey = data[pos + 6:pos + 22].hex()
            if ckey in wanted:
                found[ckey] = data[pos + 22:pos + 38].hex()
            pos += 22 + count * 16
    if wanted - found.keys():
        raise ValueError('ARM64 content keys missing from encoding manifest')
    return found


class CDN:
    def __init__(self, row):
        hosts = row.get('CDN Hosts', '').split()
        allowed = [h for h in hosts if re.fullmatch(r'[a-zA-Z0-9.-]+', h)
                   and (h.endswith('.blizzard.com') or h.endswith('.battle.net'))]
        if not allowed:
            raise ValueError('no recognized Blizzard CDN host')
        self.base = 'https://' + allowed[0] + '/tpr/wow'

    def fetch(self, kind, key, byte_range=None):
        base_key = key.removesuffix('.index')
        if kind not in ('data', 'config') or not KEY.fullmatch(base_key):
            raise ValueError('invalid CDN key')
        url = f'{self.base}/{kind}/{key[:2]}/{key[2:4]}/{key}'
        request = urllib.request.Request(url, headers={'User-Agent': 'gamenative-wow-classic-era/1'})
        if byte_range:
            offset, size = byte_range
            if offset < 0 or not 0 < size <= LIMIT:
                raise ValueError('invalid archive range')
            request.add_header('Range', f'bytes={offset}-{offset + size - 1}')
        with urllib.request.urlopen(request, timeout=45) as response:
            if byte_range and (response.status != 206 or not response.headers.get('Content-Range', '').startswith(f'bytes {offset}-{offset + size - 1}/')):
                raise ValueError('CDN did not honor the requested byte range')
            limit = size if byte_range else LIMIT
            content = response.read(limit + 1)
            if len(content) > limit or (byte_range and len(content) != size):
                raise ValueError('CDN response size mismatch')
        return content

    def config(self, key):
        data = self.fetch('config', key)
        if md5(data) != key:
            raise ValueError('CDN config checksum mismatch')
        return read_config(data.decode('utf-8'))

    def decoded(self, ekey, ckey, byte_range=None):
        # For ranges, ekey is the containing archive; decoded CKey is authoritative.
        data = blte_decode(self.fetch('data', ekey, byte_range))
        if md5(data) != ckey:
            raise ValueError('Blizzard content checksum mismatch')
        return data


def locate_in_archives(cdn, install_dir, archives, wanted):
    found = {}
    for archive in archives:
        if not KEY.fullmatch(archive):
            raise ValueError('invalid archive key')
        path = install_dir / 'Data/indices' / f'{archive}.index'
        data = path.read_bytes() if path.exists() else cdn.fetch('data', archive + '.index')
        for block in range(0, len(data) // 4096 * 4096, 4096):
            for pos in range(block, block + 4096 - 23, 24):
                ekey = data[pos:pos + 16].hex()
                if ekey in wanted:
                    size, offset = struct.unpack('>II', data[pos + 16:pos + 24])
                    if 0 < size <= LIMIT:
                        found[ekey] = (archive, offset, size)
        if wanted <= found.keys():
            break
    return found


def prepare(install_dir, output, dry_run=False):
    install_dir, output = Path(install_dir).resolve(), Path(output).resolve()
    if output == install_dir or output in install_dir.parents or install_dir in output.parents:
        raise ValueError('staging directory must be separate from the source installation')
    if output.exists():
        raise ValueError('output must not already exist; choose a new staging directory')
    row = active_row(install_dir / '.build.info')
    print(f'Product {PRODUCT}, build {row.get("Version", "unknown")}')
    cdn = CDN(row)
    build = cdn.config(row['Build Key'])
    install_keys, encoding_keys = build['install'], build['encoding']
    entries = parse_install(cdn.decoded(install_keys[1], install_keys[0]))
    files = select_files(entries)
    print(f'Found {len(files)} Windows ARM64 EXE/DLL files ({sum(v[1] for v in files.values())} decoded bytes)')
    for name in files:
        print(name)
    if dry_run:
        print('Dry-run: inspected build/install metadata only; no output or game files written.')
        return
    encoding = cdn.decoded(encoding_keys[1], encoding_keys[0])
    ekeys = ckeys_to_ekeys(encoding, {v[0] for v in files.values()})
    archives = cdn.config(row['CDN Key'])['archives']
    locations = None
    # Verify every payload before creating the staging tree. Source is always read-only.
    verified = {}
    for name, (ckey, expected_size) in files.items():
        ekey = ekeys[ckey]
        try:
            content = cdn.decoded(ekey, ckey)
        except urllib.error.HTTPError as error:
            # Packed-only payloads can be reported as forbidden or missing by
            # Blizzard's edge. Only this loose-payload lookup falls back.
            if error.code not in (403, 404):
                raise
            if locations is None:
                locations = locate_in_archives(cdn, install_dir, archives, set(ekeys.values()))
            if ekey not in locations:
                raise ValueError(f'{name}: encoded payload not located in CDN archives') from error
            archive, offset, size = locations[ekey]
            content = cdn.decoded(archive, ckey, (offset, size))
        if len(content) != expected_size:
            raise ValueError(f'{name}: decoded file size mismatch')
        if name.casefold() == f'{FLAVOR}/WowClassic-arm64.exe'.casefold():
            verify_arm64_pe(content)
        verified[name] = content
        print(f'Verified {name}', flush=True)
    output.mkdir(parents=True, exist_ok=False)
    for name, content in verified.items():
        destination = output.joinpath(*safe_name(name).parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)
    (output / 'preparation.json').write_text(json.dumps({
        'product': PRODUCT, 'version': row.get('Version'),
        'build_key': row['Build Key'],
        'files': {n: {'content_md5': files[n][0], 'sha256': hashlib.sha256(c).hexdigest()}
                  for n, c in verified.items()},
    }, indent=2) + '\n')
    print('Staging complete. Overlay these _classic_era_ files onto a COPY of the SAME source installation.')
    print('Transfer that copy including Data, .build.info and _classic_era_. Do not mix builds.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    prepare(args.install_dir, args.output, args.dry_run)


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, IndexError, struct.error, zlib.error) as error:
        sys.exit(f'Preparation failed: {error} {getattr(error, "url", "")}'.rstrip())
