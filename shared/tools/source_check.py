#!/usr/bin/env python3
"""Read-only Sourcify source discovery; no credentials or filesystem access."""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request

ZTO = '0xd782bdea4ef02a0bd391eb9089470c8080f0a68e'
BASE = 'https://sourcify.dev/server/v2/contract/1/'
LIMIT = 8 * 1024 * 1024


def public_opener():
    # An explicit empty mapping prevents urllib from discovering proxy settings.
    # Reject redirects so an API response cannot steer this reader elsewhere.
    class NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            raise ValueError('Source provider redirect refused')
    return urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())


def summarize(data, address):
    if not isinstance(data, dict):
        raise ValueError('Expected an object')
    if str(data.get('chainId')) != '1' or str(data.get('address', '')).lower() != address.lower():
        raise ValueError('Response chain or address differs from request')
    if 'match' not in data:
        raise ValueError('Missing verification match')
    match = data['match']
    if match not in (None, 'exact_match', 'match'):
        raise ValueError('Unrecognized verification match')
    sources = data.get('sources', {})
    if sources is None:
        sources = {}
    if not isinstance(sources, dict):
        raise ValueError('Invalid sources object')
    bundle = {}
    for name, entry in sources.items():
        if not isinstance(name, str) or not isinstance(entry, dict) or not isinstance(entry.get('content'), str):
            raise ValueError('Invalid source entry')
        # Keep filenames as data, never write paths supplied by a server.
        bundle[name] = entry['content']
    return {'chainId': 1, 'address': address.lower(), 'provider': 'Sourcify',
            'match': match, 'status': 'unverified' if match is None else
            ('source_available' if bundle else 'verified_without_source'),
            'sourceCount': len(bundle), 'sources': bundle,
            'limitation': 'Provider-reported verification; not an independent bytecode rebuild or safety assessment.'}


def fetch(address):
    if not isinstance(address, str) or not re.fullmatch(r'0x[0-9a-fA-F]{40}', address):
        raise ValueError('address must be a 20-byte hex address')
    request = urllib.request.Request(BASE + address + '?fields=all',
                                    headers={'User-Agent': 'Pepeolithic-Line4-SourceCheck/1.0',
                                             'Accept': 'application/json'})
    try:
        response = public_opener().open(request, timeout=30)
    except urllib.error.HTTPError as error:
        if error.code != 404:
            raise
        # Sourcify returns a structured null-match object with HTTP 404.
        response = error
    with response:
        raw = response.read(LIMIT + 1)
    if len(raw) > LIMIT:
        raise ValueError('Response exceeds 8 MiB limit')
    return summarize(json.loads(raw), address)


def self_test():
    transport_test()
    base = {'chainId': '1', 'address': ZTO, 'match': None}
    assert summarize(base, ZTO)['status'] == 'unverified'
    matched = dict(base, match='exact_match', sources={'../a.sol': {'content': 'contract A {}'}})
    result = summarize(matched, ZTO)
    assert result['sourceCount'] == 1 and result['sources']['../a.sol'] == 'contract A {}'
    assert summarize(dict(base, match='match'), ZTO)['status'] == 'verified_without_source'
    for bad in (dict(base, chainId='2'), dict(base, address='0x0'),
                dict(base, match='unknown'), dict(base, sources=[]),
                dict(base, sources={'a': {'content': 2}})):
        try:
            summarize(bad, ZTO)
        except ValueError:
            continue
        raise AssertionError('Malformed response accepted')
    print('PASS: absent, matched, missing-source, mismatched identity, malformed payload, path-as-data')


def transport_test():
    # Fail immediately if urllib tries to discover proxies; no environment is read.
    from unittest.mock import patch
    from io import BytesIO
    payload = json.dumps({'chainId': '1', 'address': ZTO, 'match': None}).encode()
    with patch.object(urllib.request, 'getproxies', side_effect=AssertionError('Proxy discovery')):
        opener = public_opener()
        assert not any(isinstance(h, urllib.request.ProxyHandler) for h in opener.handlers)
        with patch.object(urllib.request.OpenerDirector, 'open', return_value=BytesIO(payload)) as call:
            assert fetch(ZTO)['status'] == 'unverified'
            request = call.call_args.args[0]
            assert request.full_url == BASE + ZTO + '?fields=all'
            assert request.get_header('User-agent').startswith('Pepeolithic-')
            assert call.call_args.kwargs['timeout'] == 30
        error = urllib.error.HTTPError(BASE + ZTO, 404, 'Not found', {}, BytesIO(payload))
        with patch.object(urllib.request.OpenerDirector, 'open', side_effect=error):
            assert fetch(ZTO)['status'] == 'unverified'
        for raw in (b'not JSON', b'x' * (LIMIT + 1)):
            with patch.object(urllib.request.OpenerDirector, 'open', return_value=BytesIO(raw)):
                try:
                    fetch(ZTO)
                except ValueError:
                    pass
                else:
                    raise AssertionError('Invalid response accepted')
        redirect = next(h for h in opener.handlers if isinstance(h, urllib.request.HTTPRedirectHandler))
        for target in ('https://example.invalid/', 'file:///outside-workspace'):
            try:
                redirect.redirect_request(None, None, 302, 'Found', {}, target)
            except ValueError:
                pass
            else:
                raise AssertionError('Redirect accepted')
        with patch.object(urllib.request.OpenerDirector, 'open', side_effect=AssertionError('Network reached')):
            try:
                fetch('../not-an-address')
            except ValueError:
                pass
            else:
                raise AssertionError('Invalid address accepted')
    print('PASS: no proxy discovery, bounded transport, structured 404, redirect rejection, address validation')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--address', default=ZTO)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0
    if not re.fullmatch(r'0x[0-9a-fA-F]{40}', args.address):
        parser.error('address must be a 20-byte hex address')
    try:
        print(json.dumps(fetch(args.address), indent=2, sort_keys=True))
        return 0
    except (ValueError, urllib.error.URLError, TimeoutError) as error:
        print('Source lookup failed: ' + str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
