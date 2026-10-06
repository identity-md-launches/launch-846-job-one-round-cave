#!/usr/bin/env python3
"""Read-only eth_call preview of an unsigned Ethereum contract interaction."""

import argparse
import json
import re
import sys
import urllib.error
import urllib.request


ZTO = "0xd782bdea4ef02a0bd391eb9089470c8080f0a68e"
POOL_MANAGER = "0x000000000004444c5dc75cb358380d2e3de08a90"
DEMO_FROM = "0x0000000000000000000000000000000000000001"
DEFAULT_RPC = "https://ethereum-rpc.publicnode.com"
MAX_RESPONSE_BYTES = 262144

USER_AGENT = "IdentityMD-call-preview/1.0 (read-only eth_call)"


def address(value):
    if not re.fullmatch(r"0x[0-9a-fA-F]{40}", value):
        raise argparse.ArgumentTypeError("expected a 20-byte 0x-prefixed address")
    return value.lower()


def calldata(value):
    if not re.fullmatch(r"0x(?:[0-9a-fA-F]{2})*", value):
        raise argparse.ArgumentTypeError("expected even-length 0x-prefixed hex data")
    return value.lower()


def nonnegative_int(value):
    try:
        number = int(value, 0) if value.startswith("0x") else int(value, 10)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("expected a nonnegative integer") from exc
    if number < 0:
        raise argparse.ArgumentTypeError("expected a nonnegative integer")
    return number


def block_tag(value):
    if value in ("latest", "safe", "finalized", "earliest", "pending"):
        return value
    return hex(nonnegative_int(value))


def rpc_call(url, transaction, block):
    request = urllib.request.Request(
        url,
        data=json.dumps({"jsonrpc": "2.0", "id": 1, "method": "eth_call",
                         "params": [transaction, block]}, separators=(",", ":")).encode(),
        headers={"Content-Type": "application/json", "User-Agent": USER_AGENT},
        method="POST",
    )
    # Explicit empty proxy map avoids consulting the host's proxy environment.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(request, timeout=20) as response:
        raw = response.read(MAX_RESPONSE_BYTES + 1)
    return parse_response(raw)



def parse_response(raw):
    """Bound and validate an eth_call JSON-RPC envelope before interpreting it."""
    if len(raw) > MAX_RESPONSE_BYTES:
        raise ValueError("JSON-RPC response exceeds size limit")
    payload = json.loads(raw)
    if (not isinstance(payload, dict) or payload.get("jsonrpc") != "2.0"
            or type(payload.get("id")) is not int or payload["id"] != 1
            or (("result" in payload) == ("error" in payload))):
        raise ValueError("malformed JSON-RPC response envelope")
    if "error" in payload:
        error = payload["error"]
        if (not isinstance(error, dict) or type(error.get("code")) is not int
                or not isinstance(error.get("message"), str)):
            raise ValueError("malformed JSON-RPC error")
    elif (not isinstance(payload["result"], str)
          or not re.fullmatch(r"0x(?:[0-9a-fA-F]{2})*", payload["result"])):
        raise ValueError("invalid eth_call result")
    return payload

def revert_data(value):
    """Find an ABI revert payload in common JSON-RPC error shapes."""
    if isinstance(value, str):
        if re.fullmatch(r"0x(?:[0-9a-fA-F]{2}){4,}", value):
            return value.lower()
        return None
    if isinstance(value, dict):
        for key in ("data", "result", "return", "originalError"):
            found = revert_data(value.get(key))
            if found:
                return found
        for child in value.values():
            found = revert_data(child)
            if found:
                return found
    if isinstance(value, list):
        for child in value:
            found = revert_data(child)
            if found:
                return found
    return None


def explain_revert(payload):
    if not payload:
        return None
    raw = bytes.fromhex(payload[2:])
    selector = payload[:10]
    if selector == "0x08c379a0" and len(raw) >= 4 + 64:
        offset = int.from_bytes(raw[4:36], "big")
        start = 4 + offset
        if start + 32 <= len(raw):
            length = int.from_bytes(raw[start:start + 32], "big")
            if start + 32 + length <= len(raw):
                message = raw[start + 32:start + 32 + length].decode("utf-8", "replace")
                return {"kind": "Error(string)", "message": message}
    if selector == "0x4e487b71" and len(raw) >= 36:
        return {"kind": "Panic(uint256)", "code": hex(int.from_bytes(raw[4:36], "big"))}
    return {"kind": "custom_or_unknown_error", "selector": selector}


def decode_result(raw, kind):
    if kind == "raw":
        return raw
    data = bytes.fromhex(raw[2:])
    if len(data) != 32:
        raise ValueError(f"{kind} decoding needs exactly one 32-byte return word")
    number = int.from_bytes(data, "big")
    if kind == "uint256":
        return str(number)
    if kind == "bool":
        if number not in (0, 1):
            raise ValueError("bool return word must be 0 or 1")
        return bool(number)
    if number >> 160:
        raise ValueError("address return word has nonzero high bytes")
    return "0x" + data[-20:].hex()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo", action="store_true", help="preview a one-base-unit ZTO transfer from an empty address")
    parser.add_argument("--to", type=address, help="contract address")
    parser.add_argument("--from", dest="sender", type=address, help="hypothetical sender address")
    parser.add_argument("--data", type=calldata, default="0x", help="ABI calldata, default 0x")
    parser.add_argument("--value-wei", type=nonnegative_int, default=0)
    parser.add_argument("--gas", type=nonnegative_int, help="optional gas limit for the preview")
    parser.add_argument("--block", type=block_tag, default="latest")
    parser.add_argument("--rpc", default=DEFAULT_RPC, help="Ethereum JSON-RPC HTTPS endpoint")
    parser.add_argument("--result-type", choices=("raw", "uint256", "bool", "address"), default="raw")
    args = parser.parse_args(argv)
    if args.demo:
        if args.to or args.sender or args.data != "0x" or args.value_wei or args.gas is not None:
            parser.error("--demo cannot be combined with transaction fields")
        args.to = ZTO
        args.sender = DEMO_FROM
        args.data = "0xa9059cbb" + POOL_MANAGER[2:].rjust(64, "0") + (1).to_bytes(32, "big").hex()
        args.result_type = "bool"
    if not args.to:
        parser.error("--to is required unless --demo is used")
    if not args.rpc.startswith("https://"):
        parser.error("--rpc must be an HTTPS URL")

    transaction = {"to": args.to, "data": args.data, "value": hex(args.value_wei)}
    if args.sender:
        transaction["from"] = args.sender
    if args.gas is not None:
        transaction["gas"] = hex(args.gas)
    report = {"method": "eth_call", "block": args.block, "transaction": transaction,
              "sent": False}
    try:
        response = rpc_call(args.rpc, transaction, args.block)
        if "error" in response:
            error = response["error"]
            raw = revert_data(error)
            message = error.get("message", "") if isinstance(error, dict) else str(error)
            is_revert = bool(raw) or "revert" in message.lower()
            report["status"] = "reverted" if is_revert else "rpc_error"
            report["error"] = {"message": message}
            if raw:
                report["error"]["data"] = raw
                report["error"]["decoded"] = explain_revert(raw)
        else:
            raw = response.get("result")
            if not isinstance(raw, str) or not re.fullmatch(r"0x(?:[0-9a-fA-F]{2})*", raw):
                raise ValueError("missing or invalid eth_call result")
            report["status"] = "succeeded"
            report["return_data"] = raw.lower()
            if args.result_type != "raw":
                try:
                    report["decoded_return"] = decode_result(raw, args.result_type)
                except ValueError as exc:
                    report["decode_error"] = str(exc)
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError, RecursionError) as exc:
        report["status"] = "rpc_error"
        report["error"] = {"message": str(exc)}
    print(json.dumps(report, indent=2))
    return 0 if report["status"] in ("succeeded", "reverted") else 2


if __name__ == "__main__":
    sys.exit(main())
