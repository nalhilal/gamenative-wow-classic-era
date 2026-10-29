# SPDX-License-Identifier: MIT
import hashlib
import io
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import shutil
import subprocess
from unittest.mock import patch
import urllib.error
import zlib

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import fetch_components as download
import merge_config
import prepare_client as client


class Downloads(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dest = Path(self.tmp.name)
        self.data = b'public test payload'
        self.item = {'filename': 'component.zip', 'url': 'https://example.invalid/component.zip',
                     'sha256': hashlib.sha256(self.data).hexdigest()}

    def test_download_and_reuse(self):
        target = download.fetch(self.item, self.dest, opener=lambda *a, **k: io.BytesIO(self.data))
        self.assertEqual(target.read_bytes(), self.data)
        download.fetch(self.item, self.dest, verify_only=True,
                       opener=lambda *a, **k: self.fail('network called for an existing verified file'))

    def test_bad_download_leaves_no_final_or_partial(self):
        with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
            download.fetch(self.item, self.dest, opener=lambda *a, **k: io.BytesIO(b'changed'))
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_changed_existing_and_missing(self):
        with self.assertRaisesRegex(ValueError, 'missing'):
            download.fetch(self.item, self.dest, verify_only=True)
        p = self.dest / self.item['filename']
        p.write_bytes(b'bad')
        with self.assertRaisesRegex(ValueError, 'existing file checksum mismatch'):
            download.fetch(self.item, self.dest)
        self.assertEqual(p.read_bytes(), b'bad')

    def test_interrupted_download_cleaned(self):
        class Broken(io.BytesIO):
            def read(self, *args):
                raise OSError('interrupted')
        with self.assertRaises(OSError):
            download.fetch(self.item, self.dest, opener=lambda *a, **k: Broken())
        self.assertEqual(list(self.dest.iterdir()), [])

    def test_stale_partial_not_overwritten(self):
        partial = self.dest / 'component.zip.part'
        partial.write_bytes(b'keep')
        with self.assertRaisesRegex(ValueError, '.part already exists'):
            download.fetch(self.item, self.dest)
        self.assertEqual(partial.read_bytes(), b'keep')

    def test_unsafe_filename(self):
        for name in ('../outside.zip', '/outside.zip', 'folder\\outside.zip'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                download.fetch(dict(self.item, filename=name), self.dest)


class ConfigMerge(unittest.TestCase):
    def test_preserves_unrelated_and_removes_duplicate_target_keys(self):
        source = '# comment\r\nSET gxApi "D3D12"\r\nSET GxApi "Metal"\r\nSET soundVolume "0.4"\r\n'
        result = merge_config.merge(source)
        self.assertEqual(result.count('SET gxApi '), 1)
        self.assertIn('SET gxApi "D3D11"', result)
        self.assertIn('SET soundVolume "0.4"', result)
        self.assertTrue(result.startswith('# comment\n'))
        self.assertEqual(merge_config.merge(result), result)

    def test_empty_config(self):
        self.assertEqual(len(merge_config.merge('').splitlines()), 5)

    def test_cli_refuses_same_or_existing_output(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'Config.wtf'
            path.write_text('private original')
            with patch.object(sys, 'argv', ['merge', '--input', str(path), '--output', str(path)]):
                with self.assertRaises(SystemExit):
                    merge_config.main()
            other = Path(folder) / 'other.wtf'
            other.write_text('keep')
            with patch.object(sys, 'argv', ['merge', '--input', str(path), '--output', str(other)]):
                with self.assertRaises(FileExistsError):
                    merge_config.main()
            self.assertEqual(path.read_text(), 'private original')
            self.assertEqual(other.read_text(), 'keep')


class ClientMetadata(unittest.TestCase):
    def write_build(self, directory, rows):
        p = Path(directory) / '.build.info'
        header = 'Product!STRING:0|Active!DEC:1|Version!STRING:0|Build Key!HEX:16|CDN Key!HEX:16|CDN Hosts!STRING:0|CDN Path!STRING:0\n'
        p.write_text(header + '\n'.join(f'{product}|1|1.15.9.test|{"a"*32}|{"b"*32}|level3.blizzard.com|tpr/wow' for product in rows) + '\n')
        return p

    def test_selects_era_instead_of_first_active_forever(self):
        with tempfile.TemporaryDirectory() as folder:
            row = client.active_row(self.write_build(folder, ['wowf', 'wow_classic_era']))
            self.assertEqual(row['Product'], 'wow_classic_era')

    def test_missing_and_ambiguous_product(self):
        with tempfile.TemporaryDirectory() as folder:
            for products in (['wowf'], ['wow_classic_era', 'wow_classic_era']):
                with self.subTest(products=products), self.assertRaises(ValueError):
                    client.active_row(self.write_build(folder, products))

    def test_safe_paths(self):
        for name in ('../escape.exe', '/escape.exe', 'C:\\escape.exe', 'a//b.dll', '_retail_/x.exe', 'a/../b.exe'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                client.safe_name(name)
        self.assertEqual(str(client.safe_name('Utils\\helper.dll')), 'Utils/helper.dll')

    def test_filters_architecture_and_requires_era_exe(self):
        era = ('_classic_era_/WowClassic-arm64.exe', 'a' * 32, 100, {'Windows', 'arm64'})
        x64 = ('_classic_era_/WowClassic.exe', 'b' * 32, 100, {'Windows', 'x86_64'})
        self.assertEqual(list(client.select_files([era, x64])), [era[0]])
        with self.assertRaisesRegex(ValueError, 'no Classic Era'):
            client.select_files([x64])
        with self.assertRaisesRegex(ValueError, 'case-colliding'):
            client.select_files([era, (era[0].replace('WowClassic', 'WOWCLASSIC'), *era[1:])])

    def test_pe_machine(self):
        data = bytearray(128)
        data[:2] = b'MZ'
        data[60:64] = (64).to_bytes(4, 'little')
        data[64:70] = b'PE\0\0' + (0xaa64).to_bytes(2, 'little')
        client.verify_arm64_pe(bytes(data))
        data[68:70] = (0x8664).to_bytes(2, 'little')
        with self.assertRaisesRegex(ValueError, 'not native ARM64'):
            client.verify_arm64_pe(bytes(data))

    def test_nested_support_files_are_inside_era_and_utils_case_is_merged(self):
        tags = {'Windows', 'arm64'}
        entries = [('WowClassic-arm64.exe', 'a' * 32, 100, tags),
                   ('Utils\\BlizzardBrowser.exe', 'b' * 32, 200, tags),
                   ('UTILS\\LIBCEF.DLL', 'c' * 32, 300, tags),
                   ('Utils\\swiftshader\\libEGL.dll', 'd' * 32, 400, tags)]
        files = client.select_files(entries)
        self.assertEqual(set(files), {'_classic_era_/WowClassic-arm64.exe',
                         '_classic_era_/Utils/BlizzardBrowser.exe',
                         '_classic_era_/Utils/LIBCEF.DLL',
                         '_classic_era_/Utils/swiftshader/libEGL.dll'})

    def test_install_manifest_parser(self):
        name = b'_classic_era_/WowClassic-arm64.exe\0'
        tags = b'Windows\0\0\0\x80' + b'arm64\0\0\0\x80'
        data = b'IN\1\x10' + struct.pack('>HI', 2, 1) + tags + name + bytes.fromhex('a' * 32) + struct.pack('>I', 42)
        files = client.select_files(client.parse_install(data))
        self.assertEqual(files['_classic_era_/WowClassic-arm64.exe'], ('a' * 32, 42))
        with self.assertRaises(ValueError):
            client.parse_install(data[:-1])

    def test_blte_checks_sizes_and_chunk_hashes(self):
        plain = b'hello ARM64'
        chunk = b'Z' + zlib.compress(plain)
        data = b'BLTE' + struct.pack('>I', 36) + b'\x0f\0\0\1' + struct.pack('>II', len(chunk), len(plain)) + hashlib.md5(chunk).digest() + chunk
        self.assertEqual(client.blte_decode(data), plain)
        self.assertEqual(client.blte_decode(b'BLTE\0\0\0\0N' + plain), plain)
        with self.assertRaisesRegex(ValueError, 'checksum'):
            client.blte_decode(data[:-1] + bytes([data[-1] ^ 1]))
        with self.assertRaises(ValueError):
            client.blte_decode(data[:-2])
        with self.assertRaises(ValueError):
            client.blte_decode(b'BLTE\0\0\0\0Eencrypted')

    def test_encoding_lookup_and_missing_content(self):
        header = bytearray(22)
        header[:5] = b'EN\1\x10\x10'
        header[5:7] = (1).to_bytes(2, 'big')
        header[9:13] = (1).to_bytes(4, 'big')
        page = bytearray(1024)
        page[:38] = b'\1' + b'\0' * 5 + bytes.fromhex('a' * 32) + bytes.fromhex('b' * 32)
        encoding = bytes(header) + b'\0' * 32 + page
        self.assertEqual(client.ckeys_to_ekeys(encoding, {'a' * 32}), {'a' * 32: 'b' * 32})
        with self.assertRaises(ValueError):
            client.ckeys_to_ekeys(encoding, {'c' * 32})

    def test_range_requests_must_be_honored(self):
        cdn = client.CDN({'CDN Hosts': 'level3.blizzard.com'})
        class Response(io.BytesIO):
            status = 200
            headers = {}
        with patch.object(client.urllib.request, 'urlopen', return_value=Response(b'data')):
            with self.assertRaisesRegex(ValueError, 'honor'):
                cdn.fetch('data', 'a' * 32, (12, 4))

    def test_wrong_payload_hash_rejected(self):
        cdn = client.CDN({'CDN Hosts': 'level3.blizzard.com'})
        with patch.object(cdn, 'fetch', return_value=b'BLTE\0\0\0\0Nwrong'):
            with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                cdn.decoded('a' * 32, 'b' * 32)

    def test_checksum_failure_preserves_source_and_creates_no_output(self):
        with tempfile.TemporaryDirectory() as folder:
            source, output = Path(folder) / 'source', Path(folder) / 'staging'
            source.mkdir()
            build = self.write_build(source, ['wow_classic_era'])
            before = build.read_bytes()
            fake = type('FakeCDN', (), {})()
            fake.config = lambda key: {'install': ['a' * 32, 'b' * 32], 'encoding': ['c' * 32, 'd' * 32]}
            fake.decoded = lambda *a: (_ for _ in ()).throw(ValueError('checksum mismatch'))
            with patch.object(client, 'CDN', return_value=fake):
                with self.assertRaisesRegex(ValueError, 'checksum mismatch'):
                    client.prepare(source, output)
            self.assertEqual(build.read_bytes(), before)
            self.assertFalse(output.exists())

    def test_output_must_be_separate(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / 'source'
            source.mkdir()
            with self.assertRaisesRegex(ValueError, 'separate'):
                client.prepare(source, source / 'stage')


class ControllerRecipe(unittest.TestCase):
    def test_commands_fit_and_execute_against_api_stand_in(self):
        root = Path(__file__).resolve().parents[1]
        recipe = root / 'configs/controller-commands.txt'
        for line in recipe.read_text().splitlines():
            if line.startswith('/'):
                self.assertLessEqual(len(line), 255)
        lua = shutil.which('lua') or shutil.which('lua5.4')
        if not lua:
            self.skipTest('Lua 5.2+ unavailable; recipe length checked, simulated API execution skipped')
        result = subprocess.run([lua, str(root / 'tests/controller_harness.lua'), str(recipe)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
