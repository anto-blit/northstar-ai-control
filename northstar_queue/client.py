"""Model-agnostic tool transport; stdin commands perform HTTP calls only.

This executable is a scripted client, not a learned agent or OS sandbox.
Capabilities are supplied on stdin, never on command lines or in reports.
"""
import json
import sys
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener


def call(url, token, route, body):
    address = urlsplit(url)
    if address.scheme != "http" or address.hostname != "127.0.0.1" or address.path:
        raise ValueError("Only the local experiment service is allowed")
    if route not in ("/agent", "/worker", "/operator", "/audit", "/unknown"):
        raise ValueError("Unsupported route")
    request = Request(url + route, json.dumps(body).encode("utf-8"),
                      {"Authorization": "Bearer " + token, "Content-Type": "application/json"})
    # Do not route loopback bearer credentials through environment proxy settings.
    opener = build_opener(ProxyHandler({}))
    try:
        with opener.open(request, timeout=10) as response:
            return {"status": response.status, "body": json.load(response)}
    except HTTPError as response:
        with response:
            return {"status": response.code, "body": json.load(response)}


def main():
    config = json.loads(sys.stdin.readline())
    for line in sys.stdin:
        command = json.loads(line)
        result = call(config["url"], config["token"], command["route"], command["body"])
        print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
