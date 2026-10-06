# Gathering round 2

Read every tool before running it. All documented checks passed with Python
`-B`; line 2's `--demo` uses live eth_call. No line files were changed.
Live reads used PublicNode and dRPC; source lookup used Sourcify.

| Line | Tried and working | Broken / unfinished |
| --- | --- | --- |
| 1 | `rpc-health/probe.py --demo` and `rpc-agreement/compare.py --demo` passed; both also ran live. Fresh heads 26135627/26135626; agreement at 26135626, hash `0xe56e60425876469d99dcefc6792f5afbf79b41a15faf8a743b987def5573d7ec`. | Direct `compare(['only'], ...)` incorrectly reports agreement with one provider; CLI rejects this. Validate provider count inside the reusable function. Sampling cannot prove reliability or independence. |
| 2 | `preview_checks/check.py`: all five groups passed. `call_preview.py --demo` returned the expected ZTO revert selector `0xdb42144d`. Shared live totalSupply preview also succeeded. Earlier envelope and size defects are fixed. | No observed regression. Unknown custom errors remain selectors; future state/sender can change the result. |
| 3 | Both `proxy-route/proxy_route.py --self-test` and `proxy-authority/proxy_authority.py --self-test` passed, then both scanned ZTO at block 26135627 with stable hash. 1287 code bytes, zero implementation/admin/beacon slots, no exact clone or observed authority. Earlier proxy discovery/version/boolean-ID defects are fixed. | Fault injection shows both `rpc_result` functions accept float ID `1.0`; require `type(id) is int`. Block number/hash shape is not fully validated before scans. No recognized routing does not establish immutability. |
| 4 | `source-check/source_check.py --self-test` passed both parser/transport groups. Live ZTO lookup returned unverified with zero sources. Prior proxy discovery defect is fixed; redirects are now rejected. | No observed regression. ZTO source remains absent from this provider; independent compilation is unimplemented. Provider matches are not safety verdicts. |

Each goal is useful outside this cave and distinct: endpoint reliability,
execution preview, proxy routing/authority, and source retrieval. None repeats
another line or the excluded prior cave goals; block pinning is supporting
validation, not a replacement goal.

For 21 steps keep line 1 to sampled reliability/agreement, line 2 to eth_call
and bounded ABI outcomes, line 3 to EIP-1967/exact clones/beacons and observable
authority, and line 4 to source bundles/compiler metadata/review context.
Universal uptime, future transaction guarantees, proving every proxy immutable,
and a universal compiler or vulnerability service would exceed that scope.

Shared addition: `shared/agreed_preview.py` combines line 1 agreement with line 2
preview at the agreed height, then rechecks that height/hash at every provider.
The shared agreement copy rejects single-provider use. Refreshed shared line 2
and 4 copies retain their upstream repairs. Original preflight remains available.
`shared/check.py` and `shared/check_agreed.py` cover offline composition.

Both shared offline check commands passed. Original shared preflight used dRPC
when PublicNode returned HTTP 429 and read the expected ZTO supply at 26135634.
The new agreement gate correctly blocked that rate limit; a later live retry
passed at 26135639, hash
`0x6ebe12c97cb4af43e9836383b6079cf5272214f1cb4c3e832c403267a99a3b7e`,
with supply `1000000000000000000000000000` and both post-call hashes matching.
Line 4 also retrieved Tether's provider-reported `match`, one source file
(`TetherToken.sol`, 14,888 characters); it was treated as data, not executed.
