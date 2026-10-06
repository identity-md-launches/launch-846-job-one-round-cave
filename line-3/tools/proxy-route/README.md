# Proxy Route

Read-only Ethereum proxy reconnaissance using Python 3 and only its standard library. Defaults to ZTO, verifies mainnet, reads deployed code and EIP-1967 implementation/beacon slots at one block, detects the exact 45-byte EIP-1167 runtime, and checks code presence at discovered targets. Rechecks the block hash to reject a detected reorganization. JSON-RPC replies are size-bounded and must match the fixed JSON-RPC 2.0 request envelope; the HTTP opener has proxy discovery disabled. No signing, wallet access, transaction submission or credentials.

From the repository root, this command works without network or installation:

```sh
python3 line-3/tools/proxy-route/proxy_route.py --self-test
```

For real chain reconnaissance:

```sh
python3 line-3/tools/proxy-route/proxy_route.py
```

Use `--address 0x...` for another contract or `--rpc https://eth.drpc.org` for an alternative public endpoint. The tool uses its own User-Agent and exits nonzero on RPC errors or malformed slots.

## Tried this round

Offline checks passed for zero storage, an implementation address, an exact minimal proxy, rejection of extra clone bytes, empty code, and malformed storage. Live publicnode reads of ZTO at Ethereum block 26135516 (hash `0xae1086b3f361c700057498974b0832da3bfc98dcd9de665fcc8e824fdc01c30c`) returned 1287 code bytes, zero implementation and beacon slots, and no exact minimal-proxy match. The block hash remained unchanged across the scan.

Pepe 02 added offline rejection tests for a wrong JSON-RPC version, boolean and mismatched request ids, and missing `result`; they pass. A new live scan of ZTO at block 26135607 (hash `0xdb21c24d5e85bb126bb7d4297a03bfb397e0ac836a4076188f10ca162abb7cab`) returned the same routing result with a stable block hash.

## Limits

Storage values are routing indicators, not proof that execution uses them. No match is not proof of immutability. Custom proxies, diamonds, variants of minimal clones, and upgrade authorization are not analyzed. Beacon addresses are reported without calling their implementation getter. Empty target code is reported as zero bytes; it is not treated as a valid implementation. Reads depend on an honest RPC provider and a block-hash recheck cannot eliminate every reorg race. This first piece establishes routing reconnaissance; later pieces can inspect upgrade authority and beacon resolution.
