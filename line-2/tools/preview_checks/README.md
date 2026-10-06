# Preview checks

Offline, standard-library regression checks for the unsigned Ethereum call preview. They exercise strict JSON-RPC identity/version and result/error exclusivity, malformed error objects, size limits, ABI scalar boundaries, nested revert data, and truncated Error(string) payloads. No network, keys, environment discovery or transaction sending is involved.

From the repository root:

```sh
python3 -B line-2/tools/preview_checks/check.py
```

Tried: all five test groups passed. The repaired companion preview rejects boolean IDs, missing versions, conflicting result/error envelopes and responses larger than 262144 bytes. Its HTTP reader requests at most 262145 bytes before rejection. A live read-only ZTO transfer preview against PublicNode still returned the expected `reverted` outcome, selector `0xdb42144d`.

These checks establish behavior for supplied fixtures, not provider honesty or future transaction success. Unknown custom errors remain selectors. Response bounds apply to the body, not transport headers; Python's JSON parser may reject very deeply nested bodies. The preview reports those as RPC errors.
