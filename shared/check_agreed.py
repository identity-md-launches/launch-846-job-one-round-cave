"""Offline checks for the agreement-gated call preview."""
from unittest.mock import patch
import agreed_preview as p


def check():
    endpoints = ['https://a.invalid', 'https://b.invalid']
    block_hash = '0x' + 'ab' * 32
    sample = {'status': 'agreement', 'common_height': 100,
              'common_blocks': [{'block_hash': block_hash}] * 2}
    with patch.object(p.agreement, 'compare', return_value=sample) as compare, \
         patch.object(p.call_preview, 'rpc_call', return_value={'result': '0x' + (42).to_bytes(32, 'big').hex()}) as call, \
         patch.object(p.rpc_health, 'rpc', return_value={'number': '0x64', 'hash': block_hash}) as rpc:
        result = p.preview(endpoints)
        assert result['preview']['decoded'] == '42' and result['sent'] is False
        assert call.call_args.args[2] == '0x64'
        assert [c.args[0] for c in rpc.call_args_list] == endpoints
        for status in ['disagreement', 'inconclusive', 'lagging']:
            compare.return_value = {'status': status}
            call.reset_mock()
            assert p.preview(endpoints)['status'] == 'blocked'
            call.assert_not_called()
        compare.return_value = sample
        for bad in [{'number': '0x65', 'hash': block_hash}, {'number': '0x64', 'hash': '0x' + 'cd' * 32}]:
            rpc.side_effect = [{'number': '0x64', 'hash': block_hash}, bad]
            try:
                p.preview(endpoints)
            except ValueError:
                pass
            else:
                raise AssertionError('second-provider block change accepted')
        rpc.side_effect = None
        call.return_value = {'error': {'code': 3, 'message': 'execution reverted', 'data': '0xdb42144d'}}
        assert p.preview(endpoints)['preview']['status'] == 'reverted'
        call.return_value = {'error': {'code': -32000, 'message': 'unavailable'}}
        assert p.preview(endpoints)['preview']['status'] == 'rpc_error'
        call.return_value = {'result': '0x'}
        assert 'decode_error' in p.preview(endpoints)['preview']
    for invalid in [[], endpoints[:1], [endpoints[0]] * 2]:
        try:
            p.preview(invalid)
        except ValueError:
            pass
        else:
            raise AssertionError('insufficient independent endpoint URLs accepted')
    p.agreement.demo()
    print('PASS: agreement gate, exact height, both rechecks, drift rejection, revert/RPC/decode outcomes')


if __name__ == '__main__':
    check()
