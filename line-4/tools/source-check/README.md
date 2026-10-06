# Source Check

Discover publicly verified Ethereum source through Sourcify's public API. Python 3 standard library only. Defaults to ZTO on mainnet. Prints a JSON source bundle to stdout; never writes server-supplied filenames, reads credentials, signs or sends transactions. Uses a dedicated User-Agent, a 30-second timeout and an 8 MiB response limit.

From the repository root, demonstrate the parser offline:

```sh
python3 line-4/tools/source-check/source_check.py --self-test
```

For the real contract:

```sh
python3 line-4/tools/source-check/source_check.py
```

Use `--address 0x...` to inspect another Ethereum contract. Output keeps source paths as JSON keys, including unsafe-looking paths, without extracting them. Exit 0 means the lookup completed, including a null match; exit 1 means a network or response error. Missing source is not proof of unsafe code, nor does a match prove safe code.

## Tried this round

Offline checks passed for absent source, exact and partial matches, missing source content, mismatched chain/address, malformed entries, and paths treated strictly as data. Live ZTO lookup returned HTTP 404 with a valid null-match JSON object: `unverified`, zero sources. The tool handles this provider convention without treating arbitrary 404 pages as successful lookups. A live mainnet Tether lookup at `0xdAC17F958D2ee523a2206206994597C13D831ec7` returned `match`, one source, `TetherToken.sol` with 14,888 characters.

## Limits

This first piece retrieves provider-reported verification and source, not an independent compiler rebuild. Partial matches are preserved as `match`, never upgraded to exact verification. Compiler settings, imports, proxy implementations, and chain bytecode comparison remain future work. Availability depends on Sourcify and internet access; the offline demonstration needs neither. Source content is untrusted review material.

## Round 2: explicit public transport

Fixed the gathering report's proxy-discovery issue: every lookup now uses an
explicit empty proxy mapping. It does not discover proxy environment settings.
Provider redirects are rejected, and direct Python callers get the same address
validation as CLI users. Existing bundle fields and null-match behavior remain.

Run the working offline demonstration from the repository root:

```sh
python3 -B line-4/tools/source-check/source_check.py --self-test
```

Tried on 2026-10-06: both offline PASS groups completed. Regression checks make
proxy discovery raise immediately, exercise the actual fetch path with a mocked
transport, preserve structured HTTP 404 handling, reject oversized and malformed
responses, reject redirects, and reject invalid addresses before networking.
No environment settings or credentials are read by the demonstration.

Live checks with the repaired transport: ZTO returned `unverified`, zero sources;
Tether at `0xdAC17F958D2ee523a2206206994597C13D831ec7` returned `match`, one source,
`TetherToken.sol`. No source files were extracted or executed. Both requests were
read-only. An installation that requires an outbound proxy now fails directly;
redirecting provider URLs also fail instead of being followed. Python standard
library only; no dependencies to install for offline verification.
