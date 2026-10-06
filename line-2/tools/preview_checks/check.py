#!/usr/bin/env python3
"""Offline regression checks for unsigned call preview; no network or secrets."""
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch

path = Path(__file__).resolve().parents[1] / 'call_preview' / 'call_preview.py'
spec = importlib.util.spec_from_file_location('preview', path)
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)


class PreviewChecks(unittest.TestCase):
    def parse(self, value):
        return p.parse_response(json.dumps(value).encode())

    def test_envelopes(self):
        good = {'jsonrpc': '2.0', 'id': 1, 'result': '0x'}
        self.assertEqual(self.parse(good), good)
        bad = [dict(good, id=True), dict(good, id=2), dict(good, id='1'),
               dict(good, jsonrpc='1.0'), {'id': 1, 'result': '0x'},
               dict(good, error={'code': 3, 'message': 'reverted'}),
               {'jsonrpc': '2.0', 'id': 1}, dict(good, result='0x0'),
               {'jsonrpc': '2.0', 'id': 1, 'error': {'code': True, 'message': 'bad'}}]
        for value in bad:
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.parse(value)
        error = {'jsonrpc': '2.0', 'id': 1, 'error': {'code': 3, 'message': 'execution reverted'}}
        self.assertEqual(self.parse(error), error)

    def test_size_and_json(self):
        for raw in [b'x', b'[]', b' ' * (p.MAX_RESPONSE_BYTES + 1)]:
            with self.assertRaises(ValueError):
                p.parse_response(raw)

    def test_transport_read_bound(self):
        class Response:
            requested = None
            def __enter__(self):
                return self
            def __exit__(self, *args):
                pass
            def read(self, size):
                self.requested = size
                return b' ' * size
        response = Response()
        class Opener:
            def open(self, request, timeout):
                return response
        with patch.object(p.urllib.request, 'build_opener', return_value=Opener()):
            with self.assertRaises(ValueError):
                p.rpc_call('https://example.invalid', {'to': p.ZTO}, 'latest')
        self.assertEqual(response.requested, p.MAX_RESPONSE_BYTES + 1)

    def test_returns(self):
        word = lambda n: '0x' + n.to_bytes(32, 'big').hex()
        self.assertEqual(p.decode_result(word(2**256 - 1), 'uint256'), str(2**256 - 1))
        self.assertIs(p.decode_result(word(1), 'bool'), True)
        self.assertIs(p.decode_result(word(0), 'bool'), False)
        self.assertEqual(p.decode_result(word(1), 'address'), '0x' + '0'*39 + '1')
        for raw, kind in [(word(2), 'bool'), (word(2**160), 'address'), ('0x', 'uint256')]:
            with self.assertRaises(ValueError):
                p.decode_result(raw, kind)

    def test_reverts(self):
        word = lambda n: n.to_bytes(32, 'big').hex()
        error = '0x08c379a0' + word(32) + word(4) + b'nope'.hex() + '00'*28
        self.assertEqual(p.explain_revert(error), {'kind': 'Error(string)', 'message': 'nope'})
        self.assertEqual(p.explain_revert('0x4e487b71' + word(17))['code'], '0x11')
        self.assertEqual(p.explain_revert('0xdb42144d')['selector'], '0xdb42144d')
        self.assertEqual(p.explain_revert(error[:74])['kind'], 'custom_or_unknown_error')
        self.assertEqual(p.revert_data({'originalError': {'data': '0xdb42144d'}}), '0xdb42144d')


if __name__ == '__main__':
    unittest.main(verbosity=2)
