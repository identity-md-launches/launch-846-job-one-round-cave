# Proxy Authority

Read-only EIP-1967 authority reconnaissance using Python 3 and only the standard library. It pins the scan to one Ethereum block, reads the transparent-proxy admin and beacon slots, resolves a beacon's `implementation()` return when one is present, and records the beacon's `owner()` return as an explicitly unverified authority candidate. It checks target code sizes and rechecks the block hash before returning. It never signs, sends, accesses wallets, reads environment variables, or uses proxy environment settings.

From the repository root, this network-free command shows the parser and assessment working:

```sh
python3 line-3/tools/proxy-authority/proxy_authority.py --self-test
```

For a real chain scan of ZTO (the default):

```sh
python3 line-3/tools/proxy-authority/proxy_authority.py
```

Use `--address 0x...` for another mainnet contract or `--rpc https://eth.drpc.org` for the alternative endpoint. Responses are capped at 1 MiB and require JSON-RPC 2.0, request id `1`, and `result`.

## Tried this round

The offline self-test passed. A pinned live read of ZTO at Ethereum block 26135607 (hash `0xdb21c24d5e85bb126bb7d4297a03bfb397e0ac836a4076188f10ca162abb7cab`) returned zero EIP-1967 admin and beacon slots, so the tool reported no observable EIP-1967 authority and did not attempt arbitrary calls. Its start/end block hashes matched. This does not establish that ZTO is immutable.

## Limits

An empty EIP-1967 slot is not a proof of immutability. The tool does not discover custom proxy slots, diamonds, minimal-clone routing, timelocks, multisig membership, access-control roles, or upgrade authorization logic. A successful `owner()` response is merely reported: it is not proof of a privilege or an upgrade path. RPC results are still provider-supplied evidence.
