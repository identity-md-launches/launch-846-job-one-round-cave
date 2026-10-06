# Call preview

`call_preview.py` uses `eth_call` to preview an unsigned Ethereum interaction. It sends no transaction, reads no keys, and reports raw return data or an ABI `Error(string)`, `Panic(uint256)`, or custom-error selector when an RPC exposes revert data. The default demo previews a one-base-unit ZTO transfer from an address with no tokens, so it should revert without changing any balance.

Run from the repository root:

```sh
python3 line-2/tools/call_preview/call_preview.py --demo
```

For a custom preview, use `--to 0x... --data 0x...`, optionally with `--from`, `--value-wei`, `--gas`, `--block`, `--rpc`, and `--result-type`. `--block` accepts a decimal height, a hex height, or a standard block tag. A revert is an observed EVM outcome and exits zero; network and malformed RPC responses exit two. The preview reflects the chosen node's state at the chosen block and does not guarantee a later transaction will behave identically.

Tried against `https://ethereum-rpc.publicnode.com`: `--demo` returned `reverted` with custom selector `0xdb42144d`. A separate `totalSupply()` preview (`--to 0xd782bdea4ef02a0bd391eb9089470c8080f0a68e --data 0x18160ddd --result-type uint256`) returned `succeeded` and decoded a 32-byte integer. Custom errors without an ABI remain selectors; a preview can change as chain state changes.

Round 2 repair: responses are now capped at 262144 bytes and must carry JSON-RPC 2.0, the exact integer request ID, and exactly one valid result or error. Boolean IDs are rejected. Run the offline regression suite with `python3 -B line-2/tools/preview_checks/check.py`. The live ZTO demo was repeated successfully after this repair.
